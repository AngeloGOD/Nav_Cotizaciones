import abc
from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import session

class Repositorio(abc.ABC):

    def __init__(self, sesion: session):
        self.sesion = sesion

    @abc.abstractmethod
    def insertar(self, objeto: Base): pass
    
    @abc.abstractmethod
    def consultar_pagina(self, desplazamiento, limite): pass