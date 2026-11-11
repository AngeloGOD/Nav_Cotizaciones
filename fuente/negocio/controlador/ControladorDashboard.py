from datetime import datetime, timezone
from decimal import Decimal

from fuente.negocio.modelo.ENUMs import EstadoCotizacion


class ControladorDashboard:
    def __init__(self, servicio_cliente=None, servicio_cotizacion=None):
        self.servicio_cliente = servicio_cliente
        self.servicio_cotizacion = servicio_cotizacion

    def obtener_datos_dashboard(self):
        cotizaciones_recientes = (
            self.servicio_cotizacion.obtener_recientes(4)
            if self.servicio_cotizacion is not None
            else []
        )
        clientes_recientes = (
            self.servicio_cliente.obtener_recientes(4)
            if self.servicio_cliente is not None
            else []
        )
        return {
            "metricas": self._obtener_metricas(),
            "cotizaciones": [
                self._preparar_cotizacion(cotizacion)
                for cotizacion in cotizaciones_recientes[:3]
            ],
            "clientes": [
                self._preparar_cliente(cliente)
                for cliente in clientes_recientes[:3]
            ],
            "actividades": self._obtener_actividades(
                cotizaciones_recientes,
                clientes_recientes,
            ),
        }

    def _obtener_metricas(self):
        resumen = (
            self.servicio_cotizacion.obtener_resumen_estados()
            if self.servicio_cotizacion is not None
            else {}
        )
        pendientes = self._contar_estados(
            resumen,
            (EstadoCotizacion.BORRADOR, EstadoCotizacion.PROFORMA),
        )
        aprobadas = self._contar_estados(
            resumen,
            (
                EstadoCotizacion.ANTICIPO_RECIBIDO,
                EstadoCotizacion.EN_OPERACION,
                EstadoCotizacion.LIQUIDADA_FDA,
            ),
        )
        canceladas = self._contar_estados(
            resumen,
            (EstadoCotizacion.CANCELADA,),
        )

        ahora = datetime.now().astimezone()
        inicio_mes = ahora.replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        if inicio_mes.month == 12:
            inicio_mes_siguiente = inicio_mes.replace(
                year=inicio_mes.year + 1,
                month=1,
            )
        else:
            inicio_mes_siguiente = inicio_mes.replace(
                month=inicio_mes.month + 1,
            )
        totales = (
            self.servicio_cotizacion.sumar_totales_por_moneda_creados_entre(
                inicio_mes,
                inicio_mes_siguiente,
            )
            if self.servicio_cotizacion is not None
            else {}
        )
        monto_mensual = " · ".join(
            f"{getattr(moneda, 'value', moneda)} "
            f"${Decimal(str(total or 0)):,.2f}"
            for moneda, total in sorted(
                totales.items(),
                key=lambda item: getattr(item[0], "value", str(item[0])),
            )
        ) or "MXN $0.00"

        return {
            "pendientes": pendientes,
            "aprobadas": aprobadas,
            "rechazadas": canceladas,
            "monto_mensual": monto_mensual,
        }

    @staticmethod
    def _contar_estados(resumen, estados):
        return sum(
            int(resumen.get(estado, 0) or 0)
            for estado in estados
        )

    def _preparar_cotizacion(self, cotizacion):
        moneda = getattr(
            getattr(cotizacion, "moneda", None),
            "value",
            getattr(cotizacion, "moneda", "MXN"),
        )
        return {
            "folio": getattr(cotizacion, "folio", "") or "Sin folio",
            "fecha": self._formatear_fecha(
                getattr(cotizacion, "creado_en", None)
            ),
            "buque": getattr(
                getattr(cotizacion, "buque", None),
                "nombre",
                None,
            )
            or "Sin buque",
            "cliente": getattr(
                getattr(cotizacion, "cliente", None),
                "razon_social",
                None,
            )
            or "Sin cliente",
            "monto": (
                f"{moneda} "
                f"${Decimal(str(getattr(cotizacion, 'total', 0) or 0)):,.2f}"
            ),
            "estado": self._nombre_estado(
                getattr(cotizacion, "estado", None)
            ),
        }

    @staticmethod
    def _nombre_estado(estado):
        valor = getattr(estado, "value", estado)
        nombres = {
            "BORRADOR": "Borrador",
            "PROFORMA": "Pendiente",
            "ANTICIPO_RECIBIDO": "Anticipo recibido",
            "EN_OPERACION": "Aprobada",
            "LIQUIDADA_FDA": "Liquidada",
            "CANCELADA": "Cancelada",
        }
        return nombres.get(str(valor).upper(), "Sin estado")

    @classmethod
    def _preparar_cliente(cls, cliente):
        return {
            "nombre": getattr(cliente, "razon_social", "") or "Sin nombre",
            "detalle": f"Registro · {cls._formatear_fecha(getattr(cliente, 'creado_en', None))}",
        }

    @classmethod
    def _obtener_actividades(cls, cotizaciones, clientes):
        actividades = []
        for cotizacion in cotizaciones:
            fecha = getattr(cotizacion, "creado_en", None)
            actividades.append(
                {
                    "fecha_orden": cls._clave_fecha(fecha),
                    "icono": "cotizacion",
                    "titulo": (
                        f"Cotización {getattr(cotizacion, 'folio', '') or 'sin folio'} "
                        "registrada"
                    ),
                    "fecha": cls._formatear_fecha(fecha),
                }
            )
        for cliente in clientes:
            fecha = getattr(cliente, "creado_en", None)
            actividades.append(
                {
                    "fecha_orden": cls._clave_fecha(fecha),
                    "icono": "cliente",
                    "titulo": (
                        f"Cliente {getattr(cliente, 'razon_social', '') or 'sin nombre'} "
                        "registrado"
                    ),
                    "fecha": cls._formatear_fecha(fecha),
                }
            )
        actividades.sort(key=lambda actividad: actividad["fecha_orden"], reverse=True)
        return [
            {clave: valor for clave, valor in actividad.items() if clave != "fecha_orden"}
            for actividad in actividades[:4]
        ]

    @staticmethod
    def _clave_fecha(fecha):
        if not isinstance(fecha, datetime):
            return float("-inf")
        if fecha.tzinfo is None:
            fecha = fecha.replace(tzinfo=timezone.utc)
        return fecha.timestamp()

    @staticmethod
    def _formatear_fecha(fecha):
        if not isinstance(fecha, datetime):
            return "Fecha no disponible"
        sufijo = "a. m." if fecha.hour < 12 else "p. m."
        hora = fecha.strftime("%I:%M").lstrip("0") or "12:00"
        return f"{fecha:%d/%m/%Y} · {hora} {sufijo}"
