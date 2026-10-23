from sqlalchemy.orm.session import Session
from sqlalchemy.orm import selectinload
from fuente.negocio.modelo.Buque import Buque
from fuente.persistencia.repositorio.Repositorio import Repositorio
from sqlalchemy import select, update, delete

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

    def modificar(self, buque: Buque):
        stmt = (
            update(Buque)
            .where(Buque.id == buque.id)
            .values(
                cliente_id=buque.cliente_id,
                nombre=buque.nombre,
                numero_imo=buque.numero_imo,
                categoria_buque=buque.categoria_buque,
                subtipo_descripcion=buque.subtipo_descripcion,
                trb_arqueo_bruto=buque.trb_arqueo_bruto,
                eslora_metros=buque.eslora_metros,
                calado_metros=buque.calado_metros,
                propulsores_proa_popa=buque.propulsores_proa_popa,
                es_autopropulsado=buque.es_autopropulsado,
                bandera_pais=buque.bandera_pais,
                activo=buque.activo,
            )
        )
        self.sesion.execute(stmt)

    def eliminar(self, buque: Buque):
        stmt = delete(Buque).where(Buque.id == buque.id)
        self.sesion.execute(stmt)

    def buscar_por_id(self, id: int):
        stmt = (
            select(Buque)
            .options(selectinload(Buque.cliente))
            .where(Buque.id == id)
        )
        return self.sesion.scalars(stmt).first()

    def buscar_por_nombre(self, nombre: str):
        stmt = (
            select(Buque)
            .options(selectinload(Buque.cliente))
            .where(Buque.nombre.ilike(f"%{nombre}%"))
            .order_by(Buque.id)
            .limit(10)
        )
        return self.sesion.scalars(stmt).all()
