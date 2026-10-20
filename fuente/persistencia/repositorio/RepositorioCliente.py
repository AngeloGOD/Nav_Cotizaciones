from sqlalchemy.orm.session import Session
from fuente.negocio.modelo.Cliente import Cliente
from fuente.persistencia.repositorio.Repositorio import Repositorio
from sqlalchemy import select

class RepositorioCliente(Repositorio):

    def __init__(self, sesion: Session):
        super().__init__(sesion=sesion)

    def insertar(self, cliente: Cliente):
        self.sesion.add(cliente)
    
    def consultar_pagina(self, desplazamiento, limite):
        stmt = (
            select(Cliente)
            .order_by(Cliente.id)
            .limit(limite)
            .offset(desplazamiento)
        )
        return self.sesion.scalars(stmt).all()
