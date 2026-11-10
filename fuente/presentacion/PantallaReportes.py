import flet as ft

from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_BANNER,
    COLOR_BLANCO,
    COLOR_FONDO,
    COLOR_GRIS,
    COLOR_NEGRO,
    COLOR_NARANJA,
    COLOR_ROJO,
    COLOR_VERDE,
)
from fuente.utilidades.Componentes import banner_modulo, card, sombra_suave


class PantallaReportes(ft.Container):
    MESES = ("May", "Jun", "Jul", "Ago", "Sep", "Oct")
    INGRESOS = (54, 80, 68, 98, 103, 128)
    COTIZACIONES = (142, 175, 186, 218, 241, 286)
    APROBACIONES = (71, 74, 73, 76, 77, 78)
    RENTABILIDAD = (11, 12, 14, 15, 17, 18)
    REPORTES_ESPECIALIZADOS = (
        {
            "nombre": "Rendimiento de cotizaciones",
            "descripcion": "Estados, aprobaciones y montos.",
            "icono": ft.Icons.QUERY_STATS,
            "color": COLOR_AZUL,
            "fondo": "#EAF2FF",
            "filtro": "Estado",
            "opciones": (
                "Todos los estados",
                "Borrador",
                "Proforma",
                "Anticipo recibido",
                "En operación",
                "Liquidada",
                "Cancelada",
            ),
        },
        {
            "nombre": "Tipos de cotización",
            "descripcion": "Distribución por categoría.",
            "icono": ft.Icons.PIE_CHART_OUTLINE,
            "color": "#356AE6",
            "fondo": "#EAF2FF",
            "filtro": "Tipo",
            "opciones": (
                "Todos los tipos",
                "Proforma Puerto",
                "Víveres / Proveeduría",
                "General",
            ),
        },
        {
            "nombre": "Clientes más activos",
            "descripcion": "Clientes con mayor movimiento.",
            "icono": ft.Icons.GROUPS_OUTLINED,
            "color": COLOR_VERDE,
            "fondo": "#EAF8F0",
            "filtro": "Estado del cliente",
            "opciones": ("Todos", "Activos", "Inactivos"),
        },
        {
            "nombre": "Productos más solicitados",
            "descripcion": "Demanda y cantidades.",
            "icono": ft.Icons.INVENTORY_2_OUTLINED,
            "color": "#178F62",
            "fondo": "#EAF8F0",
            "filtro": "Producto",
            "opciones": (
                "Todos los productos",
                "Perecederos",
                "Requieren refrigeración",
            ),
        },
        {
            "nombre": "Actividad por buque",
            "descripcion": "Operaciones agrupadas por embarcación.",
            "icono": ft.Icons.DIRECTIONS_BOAT_OUTLINED,
            "color": "#8B35D3",
            "fondo": "#F4ECFF",
            "filtro": "Actividad",
            "opciones": (
                "Todos los buques",
                "Con operaciones",
                "Sin operaciones",
            ),
        },
        {
            "nombre": "Análisis financiero",
            "descripcion": "Ingresos, costos y utilidad.",
            "icono": ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
            "color": COLOR_NARANJA,
            "fondo": "#FFF2E8",
            "filtro": "Concepto",
            "opciones": ("Todos", "Productos", "Servicios"),
        },
    )
    INFORMES_DEMO = (
        {
            "nombre": "Rendimiento de cotizaciones",
            "periodo": "Octubre 2026",
            "generado": "10/11/2026 · 09:30",
            "formato": "PDF",
            "color": COLOR_ROJO,
        },
        {
            "nombre": "Clientes más activos",
            "periodo": "Sep – Oct 2026",
            "generado": "08/11/2026 · 14:15",
            "formato": "Excel",
            "color": COLOR_VERDE,
        },
        {
            "nombre": "Análisis financiero",
            "periodo": "Octubre 2026",
            "generado": "05/11/2026 · 11:42",
            "formato": "PDF",
            "color": COLOR_AZUL,
        },
    )

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
        self._datos_metricas = {
            "Ingresos": {
                "valores": self.INGRESOS,
                "total": "$531,000 MXN",
                "descripcion": "Total ilustrativo · 6 meses",
                "unidad": "miles de MXN",
                "color": COLOR_AZUL,
            },
            "Cotizaciones": {
                "valores": self.COTIZACIONES,
                "total": "1,248",
                "descripcion": "Cotizaciones ilustrativas · 6 meses",
                "unidad": "cotizaciones",
                "color": COLOR_AZUL,
            },
            "Aprobaciones": {
                "valores": self.APROBACIONES,
                "total": "78%",
                "descripcion": "Tasa ilustrativa · octubre",
                "unidad": "porcentaje",
                "color": COLOR_VERDE,
            },
            "Rentabilidad": {
                "valores": self.RENTABILIDAD,
                "total": "18%",
                "descripcion": "Margen ilustrativo · octubre",
                "unidad": "porcentaje",
                "color": COLOR_NARANJA,
            },
        }

        self._selector_periodo = ft.Dropdown(
            value=self._periodo,
            width=225,
            height=42,
            text_size=14,
            color=COLOR_BANNER,
            bgcolor=COLOR_BLANCO,
            filled=True,
            fill_color=COLOR_BLANCO,
            tooltip=(
                "Filtro de periodo para todo el dashboard; se aplicara a los datos "
                "cuando se conecte la informacion real."
            ),
            content_padding=ft.Padding(10, 7, 10, 7),
            border=ft.InputBorder.OUTLINE,
            border_color="#C8D5E4",
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
            width=260,
            height=42,
            text_size=14,
            color=COLOR_BANNER,
            bgcolor=COLOR_BLANCO,
            filled=True,
            fill_color=COLOR_BLANCO,
            tooltip=(
                "Filtro de módulo para todo el dashboard; se aplicará a los datos "
                "cuando se conecte la informacion real."
            ),
            content_padding=ft.Padding(10, 7, 10, 7),
            border=ft.InputBorder.OUTLINE,
            border_color="#C8D5E4",
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
        self._panel_indicadores = self._crear_panel_indicadores()
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
                                "Explora indicadores y análisis de ejemplo; los datos reales aún no están conectados.",
                                ft.Icons.INSERT_CHART_OUTLINED,
                                altura=108,
                                tamano_icono=58,
                                tamano_grafico=31,
                                tamano_titulo=25,
                                tamano_descripcion=14,
                                padding=ft.Padding(18, 8, 18, 8),
                            ),
                            self._barra_filtros(),
                            self._tarjetas_metricas(),
                            ft.Row(
                                height=260,
                                spacing=10,
                                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                                controls=[
                                    ft.Container(
                                        expand=4,
                                        content=self._panel_grafica,
                                    ),
                                    ft.Container(
                                        expand=1,
                                        content=self._panel_indicadores,
                                    ),
                                ],
                            ),
                            ft.Row(
                                height=154,
                                spacing=0,
                                vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                                controls=[
                                    ft.Container(
                                        expand=True,
                                        content=self._panel_recientes,
                                    ),
                                ],
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
                ft.Container(
                    padding=ft.Padding(9, 6, 9, 6),
                    bgcolor="#FFF2E8",
                    border_radius=8,
                    content=ft.Row(
                        tight=True,
                        spacing=5,
                        controls=[
                            ft.Icon(
                                ft.Icons.INFO_OUTLINE,
                                size=14,
                                color=COLOR_NARANJA,
                            ),
                            ft.Text(
                                "Datos ilustrativos",
                                size=11,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                        ],
                    ),
                ),
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
                                size=14,
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
                    on_click=self.abrir_selector_reportes,
                ),
            ],
        )

    def _tarjetas_metricas(self):
        metricas = (
            (
                "Clientes",
                "142",
                "Registros totales · demo",
                ft.Icons.GROUPS_OUTLINED,
                COLOR_AZUL,
                "#EAF2FF",
                (4, 7, 5, 9, 8, 12, 10, 15),
            ),
            (
                "Productos",
                "856",
                "Registros totales · demo",
                ft.Icons.INVENTORY_2_OUTLINED,
                COLOR_VERDE,
                "#EAF8F0",
                (5, 6, 8, 7, 11, 9, 13, 15),
            ),
            (
                "Buques",
                "67",
                "Registros totales · demo",
                ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                "#8B35D3",
                "#F4ECFF",
                (3, 5, 7, 6, 10, 9, 12, 16),
            ),
            (
                "Cotizaciones",
                "1,248",
                "Muestra de 6 meses · demo",
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

    def _tarjeta_metrica(self, titulo, valor, aclaracion, icono, color, fondo, serie):
        return card(
            ft.Row(
                spacing=9,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=50,
                        height=50,
                        alignment=ft.Alignment(0, 0),
                        bgcolor=fondo,
                        border_radius=25,
                        content=ft.Icon(icono, size=26, color=color),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=1,
                        controls=[
                            ft.Text(
                                titulo,
                                size=13,
                                color=COLOR_NEGRO,
                                tooltip=aclaracion,
                            ),
                            ft.Row(
                                spacing=3,
                                controls=[
                                    ft.Text(
                                        valor,
                                        size=22,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_BANNER,
                                    ),
                                ],
                            ),
                            ft.Text(aclaracion, size=9, color=COLOR_GRIS),
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
            tooltip="Tendencia ilustrativa; no es una comparación real",
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
            "Total ilustrativo · 6 meses",
            size=12,
            color=COLOR_GRIS,
        )
        self._valor_periodo = ft.Text(
            "$531,000 MXN",
            size=22,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BANNER,
        )
        self._indicadores_clave = ft.Column(
            spacing=8,
            controls=[
                self._fila_indicador_clave(
                    "78%", "Aprobadas · demo", COLOR_VERDE
                ),
                self._fila_indicador_clave(
                    "15", "Pendientes · demo", COLOR_NARANJA
                ),
                self._fila_indicador_clave(
                    "34", "Liquidadas · demo", COLOR_AZUL
                ),
            ],
        )
        self._grafica_mensual = self._crear_grafica_mensual(self.INGRESOS)
        self._grafica_slot = ft.Container(
            expand=True,
            content=self._grafica_mensual,
        )
        return ft.Container(
            expand=True,
            padding=12,
            bgcolor=COLOR_BLANCO,
            border=ft.Border.all(1, "#E1EAF4"),
            border_radius=14,
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Container(
                                width=38,
                                height=38,
                                alignment=ft.Alignment(0, 0),
                                bgcolor="#FFF2E8",
                                border_radius=11,
                                content=ft.Icon(
                                    ft.Icons.QUERY_STATS,
                                    size=21,
                                    color=COLOR_NARANJA,
                                ),
                            ),
                            ft.Column(
                                spacing=1,
                                controls=[
                                    ft.Text(
                                        "Resumen de desempeño",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_BANNER,
                                    ),
                                    ft.Text(
                                        "Evolución mensual · valores ilustrativos",
                                        size=11,
                                        color=COLOR_GRIS,
                                    ),
                                ],
                            ),
                            ft.Container(expand=True),
                            self._botones_metricas(),
                        ],
                    ),
                    self._grafica_slot,
                ],
            ),
        )

    def _crear_panel_indicadores(self):
        return ft.Container(
            expand=True,
            padding=14,
            bgcolor="#EAF3FF",
            border=ft.Border.all(1, "#D5E5F8"),
            border_radius=14,
            content=ft.Stack(
                expand=True,
                controls=[
                    ft.Container(
                        alignment=ft.Alignment(1, -1),
                        content=ft.Icon(
                            ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                            size=88,
                            color="#8DB9F2",
                            opacity=0.16,
                        ),
                    ),
                    ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                spacing=6,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.TRENDING_UP,
                                        size=18,
                                        color=COLOR_AZUL,
                                    ),
                                    ft.Text(
                                        "Indicadores clave",
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_BANNER,
                                    ),
                                ],
                            ),
                            self._valor_periodo,
                            self._resumen_periodo,
                            ft.Container(
                                height=1,
                                bgcolor="#D7E4F4",
                                margin=ft.Margin(0, 3, 0, 2),
                            ),
                            self._indicadores_clave,
                        ],
                    ),
                ],
            ),
        )

    def _fila_indicador_clave(self, valor, etiqueta, color):
        return ft.Row(
            spacing=6,
            controls=[
                ft.Container(
                    width=8,
                    height=8,
                    border_radius=4,
                    bgcolor=color,
                ),
                ft.Text(
                    valor,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_BANNER,
                ),
                ft.Text(
                    etiqueta,
                    size=11,
                    color=COLOR_GRIS,
                    expand=True,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        )

    def _botones_metricas(self):
        self._botones_metrica = {}
        iconos = {
            "Ingresos": ft.Icons.SHOW_CHART,
            "Cotizaciones": ft.Icons.DESCRIPTION_OUTLINED,
            "Aprobaciones": ft.Icons.CHECK_CIRCLE_OUTLINED,
            "Rentabilidad": ft.Icons.PERCENT,
        }
        controles = []
        for titulo in self._datos_metricas:
            boton = ft.Container(
                padding=ft.Padding(10, 7, 10, 7),
                border_radius=18,
                bgcolor=COLOR_AZUL if titulo == self._metrica else "#F1F5FA",
                border=ft.Border.all(
                    1,
                    COLOR_AZUL if titulo == self._metrica else "#E1E8F0",
                ),
                on_click=lambda e, valor=titulo: self._cambiar_metrica(valor),
                ink=True,
                content=ft.Row(
                    tight=True,
                    spacing=5,
                    controls=[
                        ft.Icon(
                            iconos[titulo],
                            size=14,
                            color=(
                                COLOR_BLANCO
                                if titulo == self._metrica
                                else COLOR_AZUL
                            ),
                        ),
                        ft.Text(
                            titulo,
                            size=12,
                            color=(
                                COLOR_BLANCO
                                if titulo == self._metrica
                                else COLOR_BANNER
                            ),
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            )
            self._botones_metrica[titulo] = boton
            controles.append(boton)
        return ft.Row(spacing=6, controls=controles)

    def _crear_grafica_mensual(self, valores, metrica="Ingresos"):
        datos = self._datos_metricas[metrica]
        unidad = datos["unidad"]
        color = datos["color"]
        maximo_dato = max(valores)
        if unidad == "porcentaje":
            maximo = 100
        elif unidad == "miles de MXN":
            maximo = ((maximo_dato + 19) // 20) * 20
        else:
            maximo = ((maximo_dato + 49) // 50) * 50

        def formatear_eje(valor):
            if unidad == "miles de MXN":
                return f"${int(valor)}k"
            if unidad == "porcentaje":
                return f"{int(valor)}%"
            return f"{int(valor)}"

        altura_grafica = 136
        etiquetas_eje = ft.Column(
            height=altura_grafica,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(formatear_eje(maximo), size=11, color=COLOR_GRIS),
                ft.Text(formatear_eje(maximo / 2), size=11, color=COLOR_GRIS),
                ft.Text("0", size=11, color=COLOR_GRIS),
            ],
        )
        barras = []
        for mes, valor in zip(self.MESES, valores):
            tooltip = (
                f"{mes}: ${valor * 1000:,.0f} MXN · muestra"
                if unidad == "miles de MXN"
                else f"{mes}: {valor}{'%' if unidad == 'porcentaje' else ''} · muestra"
            )
            barras.append(
                ft.Container(
                    expand=True,
                    alignment=ft.Alignment(0, 1),
                    content=ft.Container(
                        width=32,
                        height=max(7, 124 * valor / maximo),
                        bgcolor=color,
                        border_radius=ft.BorderRadius(8, 8, 2, 2),
                        tooltip=tooltip,
                    ),
                )
            )
        return ft.Container(
            height=178,
            padding=ft.Padding(4, 2, 4, 0),
            content=ft.Column(
                spacing=4,
                controls=[
                    ft.Row(
                        height=altura_grafica,
                        spacing=5,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            ft.Container(width=28, content=etiquetas_eje),
                            ft.Container(
                                expand=True,
                                padding=ft.Padding(8, 4, 8, 2),
                                bgcolor="#F8FAFD",
                                border_radius=10,
                                content=ft.Stack(
                                    expand=True,
                                    controls=[
                                        ft.Column(
                                            expand=True,
                                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                            controls=[
                                                ft.Container(height=1, bgcolor="#E4EBF3")
                                                for _ in range(3)
                                            ],
                                        ),
                                        ft.Row(
                                            expand=True,
                                            spacing=4,
                                            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                                            controls=barras,
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    ft.Row(
                        height=22,
                        spacing=4,
                        controls=[
                            ft.Container(width=28),
                            *[
                                ft.Container(
                                    expand=True,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Text(mes, size=11, color=COLOR_GRIS),
                                )
                                for mes in self.MESES
                            ],
                        ],
                    ),
                ],
            ),
        )

    def _cambiar_metrica(self, metrica):
        self._metrica = metrica
        datos = self._datos_metricas[metrica]
        self._valor_periodo.value = datos["total"]
        self._resumen_periodo.value = datos["descripcion"]
        self._grafica_mensual = self._crear_grafica_mensual(
            datos["valores"], metrica
        )
        self._grafica_slot.content = self._grafica_mensual
        for nombre, boton in self._botones_metrica.items():
            seleccionado = nombre == metrica
            boton.bgcolor = COLOR_AZUL if seleccionado else "#F1F5FA"
            boton.border = ft.Border.all(
                1,
                COLOR_AZUL if seleccionado else "#E1E8F0",
            )
            boton.content.controls[0].color = (
                COLOR_BLANCO if seleccionado else COLOR_AZUL
            )
            boton.content.controls[1].color = (
                COLOR_BLANCO if seleccionado else COLOR_BANNER
            )
        if self._page is not None:
            self._panel_grafica.update()

    def _crear_panel_recientes(self):
        return card(
            ft.Column(
                spacing=9,
                controls=[
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.HISTORY,
                                color=COLOR_NARANJA,
                                size=20,
                            ),
                            ft.Text(
                                "Informes recientes",
                                size=16,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Container(expand=True),
                            ft.Text(
                                "Ejemplos",
                                size=11,
                                color=COLOR_GRIS,
                            ),
                            ft.TextButton(
                                "Ver historial completo",
                                style=ft.ButtonStyle(color=COLOR_AZUL),
                                on_click=self.abrir_historial_completo,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=9,
                        controls=[
                            ft.Container(
                                expand=True,
                                content=self._tarjeta_informe_demo(informe),
                            )
                            for informe in self.INFORMES_DEMO
                        ],
                    ),
                    ft.Text(
                        "Datos y archivos de ejemplo: no corresponden a informes generados realmente.",
                        size=11,
                        color=COLOR_GRIS,
                    ),
                ],
            ),
            padding=12,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    def _tarjeta_informe_demo(self, informe):
        formato = informe["formato"]
        color = informe["color"]
        icono_formato = (
            ft.Icons.PICTURE_AS_PDF_OUTLINED
            if formato == "PDF"
            else ft.Icons.TABLE_VIEW_OUTLINED
        )
        return ft.Container(
            padding=ft.Padding(10, 8, 10, 8),
            border=ft.Border(
                top=ft.BorderSide(1, "#E4ECF5"),
                right=ft.BorderSide(1, "#E4ECF5"),
                bottom=ft.BorderSide(1, "#E4ECF5"),
                left=ft.BorderSide(3, color),
            ),
            border_radius=12,
            bgcolor=COLOR_BLANCO,
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Container(
                        width=38,
                        height=38,
                        alignment=ft.Alignment(0, 0),
                        border_radius=10,
                        bgcolor="#EAF2FF" if formato == "PDF" else "#EAF8F0",
                        content=ft.Icon(icono_formato, size=22, color=color),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                informe["nombre"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"{informe['periodo']} · {informe['generado']}",
                                size=12,
                                color=COLOR_GRIS,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                    ft.Container(
                        width=34,
                        height=34,
                        alignment=ft.Alignment(0, 0),
                        bgcolor="#EAF2FF",
                        border_radius=17,
                        tooltip="Ejemplo; no existe un archivo para descargar",
                        ink=True,
                        on_click=lambda e, nombre=informe["nombre"]: (
                            self._avisar_informe_demo(nombre)
                        ),
                        content=ft.Icon(
                            ft.Icons.DOWNLOAD_OUTLINED,
                            size=18,
                            color=COLOR_AZUL,
                        ),
                    ),
                ],
            ),
        )

    def _fila_informe_historial(self, informe):
        formato = informe["formato"]
        icono_formato = (
            ft.Icons.PICTURE_AS_PDF_OUTLINED
            if formato == "PDF"
            else ft.Icons.TABLE_VIEW_OUTLINED
        )
        return ft.Container(
            padding=ft.Padding(9, 7, 9, 7),
            border=ft.Border(
                bottom=ft.BorderSide(1, "#E7EEF6"),
            ),
            content=ft.Row(
                spacing=10,
                controls=[
                    ft.Container(
                        width=34,
                        height=36,
                        alignment=ft.Alignment(0, 0),
                        border_radius=8,
                        bgcolor="#EAF2FF" if formato == "PDF" else "#EAF8F0",
                        content=ft.Icon(
                            icono_formato,
                            size=22,
                            color=informe["color"],
                        ),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                informe["nombre"],
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Text(
                                f"Periodo: {informe['periodo']} · Generado: {informe['generado']}",
                                size=12,
                                color=COLOR_GRIS,
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=ft.Padding(7, 4, 7, 4),
                        bgcolor="#FFF2E8",
                        border_radius=7,
                        content=ft.Text(
                            "DEMO",
                            size=9,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_NARANJA,
                        ),
                    ),
                ],
            ),
        )

    def abrir_historial_completo(self, e=None):
        self._dialogo_historial = ft.AlertDialog(
            modal=True,
            bgcolor="#F7FAFE",
            shape=ft.RoundedRectangleBorder(radius=18),
            title=ft.Text(
                "Historial de informes",
                size=19,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BANNER,
            ),
            content=ft.Container(
                width=560,
                height=300,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Ejemplos de informes recientes",
                            size=13,
                            color=COLOR_GRIS,
                        ),
                        ft.Column(
                            expand=True,
                            spacing=0,
                            controls=[
                                self._fila_informe_historial(informe)
                                for informe in self.INFORMES_DEMO
                            ],
                        ),
                        ft.Container(
                            padding=ft.Padding(9, 7, 9, 7),
                            bgcolor="#FFF2E8",
                            border_radius=8,
                            content=ft.Text(
                                "Son datos de demostración. El historial real aparecerá cuando se generen y guarden informes.",
                                size=11,
                                color=COLOR_BANNER,
                            ),
                        ),
                    ],
                ),
            ),
            content_padding=ft.Padding(20, 0, 20, 10),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    style=ft.ButtonStyle(color=COLOR_AZUL),
                    on_click=lambda e: self._page.pop_dialog(),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._page.show_dialog(self._dialogo_historial)

    def _avisar_informe_demo(self, nombre):
        self._mensaje_generacion.value = (
            f"{nombre} es un ejemplo; todavía no hay archivo para descargar."
        )
        self._mensaje_generacion.visible = True
        if self._page is not None:
            self._mensaje_generacion.update()

    def abrir_selector_reportes(self, e=None):
        opciones = ft.Column(
            expand=True,
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                self._fila_opcion_reporte(reporte)
                for reporte in self.REPORTES_ESPECIALIZADOS
            ],
        )
        self._dialogo_selector = ft.AlertDialog(
            modal=True,
            bgcolor="#F7FAFE",
            shape=ft.RoundedRectangleBorder(radius=18),
            title=ft.Text(
                "Seleccionar tipo de reporte",
                size=19,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BANNER,
            ),
            content=ft.Container(
                width=560,
                height=430,
                content=ft.Column(
                    expand=True,
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Elige el análisis que quieres configurar.",
                            size=13,
                            color=COLOR_GRIS,
                        ),
                        ft.Divider(height=1, color="#E1EAF4"),
                        opciones,
                        ft.Container(
                            padding=10,
                            bgcolor="#EAF2FF",
                            border_radius=9,
                            content=ft.Row(
                                spacing=7,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.INFO_OUTLINE,
                                        size=15,
                                        color=COLOR_AZUL,
                                    ),
                                    ft.Text(
                                        "La configuración es visual; los datos aún no están conectados.",
                                        size=11,
                                        color=COLOR_BANNER,
                                        expand=True,
                                    ),
                                ],
                            ),
                        ),
                    ],
                ),
            ),
            content_padding=ft.Padding(20, 0, 20, 12),
            actions=[
                ft.TextButton(
                    "Cerrar",
                    style=ft.ButtonStyle(color=COLOR_AZUL),
                    on_click=lambda e: self._page.pop_dialog(),
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self._page.show_dialog(self._dialogo_selector)

    def _fila_opcion_reporte(self, reporte):
        return ft.Container(
            padding=ft.Padding(10, 8, 10, 8),
            border_radius=10,
            ink=True,
            on_click=lambda e, opcion=reporte: self._abrir_configuracion_reporte(
                opcion
            ),
            content=ft.Row(
                spacing=11,
                controls=[
                    ft.Container(
                        width=38,
                        height=38,
                        alignment=ft.Alignment(0, 0),
                        border_radius=11,
                        bgcolor=reporte["fondo"],
                        content=ft.Icon(
                            reporte["icono"],
                            size=20,
                            color=reporte["color"],
                        ),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                reporte["nombre"],
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Text(
                                reporte["descripcion"],
                                size=11,
                                color=COLOR_GRIS,
                            ),
                        ],
                    ),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        size=19,
                        color=COLOR_AZUL,
                    ),
                ],
            ),
        )

    def _abrir_configuracion_reporte(self, reporte):
        self._page.pop_dialog()
        self._reporte_seleccionado = reporte
        self._selector_periodo_reporte = ft.Dropdown(
            value=self._periodo,
            options=[
                ft.DropdownOption(key=valor, text=valor)
                for valor in (
                    "Últimos 30 días",
                    "Últimos 3 meses",
                    "Últimos 6 meses",
                    "Este año",
                )
            ],
            border_color="#C9DDF7",
            focused_border_color=COLOR_AZUL,
            border_radius=9,
            text_size=14,
            expand=True,
        )
        self._selector_filtro_reporte = ft.Dropdown(
            value=reporte["opciones"][0],
            options=[
                ft.DropdownOption(key=valor, text=valor)
                for valor in reporte["opciones"]
            ],
            border_color="#C9DDF7",
            focused_border_color=COLOR_AZUL,
            border_radius=9,
            text_size=14,
            expand=True,
        )
        self._selector_formato_reporte = ft.Dropdown(
            value="PDF",
            options=[
                ft.DropdownOption(key="PDF", text="PDF"),
                ft.DropdownOption(key="Excel", text="Excel"),
            ],
            border_color="#C9DDF7",
            focused_border_color=COLOR_AZUL,
            border_radius=9,
            text_size=14,
            width=160,
        )
        self._dialogo_configuracion = ft.AlertDialog(
            modal=True,
            bgcolor="#F7FAFE",
            shape=ft.RoundedRectangleBorder(radius=18),
            title=ft.Row(
                spacing=10,
                controls=[
                    ft.Container(
                        width=38,
                        height=38,
                        alignment=ft.Alignment(0, 0),
                        border_radius=11,
                        bgcolor=reporte["fondo"],
                        content=ft.Icon(
                            reporte["icono"],
                            size=20,
                            color=reporte["color"],
                        ),
                    ),
                    ft.Column(
                        spacing=2,
                        controls=[
                            ft.Text(
                                reporte["nombre"],
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Text(
                                "Configura los parámetros del informe",
                                size=12,
                                color=COLOR_GRIS,
                            ),
                        ],
                    ),
                ],
            ),
            content=ft.Container(
                width=470,
                content=ft.Column(
                    tight=True,
                    spacing=12,
                    controls=[
                        self._campo_configuracion(
                            "Periodo",
                            self._selector_periodo_reporte,
                        ),
                        self._campo_configuracion(
                            reporte["filtro"],
                            self._selector_filtro_reporte,
                        ),
                        self._campo_configuracion(
                            "Formato de salida",
                            self._selector_formato_reporte,
                        ),
                        ft.Container(
                            padding=10,
                            bgcolor="#FFF2E8",
                            border_radius=9,
                            content=ft.Text(
                                "La generación estará disponible cuando se conecten los datos del sistema.",
                                size=11,
                                color=COLOR_BANNER,
                            ),
                        ),
                    ],
                ),
            ),
            content_padding=ft.Padding(20, 8, 20, 10),
            actions=[
                ft.TextButton(
                    "Volver",
                    style=ft.ButtonStyle(color=COLOR_AZUL),
                    on_click=self._volver_a_reportes,
                ),
                ft.FilledButton(
                    content="Generar reporte",
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_NARANJA,
                        color=COLOR_BLANCO,
                        shape=ft.RoundedRectangleBorder(radius=9),
                    ),
                    on_click=self._generar_reporte_configurado,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            actions_padding=ft.Padding(16, 8, 16, 14),
        )
        self._page.show_dialog(self._dialogo_configuracion)

    def _campo_configuracion(self, etiqueta, control):
        return ft.Column(
            spacing=5,
            controls=[
                ft.Text(
                    etiqueta,
                    size=12,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_BANNER,
                ),
                control,
            ],
        )

    def _volver_a_reportes(self, e):
        self._page.pop_dialog()
        self.abrir_selector_reportes()

    def _generar_reporte_configurado(self, e):
        reporte = self._reporte_seleccionado["nombre"]
        periodo = self._selector_periodo_reporte.value
        filtro = self._selector_filtro_reporte.value
        formato = self._selector_formato_reporte.value
        self._page.pop_dialog()
        self._mensaje_generacion.value = (
            f"{reporte} configurado: {periodo} · {filtro} · {formato}. "
            "No se generó un archivo porque los datos aún no están conectados."
        )
        self._mensaje_generacion.visible = True
        if self._page is not None:
            self._mensaje_generacion.update()

    def _cambiar_filtros(self, e):
        self._periodo = self._selector_periodo.value
        self._modulo = self._selector_modulo.value
        self._mensaje_generacion.visible = False
        if self._page is not None:
            self._page.update()

    def generar_reporte(self, e=None):
        self.abrir_selector_reportes(e)
