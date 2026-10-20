from sqlalchemy.orm.session import Session
from sqlalchemy.orm import selectinload
from fuente.negocio.modelo.Buque import Buque
from fuente.persistencia.repositorio.Repositorio import Repositorio
from sqlalchemy import select

class RepositorioBuque(Repositorio):

    def __init__(self, sesion: Session):
        super().__init__(sesion=sesion)

    def insertar(self, buque: Buque):
        self.sesion.add(buque)
    
    def consultar_pagina(self, desplazamiento, limite):
        stmt = (
            select(Buque)
            .options(selectinload(Buque.cliente))
            .order_by(Buque.id)
            .limit(limite)
            .offset(desplazamiento)
        )
        return self.sesion.scalars(stmt).all()
