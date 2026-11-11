from fuente.persistencia.uow.AbstractUnitOfWork import AbstractUnitOfWork
from fuente.persistencia.repositorio.RepositorioCliente import RepositorioCliente
from fuente.persistencia.repositorio.RepositorioBuque import RepositorioBuque
from fuente.persistencia.repositorio.RepositorioCategoriaBuque import RepositorioCategoriaBuque
from fuente.persistencia.repositorio.RepositorioCotizacion import RepositorioCotizacion
from fuente.persistencia.repositorio.RepositorioProducto import RepositorioProducto
from fuente.persistencia.repositorio.RepositorioServicio import RepositorioServicio

class AlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.session.begin()

        self.cliente = RepositorioCliente(self.session)
        self.buque = RepositorioBuque(self.session)
        self.categoria_buque = RepositorioCategoriaBuque(self.session)
        self.producto = RepositorioProducto(self.session)
        self.servicio = RepositorioServicio(self.session)
        self.cotizacion = RepositorioCotizacion(self.session)
        return super().__enter__()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
        
    def close(self):
        self.session.close()
