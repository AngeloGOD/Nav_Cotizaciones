from datetime import date, datetime, timedelta

from fuente.negocio.controlador.ControladorRegistrarCliente import (
    ControladorRegistrarCliente,
)


class ControladorClientes:
    _TAMANO_LOTE_CONTEO = 500
    _TIPOS_PERSONA = {
        "FISICA": "FISICA",
        "PERSONA FISICA": "FISICA",
        "PERSONA FÍSICA": "FISICA",
        "MORAL": "MORAL",
        "PERSONA MORAL": "MORAL",
        "EXTRANJERO": "EXTRANJERO",
    }

    def __init__(self, servicio_cliente):
        self.servicio_cliente = servicio_cliente
        self.controlador_registro = ControladorRegistrarCliente(servicio_cliente)

    def registrar_cliente(
        self,
        razon_social,
        tipo_persona,
        direccion=None,
        rfc=None,
        telefono=None,
        correo_elect=None,
        es_nuevo_cliente=False,
        activo=True,
    ):
        return self.controlador_registro.registrar_cliente(
            razon_social=razon_social,
            tipo_persona=tipo_persona,
            direccion=direccion,
            rfc=rfc,
            telefono=telefono,
            correo_elect=correo_elect,
            es_nuevo_cliente=es_nuevo_cliente,
            activo=activo,
        )

    @staticmethod
    def _valores_filtro(valor):
        if valor is None:
            return []
        if isinstance(valor, str):
            return [valor]
        return list(valor)

    @staticmethod
    def _normalizar_fecha(valor, etiqueta):
        if valor in (None, ""):
            return None, None
        if isinstance(valor, datetime):
            return valor, valor.date()
        if isinstance(valor, date):
            return valor, valor
        if isinstance(valor, str):
            texto = valor.strip()
            if not texto:
                return None, None
            for formato in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    fecha = datetime.strptime(texto, formato).date()
                    return texto, fecha
                except ValueError:
                    continue
            try:
                fecha_hora = datetime.fromisoformat(texto)
            except ValueError as error:
                raise ValueError(
                    f"La fecha '{etiqueta}' no es válida. Usa el formato dd/mm/aaaa."
                ) from error
            return texto, fecha_hora.date()
        raise ValueError(
            f"La fecha '{etiqueta}' no es válida. Usa el formato dd/mm/aaaa."
        )

    @classmethod
    def normalizar_filtros(cls, filtros=None, texto=""):
        filtros = filtros or {}
        filtros_servicio = {}

        tipos_crudos = cls._valores_filtro(filtros.get("tipos_persona"))
        tipos = set()
        for valor in tipos_crudos:
            tipo = cls._TIPOS_PERSONA.get(str(valor).strip().upper())
            if tipo is None:
                raise ValueError("El filtro de tipo de persona contiene una opción no válida.")
            tipos.add(tipo)
        if tipos and len(tipos) < len(set(cls._TIPOS_PERSONA.values())):
            filtros_servicio["tipo_persona"] = sorted(tipos)

        estados = {
            str(valor).strip().upper()
            for valor in cls._valores_filtro(filtros.get("estados"))
        }
        estados_validos = estados & {"ACTIVO", "INACTIVO"}
        if estados - {"ACTIVO", "INACTIVO"}:
            raise ValueError("El filtro de estado contiene una opción no válida.")
        if len(estados_validos) == 1:
            filtros_servicio["estado_activo"] = [
                next(iter(estados_validos)) == "ACTIVO"
            ]

        tipos_cliente = {
            str(valor).strip().upper()
            for valor in cls._valores_filtro(filtros.get("tipos_cliente"))
        }
        tipos_cliente_validos = tipos_cliente & {"NUEVO", "EXISTENTE"}
        if tipos_cliente - {"NUEVO", "EXISTENTE"}:
            raise ValueError("El filtro de tipo de cliente contiene una opción no válida.")
        if len(tipos_cliente_validos) == 1:
            filtros_servicio["es_nuevo"] = [
                next(iter(tipos_cliente_validos)) == "NUEVO"
            ]

        fecha_desde, fecha_desde_obj = cls._normalizar_fecha(
            filtros.get("fecha_desde"), "desde"
        )
        fecha_hasta, fecha_hasta_obj = cls._normalizar_fecha(
            filtros.get("fecha_hasta"), "hasta"
        )
        if fecha_desde and fecha_hasta and fecha_desde_obj > fecha_hasta_obj:
            raise ValueError("La fecha 'desde' no puede ser posterior a la fecha 'hasta'.")
        if fecha_desde:
            filtros_servicio["fecha_desde"] = fecha_desde
        if fecha_hasta:
            filtros_servicio["fecha_hasta"] = fecha_hasta

        texto = (texto or "").strip()
        if texto:
            filtros_servicio["nombre"] = texto

        return filtros_servicio

    @staticmethod
    def _fecha_cliente(cliente, zona_local):
        fecha_creacion = getattr(cliente, "creado_en", None)
        if isinstance(fecha_creacion, datetime):
            if fecha_creacion.tzinfo is not None:
                fecha_creacion = fecha_creacion.astimezone(zona_local)
            return fecha_creacion.date()
        if isinstance(fecha_creacion, date):
            return fecha_creacion
        return None

    def obtener_clientes(self, texto="", limit=10, offset=0, filtros=None):
        if limit <= 0:
            raise ValueError("El límite de clientes debe ser mayor que cero.")
        if offset < 0:
            raise ValueError("El desplazamiento no puede ser negativo.")

        filtros_servicio = self.normalizar_filtros(filtros, texto)
        fecha_hasta_obj = self._normalizar_fecha(
            (filtros or {}).get("fecha_hasta"), "hasta"
        )[1]
        zona_local = datetime.now().astimezone().tzinfo
        if fecha_hasta_obj:
            # El servicio limita la hora final a 23:59:59. Consultar el día
            # siguiente permite incluir fracciones de segundo del día elegido.
            filtros_servicio["fecha_hasta"] = (
                fecha_hasta_obj + timedelta(days=1)
            ).isoformat()

        if not filtros_servicio:
            pagina = (offset // limit) + 1
            clientes = self.servicio_cliente.obtener_pagina(pagina, limit) or []
            total = self.servicio_cliente.obtener_cantidad_registros()
            inicio_en_pagina = offset % limit
            if inicio_en_pagina and len(clientes) == limit:
                clientes += (
                    self.servicio_cliente.obtener_pagina(pagina + 1, limit) or []
                )
            return clientes[inicio_en_pagina : inicio_en_pagina + limit], total

        clientes_pagina = []
        total = 0
        pagina = 1
        while True:
            lote_consultado = (
                self.servicio_cliente.obtener_pagina(
                    pagina,
                    self._TAMANO_LOTE_CONTEO,
                    filtros_servicio,
                )
                or []
            )
            fin_consulta = len(lote_consultado) < self._TAMANO_LOTE_CONTEO
            lote = lote_consultado
            if fecha_hasta_obj:
                lote = []
                for cliente in lote_consultado:
                    fecha_cliente = self._fecha_cliente(cliente, zona_local)
                    if fecha_cliente is not None and fecha_cliente <= fecha_hasta_obj:
                        lote.append(cliente)
            inicio_lote = total
            fin_lote = inicio_lote + len(lote)
            inicio_solicitado = max(offset, inicio_lote)
            fin_solicitado = min(offset + limit, fin_lote)
            if inicio_solicitado < fin_solicitado:
                clientes_pagina.extend(
                    lote[
                        inicio_solicitado - inicio_lote :
                        fin_solicitado - inicio_lote
                    ]
                )
            total = fin_lote
            if fin_consulta:
                break
            pagina += 1

        return clientes_pagina, total

    def obtener_pagina(self, pagina, limite=10):
        return self.servicio_cliente.obtener_pagina(pagina, limite)

    def modificar_cliente(
        self,
        cliente,
        razon_social,
        tipo_persona,
        direccion=None,
        rfc=None,
        telefono=None,
        correo_elect=None,
        es_nuevo_cliente=False,
        activo=True,
    ):
        datos = ControladorRegistrarCliente.normalizar_datos_cliente(
            razon_social,
            tipo_persona,
            direccion,
            rfc,
            telefono,
            correo_elect,
            es_nuevo_cliente,
            activo,
        )
        for atributo, valor in datos.items():
            setattr(cliente, atributo, valor)

        self.servicio_cliente.modificar_cliente(cliente)
        return cliente

    def eliminar_cliente(self, cliente):
        self.servicio_cliente.eliminar_cliente(cliente)
