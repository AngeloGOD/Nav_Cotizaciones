from decimal import Decimal, InvalidOperation

from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.session import Session

from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.CategoriaBuque import CategoriaBuque
from fuente.persistencia.repositorio.Repositorio import Repositorio


class RepositorioBuque(Repositorio):
    def __init__(self, sesion: Session):
        super().__init__(sesion=sesion)

    def insertar(self, buque: Buque):
        self.sesion.add(buque)

    @staticmethod
    def _decimal_o_none(valor):
        if valor is None or str(valor).strip() == "":
            return None
        try:
            return Decimal(str(valor).strip())
        except (InvalidOperation, ValueError, TypeError):
            return None

    def _construir_condiciones(self, texto="", filtros=None):
        filtros = filtros or {}
        condiciones = []
        texto = (texto or "").strip()
        if texto:
            patron = f"%{texto}%"
            condiciones.append(or_(
                Buque.nombre.ilike(patron),
                Buque.numero_imo.ilike(patron),
                Buque.bandera_pais.ilike(patron),
                Buque.subtipo_descripcion.ilike(patron),
                Buque.categoria_buque.has(CategoriaBuque.categoria.ilike(patron)),
            ))

        categorias = filtros.get("categorias") or []
        if categorias:
            categorias_ids = []
            categorias_nombres = []
            for categoria in categorias:
                if isinstance(categoria, CategoriaBuque) and categoria.id is not None:
                    categorias_ids.append(int(categoria.id))
                elif isinstance(categoria, int) or (isinstance(categoria, str) and categoria.strip().isdigit()):
                    categorias_ids.append(int(str(categoria).strip()))
                elif isinstance(categoria, str) and categoria.strip():
                    categorias_nombres.append(categoria.strip().upper())

            condiciones_cat = []
            if categorias_ids:
                condiciones_cat.append(Buque.categoria_buque_id.in_(categorias_ids))
            if categorias_nombres:
                condiciones_cat.append(
                    Buque.categoria_buque.has(
                        func.upper(CategoriaBuque.categoria).in_(categorias_nombres)
                    )
                )
            if condiciones_cat:
                condiciones.append(or_(*condiciones_cat))

        banderas = {
            str(p).strip().casefold()
            for p in (filtros.get("banderas") or [])
            if p is not None and str(p).strip()
        }
        if banderas:
            condiciones.append(func.lower(Buque.bandera_pais).in_([p.lower() for p in banderas]))

        autopropulsion = {str(v).upper() for v in (filtros.get("autopropulsion") or [])}
        if len(autopropulsion) == 1:
            condiciones.append(Buque.es_autopropulsado.is_(next(iter(autopropulsion)) == "SI"))

        propulsores = {str(v).upper() for v in (filtros.get("propulsores") or [])}
        if len(propulsores) == 1:
            condiciones.append(Buque.propulsores_proa_popa.is_(next(iter(propulsores)) == "SI"))

        estados = {str(v).upper() for v in (filtros.get("estados") or [])}
        if len(estados) == 1:
            condiciones.append(Buque.activo.is_(next(iter(estados)) == "ACTIVO"))

        for clave_min, clave_max, columna in (
            ("trb_min", "trb_max", Buque.trb),
            ("eslora_min", "eslora_max", Buque.eslora),
            ("calado_min", "calado_max", Buque.calado),
        ):
            minimo = self._decimal_o_none(filtros.get(clave_min))
            maximo = self._decimal_o_none(filtros.get(clave_max))
            if minimo is not None:
                condiciones.append(columna >= minimo)
            if maximo is not None:
                condiciones.append(columna <= maximo)
        return condiciones

    def consultar_pagina(self, desplazamiento, limite, filtros=None, texto=""):
        stmt = select(Buque).options(
            selectinload(Buque.cliente),
            selectinload(Buque.categoria_buque),
        )
        condiciones = self._construir_condiciones(texto=texto, filtros=filtros)
        if condiciones:
            stmt = stmt.where(and_(*condiciones))
        stmt = stmt.order_by(Buque.id).limit(limite).offset(desplazamiento)
        return self.sesion.scalars(stmt).all()

    def contar(self, filtros=None, texto=""):
        stmt = select(func.count()).select_from(Buque)
        condiciones = self._construir_condiciones(texto=texto, filtros=filtros)
        if condiciones:
            stmt = stmt.where(and_(*condiciones))
        return self.sesion.scalar(stmt) or 0

    def contar_registros(self):
        return self.sesion.scalar(select(func.count()).select_from(Buque)) or 0

    def modificar(self, buque: Buque):
        stmt = update(Buque).where(Buque.id == buque.id).values(
            cliente_id=buque.cliente_id,
            nombre=buque.nombre,
            numero_imo=buque.numero_imo,
            categoria_buque_id=buque.categoria_buque_id,
            subtipo_descripcion=buque.subtipo_descripcion,
            trb=buque.trb,
            eslora=buque.eslora,
            calado=buque.calado,
            propulsores_proa_popa=buque.propulsores_proa_popa,
            es_autopropulsado=buque.es_autopropulsado,
            bandera_pais=buque.bandera_pais,
            activo=buque.activo,
        )
        self.sesion.execute(stmt)

    def eliminar(self, buque: Buque):
        self.sesion.execute(delete(Buque).where(Buque.id == buque.id))

    def buscar_por_id(self, id: int):
        stmt = (
            select(Buque)
            .options(
                selectinload(Buque.cliente),
                selectinload(Buque.categoria_buque),
            )
            .where(Buque.id == id)
        )
        return self.sesion.scalars(stmt).first()

    def buscar_por_nombre(self, nombre: str):
        stmt = (
            select(Buque)
            .options(
                selectinload(Buque.cliente),
                selectinload(Buque.categoria_buque),
            )
            .where(Buque.nombre.ilike(f"%{nombre}%"))
            .order_by(Buque.id)
            .limit(10)
        )
        return self.sesion.scalars(stmt).all()

    def obtener_banderas_registradas(self) -> list[str]:
        stmt = (
            select(func.distinct(Buque.bandera_pais))
            .where(
                Buque.bandera_pais.is_not(None),
                func.trim(Buque.bandera_pais) != "",
            )
            .order_by(Buque.bandera_pais)
        )
        return [b for b in self.sesion.scalars(stmt).all() if b]
