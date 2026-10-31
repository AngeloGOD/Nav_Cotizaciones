from datetime import datetime, date, time
from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork as auow
from fuente.negocio.modelo.Cliente import Cliente
from fuente.negocio.modelo.ENUMs import TipoPersona

class ServicioCliente():

    _MAPA_TIPO_PERSONA = {
        "FISICA": TipoPersona.FISICA,
        "PERSONA FISICA": TipoPersona.FISICA,
        "PERSONA FÍSICA": TipoPersona.FISICA,
        "MORAL": TipoPersona.MORAL,
        "PERSONA MORAL": TipoPersona.MORAL,
        "EXTRANJERO": TipoPersona.EXTRANJERO,
    }

    def __init__(self, uow: auow):
        self.uow = uow

    def registrar_cliente(self, cliente: Cliente):
        with self.uow:
            self.uow.cliente.insertar(cliente)
            self.uow.commit()

    def _limpiar_fecha(self, valor_fecha, es_hasta=False):
        if not valor_fecha:
            return None

        tz_local = datetime.now().astimezone().tzinfo
        hora_objetivo = time(23, 59, 59) if es_hasta else time(0, 0, 0)

        if isinstance(valor_fecha, datetime):
            fecha_dt = valor_fecha.replace(
                hour=hora_objetivo.hour,
                minute=hora_objetivo.minute,
                second=hora_objetivo.second,
                microsecond=0,
            )
            return fecha_dt if fecha_dt.tzinfo else fecha_dt.replace(tzinfo=tz_local)

        if isinstance(valor_fecha, date):
            return datetime.combine(valor_fecha, hora_objetivo, tzinfo=tz_local)

        if isinstance(valor_fecha, str):
            texto = valor_fecha.strip()
            if not texto:
                return None
            for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                try:
                    fecha_base = datetime.strptime(texto, fmt).date()
                    return datetime.combine(fecha_base, hora_objetivo, tzinfo=tz_local)
                except ValueError:
                    continue
            try:
                fecha_dt = datetime.fromisoformat(texto)
                fecha_dt = fecha_dt.replace(
                    hour=hora_objetivo.hour,
                    minute=hora_objetivo.minute,
                    second=hora_objetivo.second,
                    microsecond=0,
                )
                return fecha_dt if fecha_dt.tzinfo else fecha_dt.replace(tzinfo=tz_local)
            except ValueError:
                return None

        return None

    def _limpiar_filtros(self, filtros: dict) -> dict:
        filtros_limpios = {}

        if "tipo_persona" in filtros:
            tipos_crudos = filtros.get("tipo_persona") or []
            tipos_normalizados = []
            for t in tipos_crudos:
                if isinstance(t, TipoPersona):
                    valor = t
                elif isinstance(t, str):
                    valor = self._MAPA_TIPO_PERSONA.get(t.strip().upper(), t.strip())
                else:
                    valor = t
                if valor not in tipos_normalizados:
                    tipos_normalizados.append(valor)

            if len(tipos_normalizados) >= 3:
                filtros_limpios["tipo_persona"] = []
            else:
                filtros_limpios["tipo_persona"] = tipos_normalizados

        if "estado_activo" in filtros:
            estados_crudos = filtros.get("estado_activo") or []
            estados_unicos = list(dict.fromkeys(estados_crudos))
            if len(estados_unicos) >= 2:
                filtros_limpios["estado_activo"] = []
            else:
                filtros_limpios["estado_activo"] = estados_unicos

        if "es_nuevo" in filtros:
            es_nuevo_crudos = filtros.get("es_nuevo") or []
            es_nuevo_unicos = list(dict.fromkeys(es_nuevo_crudos))
            if len(es_nuevo_unicos) >= 2:
                filtros_limpios["es_nuevo"] = []
            else:
                filtros_limpios["es_nuevo"] = es_nuevo_unicos

        if "fecha_desde" in filtros:
            filtros_limpios["fecha_desde"] = self._limpiar_fecha(
                filtros.get("fecha_desde"), es_hasta=False
            )

        if "fecha_hasta" in filtros:
            filtros_limpios["fecha_hasta"] = self._limpiar_fecha(
                filtros.get("fecha_hasta"), es_hasta=True
            )

        if "nombre" in filtros:
            nombre = filtros.get("nombre")
            filtros_limpios["nombre"] = nombre.strip() if isinstance(nombre, str) else ""

        return filtros_limpios

    def obtener_pagina(self, no_pagina, limite = 10, filtros: dict = {}):
        resultado = None
        desplazamiento = (no_pagina - 1) * limite
        with self.uow:
            if not filtros:
                resultado = self.uow.cliente.consultar_pagina(desplazamiento, limite, {})
            else:
                filtros_limpios = self._limpiar_filtros(filtros)
                resultado = self.uow.cliente.consultar_pagina(
                    desplazamiento, limite, filtros_limpios
                )
        return resultado

    def modificar_cliente(self, cliente: Cliente):
        with self.uow:
            self.uow.cliente.modificar(cliente)
            self.uow.commit()

    def eliminar_cliente(self, cliente: Cliente):
        with self.uow:
            self.uow.cliente.eliminar(cliente)
            self.uow.commit()

    def buscar_por_id(self, id: int):
        resultado = None
        with self.uow:
            resultado = self.uow.cliente.buscar_por_id(id)
        return resultado

    def buscar_por_nombre(self, nombre: str):
        resultado = None
        with self.uow:
            resultado = self.uow.cliente.buscar_por_nombre(nombre)
        return resultado
