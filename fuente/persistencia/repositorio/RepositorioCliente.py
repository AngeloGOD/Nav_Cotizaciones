from sqlalchemy.orm.session import Session
from fuente.negocio.modelo.Cliente import Cliente
from fuente.persistencia.repositorio.Repositorio import Repositorio
from sqlalchemy import select, update, delete, func

class RepositorioCliente(Repositorio):

    def __init__(self, sesion: Session):
        super().__init__(sesion=sesion)

    def insertar(self, cliente: Cliente):
        self.sesion.add(cliente)
    
    def consultar_pagina(self, desplazamiento, limite, filtros: dict = {}):
        stmt = select(Cliente)

        if filtros:
            tipos = filtros.get("tipo_persona", [])
            if tipos and 0 < len(tipos) < 3:
                stmt = stmt.where(Cliente.tipo_persona.in_(tipos))

            estados = filtros.get("estado_activo", [])
            if estados and 0 < len(estados) < 2:
                stmt = stmt.where(Cliente.activo.in_(estados))

            es_nuevo = filtros.get("es_nuevo", [])
            if es_nuevo and 0 < len(es_nuevo) < 2:
                stmt = stmt.where(Cliente.es_nuevo_cliente.in_(es_nuevo))

            fecha_desde = filtros.get("fecha_desde")
            if fecha_desde:
                stmt = stmt.where(Cliente.creado_en >= fecha_desde)

            fecha_hasta = filtros.get("fecha_hasta")
            if fecha_hasta:
                stmt = stmt.where(Cliente.creado_en <= fecha_hasta)

            nombre = filtros.get("nombre", "")
            if nombre and len(nombre) > 0:
                stmt = stmt.where(Cliente.razon_social.ilike(f"%{nombre}%"))

        stmt = (
            stmt.order_by(Cliente.id)
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

    def contar_registros(self):
        stmt = select(func.count()).select_from(Cliente)
        return self.sesion.scalar(stmt)
