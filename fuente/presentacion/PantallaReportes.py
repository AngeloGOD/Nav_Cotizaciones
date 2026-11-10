import flet as ft

from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_BANNER,
    COLOR_BLANCO,
    COLOR_FONDO,
    COLOR_GRIS,
    COLOR_NARANJA,
    COLOR_ROJO,
    COLOR_VERDE,
)
from fuente.utilidades.Componentes import banner_modulo, card, sombra_suave


class PantallaReportes(ft.Container):
    MESES = ("May", "Jun", "Jul", "Ago", "Sep", "Oct")
    INGRESOS = (54, 80, 68, 98, 103, 128)
    COTIZACIONES = (42, 63, 54, 76, 82, 100)
    ACTIVIDAD = (35, 57, 48, 71, 68, 88)

    def __init__(self, page):
        super().__init__(expand=True, bgcolor=COLOR_FONDO)
        self._page = page
        self._periodo = "Últimos 6 meses"
        self._modulo = "Todos los módulos"
        self._metrica = "Ingresos"
        self._mensaje_generacion = ft.Text(
            "",
            size=11,
            color=COLOR_GRIS,
            visible=False,
        )

        self._selector_periodo = ft.Dropdown(
            value=self._periodo,
            width=205,
            height=42,
            text_size=12,
            content_padding=ft.Padding(10, 7, 10, 7),
            border=ft.InputBorder.OUTLINE,
            border_color="#DCE6F2",
            focused_border_color=COLOR_AZUL,
            border_radius=9,
            leading_icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            options=[
                ft.DropdownOption(key=valor, text=valor)
                for valor in (
                    "Últimos 30 días",
                    "Últimos 3 meses",
                    "Últimos 6 meses",
                    "Este año",
                )
            ],
            on_select=self._cambiar_filtros,
        )
        self._selector_modulo = ft.Dropdown(
            value=self._modulo,
            width=210,
            height=42,
            text_size=12,
            content_padding=ft.Padding(10, 7, 10, 7),
            border=ft.InputBorder.OUTLINE,
            border_color="#DCE6F2",
            focused_border_color=COLOR_AZUL,
            border_radius=9,
            leading_icon=ft.Icons.LAYERS_OUTLINED,
            options=[
                ft.DropdownOption(key=valor, text=valor)
                for valor in (
                    "Todos los módulos",
                    "Clientes",
                    "Productos",
                    "Buques",
                    "Cotizaciones",
                    "Servicios",
                )
            ],
            on_select=self._cambiar_filtros,
        )

        self._panel_grafica = self._crear_panel_grafica()
        self._panel_destacados = self._crear_panel_destacados()
        self._panel_distribucion = self._crear_panel_distribucion()
        self._panel_buques = self._crear_panel_buques()
        self._panel_recientes = self._crear_panel_recientes()

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    padding=ft.Padding(14, 8, 14, 16),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            banner_modulo(
                                "fondo_puerto.jpg",
                                "Reportes",
                                "Análisis y Estadísticas",
                                "Consulta el rendimiento de tu operación con reportes detallados y visuales.",
                                ft.Icons.INSERT_CHART_OUTLINED,
                                altura=116,
                                tamano_icono=58,
                                tamano_grafico=31,
                                tamano_titulo=25,
                                tamano_descripcion=12,
                                padding=ft.Padding(18, 8, 18, 8),
                            ),
                            self._barra_filtros(),
                            self._tarjetas_metricas(),
                            ft.Row(
                                height=218,
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                                controls=[
                                    ft.Container(
                                        expand=7,
                                        content=self._panel_grafica,
                                    ),
                                    ft.Container(
                                        expand=4,
                                        content=self._panel_destacados,
                                    ),
                                ],
                            ),
                            ft.Row(
                                height=180,
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                                controls=[
                                    ft.Container(
                                        expand=4,
                                        content=self._panel_distribucion,
                                    ),
                                    ft.Container(
                                        expand=4,
                                        content=self._panel_buques,
                                    ),
                                    ft.Container(
                                        expand=4,
                                        content=self._panel_recientes,
                                    ),
                                ],
                            ),
                            ft.Text(
                                "Vista de demostración · Los indicadores y reportes se conectarán a los datos de operación.",
                                size=10,
                                color=COLOR_GRIS,
                                text_align=ft.TextAlign.RIGHT,
                            ),
                        ],
                    ),
                )
            ],
        )

    def _barra_filtros(self):
        return ft.Row(
            spacing=9,
            controls=[
                self._selector_periodo,
                self._selector_modulo,
                ft.Container(expand=True),
                self._mensaje_generacion,
                ft.FilledButton(
                    content=ft.Row(
                        tight=True,
                        spacing=7,
                        controls=[
                            ft.Icon(
                                ft.Icons.ANALYTICS_OUTLINED,
                                size=17,
                                color=COLOR_BLANCO,
                            ),
                            ft.Text(
                                "Generar reporte",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BLANCO,
                            ),
                        ],
                    ),
                    height=42,
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_NARANJA,
                        shape=ft.RoundedRectangleBorder(radius=9),
                        padding=ft.Padding(15, 0, 15, 0),
                    ),
                    on_click=self.generar_reporte,
                ),
            ],
        )

    def _tarjetas_metricas(self):
        metricas = (
            (
                "Clientes",
                "142",
                "+8%",
                ft.Icons.GROUPS_OUTLINED,
                COLOR_AZUL,
                "#EAF2FF",
                (4, 7, 5, 9, 8, 12, 10, 15),
            ),
            (
                "Productos",
                "856",
                "+5%",
                ft.Icons.INVENTORY_2_OUTLINED,
                COLOR_VERDE,
                "#EAF8F0",
                (5, 6, 8, 7, 11, 9, 13, 15),
            ),
            (
                "Buques",
                "67",
                "+12%",
                ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                "#8B35D3",
                "#F4ECFF",
                (3, 5, 7, 6, 10, 9, 12, 16),
            ),
            (
                "Cotizaciones",
                "1,248",
                "+10%",
                ft.Icons.DESCRIPTION_OUTLINED,
                COLOR_NARANJA,
                "#FFF2E8",
                (4, 5, 7, 9, 8, 11, 13, 16),
            ),
        )
        return ft.Row(
            spacing=9,
            controls=[
                ft.Container(
                    expand=True,
                    content=self._tarjeta_metrica(
                        titulo,
                        valor,
                        cambio,
                        icono,
                        color,
                        fondo,
                        serie,
                    ),
                )
                for (
                    titulo,
                    valor,
                    cambio,
                    icono,
                    color,
                    fondo,
                    serie,
                ) in metricas
            ],
        )

    def _tarjeta_metrica(self, titulo, valor, cambio, icono, color, fondo, serie):
        return card(
            ft.Row(
                spacing=9,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=42,
                        height=42,
                        alignment=ft.Alignment(0, 0),
                        bgcolor=fondo,
                        border_radius=21,
                        content=ft.Icon(icono, size=22, color=color),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=1,
                        controls=[
                            ft.Text(titulo, size=11, color=COLOR_GRIS),
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Text(
                                        valor,
                                        size=21,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_BANNER,
                                    ),
                                    ft.Text(
                                        f"↑ {cambio}",
                                        size=10,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_VERDE,
                                    ),
                                ],
                            ),
                        ],
                    ),
                    self._mini_barras(serie, color),
                ],
            ),
            padding=10,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
        )

    def _mini_barras(self, valores, color):
        return ft.Container(
            width=66,
            height=34,
            alignment=ft.Alignment(0, 1),
            content=ft.Row(
                spacing=3,
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    ft.Container(
                        width=5,
                        height=max(5, valor * 1.7),
                        bgcolor=color,
                        border_radius=3,
                        opacity=0.45 + (indice / len(valores)) * 0.55,
                    )
                    for indice, valor in enumerate(valores)
                ],
            ),
        )

    def _crear_panel_grafica(self):
        self._resumen_periodo = ft.Text(
            "Total del periodo",
            size=11,
            color=COLOR_GRIS,
        )
        self._valor_periodo = ft.Text(
            "$128,450 MXN",
            size=21,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BANNER,
        )
        self._variacion_periodo = ft.Text(
            "↑ +14.2%",
            size=11,
            weight=ft.FontWeight.BOLD,
            color=COLOR_VERDE,
        )
        self._grafica_mensual = self._crear_grafica_mensual(self.INGRESOS)
        return card(
            ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.BAR_CHART,
                                size=20,
                                color=COLOR_NARANJA,
                            ),
                            ft.Text(
                                "Resumen General",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Container(expand=True),
                            self._botones_metricas(),
                        ],
                    ),
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                expand=True,
                                content=self._grafica_mensual,
                            ),
                            ft.Container(
                                width=150,
                                height=126,
                                padding=12,
                                bgcolor="#F0F6FF",
                                border_radius=10,
                                content=ft.Column(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    spacing=7,
                                    controls=[
                                        self._resumen_periodo,
                                        self._valor_periodo,
                                        ft.Container(
                                            padding=ft.Padding(8, 4, 8, 4),
                                            bgcolor="#DDF5E8",
                                            border_radius=14,
                                            content=self._variacion_periodo,
                                        ),
                                        ft.Row(
                                            alignment=ft.MainAxisAlignment.END,
                                            controls=[
                                                self._mini_barras(
                                                    (3, 5, 7, 10), COLOR_AZUL
                                                )
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                ],
            ),
            padding=12,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    def _botones_metricas(self):
        self._botones_metrica = {}
        controles = []
        for titulo in ("Ingresos", "Cotizaciones", "Actividad"):
            boton = ft.Container(
                padding=ft.Padding(10, 6, 10, 6),
                border_radius=16,
                bgcolor=COLOR_AZUL if titulo == self._metrica else COLOR_BLANCO,
                on_click=lambda e, valor=titulo: self._cambiar_metrica(valor),
                ink=True,
                content=ft.Text(
                    titulo,
                    size=10,
                    color=(
                        COLOR_BLANCO
                        if titulo == self._metrica
                        else COLOR_BANNER
                    ),
                    weight=ft.FontWeight.BOLD,
                ),
            )
            self._botones_metrica[titulo] = boton
            controles.append(boton)
        return ft.Row(spacing=3, controls=controles)

    def _crear_grafica_mensual(self, valores):
        maximo = max(valores)
        barras = []
        for mes, valor in zip(self.MESES, valores):
            barras.append(
                ft.Column(
                    expand=True,
                    spacing=4,
                    alignment=ft.MainAxisAlignment.END,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=14,
                            height=max(10, 104 * valor / maximo),
                            bgcolor=COLOR_AZUL,
                            border_radius=ft.BorderRadius(5, 5, 2, 2),
                            tooltip=f"{mes}: {valor}",
                        ),
                        ft.Text(mes, size=9, color=COLOR_GRIS),
                    ],
                )
            )
        return ft.Container(
            height=138,
            padding=ft.Padding(4, 5, 4, 0),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        height=108,
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=barras,
                    ),
                    ft.Divider(height=1, color="#DCE6F2"),
                ],
            ),
        )

    def _cambiar_metrica(self, metrica):
        self._metrica = metrica
        valores = {
            "Ingresos": self.INGRESOS,
            "Cotizaciones": self.COTIZACIONES,
            "Actividad": self.ACTIVIDAD,
        }[metrica]
        self._valor_periodo.value = {
            "Ingresos": "$128,450 MXN",
            "Cotizaciones": "1,248",
            "Actividad": "326 operaciones",
        }[metrica]
        self._resumen_periodo.value = {
            "Ingresos": "Total del periodo",
            "Cotizaciones": "Cotizaciones",
            "Actividad": "Operaciones registradas",
        }[metrica]
        self._grafica_mensual = self._crear_grafica_mensual(valores)
        self._panel_grafica.content.controls[1].controls[0].content = (
            self._grafica_mensual
        )
        for nombre, boton in self._botones_metrica.items():
            seleccionado = nombre == metrica
            boton.bgcolor = COLOR_AZUL if seleccionado else COLOR_BLANCO
            boton.content.color = COLOR_BLANCO if seleccionado else COLOR_BANNER
        if self._page is not None:
            self._panel_grafica.update()

    def _crear_panel_destacados(self):
        reportes = (
            (
                "Rendimiento de Cotizaciones",
                "Ventas, aprobaciones y montos",
                ft.Icons.BAR_CHART,
                COLOR_AZUL,
                "#EAF2FF",
            ),
            (
                "Clientes más Activos",
                "Top 10 por número de cotizaciones",
                ft.Icons.GROUPS_OUTLINED,
                COLOR_VERDE,
                "#EAF8F0",
            ),
            (
                "Productos más Solicitados",
                "Por categoría y volumen",
                ft.Icons.INVENTORY_2_OUTLINED,
                "#8B35D3",
                "#F4ECFF",
            ),
            (
                "Análisis Financiero",
                "Ingresos, costos y utilidad",
                ft.Icons.ATTACH_MONEY,
                COLOR_NARANJA,
                "#FFF2E8",
            ),
        )
        return card(
            ft.Column(
                expand=True,
                spacing=6,
                controls=[
                    self._encabezado_panel(
                        ft.Icons.STAR,
                        "Reportes Destacados",
                        COLOR_NARANJA,
                    ),
                    *[
                        ft.Container(
                            padding=ft.Padding(7, 5, 7, 5),
                            border=ft.Border.all(1, "#E4ECF5"),
                            border_radius=9,
                            ink=True,
                            on_click=lambda e, nombre=nombre: self._mostrar_detalle(
                                nombre
                            ),
                            content=ft.Row(
                                spacing=7,
                                controls=[
                                    ft.Container(
                                        width=30,
                                        height=30,
                                        alignment=ft.Alignment(0, 0),
                                        border_radius=8,
                                        bgcolor=fondo,
                                        content=ft.Icon(
                                            icono,
                                            size=17,
                                            color=color,
                                        ),
                                    ),
                                    ft.Column(
                                        expand=True,
                                        spacing=1,
                                        controls=[
                                            ft.Text(
                                                nombre,
                                                size=10,
                                                weight=ft.FontWeight.BOLD,
                                                color=COLOR_BANNER,
                                                max_lines=1,
                                            ),
                                            ft.Text(
                                                descripcion,
                                                size=9,
                                                color=COLOR_GRIS,
                                                max_lines=1,
                                            ),
                                        ],
                                    ),
                                    ft.Icon(
                                        ft.Icons.CHEVRON_RIGHT,
                                        size=17,
                                        color=COLOR_AZUL,
                                    ),
                                ],
                            ),
                        )
                        for nombre, descripcion, icono, color, fondo in reportes
                    ],
                ],
            ),
            padding=12,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    def _crear_panel_distribucion(self):
        segmentos = (
            ("Proforma Puerto", "42%", COLOR_AZUL),
            ("Víveres / Proveeduría", "34%", COLOR_NARANJA),
            ("General", "24%", "#8B35D3"),
        )
        return card(
            ft.Column(
                spacing=10,
                controls=[
                    self._encabezado_panel(
                        ft.Icons.PIE_CHART_OUTLINE,
                        "Distribución de Cotizaciones",
                        COLOR_NARANJA,
                    ),
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Stack(
                                width=110,
                                height=110,
                                alignment=ft.Alignment(0, 0),
                                controls=[
                                    ft.ProgressRing(
                                        value=0.42,
                                        width=100,
                                        height=100,
                                        stroke_width=13,
                                        color=COLOR_AZUL,
                                        bgcolor="#E9EFF7",
                                    ),
                                    ft.Container(
                                        width=66,
                                        height=66,
                                        alignment=ft.Alignment(0, 0),
                                        bgcolor=COLOR_BLANCO,
                                        border_radius=33,
                                        content=ft.Column(
                                            spacing=0,
                                            alignment=ft.MainAxisAlignment.CENTER,
                                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                            controls=[
                                                ft.Text(
                                                    "1,248",
                                                    size=15,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=COLOR_BANNER,
                                                ),
                                                ft.Text(
                                                    "Total",
                                                    size=9,
                                                    color=COLOR_GRIS,
                                                ),
                                            ],
                                        ),
                                    ),
                                ],
                            ),
                            ft.Column(
                                expand=True,
                                spacing=8,
                                controls=[
                                    self._leyenda_distribucion(
                                        nombre, porcentaje, color
                                    )
                                    for nombre, porcentaje, color in segmentos
                                ],
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=0,
                        controls=[
                            ft.Container(
                                expand=int(porcentaje[:-1]),
                                height=7,
                                bgcolor=color,
                                border_radius=ft.BorderRadius(
                                    4 if indice == 0 else 0,
                                    4 if indice == len(segmentos) - 1 else 0,
                                    4 if indice == 0 else 0,
                                    4 if indice == len(segmentos) - 1 else 0,
                                ),
                            )
                            for indice, (_, porcentaje, color) in enumerate(
                                segmentos
                            )
                        ],
                    ),
                ],
            ),
            padding=12,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    def _leyenda_distribucion(self, nombre, porcentaje, color):
        return ft.Row(
            spacing=6,
            controls=[
                ft.Container(width=8, height=8, bgcolor=color, border_radius=4),
                ft.Text(
                    nombre,
                    size=9,
                    color=COLOR_BANNER,
                    expand=True,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    porcentaje,
                    size=9,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_BANNER,
                ),
            ],
        )

    def _crear_panel_buques(self):
        buques = (
            ("M/V Oceanic", 66),
            ("M/V Pacific Star", 72),
            ("M/V Horizon", 91),
            ("M/V Voyager", 84),
            ("M/V Atlantic", 59),
        )
        maximo = max(valor for _, valor in buques)
        return card(
            ft.Column(
                spacing=8,
                controls=[
                    self._encabezado_panel(
                        ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                        "Actividad por Buque",
                        COLOR_NARANJA,
                    ),
                    ft.Row(
                        height=117,
                        spacing=6,
                        alignment=ft.MainAxisAlignment.SPACE_AROUND,
                        vertical_alignment=ft.CrossAxisAlignment.END,
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=4,
                                alignment=ft.MainAxisAlignment.END,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        width=22,
                                        height=72 * valor / maximo,
                                        bgcolor=COLOR_AZUL,
                                        border_radius=ft.BorderRadius(4, 4, 0, 0),
                                    ),
                                    ft.Text(
                                        nombre,
                                        size=8,
                                        color=COLOR_GRIS,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ],
                            )
                            for nombre, valor in buques
                        ],
                    ),
                ],
            ),
            padding=12,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    def _crear_panel_recientes(self):
        recientes = (
            ("Reporte de Clientes - Oct 2026", "23/10/2026 · 10:32", "PDF", COLOR_ROJO),
            ("Análisis de Cotizaciones", "20/10/2026 · 14:17", "XLS", COLOR_VERDE),
            ("Reporte Financiero - Sep 2026", "30/09/2026 · 09:45", "PDF", COLOR_AZUL),
        )
        return card(
            ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        controls=[
                            self._encabezado_panel(
                                ft.Icons.ACCESS_TIME,
                                "Reportes Recientes",
                                COLOR_NARANJA,
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                "Ver todos →",
                                on_click=lambda e: self._mostrar_detalle(
                                    "Reportes recientes"
                                ),
                            ),
                        ],
                    ),
                    *[
                        ft.Container(
                            padding=ft.Padding(4, 3, 3, 3),
                            border=ft.Border(
                                bottom=ft.BorderSide(1, "#EDF1F6")
                            ),
                            content=ft.Row(
                                spacing=7,
                                controls=[
                                    ft.Container(
                                        width=24,
                                        height=27,
                                        alignment=ft.Alignment(0, 0),
                                        bgcolor=f"{color}18",
                                        border_radius=5,
                                        content=ft.Text(
                                            formato,
                                            size=8,
                                            weight=ft.FontWeight.BOLD,
                                            color=color,
                                        ),
                                    ),
                                    ft.Column(
                                        expand=True,
                                        spacing=1,
                                        controls=[
                                            ft.Text(
                                                titulo,
                                                size=9,
                                                weight=ft.FontWeight.BOLD,
                                                color=COLOR_BANNER,
                                                max_lines=1,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                            ft.Text(
                                                fecha,
                                                size=8,
                                                color=COLOR_GRIS,
                                            ),
                                        ],
                                    ),
                                    ft.IconButton(
                                        icon=ft.Icons.DOWNLOAD_OUTLINED,
                                        icon_color=COLOR_AZUL,
                                        icon_size=17,
                                        tooltip="Descargar reporte",
                                        on_click=lambda e, nombre=titulo: self._mostrar_detalle(
                                            nombre
                                        ),
                                    ),
                                ],
                            ),
                        )
                        for titulo, fecha, formato, color in recientes
                    ],
                ],
            ),
            padding=12,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    def _encabezado_panel(self, icono, titulo, color):
        return ft.Row(
            spacing=7,
            controls=[
                ft.Icon(icono, size=19, color=color),
                ft.Text(
                    titulo,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_BANNER,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        )

    def _cambiar_filtros(self, e):
        self._periodo = self._selector_periodo.value
        self._modulo = self._selector_modulo.value
        self._mensaje_generacion.visible = False
        if self._page is not None:
            self._page.update()

    def generar_reporte(self, e=None):
        self._mensaje_generacion.value = (
            f"Vista demostrativa: {self._periodo} · {self._modulo}"
        )
        self._mensaje_generacion.visible = True
        if self._page is not None:
            self._mensaje_generacion.update()

    def _mostrar_detalle(self, titulo):
        self._mensaje_generacion.value = (
            f"{titulo}: vista de demostración, sin datos conectados."
        )
        self._mensaje_generacion.visible = True
        if self._page is not None:
            self._mensaje_generacion.update()
