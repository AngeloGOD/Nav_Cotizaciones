from __future__ import annotations

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.session import Session

from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.Cliente import Cliente
from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.Cotizacion import Cotizacion, DetalleCotizacion
from fuente.negocio.modelo.ENUMs import EstadoCotizacion, Moneda
from fuente.persistencia.repositorio.Repositorio import Repositorio


class RepositorioCotizacion(Repositorio):

    def __init__(self, sesion: Session):
        super().__init__(sesion=sesion)

    @staticmethod
    def _opciones_carga():
        return (
            selectinload(Cotizacion.cliente),
            selectinload(Cotizacion.buque).selectinload(Buque.categoria_buque),
            selectinload(Cotizacion.buque).selectinload(Buque.cliente),
            selectinload(Cotizacion.detalles)
            .selectinload(DetalleCotizacion.concepto)
            .selectinload(Concepto.categoria_pda),
            selectinload(Cotizacion.detalles)
            .selectinload(DetalleCotizacion.concepto)
            .selectinload(Concepto.proveedores),
        )

    def obtener_siguiente_id(self) -> int:
        stmt_max = select(func.coalesce(func.max(Cotizacion.id), 0) + 1)
        siguiente_por_max = int(self.sesion.scalar(stmt_max) or 1)

        bind = getattr(self.sesion, "bind", None) or self.sesion.get_bind()
        nombre_dialecto = (
            getattr(getattr(bind, "dialect", None), "name", "")
            if bind is not None
            else ""
        )

        if nombre_dialecto == "postgresql":
            try:
                with self.sesion.begin_nested():
                    nombre_secuencia = self.sesion.scalar(
                        text("SELECT pg_get_serial_sequence('cotizacion', 'id')")
                    )
                    if nombre_secuencia:
                        fila = self.sesion.execute(
                            text(
                                f"SELECT last_value, is_called FROM {nombre_secuencia}"
                            )
                        ).first()
                        if fila is not None:
                            ultimo_valor = int(fila[0])
                            fue_llamada = bool(fila[1])
                            siguiente_secuencia = (
                                ultimo_valor + 1 if fue_llamada else ultimo_valor
                            )
                            return max(siguiente_por_max, siguiente_secuencia)
            except Exception:
                return siguiente_por_max

        return siguiente_por_max

    def insertar(self, cotizacion: Cotizacion) -> Cotizacion:
        if cotizacion.cliente is not None:
            if cotizacion.cliente_id is None and cotizacion.cliente.id is not None:
                cotizacion.cliente_id = cotizacion.cliente.id
            if cotizacion.cliente not in self.sesion and cotizacion.cliente_id is not None:
                cotizacion.cliente = self.sesion.get(Cliente, cotizacion.cliente_id)

        if cotizacion.buque is not None:
            if cotizacion.buque_id is None and cotizacion.buque.id is not None:
                cotizacion.buque_id = cotizacion.buque.id
            if cotizacion.buque not in self.sesion and cotizacion.buque_id is not None:
                cotizacion.buque = self.sesion.get(Buque, cotizacion.buque_id)

        for idx, detalle in enumerate(cotizacion.detalles or [], start=1):
            if detalle.disc is None or detalle.disc <= 0:
                detalle.disc = idx
            if detalle.concepto is not None:
                if detalle.concepto_id is None and detalle.concepto.id is not None:
                    detalle.concepto_id = detalle.concepto.id
                if detalle.concepto not in self.sesion and detalle.concepto_id is not None:
                    detalle.concepto = self.sesion.get(Concepto, detalle.concepto_id)

        self.sesion.add(cotizacion)
        self.sesion.flush()
        return cotizacion

    def buscar_por_id(self, id_cotizacion: int) -> Cotizacion | None:
        stmt = (
            select(Cotizacion)
            .options(*self._opciones_carga())
            .where(Cotizacion.id == id_cotizacion)
            .execution_options(populate_existing=True)
        )
        return self.sesion.scalars(stmt).first()

    def buscar_por_folio(self, folio: str) -> Cotizacion | None:
        folio_limpio = (folio or "").strip()
        if not folio_limpio:
            return None
        stmt = (
            select(Cotizacion)
            .options(*self._opciones_carga())
            .where(Cotizacion.folio.ilike(folio_limpio))
            .execution_options(populate_existing=True)
        )
        return self.sesion.scalars(stmt).first()

    def buscar_por_nombre(self, nombre: str) -> list[Cotizacion]:
        return self.consultar_pagina(0, 10, {"texto": nombre})

    @staticmethod
    def _aplicar_filtros(stmt, filtros: dict | None = None):
        if not filtros:
            return stmt

        condiciones = []
        texto = (filtros.get("texto") or filtros.get("busqueda") or "").strip()
        if texto:
            patron = f"%{texto}%"
            stmt = stmt.join(Cotizacion.cliente).join(Cotizacion.buque)
            condiciones.append(
                or_(
                    Cotizacion.folio.ilike(patron),
                    Cliente.razon_social.ilike(patron),
                    Buque.nombre.ilike(patron),
                )
            )

        estados = filtros.get("estados")
        if estados is None and "estado" in filtros and filtros["estado"] is not None:
            estados = filtros["estado"]
        if estados:
            if isinstance(estados, (list, tuple, set)):
                lista_estados = [
                    e if isinstance(e, EstadoCotizacion) else EstadoCotizacion(str(e).upper())
                    for e in estados
                ]
                if lista_estados:
                    condiciones.append(Cotizacion.estado.in_(lista_estados))
            else:
                estado_enum = (
                    estados
                    if isinstance(estados, EstadoCotizacion)
                    else EstadoCotizacion(str(estados).upper())
                )
                condiciones.append(Cotizacion.estado == estado_enum)

        monedas = filtros.get("monedas")
        if monedas is None and "moneda" in filtros and filtros["moneda"] is not None:
            monedas = filtros["moneda"]
        if monedas:
            if isinstance(monedas, (list, tuple, set)):
                lista_monedas = [
                    m if isinstance(m, Moneda) else Moneda(str(m).upper())
                    for m in monedas
                ]
                if lista_monedas:
                    condiciones.append(Cotizacion.moneda.in_(lista_monedas))
            else:
                moneda_enum = (
                    monedas
                    if isinstance(monedas, Moneda)
                    else Moneda(str(monedas).upper())
                )
                condiciones.append(Cotizacion.moneda == moneda_enum)

        if filtros.get("cliente_id") is not None:
            condiciones.append(Cotizacion.cliente_id == int(filtros["cliente_id"]))

        if filtros.get("buque_id") is not None:
            condiciones.append(Cotizacion.buque_id == int(filtros["buque_id"]))

        fecha_desde = filtros.get("fecha_desde")
        if fecha_desde is not None:
            condiciones.append(Cotizacion.fecha_arribo >= fecha_desde)

        fecha_hasta = filtros.get("fecha_hasta")
        if fecha_hasta is not None:
            condiciones.append(Cotizacion.fecha_arribo <= fecha_hasta)

        if condiciones:
            stmt = stmt.where(and_(*condiciones))

        return stmt

    def consultar_pagina(
        self, desplazamiento: int, limite: int, filtros: dict | None = None
    ) -> list[Cotizacion]:
        stmt = select(Cotizacion).options(*self._opciones_carga())
        stmt = self._aplicar_filtros(stmt, filtros)
        stmt = (
            stmt.order_by(Cotizacion.id.desc())
            .limit(limite)
            .offset(desplazamiento)
        )
        return list(self.sesion.scalars(stmt).all())

    def contar_registros(self, filtros: dict | None = None) -> int:
        stmt = select(func.count(Cotizacion.id)).select_from(Cotizacion)
        stmt = self._aplicar_filtros(stmt, filtros)
        return int(self.sesion.scalar(stmt) or 0)

    def contar_por_estado(self) -> dict[EstadoCotizacion, int]:
        conteos: dict[EstadoCotizacion, int] = {
            estado: 0 for estado in EstadoCotizacion
        }
        stmt = select(Cotizacion.estado, func.count(Cotizacion.id)).group_by(
            Cotizacion.estado
        )
        for estado, cantidad in self.sesion.execute(stmt).all():
            if estado is not None:
                estado_enum = (
                    estado
                    if isinstance(estado, EstadoCotizacion)
                    else EstadoCotizacion(str(estado))
                )
                conteos[estado_enum] = int(cantidad)
        return conteos

    def modificar(self, cotizacion: Cotizacion) -> Cotizacion:
        if cotizacion.id is None:
            raise ValueError("La cotización a modificar debe tener un ID válido.")

        existente = self.sesion.get(Cotizacion, cotizacion.id)
        if existente is None:
            raise ValueError(
                f"No se encontró la cotización con id={cotizacion.id} para modificar."
            )

        datos_nuevos_detalles = []
        for detalle in list(cotizacion.detalles or []):
            concepto_id = detalle.concepto_id
            if concepto_id is None and detalle.concepto is not None:
                concepto_id = detalle.concepto.id
            datos_nuevos_detalles.append(
                {
                    "concepto_id": concepto_id,
                    "cantidad": detalle.cantidad,
                    "precio_unitario": detalle.precio_unitario,
                    "subtotal": detalle.subtotal,
                    "iva": detalle.iva,
                    "factura": detalle.factura,
                    "observaciones": detalle.observaciones,
                }
            )

        existente.folio = cotizacion.folio
        existente.cliente_id = (
            cotizacion.cliente_id
            if cotizacion.cliente_id is not None
            else (cotizacion.cliente.id if cotizacion.cliente is not None else existente.cliente_id)
        )
        existente.buque_id = (
            cotizacion.buque_id
            if cotizacion.buque_id is not None
            else (cotizacion.buque.id if cotizacion.buque is not None else existente.buque_id)
        )
        existente.fecha_arribo = cotizacion.fecha_arribo
        existente.fecha_zarpe = cotizacion.fecha_zarpe
        existente.horas_estancia = cotizacion.horas_estancia
        existente.moneda = cotizacion.moneda
        existente.tipo_cambio = cotizacion.tipo_cambio
        existente.estado = cotizacion.estado
        existente.total = cotizacion.total

        existente.detalles.clear()
        self.sesion.flush()

        for idx, datos in enumerate(datos_nuevos_detalles, start=1):
            nuevo_detalle = DetalleCotizacion(
                cotizacion_id=existente.id,
                disc=idx,
                concepto_id=datos["concepto_id"],
                cantidad=datos["cantidad"],
                precio_unitario=datos["precio_unitario"],
                subtotal=datos["subtotal"],
                iva=datos["iva"],
                factura=datos["factura"],
                observaciones=datos["observaciones"],
            )
            existente.detalles.append(nuevo_detalle)

        self.sesion.flush()
        return existente

    def eliminar(self, registro):
        self.sesion.delete(registro)
