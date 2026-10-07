from sqlalchemy.orm.session import Session
from fuente.negocio.modelo.Embarcacion import Embarcacion
from fuente.persistencia.repositorio.Repositorio import Repositorio
from sqlalchemy import select

class RepositorioEmbarcacion(Repositorio):

    def __init__(self, sesion: Session):
        super().__init__(sesion=sesion)

    def insertar(self, embarcacion: Embarcacion):
        self.sesion.add(embarcacion)
    
    def consultar_pagina(self, desplazamiento, limite):
        stmt = (
            select(Embarcacion)
            .order_by(Embarcacion.id_embarcacion)
            .limit(limite)
            .offset(desplazamiento)
        )
        return self.sesion.scalars(stmt).all()