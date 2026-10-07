from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork as auow
from fuente.negocio.modelo.Cliente import Cliente

class ServicioCliente():

    def __init__(self, uow: auow):
        self.uow = uow

    def registrar_cliente(self, cliente: Cliente):
        with self.uow:
            self.uow.cliente.insertar(cliente)
            self.uow.commit()
    
