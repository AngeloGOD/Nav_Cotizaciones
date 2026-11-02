from datetime import date, datetime

from fuente.negocio.controlador.ControladorRegistrarCliente import (
    ControladorRegistrarCliente,
)
from fuente.negocio.modelo.ENUMs import TipoPersona


class ControladorClientes:
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
            try:
                tipo = (
                    valor
                    if isinstance(valor, TipoPersona)
                    else TipoPersona(str(valor).strip().upper())
                )
            except (TypeError, ValueError):
                raise ValueError("El filtro de tipo de persona contiene una opción no válida.")
            tipos.add(tipo)
        if tipos and len(tipos) < len(TipoPersona):
            filtros_servicio["tipo_persona"] = sorted(tipo.value for tipo in tipos)

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
            filtros_servicio["rfc"] = texto

        return filtros_servicio

    def obtener_clientes(self, texto="", limit=10, offset=0, filtros=None):
        if limit <= 0:
            raise ValueError("El límite de clientes debe ser mayor que cero.")
        if offset < 0:
            raise ValueError("El desplazamiento no puede ser negativo.")

        filtros_servicio = self.normalizar_filtros(filtros, texto)
        return self.servicio_cliente.consultar_pagina(
            desplazamiento=offset,
            limite=limit,
            filtros=filtros_servicio,
        )

    def obtener_pagina(self, pagina, limite=10):
        return self.servicio_cliente.obtener_pagina(pagina, limite)

    def buscar_por_rfc(self, rfc):
        return self.servicio_cliente.buscar_por_rfc(rfc)

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
