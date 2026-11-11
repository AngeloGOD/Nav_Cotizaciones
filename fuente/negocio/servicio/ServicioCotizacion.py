from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import logging
import math
import uuid

from sqlalchemy.exc import SQLAlchemyError

from fuente.negocio.especificaciones.EspecificacionBase import ContextoEscala
from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.Cotizacion import Cotizacion, DetalleCotizacion
from fuente.negocio.modelo.ENUMs import EstadoCotizacion, Moneda, VariableMedida
from fuente.negocio.modelo.Servicio import Servicio
from fuente.negocio.servicio.ServicioServicio import ServicioServicio
from fuente.persistencia.uow.AbstractUnitOfWork import AbstractUnitOfWork

DOS_DECIMALES = Decimal("0.01")
CUATRO_DECIMALES = Decimal("0.0001")


class ServicioCotizacion:

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow
        self._servicio_catalogo = ServicioServicio(uow=uow)

    def obtener_siguiente_folio_pda(self) -> str:
        with self.uow as uow:
            siguiente_id = uow.cotizacion.obtener_siguiente_id()
            return f"PDA.-{int(siguiente_id):04d}"

    @staticmethod
    def construir_datos_calculo(
        buque: Buque | None,
        horas_estancia: Decimal | int | float | str = Decimal("24.00"),
        dias_estancia: int | None = None,
        datos_adicionales: dict[str, Decimal] | None = None,
    ) -> dict[str, Decimal]:
        horas = Decimal(
            str(horas_estancia if horas_estancia is not None else "24.00")
        )
        if dias_estancia is not None:
            dias = int(dias_estancia)
        elif horas > Decimal("0"):
            dias = max(1, int(math.ceil(horas / Decimal("24"))))
        else:
            dias = 1

        trb = (
            Decimal(str(getattr(buque, "trb", "0.00") or "0.00"))
            if buque
            else Decimal("0.00")
        )
        eslora = (
            Decimal(str(getattr(buque, "eslora", "0.00") or "0.00"))
            if buque
            else Decimal("0.00")
        )

        datos: dict[str, Decimal] = {
            VariableMedida.TRB.value: trb,
            VariableMedida.ESLORA.value: eslora,
            VariableMedida.HORAS_ESTANCIA.value: horas,
            VariableMedida.DIAS_ESTANCIA.value: Decimal(str(dias)),
            VariableMedida.TONELADAS.value: Decimal("0.00"),
            VariableMedida.CONTENEDORES.value: Decimal("0.00"),
            VariableMedida.M3.value: Decimal("0.00"),
            VariableMedida.PASAJEROS.value: Decimal("0.00"),
            VariableMedida.PESO_KG.value: Decimal("0.00"),
            VariableMedida.DIAS_ALMACENAJE.value: Decimal("0.00"),
            VariableMedida.CANTIDAD_EVENTOS.value: Decimal("1.00"),
        }
        if datos_adicionales:
            for clave, valor in datos_adicionales.items():
                datos[str(clave)] = Decimal(str(valor))
        return datos

    @staticmethod
    def convertir_monto(
        monto_mxn: Decimal,
        moneda: Moneda | str = Moneda.MXN,
        tipo_cambio: Decimal | int | float | str = Decimal("1.0000"),
    ) -> Decimal:
        monto = Decimal(str(monto_mxn or "0.00"))
        moneda_valor = (
            moneda.value
            if isinstance(moneda, Moneda)
            else str(moneda or "MXN").upper()
        )
        if moneda_valor == Moneda.USD.value:
            tc = Decimal(str(tipo_cambio or "1.0000"))
            if tc <= Decimal("0"):
                raise ValueError(
                    "El tipo de cambio debe ser estrictamente mayor a 0 para cotizaciones en USD."
                )
            return (monto / tc).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)
        return monto.quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)

    @staticmethod
    def determinar_observacion_servicio(
        servicio: Servicio,
        horas_estancia: Decimal | int | float | str = Decimal("24.00"),
        etiqueta_maniobra: str = "",
        agrupar_entrada_salida: bool = True,
    ) -> str | None:
        if getattr(servicio, "requiere_entrada_salida", False):
            if agrupar_entrada_salida:
                return "ARRIBO Y ZARPE"
            return etiqueta_maniobra or "ON ARRIVAL"

        var_primaria = getattr(servicio, "variable_primaria", None)
        var_secundaria = getattr(servicio, "variable_secundaria", None)
        horas_dec = Decimal(
            str(horas_estancia if horas_estancia is not None else "24")
        )
        horas_str = (
            str(int(horas_dec))
            if horas_dec == int(horas_dec)
            else str(horas_dec.normalize())
        )
        nombre_upper = (getattr(servicio, "nombre_es", "") or "").upper()

        if (
            var_primaria == VariableMedida.HORAS_ESTANCIA
            or var_secundaria == VariableMedida.HORAS_ESTANCIA
        ):
            if "ATRAQUE" in nombre_upper:
                return f"{horas_str} HORAS DE ATRAQUE"
            return f"{horas_str} HORAS DE SERVICIO"

        if "APOYO AMARRE" in nombre_upper:
            return "ARRIBO"

        if (
            "DERECHOS FONDEO" in nombre_upper
            or "CUOTA DE AGENCIAMIENTO" in nombre_upper
        ):
            return "OVERTIME"

        return etiqueta_maniobra or None

    def construir_detalle_servicio(
        self,
        servicio: Servicio,
        buque: Buque | None,
        horas_estancia: Decimal | int | float | str = Decimal("24.00"),
        moneda: Moneda | str = Moneda.MXN,
        tipo_cambio: Decimal | int | float | str = Decimal("1.0000"),
        disc: int = 1,
        cantidad: Decimal | int | float | str | None = None,
        observaciones: str | None = None,
        agrupar_entrada_salida: bool = True,
        datos_adicionales: dict[str, Decimal] | None = None,
    ) -> DetalleCotizacion:
        if (
            getattr(servicio, "id", None) is not None
            and (
                "categoria_pda" not in getattr(servicio, "__dict__", {})
                or "proveedores" not in getattr(servicio, "__dict__", {})
            )
            and self.uow is not None
        ):
            with self.uow as uow:
                servicio_hidratado = uow.servicio.buscar_por_id(int(servicio.id))
                if servicio_hidratado is not None:
                    servicio = servicio_hidratado

        horas_dec = Decimal(
            str(horas_estancia if horas_estancia is not None else "24.00")
        )
        datos_calculo = self.construir_datos_calculo(
            buque=buque,
            horas_estancia=horas_dec,
            datos_adicionales=datos_adicionales,
        )
        cuota_mxn = Decimal(str(servicio.calcular_cuota_basica(datos_calculo)))
        precio_unitario = self.convertir_monto(
            cuota_mxn, moneda=moneda, tipo_cambio=tipo_cambio
        )

        if cantidad is not None:
            cantidad_dec = Decimal(str(cantidad)).quantize(
                DOS_DECIMALES, rounding=ROUND_HALF_UP
            )
        elif (
            getattr(servicio, "requiere_entrada_salida", False)
            and agrupar_entrada_salida
        ):
            cantidad_dec = Decimal("2.00")
        else:
            cantidad_dec = Decimal("1.00")

        subtotal = (precio_unitario * cantidad_dec).quantize(
            DOS_DECIMALES, rounding=ROUND_HALF_UP
        )
        tasa_iva = Decimal(
            str(
                servicio.tasa_iva
                if getattr(servicio, "tasa_iva", None) is not None
                else "0.1600"
            )
        )
        iva = (subtotal * tasa_iva).quantize(
            DOS_DECIMALES, rounding=ROUND_HALF_UP
        )

        if observaciones is None:
            observaciones_final = self.determinar_observacion_servicio(
                servicio=servicio,
                horas_estancia=horas_dec,
                agrupar_entrada_salida=agrupar_entrada_salida,
            )
        else:
            observaciones_final = observaciones

        detalle = DetalleCotizacion(
            disc=int(disc),
            concepto_id=int(servicio.id),
            concepto=servicio,
            cantidad=cantidad_dec,
            precio_unitario=precio_unitario,
            subtotal=subtotal,
            iva=iva,
            factura=None,
            observaciones=observaciones_final,
        )
        return detalle

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
            if cotizacion.tipo_cambio is None or Decimal(
                str(cotizacion.tipo_cambio)
            ) <= Decimal("0"):
                raise ValueError(
                    "El tipo de cambio debe ser estrictamente mayor a 0 para cotizaciones en USD."
                )
            cotizacion.tipo_cambio = Decimal(
                str(cotizacion.tipo_cambio)
            ).quantize(CUATRO_DECIMALES, rounding=ROUND_HALF_UP)

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
                if (
                    detalle.concepto_id is None
                    and detalle.concepto.id is not None
                ):
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
        buque_id: int | Buque | None = None,
        horas_estancia: Decimal = Decimal("24.00"),
        moneda: Moneda = Moneda.MXN,
        tipo_cambio: Decimal = Decimal("1.0000"),
        transporta_mercancia_peligrosa: bool = False,
        propulsores_en_optimas_condiciones: bool = True,
        agrupar_entrada_salida: bool = False,
        *,
        buque: Buque | None = None,
    ) -> list[DetalleCotizacion]:
        moneda_enum = (
            moneda
            if isinstance(moneda, Moneda)
            else Moneda(str(moneda).upper())
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

        buque_obj: Buque | None = buque if buque is not None else (
            buque_id if isinstance(buque_id, Buque) else None
        )
        id_buque_resuelto: int | None = (
            int(buque_obj.id)
            if buque_obj is not None and getattr(buque_obj, "id", None) is not None
            else (
                int(buque_id)
                if buque_id is not None and not isinstance(buque_id, Buque)
                else None
            )
        )

        with self.uow as uow:
            if id_buque_resuelto is not None:
                buque_bd = uow.buque.buscar_por_id(id_buque_resuelto)
                if buque_bd is not None:
                    buque_obj = buque_bd
            if buque_obj is None:
                raise ValueError(
                    f"No se encontró el buque con id={id_buque_resuelto}."
                )
            categoria_buque_id = getattr(buque_obj, "categoria_buque_id", None)
            if (
                categoria_buque_id is None
                and getattr(buque_obj, "categoria_buque", None) is not None
            ):
                categoria_buque_id = getattr(
                    buque_obj.categoria_buque, "id", None
                )
            candidatos = (
                uow.servicio.obtener_candidatos_obligatorios_y_condicionales(
                    categoria_buque_id
                )
            )

        contexto = ContextoEscala(
            buque=buque_obj,
            transporta_mercancia_peligrosa=bool(transporta_mercancia_peligrosa),
            propulsores_en_optimas_condiciones=bool(
                propulsores_en_optimas_condiciones
            ),
            dias_estancia=dias_estancia_int,
            horas_estancia=horas,
        )
        datos_calculo: dict[str, Decimal] = {
            "TRB": Decimal(str(buque_obj.trb)),
            "ESLORA": Decimal(str(buque_obj.eslora)),
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
                obs = (
                    self.determinar_observacion_servicio(
                        servicio=servicio,
                        horas_estancia=horas,
                        agrupar_entrada_salida=agrupar_entrada_salida,
                    )
                    if agrupar_entrada_salida
                    else None
                )
                detalles.append(
                    DetalleCotizacion(
                        concepto_id=servicio.id,
                        concepto=servicio,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                        subtotal=subtotal,
                        iva=iva,
                        observaciones=obs,
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
                    tasas[detalle.concepto_id] = Decimal(
                        str(concepto_bd.tasa_iva)
                    )
        return tasas

    def registrar_cotizacion(self, cotizacion: Cotizacion) -> Cotizacion:
        if cotizacion is None:
            raise ValueError("La cotización no puede ser nula.")
        if not cotizacion.detalles:
            raise ValueError(
                "La cotización debe contener al menos un detalle para registrarse."
            )

        folio_actual = (cotizacion.folio or "").strip()

        try:
            with self.uow as uow:
                id_sugerido = uow.cotizacion.obtener_siguiente_id()
                folio_sugerido = f"PDA.-{int(id_sugerido):04d}"

                es_folio_provisional = (
                    not folio_actual
                    or folio_actual.upper() in ("PROVISIONAL", "AUTO", "PENDIENTE")
                    or folio_actual == folio_sugerido
                )

                if not es_folio_provisional:
                    existente = uow.cotizacion.buscar_por_folio(folio_actual)
                    if existente is not None:
                        raise ValueError(
                            f"Ya existe una cotización registrada con el folio '{folio_actual}'."
                        )
                    cotizacion.folio = folio_actual
                else:
                    cotizacion.folio = f"__PROVISIONAL_{uuid.uuid4().hex[:10]}__"

                tasas = self._obtener_tasas_iva_conceptos(uow, cotizacion)
                self.recalcular_cotizacion(cotizacion, tasas_iva_por_concepto=tasas)
                uow.cotizacion.insertar(cotizacion)

                if es_folio_provisional and cotizacion.id is not None:
                    cotizacion.folio = f"PDA.-{int(cotizacion.id):04d}"
                    uow.session.flush()

                uow.commit()
                return uow.cotizacion.buscar_por_id(cotizacion.id)
        except SQLAlchemyError:
            logging.exception("No se pudo persistir la cotización.")
            raise

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

    def eliminar_cotizaciones(self, ids: list[int]) -> int:
        ids_unicos = list(dict.fromkeys(int(id_cotizacion) for id_cotizacion in ids))
        if not ids_unicos:
            return 0

        with self.uow as uow:
            cotizaciones = []
            for id_cotizacion in ids_unicos:
                cotizacion = uow.cotizacion.buscar_por_id(id_cotizacion)
                if cotizacion is None:
                    raise ValueError(
                        f"La cotización con identificador {id_cotizacion} ya no existe."
                    )
                cotizaciones.append(cotizacion)

            for cotizacion in cotizaciones:
                uow.cotizacion.eliminar(cotizacion)
            uow.commit()
        return len(cotizaciones)

    def consultar_pagina(
        self,
        no_pagina: int = 1,
        limite: int = 10,
        filtros: dict | None = None,
        texto: str = "",
    ) -> tuple[list[Cotizacion], int]:
        pagina_valida = max(1, int(no_pagina))
        desplazamiento = (pagina_valida - 1) * int(limite)
        filtros_consulta = dict(filtros or {})
        if texto and texto.strip():
            filtros_consulta["texto"] = texto.strip()
        with self.uow as uow:
            registros = uow.cotizacion.consultar_pagina(
                desplazamiento, limite, filtros_consulta
            )
            total = uow.cotizacion.contar_registros(filtros_consulta)
            return registros, total

    def obtener_pagina(
        self, pagina: int = 1, limite: int = 10, filtros: dict | None = None
    ) -> list[Cotizacion]:
        pagina_valida = max(1, int(pagina))
        desplazamiento = (pagina_valida - 1) * limite
        with self.uow as uow:
            return uow.cotizacion.consultar_pagina(
                desplazamiento, limite, filtros
            )

    def obtener_recientes(self, limite: int = 3) -> list[Cotizacion]:
        with self.uow as uow:
            return uow.cotizacion.obtener_recientes(limite)

    def sumar_totales_por_moneda_creados_entre(
        self, desde: datetime, hasta: datetime
    ) -> dict[Moneda, Decimal]:
        with self.uow as uow:
            return uow.cotizacion.sumar_totales_por_moneda_creados_entre(
                desde, hasta
            )

    def obtener_cantidad_registros(self, filtros: dict | None = None) -> int:
        with self.uow as uow:
            return uow.cotizacion.contar_registros(filtros)

    def obtener_resumen_estados(self) -> dict[EstadoCotizacion, int]:
        with self.uow as uow:
            return uow.cotizacion.contar_por_estado()
