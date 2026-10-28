from fuente.negocio.controlador.ControladorRegistrarCliente import (
    ControladorRegistrarCliente,
)


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
