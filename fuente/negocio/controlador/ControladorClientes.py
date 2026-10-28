from fuente.negocio.modelo.Cliente import Cliente
from fuente.negocio.modelo.ENUMs import TipoPersona


class ControladorClientes:
    def __init__(self, servicio_cliente):
        self.servicio_cliente = servicio_cliente

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
        datos = self._normalizar_datos_cliente(
            razon_social,
            tipo_persona,
            direccion,
            rfc,
            telefono,
            correo_elect,
            es_nuevo_cliente,
            activo,
        )
        cliente = Cliente(**datos)
        self.servicio_cliente.registrar_cliente(cliente)
        return cliente

    def obtener_clientes(self, texto="", limit=10, offset=0):
        texto = (texto or "").strip()
        if texto:
            resultados = self.servicio_cliente.buscar_por_nombre(texto) or []
            return resultados[offset : offset + limit], len(resultados)

        pagina = (offset // limit) + 1 if limit else 1
        clientes = self.servicio_cliente.obtener_pagina(pagina, limit) or []
        return clientes, len(clientes)

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
        datos = self._normalizar_datos_cliente(
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

    @staticmethod
    def _normalizar_datos_cliente(
        razon_social,
        tipo_persona,
        direccion,
        rfc,
        telefono,
        correo_elect,
        es_nuevo_cliente,
        activo,
    ):
        if isinstance(tipo_persona, str):
            tipo_persona = TipoPersona(tipo_persona.strip().upper())

        return {
            "razon_social": razon_social.strip(),
            "tipo_persona": tipo_persona,
            "direccion": direccion.strip() if direccion and direccion.strip() else None,
            "rfc": rfc.strip().upper() if rfc and rfc.strip() else None,
            "telefono": telefono.strip() if telefono and telefono.strip() else None,
            "correo_elect": (
                correo_elect.strip()
                if correo_elect and correo_elect.strip()
                else None
            ),
            "es_nuevo_cliente": bool(es_nuevo_cliente),
            "activo": bool(activo),
        }
