from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from sqlalchemy import and_, func, select

from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.Cliente import Cliente
from fuente.negocio.modelo.Cotizacion import Cotizacion, DetalleCotizacion
from fuente.negocio.modelo.ENUMs import EstadoCotizacion, Moneda
from fuente.negocio.modelo.Producto import Producto
from fuente.negocio.modelo.Servicio import Servicio


class ServicioReportes:
    PERIODOS = {
        "Últimos 30 días": 30,
        "Últimos 3 meses": 3,
        "Últimos 6 meses": 6,
        "Este año": 12,
    }

    def __init__(self, uow):
        self.uow = uow

    @classmethod
    def _rango_periodo(cls, periodo: str):
        ahora = datetime.now().astimezone()
        if periodo == "Este año":
            desde = ahora.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0
            )
        elif periodo == "Últimos 30 días":
            desde = ahora - timedelta(days=30)
        else:
            meses = cls.PERIODOS.get(periodo)
            if meses is None:
                raise ValueError(f"El periodo '{periodo}' no es válido.")
            indice_mes = ahora.year * 12 + ahora.month - 1 - meses + 1
            anio, mes_cero = divmod(indice_mes, 12)
            desde = ahora.replace(
                year=anio,
                month=mes_cero + 1,
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
        hasta = ahora + timedelta(microseconds=1)
        return desde, hasta

    @staticmethod
    def _siguiente_mes(fecha):
        if fecha.month == 12:
            return fecha.replace(
                year=fecha.year + 1, month=1, day=1
            )
        return fecha.replace(month=fecha.month + 1, day=1)

    @classmethod
    def _crear_intervalos(cls, desde, hasta, periodo):
        if periodo == "Últimos 30 días":
            intervalos = []
            for indice in range(6):
                inicio = desde + (hasta - desde) * indice / 6
                fin = desde + (hasta - desde) * (indice + 1) / 6
                intervalos.append(
                    (inicio, fin, f"{inicio:%d/%m}–{(fin - timedelta(days=1)):%d/%m}")
                )
            return intervalos

        intervalos = []
        meses_es = (
            "Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic",
        )
        cursor = desde.replace(day=1)
        while cursor < hasta:
            fin = cls._siguiente_mes(cursor)
            etiqueta = f"{meses_es[cursor.month - 1]} {cursor.year}"
            intervalos.append((cursor, min(fin, hasta), etiqueta))
            cursor = fin
        return intervalos

    @staticmethod
    def _contar_en_intervalos(fechas, intervalos):
        cantidades = [0] * len(intervalos)
        for fecha in fechas:
            if fecha is None:
                continue
            if fecha.tzinfo is None:
                fecha = fecha.replace(tzinfo=intervalos[0][0].tzinfo)
            for indice, (inicio, fin, _) in enumerate(intervalos):
                if inicio <= fecha < fin:
                    cantidades[indice] += 1
                    break
        return cantidades

    @staticmethod
    def _estado_desde_etiqueta(etiqueta):
        equivalencias = {
            "Borrador": EstadoCotizacion.BORRADOR,
            "Proforma": EstadoCotizacion.PROFORMA,
            "Anticipo recibido": EstadoCotizacion.ANTICIPO_RECIBIDO,
            "En operación": EstadoCotizacion.EN_OPERACION,
            "Liquidada": EstadoCotizacion.LIQUIDADA_FDA,
            "Cancelada": EstadoCotizacion.CANCELADA,
        }
        try:
            return equivalencias[etiqueta]
        except KeyError as error:
            raise ValueError(f"El estado '{etiqueta}' no es válido.") from error

    def obtener_resumen(self, periodo="Últimos 6 meses", modulo="Todos los módulos"):
        desde, hasta = self._rango_periodo(periodo)
        intervalos = self._crear_intervalos(desde, hasta, periodo)

        with self.uow as uow:
            session = uow.session
            totales = {
                "clientes": int(session.scalar(select(func.count()).select_from(Cliente)) or 0),
                "productos": int(session.scalar(select(func.count()).select_from(Producto)) or 0),
                "servicios": int(session.scalar(select(func.count()).select_from(Servicio)) or 0),
                "buques": int(session.scalar(select(func.count()).select_from(Buque)) or 0),
                "cotizaciones": int(session.scalar(select(func.count()).select_from(Cotizacion)) or 0),
            }
            cotizaciones = session.execute(
                select(
                    Cotizacion.creado_en,
                    Cotizacion.estado,
                    Cotizacion.total,
                    Cotizacion.moneda,
                ).where(
                    Cotizacion.creado_en >= desde,
                    Cotizacion.creado_en < hasta,
                )
            ).all()
            clientes = session.scalars(
                select(Cliente.creado_en).where(
                    Cliente.creado_en >= desde,
                    Cliente.creado_en < hasta,
                )
            ).all()
            detalle_productos = session.execute(
                select(Cotizacion.creado_en, DetalleCotizacion.cantidad)
                .join(
                    DetalleCotizacion,
                    DetalleCotizacion.cotizacion_id == Cotizacion.id,
                )
                .join(Producto, Producto.id == DetalleCotizacion.concepto_id)
                .where(
                    Cotizacion.creado_en >= desde,
                    Cotizacion.creado_en < hasta,
                )
            ).all()
            detalle_servicios = session.execute(
                select(Cotizacion.creado_en, DetalleCotizacion.cantidad)
                .join(
                    DetalleCotizacion,
                    DetalleCotizacion.cotizacion_id == Cotizacion.id,
                )
                .join(Servicio, Servicio.id == DetalleCotizacion.concepto_id)
                .where(
                    Cotizacion.creado_en >= desde,
                    Cotizacion.creado_en < hasta,
                )
            ).all()

        labels = [etiqueta for _, _, etiqueta in intervalos]
        quote_counts = [0] * len(intervalos)
        quote_amounts = [Decimal("0")] * len(intervalos)
        approved = [0] * len(intervalos)
        for fecha, estado, total, moneda in cotizaciones:
            if fecha is None:
                continue
            if fecha.tzinfo is None:
                fecha = fecha.replace(tzinfo=desde.tzinfo)
            for indice, (inicio, fin, _) in enumerate(intervalos):
                if inicio <= fecha < fin:
                    quote_counts[indice] += 1
                    if moneda == Moneda.MXN:
                        quote_amounts[indice] += Decimal(str(total or 0))
                    if estado in (
                        EstadoCotizacion.ANTICIPO_RECIBIDO,
                        EstadoCotizacion.EN_OPERACION,
                        EstadoCotizacion.LIQUIDADA_FDA,
                    ):
                        approved[indice] += 1
                    break

        client_counts = self._contar_en_intervalos(clientes, intervalos)
        product_units = [Decimal("0")] * len(intervalos)
        for fecha, cantidad in detalle_productos:
            if fecha is None:
                continue
            if fecha.tzinfo is None:
                fecha = fecha.replace(tzinfo=desde.tzinfo)
            for indice, (inicio, fin, _) in enumerate(intervalos):
                if inicio <= fecha < fin:
                    product_units[indice] += Decimal(str(cantidad or 0))
                    break
        service_units = [Decimal("0")] * len(intervalos)
        for fecha, cantidad in detalle_servicios:
            if fecha is None:
                continue
            if fecha.tzinfo is None:
                fecha = fecha.replace(tzinfo=desde.tzinfo)
            for indice, (inicio, fin, _) in enumerate(intervalos):
                if inicio <= fecha < fin:
                    service_units[indice] += Decimal(str(cantidad or 0))
                    break

        approval_rates = [
            round(aprobadas / cantidad * 100, 1) if cantidad else 0
            for aprobadas, cantidad in zip(approved, quote_counts)
        ]
        if modulo == "Productos":
            actividad = [float(value) for value in product_units]
            unidad_actividad = "unidades de producto"
        elif modulo == "Servicios":
            actividad = [float(value) for value in service_units]
            unidad_actividad = "unidades de servicio"
        elif modulo in ("Buques", "Cotizaciones"):
            actividad = quote_counts
            unidad_actividad = "cotizaciones"
        else:
            actividad = [float(value) for value in client_counts]
            unidad_actividad = "clientes nuevos"
        series = {
            "Ingresos": [float(value / Decimal("1000")) for value in quote_amounts],
            "Cotizaciones": quote_counts,
            "Aprobaciones": approval_rates,
            "Actividad": actividad,
            "Clientes": client_counts,
            "Servicios": [float(value) for value in service_units],
        }

        suma_total = sum(quote_amounts, Decimal("0"))
        tasa_aprobacion = (
            round(sum(approved) / sum(quote_counts) * 100, 1)
            if sum(quote_counts)
            else 0
        )
        return {
            "desde": desde,
            "hasta": hasta,
            "labels": labels,
            "totales": totales,
            "series": series,
            "cotizaciones_periodo": sum(quote_counts),
            "monto_mxn_periodo": suma_total,
            "aprobacion_periodo": tasa_aprobacion,
            "pendientes_periodo": sum(
                1
                for _, estado, _, _ in cotizaciones
                if estado in (EstadoCotizacion.BORRADOR, EstadoCotizacion.PROFORMA)
            ),
            "liquidadas_periodo": sum(
                1
                for _, estado, _, _ in cotizaciones
                if estado == EstadoCotizacion.LIQUIDADA_FDA
            ),
            "unidad_grafica": unidad_actividad,
        }

    def obtener_informe(self, nombre, periodo, filtro):
        desde, hasta = self._rango_periodo(periodo)
        with self.uow as uow:
            session = uow.session
            if nombre == "Rendimiento de cotizaciones":
                intervalos = self._crear_intervalos(desde, hasta, periodo)
                stmt = select(
                    Cotizacion.creado_en,
                    Cotizacion.estado,
                    Cotizacion.moneda,
                    Cotizacion.total,
                ).where(
                    Cotizacion.creado_en >= desde,
                    Cotizacion.creado_en < hasta,
                )
                if filtro != "Todos los estados":
                    stmt = stmt.where(
                        Cotizacion.estado == self._estado_desde_etiqueta(filtro)
                    )
                agregados = [
                    {
                        "Cotizaciones": 0,
                        "Aprobadas": 0,
                        "Monto MXN": Decimal("0"),
                        "Monto USD": Decimal("0"),
                    }
                    for _ in intervalos
                ]
                for fecha, estado, moneda, total in session.execute(stmt).all():
                    if fecha is None:
                        continue
                    if fecha.tzinfo is None:
                        fecha = fecha.replace(tzinfo=desde.tzinfo)
                    for indice, (inicio, fin, _) in enumerate(intervalos):
                        if inicio <= fecha < fin:
                            grupo = agregados[indice]
                            grupo["Cotizaciones"] += 1
                            if estado in (
                                EstadoCotizacion.ANTICIPO_RECIBIDO,
                                EstadoCotizacion.EN_OPERACION,
                                EstadoCotizacion.LIQUIDADA_FDA,
                            ):
                                grupo["Aprobadas"] += 1
                            grupo[
                                "Monto MXN" if moneda == Moneda.MXN else "Monto USD"
                            ] += Decimal(str(total or 0))
                            break
                rows = []
                for (_, _, etiqueta), grupo in zip(intervalos, agregados):
                    rows.append(
                        {
                            "Periodo": etiqueta,
                            **grupo,
                            "Tasa de aprobación": (
                                round(
                                    grupo["Aprobadas"]
                                    / grupo["Cotizaciones"]
                                    * 100,
                                    1,
                                )
                                if grupo["Cotizaciones"]
                                else 0
                            ),
                        }
                    )
                columns = {
                    "Periodo": "Periodo",
                    "Cotizaciones": "Cotizaciones",
                    "Aprobadas": "Aprobadas",
                    "Tasa de aprobación": "Tasa de aprobación",
                    "Monto MXN": "Monto MXN",
                    "Monto USD": "Monto USD",
                }
                chart = [
                    (row["Periodo"], row["Cotizaciones"])
                    for row in rows
                ]
                total_cotizaciones = sum(row["Cotizaciones"] for row in rows)
                total_aprobadas = sum(row["Aprobadas"] for row in rows)
                metrics = {
                    "Cotizaciones": total_cotizaciones,
                    "Aprobadas": (
                        f"{total_aprobadas / total_cotizaciones * 100:.1f}%"
                        if total_cotizaciones
                        else "0%"
                    ),
                }
            elif nombre == "Cotizaciones por estado":
                stmt = (
                    select(
                        Cotizacion.estado,
                        Cotizacion.moneda,
                        func.count(Cotizacion.id),
                        func.coalesce(func.sum(Cotizacion.total), 0),
                    )
                    .where(Cotizacion.creado_en >= desde, Cotizacion.creado_en < hasta)
                    .group_by(Cotizacion.estado, Cotizacion.moneda)
                    .order_by(Cotizacion.estado, Cotizacion.moneda)
                )
                if filtro != "Todos los estados":
                    stmt = stmt.where(
                        Cotizacion.estado == self._estado_desde_etiqueta(filtro)
                    )
                rows = [
                    {
                        "Estado": getattr(estado, "value", estado),
                        "Moneda": getattr(moneda, "value", moneda),
                        "Cotizaciones": cantidad,
                        "Monto cotizado": Decimal(str(total or 0)),
                    }
                    for estado, moneda, cantidad, total in session.execute(stmt).all()
                ]
                columns = {
                    "Estado": "Estado",
                    "Moneda": "Moneda",
                    "Cotizaciones": "Cotizaciones",
                    "Monto cotizado": "Monto cotizado",
                }
                chart = [
                    (f"{row['Estado']} {row['Moneda']}", row["Cotizaciones"])
                    for row in rows
                ]
                metrics = {
                    "Cotizaciones": sum(row["Cotizaciones"] for row in rows),
                    "Estados": len(rows),
                }
            elif nombre == "Clientes más activos":
                stmt = (
                    select(
                        Cliente.razon_social,
                        Cliente.activo,
                        func.count(Cotizacion.id).label("cotizaciones"),
                    )
                    .join(Cotizacion, Cotizacion.cliente_id == Cliente.id)
                    .where(
                        Cotizacion.creado_en >= desde,
                        Cotizacion.creado_en < hasta,
                    )
                    .group_by(Cliente.id, Cliente.razon_social, Cliente.activo)
                    .order_by(func.count(Cotizacion.id).desc())
                )
                if filtro == "Activos":
                    stmt = stmt.where(Cliente.activo.is_(True))
                elif filtro == "Inactivos":
                    stmt = stmt.where(Cliente.activo.is_(False))
                rows = [
                    {
                        "Cliente": nombre_cliente,
                        "Estado": "Activo" if activo else "Inactivo",
                        "Cotizaciones": cantidad,
                    }
                    for nombre_cliente, activo, cantidad in session.execute(stmt).all()
                ]
                columns = {
                    "Cliente": "Cliente",
                    "Estado": "Estado",
                    "Cotizaciones": "Cotizaciones",
                }
                chart = [(row["Cliente"], row["Cotizaciones"]) for row in rows[:10]]
                metrics = {"Clientes con actividad": len(rows)}
            elif nombre == "Productos más solicitados":
                stmt = (
                    select(
                        Producto.nombre_es,
                        Cotizacion.moneda,
                        func.sum(DetalleCotizacion.cantidad).label("cantidad"),
                        func.sum(DetalleCotizacion.subtotal).label("subtotal"),
                    )
                    .join(
                        DetalleCotizacion,
                        DetalleCotizacion.concepto_id == Producto.id,
                    )
                    .join(Cotizacion, Cotizacion.id == DetalleCotizacion.cotizacion_id)
                    .where(
                        Cotizacion.creado_en >= desde,
                        Cotizacion.creado_en < hasta,
                    )
                    .group_by(Producto.id, Producto.nombre_es, Cotizacion.moneda)
                    .order_by(func.sum(DetalleCotizacion.cantidad).desc())
                )
                if filtro == "Perecederos":
                    stmt = stmt.where(Producto.es_perecedero.is_(True))
                elif filtro == "Requieren refrigeración":
                    stmt = stmt.where(Producto.requiere_refrigeracion.is_(True))
                rows = [
                    {
                        "Producto": producto,
                        "Moneda": getattr(moneda, "value", moneda),
                        "Cantidad solicitada": Decimal(str(cantidad or 0)),
                        "Subtotal cotizado": Decimal(str(subtotal or 0)),
                    }
                    for producto, moneda, cantidad, subtotal in session.execute(stmt).all()
                ]
                columns = {
                    "Producto": "Producto",
                    "Moneda": "Moneda",
                    "Cantidad solicitada": "Cantidad solicitada",
                    "Subtotal cotizado": "Subtotal cotizado",
                }
                chart = [
                    (
                        f"{row['Producto']} {row['Moneda']}",
                        float(row["Cantidad solicitada"]),
                    )
                    for row in rows[:10]
                ]
                metrics = {"Productos solicitados": len(rows)}
            elif nombre == "Actividad por buque":
                stmt = (
                    select(
                        Buque.nombre,
                        func.count(Cotizacion.id).label("cotizaciones"),
                        func.max(Cotizacion.creado_en).label("ultima"),
                    )
                    .outerjoin(
                        Cotizacion,
                        and_(
                            Cotizacion.buque_id == Buque.id,
                            Cotizacion.creado_en >= desde,
                            Cotizacion.creado_en < hasta,
                        ),
                    )
                    .group_by(Buque.id, Buque.nombre)
                    .order_by(func.count(Cotizacion.id).desc(), Buque.nombre)
                )
                if filtro == "Con cotizaciones":
                    stmt = stmt.having(func.count(Cotizacion.id) > 0)
                elif filtro == "Sin cotizaciones":
                    stmt = stmt.having(func.count(Cotizacion.id) == 0)
                rows = [
                    {
                        "Buque": nombre_buque,
                        "Cotizaciones": cantidad,
                        "Última actividad": ultima,
                    }
                    for nombre_buque, cantidad, ultima in session.execute(stmt).all()
                ]
                columns = {
                    "Buque": "Buque",
                    "Cotizaciones": "Cotizaciones",
                    "Última actividad": "Última actividad",
                }
                chart = [(row["Buque"], row["Cotizaciones"]) for row in rows[:10]]
                metrics = {
                    "Buques": len(rows),
                    "Cotizaciones": sum(row["Cotizaciones"] for row in rows),
                }
            elif nombre == "Análisis financiero":
                stmt = (
                    select(
                        Cotizacion.moneda,
                        func.coalesce(func.sum(Cotizacion.total), 0),
                        func.count(Cotizacion.id),
                    )
                    .where(Cotizacion.creado_en >= desde, Cotizacion.creado_en < hasta)
                )
                if filtro in (Moneda.MXN.value, Moneda.USD.value):
                    stmt = stmt.where(Cotizacion.moneda == Moneda(filtro))
                stmt = stmt.group_by(Cotizacion.moneda).order_by(Cotizacion.moneda)
                rows = [
                    {
                        "Moneda": getattr(moneda, "value", moneda),
                        "Total cotizado": Decimal(str(total or 0)),
                        "Cotizaciones": cantidad,
                    }
                    for moneda, total, cantidad in session.execute(stmt).all()
                ]
                columns = {
                    "Moneda": "Moneda",
                    "Total cotizado": "Total cotizado",
                    "Cotizaciones": "Cotizaciones",
                }
                chart = [(row["Moneda"], float(row["Total cotizado"])) for row in rows]
                metrics = {"Monedas": len(rows), "Cotizaciones": sum(row["Cotizaciones"] for row in rows)}
            else:
                raise ValueError(f"El tipo de informe '{nombre}' no es válido.")

        return {
            "nombre": nombre,
            "periodo": periodo,
            "desde": desde,
            "hasta": hasta,
            "rows": rows,
            "columns": columns,
            "chart": chart,
            "metrics": metrics,
        }
