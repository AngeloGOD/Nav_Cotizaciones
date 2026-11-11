from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
import math

from fuente.negocio.especificaciones.EspecificacionBase import ContextoEscala
from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.Cotizacion import Cotizacion, DetalleCotizacion
from fuente.negocio.modelo.ENUMs import EstadoCotizacion, Moneda
from fuente.negocio.servicio.ServicioServicio import ServicioServicio
from fuente.persistencia.uow.AbstractUnitOfWork import AbstractUnitOfWork

DOS_DECIMALES = Decimal("0.01")
CUATRO_DECIMALES = Decimal("0.0001")


class ServicioCotizacion:

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self._servicio_catalogo = ServicioServicio(uow=uow)

    def recalcular_cotizacion(
        self,
        cotizacion: Cotizacion,
        tasas_iva_por_concepto: dict[int, Decimal] | None = None,
    ) -> Cotizacion:
        if cotizacion.moneda is None:
            cotizacion.moneda = Moneda.MXN
        elif not isinstance(cotizacion.moneda, Moneda):
            cotizacion.moneda = Moneda(str(cotizacion.moneda).upper())

        if cotizacion.moneda == Moneda.MXN:
            cotizacion.tipo_cambio = Decimal("1.0000")
        else:
            if cotizacion.tipo_cambio is None or Decimal(str(cotizacion.tipo_cambio)) <= Decimal("0"):
                raise ValueError(
                    "El tipo de cambio debe ser estrictamente mayor a 0 para cotizaciones en USD."
                )
            cotizacion.tipo_cambio = Decimal(str(cotizacion.tipo_cambio)).quantize(
                CUATRO_DECIMALES, rounding=ROUND_HALF_UP
            )

        tasas_lookup = tasas_iva_por_concepto or {}
        total_acumulado = Decimal("0.00")

        for idx, detalle in enumerate(cotizacion.detalles or [], start=1):
            detalle.disc = idx

            cantidad = Decimal(
                str(detalle.cantidad if detalle.cantidad is not None else "1.00")
            ).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)
            if cantidad <= Decimal("0.00"):
                raise ValueError(
                    f"La cantidad del renglón {idx} debe ser mayor a cero."
                )

            precio_unitario = Decimal(
                str(
                    detalle.precio_unitario
                    if detalle.precio_unitario is not None
                    else "0.00"
                )
            ).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)
            if precio_unitario < Decimal("0.00"):
                raise ValueError(
                    f"El precio unitario del renglón {idx} no puede ser negativo."
                )

            detalle.cantidad = cantidad
            detalle.precio_unitario = precio_unitario
            detalle.subtotal = (cantidad * precio_unitario).quantize(
                DOS_DECIMALES, rounding=ROUND_HALF_UP
            )

            tasa_iva: Decimal | None = None
            if (
                detalle.concepto is not None
                and getattr(detalle.concepto, "tasa_iva", None) is not None
            ):
                tasa_iva = Decimal(str(detalle.concepto.tasa_iva))
                if detalle.concepto_id is None and detalle.concepto.id is not None:
                    detalle.concepto_id = detalle.concepto.id
            elif detalle.concepto_id in tasas_lookup:
                tasa_iva = Decimal(str(tasas_lookup[detalle.concepto_id]))

            if tasa_iva is not None:
                detalle.iva = (detalle.subtotal * tasa_iva).quantize(
                    DOS_DECIMALES, rounding=ROUND_HALF_UP
                )
            elif detalle.iva is not None:
                detalle.iva = Decimal(str(detalle.iva)).quantize(
                    DOS_DECIMALES, rounding=ROUND_HALF_UP
                )
            else:
                detalle.iva = Decimal("0.00")

            total_acumulado += detalle.subtotal + detalle.iva

        cotizacion.total = total_acumulado.quantize(
            DOS_DECIMALES, rounding=ROUND_HALF_UP
        )
        return cotizacion

    def construir_detalles_obligatorios_para_buque(
        self,
        buque_id: int,
        horas_estancia: Decimal,
        moneda: Moneda = Moneda.MXN,
        tipo_cambio: Decimal = Decimal("1.0000"),
        transporta_mercancia_peligrosa: bool = False,
        propulsores_en_optimas_condiciones: bool = True,
        agrupar_entrada_salida: bool = False,
    ) -> list[DetalleCotizacion]:
        moneda_enum = (
            moneda if isinstance(moneda, Moneda) else Moneda(str(moneda).upper())
        )
        if moneda_enum == Moneda.MXN:
            tc = Decimal("1.0000")
        else:
            tc = Decimal(str(tipo_cambio))
            if tc <= Decimal("0"):
                raise ValueError(
                    "El tipo de cambio debe ser estrictamente mayor a 0 para cotizaciones en USD."
                )

        horas = Decimal(str(horas_estancia))
        if horas <= Decimal("0"):
            raise ValueError("Las horas de estancia deben ser mayores a 0.")

        dias_estancia_int = max(1, math.ceil(horas / Decimal("24")))
        dias_estancia_dec = Decimal(dias_estancia_int)

        with self.uow as uow:
            buque = uow.buque.buscar_por_id(buque_id)
            if buque is None:
                raise ValueError(f"No se encontró el buque con id={buque_id}.")
            candidatos = uow.servicio.obtener_candidatos_obligatorios_y_condicionales(
                buque.categoria_buque_id
            )

        contexto = ContextoEscala(
            buque=buque,
            transporta_mercancia_peligrosa=transporta_mercancia_peligrosa,
            propulsores_en_optimas_condiciones=propulsores_en_optimas_condiciones,
            dias_estancia=dias_estancia_int,
            horas_estancia=horas,
        )
        datos_calculo: dict[str, Decimal] = {
            "TRB": Decimal(str(buque.trb)),
            "ESLORA": Decimal(str(buque.eslora)),
            "HORAS_ESTANCIA": horas,
            "DIAS_ESTANCIA": dias_estancia_dec,
        }

        detalles: list[DetalleCotizacion] = []
        for servicio in candidatos:
            if not self._servicio_catalogo.cumple_condicion_obligatoriedad(
                servicio, contexto
            ):
                continue

            cuota_mxn = Decimal(str(servicio.calcular_cuota_basica(datos_calculo)))
            precio_unitario = (cuota_mxn / tc).quantize(
                DOS_DECIMALES, rounding=ROUND_HALF_UP
            )
            tasa_iva = Decimal(
                str(
                    servicio.tasa_iva
                    if servicio.tasa_iva is not None
                    else "0.1600"
                )
            )

            if servicio.requiere_entrada_salida:
                if agrupar_entrada_salida:
                    cantidad = Decimal("2.00")
                    subtotal = (cantidad * precio_unitario).quantize(
                        DOS_DECIMALES, rounding=ROUND_HALF_UP
                    )
                    iva = (subtotal * tasa_iva).quantize(
                        DOS_DECIMALES, rounding=ROUND_HALF_UP
                    )
                    detalles.append(
                        DetalleCotizacion(
                            concepto_id=servicio.id,
                            concepto=servicio,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            subtotal=subtotal,
                            iva=iva,
                            observaciones="ARRIBO Y ZARPE",
                        )
                    )
                else:
                    for etiqueta in ("ON ARRIVAL", "ON DEPARTURE"):
                        cantidad = Decimal("1.00")
                        subtotal = (cantidad * precio_unitario).quantize(
                            DOS_DECIMALES, rounding=ROUND_HALF_UP
                        )
                        iva = (subtotal * tasa_iva).quantize(
                            DOS_DECIMALES, rounding=ROUND_HALF_UP
                        )
                        detalles.append(
                            DetalleCotizacion(
                                concepto_id=servicio.id,
                                concepto=servicio,
                                cantidad=cantidad,
                                precio_unitario=precio_unitario,
                                subtotal=subtotal,
                                iva=iva,
                                observaciones=etiqueta,
                            )
                        )
            else:
                cantidad = Decimal("1.00")
                subtotal = (cantidad * precio_unitario).quantize(
                    DOS_DECIMALES, rounding=ROUND_HALF_UP
                )
                iva = (subtotal * tasa_iva).quantize(
                    DOS_DECIMALES, rounding=ROUND_HALF_UP
                )
                detalles.append(
                    DetalleCotizacion(
                        concepto_id=servicio.id,
                        concepto=servicio,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        subtotal=subtotal,
                        iva=iva,
                        observaciones=None,
                    )
                )

        for idx, detalle in enumerate(detalles, start=1):
            detalle.disc = idx

        return detalles

    def _obtener_tasas_iva_conceptos(
        self, uow: AbstractUnitOfWork, cotizacion: Cotizacion
    ) -> dict[int, Decimal]:
        tasas: dict[int, Decimal] = {}
        for detalle in cotizacion.detalles or []:
            if detalle.concepto is None and detalle.concepto_id is not None:
                concepto_bd = uow.session.get(Concepto, detalle.concepto_id)
                if concepto_bd is not None and concepto_bd.tasa_iva is not None:
                    tasas[detalle.concepto_id] = Decimal(str(concepto_bd.tasa_iva))
        return tasas

    def registrar_cotizacion(self, cotizacion: Cotizacion) -> Cotizacion:
        if cotizacion is None:
            raise ValueError("La cotización no puede ser nula.")
        if not cotizacion.folio or not cotizacion.folio.strip():
            raise ValueError("El folio de la cotización es obligatorio.")
        if not cotizacion.detalles:
            raise ValueError(
                "La cotización debe contener al menos un detalle para registrarse."
            )

        cotizacion.folio = cotizacion.folio.strip()

        with self.uow as uow:
            existente = uow.cotizacion.buscar_por_folio(cotizacion.folio)
            if existente is not None:
                raise ValueError(
                    f"Ya existe una cotización registrada con el folio '{cotizacion.folio}'."
                )

            tasas = self._obtener_tasas_iva_conceptos(uow, cotizacion)
            self.recalcular_cotizacion(cotizacion, tasas_iva_por_concepto=tasas)
            uow.cotizacion.insertar(cotizacion)
            uow.commit()
            return uow.cotizacion.buscar_por_id(cotizacion.id)

    def modificar_cotizacion(self, cotizacion: Cotizacion) -> Cotizacion:
        if cotizacion is None or cotizacion.id is None:
            raise ValueError(
                "La cotización a modificar debe tener un identificador válido."
            )
        if not cotizacion.folio or not cotizacion.folio.strip():
            raise ValueError("El folio de la cotización es obligatorio.")
        if not cotizacion.detalles:
            raise ValueError(
                "La cotización debe conservar al menos un detalle al modificarse."
            )

        cotizacion.folio = cotizacion.folio.strip()

        with self.uow as uow:
            duplicado = uow.cotizacion.buscar_por_folio(cotizacion.folio)
            if duplicado is not None and duplicado.id != cotizacion.id:
                raise ValueError(
                    f"Ya existe otra cotización con el folio '{cotizacion.folio}'."
                )

            tasas = self._obtener_tasas_iva_conceptos(uow, cotizacion)
            self.recalcular_cotizacion(cotizacion, tasas_iva_por_concepto=tasas)
            uow.cotizacion.modificar(cotizacion)
            uow.commit()
            return uow.cotizacion.buscar_por_id(cotizacion.id)

    def cambiar_estado_cotizacion(
        self, cotizacion_id: int, nuevo_estado: EstadoCotizacion
    ) -> Cotizacion:
        estado_enum = (
            nuevo_estado
            if isinstance(nuevo_estado, EstadoCotizacion)
            else EstadoCotizacion(str(nuevo_estado).upper())
        )
        with self.uow as uow:
            existente = uow.cotizacion.buscar_por_id(cotizacion_id)
            if existente is None:
                raise ValueError(
                    f"No existe la cotización con id={cotizacion_id}."
                )
            existente.estado = estado_enum
            uow.session.flush()
            uow.commit()
            return uow.cotizacion.buscar_por_id(cotizacion_id)

    def buscar_por_id(self, id_cotizacion: int) -> Cotizacion | None:
        with self.uow as uow:
            return uow.cotizacion.buscar_por_id(id_cotizacion)

    def buscar_por_folio(self, folio: str) -> Cotizacion | None:
        with self.uow as uow:
            return uow.cotizacion.buscar_por_folio(folio)

    def obtener_pagina(
        self, pagina: int, limite: int = 10, filtros: dict | None = None
    ) -> list[Cotizacion]:
        pagina_valida = max(1, int(pagina))
        desplazamiento = (pagina_valida - 1) * limite
        with self.uow as uow:
            return uow.cotizacion.consultar_pagina(desplazamiento, limite, filtros)

    def obtener_cantidad_registros(self, filtros: dict | None = None) -> int:
        with self.uow as uow:
            return uow.cotizacion.contar_registros(filtros)

    def obtener_resumen_estados(self) -> dict[str, int]:
        with self.uow as uow:
            return uow.cotizacion.contar_por_estado()
