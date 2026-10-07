from sqlalchemy.orm import session
from fuente.negocio.modelo.Cliente import Clientefinal
from sqlalchemy import select

class RepositorioCliente:

    def __init__(self, sesion: session):
        self.sesion = sesion

    def insertar(self, cliente: Clientefinal):
        self.sesion.add(cliente)
    
    def consultar_pagina(self, desplazamiento, limite):
        print("\n\n\n hola mundo")
        stmt = (
            select(Clientefinal)
            .order_by(Clientefinal.id_cliente)
            .limit(limite)
            .offset(desplazamiento)
        )
        print(stmt)
        return self.sesion.scalars(stmt).all()