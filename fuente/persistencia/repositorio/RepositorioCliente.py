from sqlalchemy.orm import session
from fuente.negocio.modelo import Cliente

class RepositorioCliente:

    def __init__(self, sesion: session):
        self.sesion = sesion

    def insertar(self, cliente: Cliente):
        self.sesion.add(cliente)
    
    def obtenerPagina(self, desplazamiento, limite = 10):
        pass