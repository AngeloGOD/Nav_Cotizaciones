from sqlalchemy.orm.session import Session
from fuente.negocio.modelo.Producto import Producto
from fuente.persistencia.repositorio.Repositorio import Repositorio
from sqlalchemy import select

class RepositorioProducto(Repositorio):

    def __init__(self, sesion: Session):
        super().__init__(sesion=sesion)

    def insertar(self, producto: Producto):
        self.sesion.add(producto)
    
    def consultar_pagina(self, desplazamiento, limite):
        stmt = (
            select(Producto)
            .order_by(Producto.id_producto)
            .limit(limite)
            .offset(desplazamiento)
        )
        return self.sesion.scalars(stmt).all()
