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
        if isinstance(tipo_persona, str):
            tipo_persona = TipoPersona(tipo_persona.strip().upper())

        cliente = Cliente(
            razon_social=razon_social.strip(),
            direccion=direccion.strip() if direccion and direccion.strip() else None,
            rfc=rfc.strip().upper() if rfc and rfc.strip() else None,
            telefono=telefono.strip() if telefono and telefono.strip() else None,
            correo_elect=correo_elect.strip() if correo_elect and correo_elect.strip() else None,
            tipo_persona=tipo_persona,
            es_nuevo_cliente=bool(es_nuevo_cliente),
            activo=bool(activo),
        )
        self.servicio_cliente.registrar_cliente(cliente)
        return cliente

    def obtener_clientes(self, texto="", limit=10, offset=0):
        pagina = (offset // limit) + 1 if limit else 1
        clientes = self.servicio_cliente.obtener_pagina(pagina, limit) or []

        texto = (texto or "").strip().lower()
        if texto:
            clientes = [
                cliente
                for cliente in clientes
                if texto in (cliente.razon_social or "").lower()
                or texto in (cliente.rfc or "").lower()
                or texto in (cliente.direccion or "").lower()
                or texto in (cliente.telefono or "").lower()
                or texto in (cliente.correo_elect or "").lower()
                or texto in (
                    cliente.tipo_persona.value
                    if hasattr(cliente.tipo_persona, "value")
                    else str(cliente.tipo_persona or "")
                ).lower()
            ]

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
        if isinstance(tipo_persona, str):
            tipo_persona = TipoPersona(tipo_persona.strip().upper())

        cliente.razon_social = razon_social.strip()
        cliente.direccion = (
            direccion.strip() if direccion and direccion.strip() else None
        )
        cliente.rfc = rfc.strip().upper() if rfc and rfc.strip() else None
        cliente.telefono = (
            telefono.strip() if telefono and telefono.strip() else None
        )
        cliente.correo_elect = (
            correo_elect.strip()
            if correo_elect and correo_elect.strip()
            else None
        )
        cliente.tipo_persona = tipo_persona
        cliente.es_nuevo_cliente = bool(es_nuevo_cliente)
        cliente.activo = bool(activo)

        self.servicio_cliente.modificar_cliente(cliente)
        return cliente

    def eliminar_cliente(self, cliente):
        self.servicio_cliente.eliminar_cliente(cliente)
