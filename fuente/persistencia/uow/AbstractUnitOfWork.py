from __future__ import annotations
import abc
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fuente.persistencia.repositorio.RepositorioBuque import RepositorioBuque
    from fuente.persistencia.repositorio.RepositorioCategoriaBuque import RepositorioCategoriaBuque
    from fuente.persistencia.repositorio.RepositorioCliente import RepositorioCliente
    from fuente.persistencia.repositorio.RepositorioProducto import RepositorioProducto
    from fuente.persistencia.repositorio.RepositorioServicio import RepositorioServicio


class AbstractUnitOfWork(abc.ABC):
    cliente: RepositorioCliente
    buque: RepositorioBuque
    categoria_buque: RepositorioCategoriaBuque
    producto: RepositorioProducto
    servicio: RepositorioServicio

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, traceback):
        if exc_type is not None:
            self.rollback()
        self.close()

    @abc.abstractmethod
    def commit(self): pass

    @abc.abstractmethod
    def rollback(self): pass
    
    @abc.abstractmethod
    def close(self): pass