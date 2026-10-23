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

    @abc.abstractmethod
    def modificar(self, objeto: Base): pass

    @abc.abstractmethod
    def eliminar(self, objeto: Base): pass

    @abc.abstractmethod
    def buscar_por_id(self, id: int): pass

    @abc.abstractmethod
    def buscar_por_nombre(self, nombre: str): pass
