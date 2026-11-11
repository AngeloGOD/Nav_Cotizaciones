from __future__ import annotations

from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import selectinload, with_polymorphic
from sqlalchemy.orm.session import Session

from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.CategoriaBuque import CategoriaBuque
from fuente.negocio.modelo.CategoriaPDA import CategoriaPDA
from fuente.negocio.modelo.ENUMs import CaracterServicio, TipoProveedor
from fuente.negocio.modelo.Proveedor import Proveedor
from fuente.negocio.modelo.Servicio import (
    Servicio,
    ServicioCuotaFija,
    ServicioFactorCompuesto,
    ServicioFactorUnitario,
    ServicioIncremental,
    ServicioLinealMixto,
    ServicioRango,
)
from fuente.persistencia.repositorio.Repositorio import Repositorio


class RepositorioServicio(Repositorio):
    """repo para manejar el polimorfismo de servicio"""

    def __init__(self, sesion: Session):
        super().__init__(sesion=sesion)
        self._entidad_polimorfica = with_polymorphic(Servicio, "*")

    def _consulta_base_polimorfica(self, incluir_detalles_tarifa: bool = True):
        entidad = self._entidad_polimorfica
        opciones = [
            selectinload(entidad.categoria_buque),
            selectinload(entidad.categoria_pda),
            selectinload(entidad.proveedores),
        ]
        if incluir_detalles_tarifa:
            opciones.extend(
                [
                    selectinload(entidad.ServicioRango.rangos),
                    selectinload(entidad.ServicioIncremental.tramos),
                ]
            )
        return select(entidad).options(*opciones)

    def insertar(
        self, servicio: Servicio, proveedor_ids: list[int] | None = None
    ):
        sku = (servicio.sku or "").strip()
        if sku:
            existente = self.sesion.scalar(
                select(Servicio.__table__.c.id).where(
                    Servicio.__table__.c.sku == sku
                )
            )
            if existente is not None:
                raise ValueError(f"El SKU '{sku}' ya está registrado.")
            servicio.sku = sku
        else:
            servicio.sku = None

        categoria_pda = self.sesion.get(CategoriaPDA, servicio.categoria_pda_id)
        if categoria_pda is None:
            raise ValueError("La categoría PDA seleccionada ya no existe.")

        categoria_buque = None
        if servicio.categoria_buque_id is not None:
            categoria_buque = self.sesion.get(
                CategoriaBuque, servicio.categoria_buque_id
            )
            if categoria_buque is None:
                raise ValueError("La categoría de buque seleccionada ya no existe.")

        proveedores = None
        if proveedor_ids is not None:
            proveedores = []
            for proveedor_id in dict.fromkeys(proveedor_ids):
                proveedor = self.sesion.get(Proveedor, proveedor_id)
                if (
                    proveedor is None
                    or not proveedor.activo
                    or proveedor.tipo_proveedor
                    not in (TipoProveedor.SERVICIOS, TipoProveedor.MIXTO)
                ):
                    raise ValueError(
                        "Uno de los proveedores seleccionados ya no está disponible."
                    )
                proveedores.append(proveedor)
            if not proveedores:
                raise ValueError("Selecciona al menos un proveedor autorizado.")

        servicio.categoria_pda = categoria_pda
        if categoria_buque is not None:
            servicio.categoria_buque = categoria_buque
        if proveedores is not None:
            servicio.proveedores = proveedores
        self.sesion.add(servicio)

    def modificar(
        self, servicio: Servicio, proveedor_ids: list[int] | None = None
    ):
        if servicio.id is None:
            raise ValueError("No se puede modificar un servicio sin identificador.")

        sku = (servicio.sku or "").strip()
        if sku:
            existente = self.sesion.scalar(
                select(Servicio.__table__.c.id).where(
                    Servicio.__table__.c.sku == sku,
                    Servicio.__table__.c.id != servicio.id,
                )
            )
            if existente is not None:
                raise ValueError(f"El SKU '{sku}' ya está registrado.")
            servicio.sku = sku
        else:
            servicio.sku = None

        categoria_pda = self.sesion.get(CategoriaPDA, servicio.categoria_pda_id)
        if categoria_pda is None:
            raise ValueError("La categoría PDA seleccionada ya no existe.")

        categoria_buque = None
        if servicio.categoria_buque_id is not None:
            categoria_buque = self.sesion.get(
                CategoriaBuque, servicio.categoria_buque_id
            )
            if categoria_buque is None:
                raise ValueError("La categoría de buque seleccionada ya no existe.")

        proveedores = []
        for proveedor_id in dict.fromkeys(proveedor_ids or []):
            proveedor = self.sesion.get(Proveedor, proveedor_id)
            if (
                proveedor is None
                or not proveedor.activo
                or proveedor.tipo_proveedor
                not in (TipoProveedor.SERVICIOS, TipoProveedor.MIXTO)
            ):
                raise ValueError(
                    "Uno de los proveedores seleccionados ya no está disponible."
                )
            proveedores.append(proveedor)
        if not proveedores:
            raise ValueError("Selecciona al menos un proveedor autorizado.")

        servicio.categoria_pda_id = categoria_pda.id
        servicio.categoria_buque_id = (
            categoria_buque.id if categoria_buque is not None else None
        )
        with self.sesion.no_autoflush:
            servicio_actualizado = self.sesion.merge(servicio)
        servicio_actualizado.categoria_pda = categoria_pda
        servicio_actualizado.categoria_buque = categoria_buque
        servicio_actualizado.proveedores = proveedores

    def eliminar(self, servicio: Servicio):
        existente = self.buscar_por_id(servicio.id) if servicio.id is not None else None
        if existente is not None:
            self.sesion.delete(existente)

    def buscar_por_id(self, id: int) -> Servicio | None:
        entidad = self._entidad_polimorfica
        stmt = self._consulta_base_polimorfica().where(entidad.id == id)
        return self.sesion.scalars(stmt).first()

    def buscar_por_nombre(self, nombre: str) -> list[Servicio]:
        entidad = self._entidad_polimorfica
        patron = f"%{(nombre or '').strip()}%"
        stmt = (
            self._consulta_base_polimorfica(incluir_detalles_tarifa=False)
            .where(
                or_(
                    entidad.nombre_es.ilike(patron),
                    entidad.nombre_en.ilike(patron),
                )
            )
            .order_by(entidad.id)
            .limit(10)
        )
        return list(self.sesion.scalars(stmt).all())

    def consultar_pagina(
        self, desplazamiento: int, limite: int, filtros: dict | None = None
    ) -> list[Servicio]:
        entidad = self._entidad_polimorfica
        filtros = filtros or {}
        condiciones = []

        if "activo" in filtros and filtros["activo"] is not None:
            condiciones.append(entidad.activo.is_(bool(filtros["activo"])))

        if "caracter" in filtros and filtros["caracter"]:
            caracter = filtros["caracter"]
            if isinstance(caracter, (list, tuple, set)):
                condiciones.append(entidad.caracter.in_(list(caracter)))
            else:
                condiciones.append(entidad.caracter == caracter)

        if "categoria_buque_id" in filtros and filtros["categoria_buque_id"] is not None:
            condiciones.append(entidad.categoria_buque_id == int(filtros["categoria_buque_id"]))

        if "nombre" in filtros and isinstance(filtros["nombre"], str) and filtros["nombre"].strip():
            patron = f"%{filtros['nombre'].strip()}%"
            condiciones.append(
                or_(
                    entidad.nombre_es.ilike(patron),
                    entidad.nombre_en.ilike(patron),
                )
            )

        stmt = self._consulta_base_polimorfica()
        if condiciones:
            stmt = stmt.where(and_(*condiciones))
        stmt = stmt.order_by(entidad.id).limit(limite).offset(desplazamiento)
        return list(self.sesion.scalars(stmt).all())

    def contar_registros(self) -> int:
        stmt = select(func.count()).select_from(Servicio)
        return self.sesion.scalar(stmt) or 0

    def obtener_candidatos_obligatorios_y_condicionales(
        self, categoria_buque_id: int | None
    ) -> list[Servicio]:
        entidad = self._entidad_polimorfica
        if categoria_buque_id is not None:
            condicion_categoria = or_(
                entidad.categoria_buque_id == categoria_buque_id,
                entidad.categoria_buque_id.is_(None),
            )
        else:
            condicion_categoria = entidad.categoria_buque_id.is_(None)

        stmt = (
            self._consulta_base_polimorfica()
            .where(
                and_(
                    Concepto.activo.is_(True),
                    entidad.caracter.in_(
                        [CaracterServicio.OBLIGATORIO, CaracterServicio.CONDICIONAL]
                    ),
                    condicion_categoria,
                )
            )
            .order_by(entidad.id)
        )
        return list(self.sesion.scalars(stmt).all())
