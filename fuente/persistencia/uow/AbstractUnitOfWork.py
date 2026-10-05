import abc

class AbstractUnitOfWork(abc.ABC):

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