from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import math

from sqlalchemy.exc import SQLAlchemyError

from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.Cliente import Cliente
from fuente.negocio.modelo.Cotizacion import Cotizacion, DetalleCotizacion
from fuente.negocio.modelo.ENUMs import (
    EstadoCotizacion,
    Moneda,
    RegimenAduanero,
)
from fuente.negocio.modelo.Servicio import Servicio
from fuente.negocio.servicio.ServicioBuque import ServicioBuque
from fuente.negocio.servicio.ServicioCliente import ServicioCliente
from fuente.negocio.servicio.ServicioCotizacion import ServicioCotizacion
from fuente.negocio.servicio.ServicioServicio import ServicioServicio


class ErrorCotizacion(Exception):
    """Excepción de negocio para errores al procesar o persistir una cotización."""


class ControladorCotizacion:
    """Controlador de aplicación que coordina la vista de Cotizaciones / Nueva Cotización con el dominio."""

    def __init__(
        self,
        servicio_cotizacion: ServicioCotizacion,
        servicio_buque: ServicioBuque | None = None,
        servicio_cliente: ServicioCliente | None = None,
        servicio_servicio: ServicioServicio | None = None,
    ):
        self.servicio_cotizacion = servicio_cotizacion
        uow = getattr(servicio_cotizacion, "uow", None)
        self.servicio_buque = (
            servicio_buque
            if servicio_buque is not None
            else (ServicioBuque(uow) if uow is not None else None)
        )
        self.servicio_cliente = (
            servicio_cliente
            if servicio_cliente is not None
            else (ServicioCliente(uow) if uow is not None else None)
        )
        self.servicio_servicio = (
            servicio_servicio
            if servicio_servicio is not None
            else (ServicioServicio(uow) if uow is not None else None)
        )

    def obtener_folio_sugerido(self) -> str:
        return self.servicio_cotizacion.obtener_siguiente_folio_pda()

    @staticmethod
    def _a_decimal(
        valor: Decimal | int | float | str | None,
        etiqueta: str,
        por_defecto: Decimal | None = None,
    ) -> Decimal:
        if valor is None or str(valor).strip() == "":
            if por_defecto is not None:
                return por_defecto
            raise ValueError(f"{etiqueta} es obligatorio.")
        texto = str(valor).strip().replace("$", "").replace(",", "")
        try:
            numero = Decimal(texto)
        except (InvalidOperation, ValueError, TypeError) as error:
            raise ValueError(f"{etiqueta} debe ser un número válido.") from error
        if not numero.is_finite():
            raise ValueError(f"{etiqueta} debe ser un número válido.")
        return numero

    @staticmethod
    def _a_fecha(
        valor: date | datetime | str | None,
        etiqueta: str,
        obligatorio: bool = False,
    ) -> datetime | None:
        if valor is None or (isinstance(valor, str) and not valor.strip()):
            if obligatorio:
                raise ValueError(f"{etiqueta} es obligatoria.")
            return None
        tz_local = datetime.now().astimezone().tzinfo
        if isinstance(valor, datetime):
            return valor if valor.tzinfo else valor.replace(tzinfo=tz_local)
        if isinstance(valor, date):
            return datetime.combine(valor, time(0, 0), tzinfo=tz_local)
        texto = str(valor).strip()
        for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
            try:
                fecha_d = datetime.strptime(texto, fmt).date()
                return datetime.combine(fecha_d, time(0, 0), tzinfo=tz_local)
            except ValueError:
                continue
        raise ValueError(f"{etiqueta} debe tener formato dd/mm/aaaa.")

    @staticmethod
    def _normalizar_moneda(moneda: Moneda | str | None) -> Moneda:
        if isinstance(moneda, Moneda):
            return moneda
        texto = str(moneda or "MXN").strip().upper()
        if texto.startswith("USD"):
            return Moneda.USD
        return Moneda.MXN

    @staticmethod
    def _normalizar_estado(
        estado: EstadoCotizacion | str | None,
    ) -> EstadoCotizacion:
        if isinstance(estado, EstadoCotizacion):
            return estado
        texto = str(estado or "PENDIENTE").strip().upper()
        mapa = {
            "PENDIENTE": EstadoCotizacion.PROFORMA,
            "PROFORMA": EstadoCotizacion.PROFORMA,
            "BORRADOR": EstadoCotizacion.BORRADOR,
            "ANTICIPO_RECIBIDO": EstadoCotizacion.ANTICIPO_RECIBIDO,
            "EN_OPERACION": EstadoCotizacion.EN_OPERACION,
            "LIQUIDADA_FDA": EstadoCotizacion.LIQUIDADA_FDA,
            "APROBADA": EstadoCotizacion.APROBADA,
            "RECHAZADA": EstadoCotizacion.RECHAZADA,
            "CANCELADA": EstadoCotizacion.RECHAZADA,
        }
        return mapa.get(texto, EstadoCotizacion.PENDIENTE)

    @classmethod
    def calcular_dias_estancia(
        cls, horas_estancia: Decimal | int | float | str | None
    ) -> int:
        try:
            horas = cls._a_decimal(
                horas_estancia, "Las horas de estancia", Decimal("0.00")
            )
        except ValueError:
            return 0
        if horas <= Decimal("0"):
            return 0
        return max(1, int(math.ceil(horas / Decimal("24"))))

    @staticmethod
    def formatear_moneda(
        monto: Decimal | int | float | str | None, incluir_signo: bool = True
    ) -> str:
        try:
            valor = Decimal(
                str(monto if monto is not None else "0.00")
                .replace("$", "")
                .replace(",", "")
                .strip()
                or "0.00"
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        except (InvalidOperation, ValueError):
            valor = Decimal("0.00")
        prefijo = "$ " if incluir_signo else ""
        return f"{prefijo}{valor:,.2f}"

    @classmethod
    def formatear_iva_celda(
        cls,
        iva: Decimal | int | float | str | None,
        tasa_iva: Decimal | int | float | str | None = None,
    ) -> str:
        try:
            iva_dec = Decimal(str(iva if iva is not None else "0.00")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        except (InvalidOperation, ValueError):
            iva_dec = Decimal("0.00")

        if iva_dec == Decimal("0.00"):
            if tasa_iva is None:
                return "$ -"
            try:
                if Decimal(str(tasa_iva)) == Decimal("0"):
                    return "$ -"
            except (InvalidOperation, ValueError):
                return "$ -"
        return cls.formatear_moneda(iva_dec)

    @classmethod
    def recalcular_importes_fila(
        cls,
        cantidad: Decimal | int | float | str,
        precio_unitario: Decimal | int | float | str,
        tasa_iva: Decimal | int | float | str = Decimal("0.1600"),
    ) -> dict[str, Decimal]:
        cant = cls._a_decimal(cantidad, "La cantidad", Decimal("0.00"))
        if cant < Decimal("0"):
            cant = Decimal("0.00")
        precio = cls._a_decimal(
            precio_unitario, "El precio unitario", Decimal("0.00")
        )
        if precio < Decimal("0"):
            precio = Decimal("0.00")
        tasa = cls._a_decimal(tasa_iva, "La tasa de IVA", Decimal("0.0000"))

        subtotal = (cant * precio).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        iva = (subtotal * tasa).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        total = (subtotal + iva).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        return {
            "cantidad": cant.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "precio_unitario": precio.quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            ),
            "subtotal": subtotal,
            "iva": iva,
            "total": total,
        }

    def calcular_servicios_obligatorios(
        self,
        buque: Buque,
        horas_estancia: Decimal | int | float | str = Decimal("24.00"),
        moneda: Moneda | str = Moneda.MXN,
        tipo_cambio: Decimal | int | float | str = Decimal("1.0000"),
        transporta_mercancia_peligrosa: bool = False,
        propulsores_optimos: bool | None = None,
        propulsores_danados: bool | None = None,
        propulsores_en_optimas_condiciones: bool | None = None,
        agrupar_entrada_salida: bool = True,
    ) -> list[DetalleCotizacion]:
        if buque is None:
            raise ValueError(
                "Debe seleccionar un buque para calcular los servicios."
            )

        horas_dec = self._a_decimal(horas_estancia, "Las horas de estancia")
        if horas_dec <= Decimal("0"):
            raise ValueError("Las horas de estancia deben ser mayores que 0.")

        moneda_enum = self._normalizar_moneda(moneda)
        tc_dec = (
            Decimal("1.0000")
            if moneda_enum == Moneda.MXN
            else self._a_decimal(tipo_cambio, "El tipo de cambio")
        )
        if tc_dec <= Decimal("0"):
            raise ValueError("El tipo de cambio debe ser mayor que 0.")

        if propulsores_en_optimas_condiciones is not None:
            propulsores_en_optimas = bool(propulsores_en_optimas_condiciones)
        elif propulsores_danados is not None:
            propulsores_en_optimas = not bool(propulsores_danados)
        elif propulsores_optimos is not None:
            propulsores_en_optimas = bool(propulsores_optimos)
        else:
            propulsores_en_optimas = True

        return self.servicio_cotizacion.construir_detalles_obligatorios_para_buque(
            buque=buque,
            horas_estancia=horas_dec,
            moneda=moneda_enum,
            tipo_cambio=tc_dec,
            transporta_mercancia_peligrosa=bool(transporta_mercancia_peligrosa),
            propulsores_en_optimas_condiciones=propulsores_en_optimas,
            agrupar_entrada_salida=agrupar_entrada_salida,
        )

    def calcular_detalle_para_servicio_manual(
        self,
        servicio: Servicio,
        buque: Buque | None = None,
        horas_estancia: Decimal | int | float | str = Decimal("24.00"),
        moneda: Moneda | str = Moneda.MXN,
        tipo_cambio: Decimal | int | float | str = Decimal("1.0000"),
        cantidad: Decimal | int | float | str | None = None,
    ) -> dict:
        if servicio is None:
            raise ValueError("Debe seleccionar un servicio válido.")

        horas_dec = self._a_decimal(
            horas_estancia, "Las horas de estancia", Decimal("24.00")
        )
        if horas_dec <= Decimal("0"):
            horas_dec = Decimal("24.00")

        moneda_enum = self._normalizar_moneda(moneda)
        tc_dec = (
            Decimal("1.0000")
            if moneda_enum == Moneda.MXN
            else self._a_decimal(
                tipo_cambio, "El tipo de cambio", Decimal("16.0000")
            )
        )
        if tc_dec <= Decimal("0"):
            raise ValueError("El tipo de cambio debe ser mayor que 0.")

        detalle = self.servicio_cotizacion.construir_detalle_servicio(
            servicio=servicio,
            buque=buque,
            horas_estancia=horas_dec,
            moneda=moneda_enum,
            tipo_cambio=tc_dec,
            disc=1,
            cantidad=cantidad,
            agrupar_entrada_salida=True,
        )

        concepto_hidratado = getattr(detalle, "concepto", None) or servicio
        proveedores = getattr(concepto_hidratado, "proveedores", None) or []
        proveedor_principal = proveedores[0] if proveedores else None

        return {
            "concepto_id": detalle.concepto_id,
            "servicio": concepto_hidratado,
            "concepto": concepto_hidratado,
            "categoria_pda": detalle.categoria_pda_nombre,
            "descripcion": concepto_hidratado.nombre_es,
            "nombre_es": concepto_hidratado.nombre_es,
            "proveedor": detalle.proveedor_nombre,
            "proveedor_id": (
                getattr(proveedor_principal, "id", None)
                if proveedor_principal is not None
                else None
            ),
            "proveedor_obj": proveedor_principal,
            "cantidad": detalle.cantidad,
            "precio_unitario": detalle.precio_unitario,
            "tasa_iva": detalle.tasa_iva,
            "subtotal": detalle.subtotal,
            "iva": detalle.iva,
            "total": detalle.total,
            "factura": detalle.factura or "",
            "observaciones": detalle.observaciones or "",
            "detalle": detalle,
        }

    def guardar_nueva_cotizacion(
        self,
        *,
        cliente: Cliente | None = None,
        cliente_id: int | None = None,
        buque: Buque | None = None,
        buque_id: int | None = None,
        detalles: list[DetalleCotizacion | dict] | None = None,
        folio: str | None = None,
        fecha_emision: date | datetime | str | None = None,
        fecha_arribo: date | datetime | str | None = None,
        fecha_zarpe: date | datetime | str | None = None,
        horas_estancia: Decimal | int | float | str = Decimal("24.00"),
        moneda: Moneda | str = Moneda.MXN,
        tipo_cambio: Decimal | int | float | str = Decimal("1.0000"),
        regimen_aduanero: RegimenAduanero | str = RegimenAduanero.NINGUNO,
        estado: EstadoCotizacion | str = EstadoCotizacion.PENDIENTE,
        transporta_mercancia_peligrosa: bool = False,
        propulsores_en_optimas_condiciones: bool | None = None,
        propulsores_danados: bool | None = None,
        observaciones: str | None = None,
        usuario_id: int | None = None,
    ) -> Cotizacion:
        id_buque_resuelto = (
            int(buque_id)
            if buque_id is not None
            else (
                int(buque.id)
                if buque is not None and getattr(buque, "id", None) is not None
                else None
            )
        )
        if id_buque_resuelto is None:
            raise ValueError("Debe seleccionar un buque para la cotización.")

        id_cliente_resuelto = (
            int(cliente_id)
            if cliente_id is not None
            else (
                int(cliente.id)
                if cliente is not None
                and getattr(cliente, "id", None) is not None
                else None
            )
        )
        if id_cliente_resuelto is None:
            raise ValueError("Debe seleccionar un cliente para la cotización.")

        horas_dec = self._a_decimal(horas_estancia, "Las horas de estancia")
        if horas_dec <= Decimal("0"):
            raise ValueError("Las horas de estancia deben ser mayores que 0.")

        moneda_enum = self._normalizar_moneda(moneda)
        tc_dec = (
            Decimal("1.0000")
            if moneda_enum == Moneda.MXN
            else self._a_decimal(tipo_cambio, "El tipo de cambio")
        )
        if tc_dec <= Decimal("0"):
            raise ValueError("El tipo de cambio debe ser mayor que 0.")

        fecha_emision_dt = (
            self._a_fecha(fecha_emision, "La fecha de emisión")
            or datetime.now().astimezone()
        )
        fecha_arribo_dt = (
            self._a_fecha(fecha_arribo, "La fecha de arribo (ETA)")
            or fecha_emision_dt
        )
        fecha_zarpe_dt = self._a_fecha(fecha_zarpe, "La fecha de zarpe (ETD)")

        if (
            fecha_arribo_dt is not None
            and fecha_zarpe_dt is not None
            and fecha_zarpe_dt < fecha_arribo_dt
        ):
            raise ValueError(
                "La fecha de zarpe (ETD) no puede ser anterior a la fecha de arribo (ETA)."
            )

        detalles_entidad: list[DetalleCotizacion] = []
        for item in detalles or []:
            if isinstance(item, DetalleCotizacion):
                concepto_obj = item.__dict__.get("concepto")
                concepto_id = getattr(item, "concepto_id", None) or (
                    getattr(concepto_obj, "id", None)
                    if concepto_obj is not None
                    else None
                )
                if concepto_id is None:
                    continue
                det = DetalleCotizacion(
                    disc=len(detalles_entidad) + 1,
                    concepto_id=int(concepto_id),
                    cantidad=item.cantidad,
                    precio_unitario=item.precio_unitario,
                    subtotal=item.subtotal,
                    iva=item.iva,
                    factura=item.factura,
                    observaciones=item.observaciones,
                )
                if concepto_obj is not None:
                    det.concepto = concepto_obj
                detalles_entidad.append(det)
            elif isinstance(item, dict):
                servicio_obj = item.get("servicio") or item.get("concepto")
                concepto_id = item.get("concepto_id") or (
                    getattr(servicio_obj, "id", None) if servicio_obj else None
                )
                if concepto_id is None:
                    continue
                cant = self._a_decimal(
                    item.get("cantidad", Decimal("1.00")),
                    "La cantidad",
                    Decimal("1.00"),
                )
                if cant <= Decimal("0"):
                    raise ValueError(
                        "La cantidad de cada concepto debe ser mayor que 0."
                    )
                precio = self._a_decimal(
                    item.get("precio_unitario", Decimal("0.00")),
                    "El precio unitario",
                    Decimal("0.00"),
                )
                tasa = self._a_decimal(
                    item.get(
                        "tasa_iva",
                        getattr(servicio_obj, "tasa_iva", Decimal("0.1600")),
                    ),
                    "La tasa de IVA",
                    Decimal("0.1600"),
                )
                subtotal = (
                    self._a_decimal(item["subtotal"], "El subtotal")
                    if "subtotal" in item and item["subtotal"] is not None
                    else (cant * precio).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                )
                iva = (
                    self._a_decimal(item["iva"], "El IVA")
                    if "iva" in item and item["iva"] is not None
                    else (subtotal * tasa).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                )

                det = DetalleCotizacion(
                    disc=len(detalles_entidad) + 1,
                    concepto_id=int(concepto_id),
                    cantidad=cant,
                    precio_unitario=precio,
                    subtotal=subtotal,
                    iva=iva,
                    factura=(str(item.get("factura") or "").strip() or None),
                    observaciones=(
                        str(item.get("observaciones") or "").strip() or None
                    ),
                )
                if servicio_obj is not None:
                    det.concepto = servicio_obj
                detalles_entidad.append(det)

        if not detalles_entidad:
            raise ValueError(
                "La cotización debe incluir al menos un servicio o concepto seleccionado."
            )

        for idx, det in enumerate(detalles_entidad, start=1):
            det.disc = idx

        estado_enum = self._normalizar_estado(estado)

        cotizacion = Cotizacion(
            folio=(folio or "").strip(),
            cliente_id=id_cliente_resuelto,
            buque_id=id_buque_resuelto,
            fecha_arribo=fecha_arribo_dt,
            fecha_zarpe=fecha_zarpe_dt,
            horas_estancia=horas_dec,
            moneda=moneda_enum,
            tipo_cambio=tc_dec,
            estado=estado_enum,
            detalles=detalles_entidad,
        )
        self.servicio_cotizacion.recalcular_cotizacion(cotizacion)

        try:
            return self.servicio_cotizacion.registrar_cotizacion(cotizacion)
        except SQLAlchemyError as error:
            raise ErrorCotizacion(
                "Ocurrió un error al guardar la cotización en la base de datos."
            ) from error

    def obtener_historial_cotizaciones(
        self,
        pagina: int = 1,
        limite: int = 10,
        filtros: dict | None = None,
        texto: str = "",
    ) -> tuple[list[Cotizacion], int]:
        if self.servicio_cotizacion is None:
            return [], 0
        return self.servicio_cotizacion.consultar_pagina(
            no_pagina=pagina,
            limite=limite,
            filtros=filtros or {},
            texto=texto or "",
        )
