from __future__ import annotations

from decimal import Decimal
import flet as ft
import flet_datatable2 as ftd

from fuente.negocio.controlador.ControladorCotizacion import ControladorCotizacion
from fuente.negocio.modelo.ENUMs import EstadoCotizacion
from fuente.presentacion.PantallaNuevaCotizacion import PantallaNuevaCotizacion
from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_BANNER,
    COLOR_FONDO,
    COLOR_GRIS,
    COLOR_NARANJA,
    COLOR_NEGRO,
    COLOR_ROJO,
    COLOR_VERDE,
)
from fuente.utilidades.Componentes import (
    badge_estado,
    banner_modulo,
    barra_busqueda,
    boton,
    card,
    paginacion,
    sombra_suave,
    tabla,
    tarjeta_indicador,
)


class PantallaCotizaciones(ft.Container):
    COTIZACIONES_DEMO = (
        {
            "folio": "PDA.-0127",
            "fecha": "26/10/2026",
            "buque": "MT MTM HOUSTON",
            "cliente": "MERITUS DE MEXICO SA DE CV",
            "monto": "$ 502,777.15 MXN",
            "estado": "PENDIENTE",
        },
        {
            "folio": "COT-2026-0048",
            "fecha": "04/11/2026",
            "buque": "MSC ORION",
            "cliente": "MSC Shipping S.A.",
            "monto": "$ 245,800.00 MXN",
            "estado": "Pendiente",
        },
        {
            "folio": "COT-2026-0047",
            "fecha": "02/11/2026",
            "buque": "MAERSK LIMA",
            "cliente": "Maersk México",
            "monto": "$ 182,400.00 MXN",
            "estado": "Aprobada",
        },
    )
    TOTAL_COTIZACIONES_DEMO = 3

    def __init__(
        self,
        main_page,
        servicio_cotizacion=None,
        servicio_buque=None,
        servicio_cliente=None,
        servicio_servicio=None,
    ):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
            padding=0,
        )
        self.main_page = main_page
        self.servicio_cotizacion = servicio_cotizacion
        self.servicio_buque = servicio_buque
        self.servicio_cliente = servicio_cliente
        self.servicio_servicio = servicio_servicio

        self.controlador = (
            ControladorCotizacion(
                servicio_cotizacion=servicio_cotizacion,
                servicio_buque=servicio_buque,
                servicio_cliente=servicio_cliente,
                servicio_servicio=servicio_servicio,
            )
            if servicio_cotizacion is not None
            else None
        )
        if self.controlador is not None:
            self.servicio_buque = self.controlador.servicio_buque
            self.servicio_cliente = self.controlador.servicio_cliente
            self.servicio_servicio = self.controlador.servicio_servicio

        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.busqueda = ""
        self.registros_actuales: list = []
        self.total_registros = 0

        self.build_ui()

    def build_ui(self) -> None:
        self._cargar_registros()
        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding(14, 8, 14, 16),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            self._encabezado(),
                            self._tarjetas_resumen(),
                            self._barra_herramientas(),
                            self._panel_historial(),
                        ],
                    ),
                )
            ],
        )

    def _cargar_registros(self) -> None:
        if self.controlador is not None:
            try:
                registros, total = self.controlador.obtener_historial_cotizaciones(
                    pagina=self.pagina_actual,
                    limite=self.registros_por_pagina,
                    texto=self.busqueda,
                )
                self.registros_actuales = registros
                self.total_registros = total
                return
            except Exception as error:
                print(f"Advertencia al consultar cotizaciones en BD: {error}")

        self.registros_actuales = []
        self.total_registros = 0

    def actualizar_historial(self) -> None:
        self.build_ui()
        try:
            pagina = None
            try:
                pagina = self.page
            except RuntimeError:
                pagina = None
            if pagina is not None:
                pagina.update()
            elif self.main_page is not None:
                self.main_page.update()
            else:
                self.update()
        except RuntimeError:
            pass

    def _encabezado(self):
        return banner_modulo(
            src="fondo_puerto.jpg",
            categoria="Gestión de cotizaciones",
            titulo="Cotizaciones",
            descripcion="Consulta el historial y prepara nuevas cotizaciones (PDA) para tus clientes y buques.",
            icono=ft.Icons.REQUEST_QUOTE_OUTLINED,
        )

    def _tarjetas_resumen(self):
        if self.controlador is not None and (
            self.total_registros > 0 or self.servicio_cotizacion is not None
        ):
            total_cot = self.total_registros
            aprobadas = sum(
                1
                for c in self.registros_actuales
                if getattr(
                    getattr(c, "estado", None),
                    "value",
                    str(getattr(c, "estado", "")),
                ).upper()
                in (
                    EstadoCotizacion.APROBADA.value,
                    EstadoCotizacion.PENDIENTE.value,
                    "PROFORMA",
                )
            )
            canceladas = sum(
                1
                for c in self.registros_actuales
                if getattr(
                    getattr(c, "estado", None),
                    "value",
                    str(getattr(c, "estado", "")),
                ).upper()
                in (EstadoCotizacion.RECHAZADA.value, "CANCELADA")
            )
            suma_total = sum(
                (
                    Decimal(str(getattr(c, "total", "0.00") or "0.00"))
                    for c in self.registros_actuales
                ),
                Decimal("0.00"),
            )
            monto_texto = f"$ {suma_total:,.2f} MXN"
            etiqueta_origen = "Registros en base de datos"
        else:
            total_cot = self.TOTAL_COTIZACIONES_DEMO
            aprobadas = 2
            canceladas = 0
            monto_texto = "$ 930,977.15 MXN"
            etiqueta_origen = "Registros de ejemplo"

        resumenes = (
            (
                "Cotizaciones totales",
                str(total_cot),
                etiqueta_origen,
                ft.Icons.DESCRIPTION_OUTLINED,
                COLOR_AZUL,
                "#EAF2FF",
                "#D7E6FF",
            ),
            (
                "Proformas activas",
                str(aprobadas),
                etiqueta_origen,
                ft.Icons.CHECK_CIRCLE_OUTLINED,
                COLOR_VERDE,
                "#EAF8F0",
                "#D5F0E2",
            ),
            (
                "Cotizaciones canceladas",
                str(canceladas),
                etiqueta_origen,
                ft.Icons.CANCEL_OUTLINED,
                COLOR_ROJO,
                "#FDECEE",
                "#F8D9DD",
            ),
            (
                "Monto total cotizado",
                monto_texto,
                etiqueta_origen,
                ft.Icons.PAYMENTS_OUTLINED,
                COLOR_NARANJA,
                "#FFF2E8",
                "#FFE1C9",
            ),
        )
        return ft.Row(
            spacing=10,
            controls=[
                ft.Container(
                    expand=True,
                    content=self._tarjeta_resumen(*resumen),
                )
                for resumen in resumenes
            ],
        )

    @staticmethod
    def _tarjeta_resumen(
        titulo,
        valor,
        descripcion,
        icono,
        color,
        fondo,
        borde,
    ):
        return tarjeta_indicador(
            titulo,
            valor,
            descripcion,
            icono,
            color,
            fondo,
            borde,
        )

    def _al_buscar(self, e) -> None:
        self.busqueda = (e.control.value or "").strip()
        self.pagina_actual = 1
        self.actualizar_historial()

    def _cambiar_pagina(self, pagina: int) -> None:
        self.pagina_actual = pagina
        self.actualizar_historial()

    def _barra_herramientas(self):
        buscador = barra_busqueda(
            hint="Buscar por folio, buque o cliente...",
            on_change=self._al_buscar,
            expand=True,
        )
        buscador.value = self.busqueda
        buscador.height = 42
        boton_filtros = boton(
            texto="Filtros",
            icono=ft.Icons.TUNE,
            tipo="secundario",
            width=160,
            height=42,
        )
        return card(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    buscador,
                    boton_filtros,
                    self._boton_nueva_cotizacion(),
                ],
            ),
            padding=10,
            radius=10,
            border_color="#E0ECF9",
            shadow=sombra_suave(),
        )

    def _panel_historial(self):
        boton_exportar = boton(
            texto="Exportar",
            icono=ft.Icons.DOWNLOAD_OUTLINED,
            tipo="secundario",
            width=120,
            height=42,
        )

        usando_bd = self.controlador is not None
        cantidad_mostrada = (
            len(self.registros_actuales)
            if usando_bd
            else len(self.COTIZACIONES_DEMO)
        )
        total_mostrar = (
            self.total_registros
            if usando_bd
            else self.TOTAL_COTIZACIONES_DEMO
        )
        subtitulo = (
            "Proformas PDA registradas en la base de datos"
            if usando_bd
            else "Muestra de registros · datos ilustrativos"
        )

        return card(
            ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=42,
                                height=42,
                                alignment=ft.Alignment(0, 0),
                                bgcolor="#FFF2E8",
                                border_radius=11,
                                content=ft.Icon(
                                    ft.Icons.LIST_ALT_OUTLINED,
                                    size=23,
                                    color=COLOR_NARANJA,
                                ),
                            ),
                            ft.Column(
                                spacing=2,
                                controls=[
                                    ft.Text(
                                        "Historial de cotizaciones",
                                        size=19,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_BANNER,
                                    ),
                                    ft.Text(
                                        subtitulo,
                                        size=12,
                                        color=COLOR_GRIS,
                                    ),
                                ],
                            ),
                            ft.Container(expand=True),
                            boton_exportar,
                        ],
                    ),
                    self._tabla_historial(),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                f"Mostrando {cantidad_mostrada} de {total_mostrar} cotizaciones",
                                size=12,
                                color=COLOR_GRIS,
                            ),
                            paginacion(
                                total_registros=max(1, total_mostrar),
                                registros_por_pagina=self.registros_por_pagina,
                                pagina_actual=self.pagina_actual,
                                on_change=self._cambiar_pagina,
                            ),
                        ],
                    ),
                ],
            ),
            padding=14,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    def _boton_nueva_cotizacion(self):
        return boton(
            texto="Nueva cotización",
            icono=ft.Icons.ADD,
            tipo="principal",
            height=42,
            on_click=lambda e: self.abrir_nueva_cotizacion(),
        )

    def _normalizar_fila_tabla(self, item) -> dict[str, str]:
        if isinstance(item, dict):
            return item
        fecha_obj = getattr(item, "creado_en", None) or getattr(
            item, "fecha_arribo", None
        )
        fecha_str = (
            fecha_obj.strftime("%d/%m/%Y")
            if hasattr(fecha_obj, "strftime")
            else str(fecha_obj or "")
        )
        buque_obj = getattr(item, "buque", None)
        buque_nombre = (
            getattr(buque_obj, "nombre", None)
            or f"Buque #{getattr(item, 'buque_id', '')}"
        )
        cliente_obj = getattr(item, "cliente", None)
        cliente_nombre = (
            getattr(cliente_obj, "razon_social", None)
            or f"Cliente #{getattr(item, 'cliente_id', '')}"
        )
        total_val = Decimal(str(getattr(item, "total", "0.00") or "0.00"))
        moneda_obj = getattr(item, "moneda", "MXN")
        moneda_str = getattr(moneda_obj, "value", str(moneda_obj or "MXN"))
        estado_obj = getattr(item, "estado", "PENDIENTE")
        estado_str = getattr(estado_obj, "value", str(estado_obj or "PENDIENTE"))

        return {
            "folio": getattr(item, "folio", ""),
            "fecha": fecha_str,
            "buque": buque_nombre,
            "cliente": cliente_nombre,
            "monto": f"$ {total_val:,.2f} {moneda_str}",
            "estado": estado_str,
        }

    def _tabla_historial(self):
        origen = (
            self.registros_actuales
            if self.controlador is not None
            else self.COTIZACIONES_DEMO
        )
        filas = []
        for registro in origen:
            cotizacion = self._normalizar_fila_tabla(registro)
            filas.append(
                ftd.DataRow2(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                cotizacion["folio"],
                                size=13,
                                color=COLOR_AZUL,
                                weight=ft.FontWeight.W_600,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(cotizacion["fecha"], size=13, color=COLOR_GRIS)
                        ),
                        ft.DataCell(
                            ft.Text(
                                cotizacion["buque"],
                                size=13,
                                color=COLOR_BANNER,
                                weight=ft.FontWeight.W_600,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                cotizacion["cliente"],
                                size=13,
                                color=COLOR_GRIS,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                cotizacion["monto"],
                                size=13,
                                color=COLOR_BANNER,
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                        ft.DataCell(
                            badge_estado(
                                cotizacion["estado"],
                                self._estado_visual(cotizacion["estado"]),
                            )
                        ),
                        ft.DataCell(self._acciones_fila()),
                    ],
                )
            )

        return tabla(
            columnas=[
                ("Folio", 155),
                ("Fecha", 110),
                ("Nombre del buque", 175),
                ("Cliente", 190),
                ("Monto total", 170),
                ("Estado", 125),
                ("Acciones", 100),
            ],
            filas=filas,
            column_spacing=6,
            horizontal_margin=8,
            heading_row_height=46,
            data_row_min_height=58,
            data_row_max_height=64,
            columnas_flexibles=True,
            heading_row_color="#EEF5FD",
            heading_text_size=14,
            heading_text_color=COLOR_NEGRO,
            vertical_lines=True,
            horizontal_lines=True,
            border_color="#E3EAF2",
            columnas_compactas=True,
        )

    @staticmethod
    def _estado_visual(estado):
        return {
            "Pendiente": "pendiente",
            "PENDIENTE": "pendiente",
            "BORRADOR": "pendiente",
            "PROFORMA": "activo",
            "APROBADA": "activo",
            "Aprobada": "activo",
            "RECHAZADA": "inactivo",
            "Rechazada": "inactivo",
            "Cancelada": "inactivo",
            "CANCELADA": "inactivo",
        }.get(str(estado), "info")

    @staticmethod
    def _acciones_fila():
        return ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=2,
            controls=[
                boton(
                    icono=ft.Icons.VISIBILITY_OUTLINED,
                    texto="Ver cotización",
                    tipo="accion",
                ),
                boton(
                    icono=ft.Icons.MORE_VERT,
                    texto="Más acciones",
                    tipo="accion",
                ),
            ],
        )

    def abrir_nueva_cotizacion(self):
        nueva_vista = PantallaNuevaCotizacion(
            self.main_page,
            vista_anterior=self,
            servicio_cotizacion=self.servicio_cotizacion,
            servicio_buque=self.servicio_buque,
            servicio_cliente=self.servicio_cliente,
            servicio_servicio=self.servicio_servicio,
            controlador=self.controlador,
        )
        if self.parent is not None:
            self.parent.content = nueva_vista
            self.parent.update()
        return nueva_vista
