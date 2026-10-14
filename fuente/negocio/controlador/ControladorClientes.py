from fuente.negocio.modelo.Cliente import Cliente


class ControladorClientes:
    def __init__(self, servicio_cliente):
        self.servicio_cliente = servicio_cliente

    def registrar_cliente(
        self,
        razon_social,
        direccion,
        rfc,
        telefono,
        correo_elect,
        tipo_cliente,
    ):
        cliente = Cliente(
            razon_social=razon_social.strip(),
            direccion=direccion.strip(),
            rfc=rfc.strip(),
            telefono=telefono.strip(),
            correo_elect=correo_elect.strip(),
            tipo_cliente=tipo_cliente.strip().capitalize(),
        )
        self.servicio_cliente.registrar_cliente(cliente)
        return cliente

    def obtener_clientes(self, texto="", limit=10, offset=0):
        pagina = (offset // limit) + 1 if limit else 1
        clientes = self.servicio_cliente.obtener_pagina(pagina, limit)

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
                or texto in (cliente.tipo_cliente or "").lower()
            ]

        return clientes, len(clientes)

    def obtener_pagina(self, pagina, limite=10):
        return self.servicio_cliente.obtener_pagina(pagina, limite)
