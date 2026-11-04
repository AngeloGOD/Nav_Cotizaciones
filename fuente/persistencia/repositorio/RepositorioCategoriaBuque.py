from sqlalchemy import func, select
from sqlalchemy.orm.session import Session

from fuente.negocio.modelo.CategoriaBuque import CategoriaBuque
from fuente.persistencia.repositorio.Repositorio import Repositorio


class RepositorioCategoriaBuque(Repositorio):

    def __init__(self, sesion: Session):
        super().__init__(sesion=sesion)

    def insertar(self, categoria_buque: CategoriaBuque):
        self.sesion.add(categoria_buque)

    def consultar_pagina(self, desplazamiento, limite, filtros: dict = {}):
        stmt = select(CategoriaBuque)
        if filtros and "nombre" in filtros:
            nombre = filtros.get("nombre")
            if isinstance(nombre, str) and nombre.strip():
                stmt = stmt.where(
                    CategoriaBuque.categoria.ilike(f"%{nombre.strip()}%")
                )
        stmt = (
            stmt.order_by(CategoriaBuque.id)
            .limit(limite)
            .offset(desplazamiento)
        )
        return self.sesion.scalars(stmt).all()

    def modificar(self, objeto):
        pass

    def eliminar(self, objeto):
        pass

    def buscar_por_id(self, id: int):
        stmt = select(CategoriaBuque).where(CategoriaBuque.id == id)
        return self.sesion.scalars(stmt).first()

    def buscar_por_nombre(self, nombre: str):
        stmt = (
            select(CategoriaBuque)
            .where(CategoriaBuque.categoria.ilike(f"%{nombre}%"))
            .order_by(CategoriaBuque.id)
            .limit(10)
        )
        return self.sesion.scalars(stmt).all()

    def contar_registros(self):
        stmt = select(func.count()).select_from(CategoriaBuque)
        return self.sesion.scalar(stmt) or 0
