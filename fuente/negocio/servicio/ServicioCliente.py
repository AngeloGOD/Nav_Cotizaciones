from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork as auow
from fuente.negocio.modelo.Cliente import Clientefinal

class ServicioCliente():

    def __init__(self, uow: auow):
        self.uow = uow

    def registrar_cliente(self, cliente: Clientefinal):
        with self.uow:
            self.uow.cliente.insertar(cliente)
            self.uow.commit()

    def obtener_pagina(self, no_pagina, limite = 10):
        resultado = None
        desplazamiento = (no_pagina - 1) * limite
        with self.uow:
            resultado = self.uow.cliente.consultar_pagina(desplazamiento, limite)
        return resultado

