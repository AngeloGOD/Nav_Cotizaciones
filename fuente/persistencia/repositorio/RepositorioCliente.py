from sqlalchemy.orm.session import Session
from fuente.negocio.modelo.Cliente import Cliente
from fuente.persistencia.repositorio.Repositorio import Repositorio
from sqlalchemy import select, update, delete

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

    def modificar(self, cliente: Cliente):
        stmt = (
            update(Cliente)
            .where(Cliente.id == cliente.id)
            .values(
                razon_social=cliente.razon_social,
                direccion=cliente.direccion,
                rfc=cliente.rfc,
                correo_elect=cliente.correo_elect,
                telefono=cliente.telefono,
                tipo_persona=cliente.tipo_persona,
                es_nuevo_cliente=cliente.es_nuevo_cliente,
                activo=cliente.activo,
            )
        )
        self.sesion.execute(stmt)

    def eliminar(self, cliente: Cliente):
        stmt = delete(Cliente).where(Cliente.id == cliente.id)
        self.sesion.execute(stmt)

    def buscar_por_id(self, id: int):
        stmt = select(Cliente).where(Cliente.id == id)
        return self.sesion.scalars(stmt).first()

    def buscar_por_nombre(self, nombre: str):
        stmt = (
            select(Cliente)
            .where(Cliente.razon_social.ilike(f"%{nombre}%"))
            .order_by(Cliente.id)
            .limit(10)
        )
        return self.sesion.scalars(stmt).all()
