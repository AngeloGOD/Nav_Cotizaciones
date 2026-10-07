from fuente.persistencia.uow.AbstractUnitOfWork import AbstractUnitOfWork
from fuente.persistencia.repositorio.RepositorioCliente import RepositorioCliente
from fuente.persistencia.repositorio.RepositorioEmbarcaciones import RepositorioEmbarcacion
from fuente.persistencia.repositorio.RepositorioProducto import RepositorioProducto

class AlchemyUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory):
        self.session_factory = session_factory

    def __enter__(self):
        self.session = self.session_factory()
        self.session.begin()

        self.cliente = RepositorioCliente(self.session)
        self.embarcacion = RepositorioEmbarcacion(self.session)
        self.producto = RepositorioProducto(self.session)
        return super().__enter__()

    def commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
        
    def close(self):
        self.session.close()