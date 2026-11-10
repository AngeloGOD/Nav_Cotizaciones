import flet as ft
import flet_datatable2 as ftd

from fuente.presentacion.PantallaNuevaCotizacion import PantallaNuevaCotizacion
from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_BANNER,
    COLOR_BLANCO,
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
    boton,
    barra_busqueda,
    card,
    paginacion,
    sombra_suave,
    tarjeta_indicador,
    tabla,
)


class PantallaCotizaciones(ft.Container):
    COTIZACIONES_DEMO = (
        {
            "folio": "COT-2026-0048",
            "fecha": "04/11/2026",
            "buque": "MSC ORION",
            "cliente": "MSC Shipping S.A.",
            "monto": "$245,800.00 MXN",
            "estado": "Pendiente",
        },
        {
            "folio": "COT-2026-0047",
            "fecha": "02/11/2026",
            "buque": "MAERSK LIMA",
            "cliente": "Maersk México",
            "monto": "$182,400.00 MXN",
            "estado": "Aprobada",
        },
        {
            "folio": "COT-2026-0046",
            "fecha": "01/11/2026",
            "buque": "NAVIOS AZURE",
            "cliente": "Navios South American",
            "monto": "$96,750.00 MXN",
            "estado": "Aprobada",
        },
        {
            "folio": "COT-2026-0045",
            "fecha": "28/10/2026",
            "buque": "ONE COMMANDER",
            "cliente": "Oceanic Logistics",
            "monto": "$123,500.00 MXN",
            "estado": "Cancelada",
        },
        {
            "folio": "COT-2026-0044",
            "fecha": "25/10/2026",
            "buque": "EVERGREEN SKY",
            "cliente": "Evergreen Line",
            "monto": "$201,300.00 MXN",
            "estado": "Aprobada",
        },
    )
    TOTAL_COTIZACIONES_DEMO = 46

    def __init__(self, main_page):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
            padding=0,
        )
        self.main_page = main_page
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

    def _encabezado(self):
        return banner_modulo(
            src="fondo_puerto.jpg",
            categoria="Gestión de cotizaciones",
            titulo="Cotizaciones",
            descripcion="Consulta el historial y prepara nuevas cotizaciones para tus clientes y buques.",
            icono=ft.Icons.REQUEST_QUOTE_OUTLINED,
        )

    def _tarjetas_resumen(self):
        resumenes = (
            (
                "Cotizaciones totales",
                str(self.TOTAL_COTIZACIONES_DEMO),
                "Registros de ejemplo",
                ft.Icons.DESCRIPTION_OUTLINED,
                COLOR_AZUL,
                "#EAF2FF",
                "#D7E6FF",
            ),
            (
                "Cotizaciones aprobadas",
                "28",
                "Aprobadas · demo",
                ft.Icons.CHECK_CIRCLE_OUTLINED,
                COLOR_VERDE,
                "#EAF8F0",
                "#D5F0E2",
            ),
            (
                "Cotizaciones canceladas",
                "6",
                "Canceladas · demo",
                ft.Icons.CANCEL_OUTLINED,
                COLOR_ROJO,
                "#FDECEE",
                "#F8D9DD",
            ),
            (
                "Monto total cotizado",
                "$531,000 MXN",
                "Monto ilustrativo",
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

    def _barra_herramientas(self):
        buscador = barra_busqueda(
            hint="Buscar por folio, buque o cliente...",
            expand=True,
        )
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
                                        "Muestra de registros · datos ilustrativos",
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
                                f"Mostrando {len(self.COTIZACIONES_DEMO)} de "
                                f"{self.TOTAL_COTIZACIONES_DEMO} cotizaciones · demo",
                                size=12,
                                color=COLOR_GRIS,
                            ),
                            paginacion(
                                total_registros=self.TOTAL_COTIZACIONES_DEMO,
                                registros_por_pagina=5,
                                pagina_actual=1,
                                on_change=lambda pagina: None,
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

    def _tabla_historial(self):
        filas = []
        for cotizacion in self.COTIZACIONES_DEMO:
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
                        ft.DataCell(ft.Text(cotizacion["fecha"], size=13, color=COLOR_GRIS)),
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
            "Aprobada": "activo",
            "Cancelada": "inactivo",
        }.get(estado, "info")

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
        self.parent.content = PantallaNuevaCotizacion(
            self.main_page,
            vista_anterior=self,
        )
        self.parent.update()
