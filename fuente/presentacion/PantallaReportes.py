import math
from datetime import datetime

import flet as ft
from sqlalchemy.exc import SQLAlchemyError

from fuente.utilidades.ExportacionArchivos import obtener_selector_archivos
from fuente.utilidades.ExportacionExcel import crear_excel_con_grafica
from fuente.utilidades.ExportacionPDF import crear_pdf
from fuente.utilidades.HistorialInformes import (
    cargar_historial_informes,
    guardar_informe_generado,
    leer_contenido_informe,
)
from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_BANNER,
    COLOR_BLANCO,
    COLOR_FONDO,
    COLOR_GRIS,
    COLOR_NARANJA,
    COLOR_VERDE,
)
from fuente.utilidades.feedback import reproducir_sonido
from fuente.utilidades.Componentes import (
    banner_modulo,
    card,
    sombra_suave,
    tarjeta_indicador,
)


class PantallaReportes(ft.Container):
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
            "nombre": "Cotizaciones por estado",
            "descripcion": "Distribución de cotizaciones por estado.",
            "icono": ft.Icons.PIE_CHART_OUTLINE,
            "color": "#356AE6",
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
            "descripcion": "Cotizaciones registradas por embarcación.",
            "icono": ft.Icons.DIRECTIONS_BOAT_OUTLINED,
            "color": "#8B35D3",
            "fondo": "#F4ECFF",
            "filtro": "Actividad",
            "opciones": (
                "Todos los buques",
                "Con cotizaciones",
                "Sin cotizaciones",
            ),
        },
        {
            "nombre": "Análisis financiero",
            "descripcion": "Totales cotizados agrupados por moneda.",
            "icono": ft.Icons.ACCOUNT_BALANCE_WALLET_OUTLINED,
            "color": COLOR_NARANJA,
            "fondo": "#FFF2E8",
            "filtro": "Moneda",
            "opciones": ("Todas las monedas", "MXN", "USD"),
        },
    )

    def __init__(self, page, servicio_reportes, informes_generados=None):
        super().__init__(expand=True, bgcolor=COLOR_FONDO)
        self._page = page
        self._servicio_reportes = servicio_reportes
        self._periodo = "Últimos 6 meses"
        self._modulo = "Todos los módulos"
        self._metrica = "Ingresos"
        self._informes_generados = (
            informes_generados if informes_generados is not None else []
        )
        self._mensaje_generacion = ft.Text(
            "",
            size=11,
            color=COLOR_GRIS,
            visible=False,
        )
        if not self._informes_generados:
            try:
                self._informes_generados.extend(cargar_historial_informes())
            except (OSError, ValueError) as error:
                self._mensaje_generacion.value = (
                    f"No se pudo cargar el historial de reportes: {error}"
                )
                self._mensaje_generacion.visible = True
        self._resumen = self._servicio_reportes.obtener_resumen(
            self._periodo, self._modulo
        )
        self._datos_metricas = self._crear_datos_metricas()

        self._selector_periodo = ft.Dropdown(
            value=self._periodo,
            width=225,
            height=44,
            dense=True,
            text_size=14,
            color=COLOR_BANNER,
            bgcolor=COLOR_BLANCO,
            filled=True,
            fill_color=COLOR_BLANCO,
            tooltip="Periodo que se aplicará a los indicadores y la gráfica.",
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
            height=44,
            dense=True,
            text_size=14,
            color=COLOR_BANNER,
            bgcolor=COLOR_BLANCO,
            filled=True,
            fill_color=COLOR_BLANCO,
            tooltip="Módulo que se aplicará a la gráfica de actividad.",
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
                        spacing=8,
                        controls=[
                            banner_modulo(
                                "fondo_puerto.jpg",
                                "Reportes",
                                "Análisis y Estadísticas",
                                "Indicadores y reportes calculados con la información registrada.",
                                ft.Icons.INSERT_CHART_OUTLINED,
                            ),
                            self._barra_filtros(),
                            ft.Column(
                                spacing=8,
                                controls=[
                                    self._tarjetas_metricas(),
                                    self._panel_inferior(),
                                ],
                            ),
                        ],
                    ),
                )
            ],
        )

    def _crear_datos_metricas(self):
        resumen = self._resumen
        series = resumen["series"]
        periodo = self._periodo.lower()
        modulo = self._modulo
        unidad_actividad = resumen["unidad_grafica"]

        return {
            "Ingresos": {
                "etiqueta": "Monto cotizado",
                "valores": series["Ingresos"],
                "total": f"${resumen['monto_mxn_periodo']:,.0f} MXN",
                "descripcion": f"Periodo: {periodo}",
                "grafica": (
                    "Importe de cotizaciones en MXN por mes; "
                    f"eje vertical en miles de MXN · {periodo}"
                ),
                "unidad": "miles de MXN",
                "color": COLOR_AZUL,
            },
            "Cotizaciones": {
                "etiqueta": "Cotizaciones",
                "valores": series["Cotizaciones"],
                "total": f"{resumen['cotizaciones_periodo']:,}",
                "descripcion": f"Generadas en {periodo}",
                "grafica": f"Cantidad de cotizaciones creadas por mes · {periodo}",
                "unidad": "cotizaciones",
                "color": COLOR_AZUL,
            },
            "Aprobaciones": {
                "etiqueta": "Tasa avanzada",
                "valores": series["Aprobaciones"],
                "total": f"{resumen['aprobacion_periodo']}%",
                "descripcion": (
                    f"Con anticipo, en operación o liquidadas · {periodo}"
                ),
                "grafica": (
                    "Porcentaje de cotizaciones con anticipo recibido, "
                    f"en operación o liquidadas · {periodo}"
                ),
                "unidad": "porcentaje",
                "color": COLOR_VERDE,
            },
            "Actividad": {
                "etiqueta": "Actividad",
                "valores": series["Actividad"],
                "total": f"{sum(series['Actividad']):,.0f} {unidad_actividad}",
                "descripcion": f"{unidad_actividad.capitalize()} · {periodo}",
                "grafica": self._descripcion_actividad(
                    modulo, unidad_actividad, periodo
                ),
                "unidad": unidad_actividad,
                "color": COLOR_NARANJA,
            },
        }

    @staticmethod
    def _descripcion_actividad(modulo, unidad, periodo):
        if modulo == "Servicios":
            detalle = "unidades de servicio incluidas en cotizaciones"
        elif modulo == "Productos":
            detalle = "unidades de producto incluidas en cotizaciones"
        elif modulo == "Clientes":
            detalle = "clientes registrados"
        elif modulo in ("Buques", "Cotizaciones"):
            detalle = "cotizaciones creadas"
        else:
            detalle = "clientes registrados (actividad predeterminada)"
        return f"{detalle.capitalize()} por mes · {periodo}; unidad: {unidad}"

    def _panel_inferior(self):
        return card(
            ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        height=350,
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
                        height=118,
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
            padding=ft.Padding(8, 4, 8, 14),
            bgcolor="#F8FAFD",
            border_color="#DCE6F1",
            radius=14,
            shadow=sombra_suave(),
            expand=True,
        )

    def _barra_filtros(self):
        return ft.Row(
            height=44,
            spacing=9,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
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
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BLANCO,
                            ),
                        ],
                    ),
                    height=38,
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
        resumen = self._resumen
        series = resumen["series"]
        metricas = (
            (
                "Clientes",
                f"{resumen['totales']['clientes']:,}",
                "Registros actuales",
                ft.Icons.GROUPS_OUTLINED,
                COLOR_AZUL,
                "#EAF2FF",
                "#D7E6FF",
                series["Clientes"],
            ),
            (
                "Servicios",
                f"{resumen['totales']['servicios']:,}",
                "Servicios registrados",
                ft.Icons.HANDYMAN_OUTLINED,
                COLOR_VERDE,
                "#EAF8F0",
                "#D5F0E2",
                series["Servicios"],
            ),
            (
                "Buques",
                f"{resumen['totales']['buques']:,}",
                "Registros actuales",
                ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                "#8B35D3",
                "#F4ECFF",
                "#E5D4F5",
                series["Cotizaciones"],
            ),
            (
                "Cotizaciones",
                f"{resumen['cotizaciones_periodo']:,}",
                f"En {self._periodo.lower()}",
                ft.Icons.DESCRIPTION_OUTLINED,
                COLOR_NARANJA,
                "#FFF2E8",
                "#FFE1C9",
                series["Cotizaciones"],
            ),
        )
        fila = ft.Row(
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
                        borde,
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
                    borde,
                    serie,
                ) in metricas
            ],
        )
        self._tarjetas_metricas_row = fila
        return fila

    def _tarjeta_metrica(
        self, titulo, valor, aclaracion, icono, color, fondo, borde, serie
    ):
        descripciones_serie = {
            "Clientes": "Clientes registrados por mes",
            "Servicios": "Unidades de servicio incluidas en cotizaciones por mes",
            "Buques": "Cotizaciones creadas por mes",
            "Cotizaciones": "Cotizaciones creadas por mes",
        }
        return tarjeta_indicador(
            titulo,
            valor,
            aclaracion,
            icono,
            color,
            fondo,
            borde,
            complemento=self._mini_barras(
                serie, color, descripciones_serie[titulo]
            ),
            tooltip=aclaracion,
        )

    def _mini_barras(self, valores, color, tooltip):
        maximo = max((float(valor) for valor in valores), default=0) or 1
        return ft.Container(
            width=66,
            height=34,
            alignment=ft.Alignment(0, 1),
            tooltip=tooltip,
            content=ft.Row(
                spacing=3,
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.END,
                controls=[
                    ft.Container(
                        width=5,
                        height=max(5, float(valor) / maximo * 30),
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
            f"Periodo: {self._periodo.lower()}",
            size=12,
            color=COLOR_GRIS,
        )
        self._valor_periodo = ft.Text(
            f"${self._resumen['monto_mxn_periodo']:,.0f} MXN",
            size=24,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BANNER,
        )
        self._indicadores_clave = ft.Column(
            spacing=8,
            controls=[
                self._fila_indicador_clave(
                    f"{self._resumen['aprobacion_periodo']}%",
                    "Con anticipo, operación o liquidadas",
                    COLOR_VERDE,
                ),
                self._fila_indicador_clave(
                    f"{self._resumen['pendientes_periodo']:,}",
                    "Pendientes",
                    COLOR_NARANJA,
                ),
                self._fila_indicador_clave(
                    f"{self._resumen['liquidadas_periodo']:,}",
                    "Liquidadas",
                    COLOR_AZUL,
                ),
            ],
        )
        self._grafica_mensual = self._crear_grafica_mensual(
            self._datos_metricas[self._metrica]["valores"], self._metrica
        )
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
                expand=True,
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
                                ],
                            ),
                            ft.Container(expand=True),
                        ],
                    ),
                    self._botones_metricas(),
                    self._grafica_slot,
                ],
            ),
            shadow=sombra_suave(),
        )

    def _crear_panel_indicadores(self):
        return ft.Container(
            expand=True,
            padding=10,
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
                        expand=True,
                        spacing=6,
                        controls=[
                            ft.Row(
                                spacing=8,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Container(
                                        width=30,
                                        height=30,
                                        alignment=ft.Alignment(0, 0),
                                        bgcolor="#DCEBFF",
                                        border_radius=9,
                                        content=ft.Icon(
                                            ft.Icons.TRENDING_UP,
                                            size=18,
                                            color=COLOR_AZUL,
                                        ),
                                    ),
                                    ft.Text(
                                        "Indicadores clave",
                                        size=15,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_BANNER,
                                    ),
                                ],
                            ),
                            ft.Container(
                                padding=ft.Padding(10, 6, 10, 6),
                                bgcolor="#F8FBFF",
                                border=ft.Border.all(1, "#D5E5F8"),
                                border_radius=10,
                                content=ft.Column(
                                    spacing=2,
                                    controls=[
                                        ft.Text(
                                            "Total del periodo",
                                            size=11,
                                            weight=ft.FontWeight.W_600,
                                            color=COLOR_GRIS,
                                        ),
                                        self._valor_periodo,
                                        self._resumen_periodo,
                                    ],
                                ),
                            ),
                            ft.Container(
                                height=1,
                                bgcolor="#D7E4F4",
                            ),
                            self._indicadores_clave,
                        ],
                    ),
                ],
            ),
            shadow=sombra_suave(),
        )

    def _fila_indicador_clave(self, valor, etiqueta, color):
        return ft.Container(
            padding=ft.Padding(9, 5, 9, 5),
            bgcolor="#F8FBFF",
            border=ft.Border.all(1, "#DCE8F5"),
            border_radius=9,
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=9,
                        height=9,
                        border_radius=5,
                        bgcolor=color,
                    ),
                    ft.Text(
                        valor,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BANNER,
                    ),
                    ft.Text(
                        etiqueta,
                        size=12,
                        color=COLOR_GRIS,
                        expand=True,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            ),
        )

    def _botones_metricas(self):
        self._botones_metrica = {}
        iconos = {
            "Ingresos": ft.Icons.SHOW_CHART,
            "Cotizaciones": ft.Icons.DESCRIPTION_OUTLINED,
            "Aprobaciones": ft.Icons.CHECK_CIRCLE_OUTLINED,
            "Actividad": ft.Icons.QUERY_STATS,
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
                tooltip=self._datos_metricas[titulo]["grafica"],
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
                            self._datos_metricas[titulo]["etiqueta"],
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
        return ft.Row(
            wrap=True,
            spacing=6,
            run_spacing=6,
            controls=controles,
        )

    def _crear_grafica_mensual(self, valores, metrica="Ingresos"):
        datos = self._datos_metricas[metrica]
        unidad = datos["unidad"]
        color = datos["color"]
        maximo_dato = max((float(valor) for valor in valores), default=0)
        if unidad == "porcentaje":
            maximo = 100
        elif unidad == "miles de MXN":
            maximo = max(20, math.ceil(maximo_dato / 20) * 20)
        elif maximo_dato <= 10:
            maximo = max(1, math.ceil(maximo_dato))
        else:
            maximo = math.ceil(maximo_dato / 10) * 10

        def formatear_eje(valor):
            if unidad == "miles de MXN":
                return f"${int(valor)}k"
            if unidad == "porcentaje":
                return f"{int(valor)}%"
            return f"{int(valor)}"

        def formatear_tooltip(mes, valor):
            if unidad == "miles de MXN":
                detalle = f"${float(valor) * 1000:,.0f} MXN"
            elif unidad == "porcentaje":
                detalle = f"{valor}%"
            else:
                detalle = f"{valor} {unidad}"
            return f"{mes}: {detalle}"

        altura_grafica = 165
        altura_trazado = altura_grafica - 6
        margen_puntos = 5
        alto_util = altura_trazado - margen_puntos * 2
        ancho_punto = 12
        ancho_paso = max(
            90,
            (((getattr(self._page, "width", None) or 1510) - 274) * 0.8 - 70)
            / max(len(valores), 1),
        )
        etiquetas_eje = ft.Column(
            height=altura_grafica,
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                ft.Text(formatear_eje(maximo), size=11, color=COLOR_GRIS),
                ft.Text(formatear_eje(maximo / 2), size=11, color=COLOR_GRIS),
                ft.Text("0", size=11, color=COLOR_GRIS),
            ],
        )
        celdas_tramo = []
        coordenadas = [
            margen_puntos + alto_util * (1 - valor / maximo)
            for valor in (float(item) for item in valores)
        ]
        etiquetas = self._resumen["labels"]
        for indice, (mes, valor) in enumerate(zip(etiquetas, valores)):
            tooltip = formatear_tooltip(mes, valor)
            if indice == 0:
                continue
            y_inicio = coordenadas[indice - 1]
            y_fin = coordenadas[indice]
            celdas_tramo.append(
                ft.Stack(
                    expand=2,
                    clip_behavior=ft.ClipBehavior.NONE,
                    controls=[
                        ft.Container(
                            left=0,
                            right=0,
                            top=(y_inicio + y_fin) / 2 - 1.5,
                            height=3,
                            bgcolor=color,
                            border_radius=2,
                            rotate=ft.Rotate(
                                angle=math.atan2(
                                    y_fin - y_inicio,
                                    ancho_paso,
                                )
                            ),
                        ),
                        *(
                            [
                                ft.Container(
                                    left=-ancho_punto / 2,
                                    top=y_inicio - ancho_punto / 2,
                                    width=ancho_punto,
                                    height=ancho_punto,
                                    bgcolor=COLOR_BLANCO,
                                    border=ft.Border.all(3, color),
                                    border_radius=ancho_punto / 2,
                                    tooltip=formatear_tooltip(
                                        etiquetas[0],
                                        valores[0],
                                    ),
                                )
                            ]
                            if indice == 1
                            else []
                        ),
                        ft.Container(
                            right=-ancho_punto / 2,
                            top=y_fin - ancho_punto / 2,
                            width=ancho_punto,
                            height=ancho_punto,
                            bgcolor=COLOR_BLANCO,
                            border=ft.Border.all(3, color),
                            border_radius=ancho_punto / 2,
                            tooltip=tooltip,
                        ),
                    ],
                )
            )
        return ft.Container(
            height=188,
            padding=ft.Padding(4, 0, 4, 0),
            content=ft.Column(
                spacing=3,
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
                                            spacing=0,
                                            vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                                            controls=[
                                                ft.Container(expand=1),
                                                *celdas_tramo,
                                                ft.Container(expand=1),
                                            ],
                                        ),
                                    ],
                                ),
                            ),
                        ],
                    ),
                    ft.Row(
                        height=20,
                        spacing=4,
                        controls=[
                            ft.Container(width=28),
                            *[
                                ft.Container(
                                    expand=True,
                                    alignment=ft.Alignment(0, 0),
                                    content=ft.Text(mes, size=12, color=COLOR_GRIS),
                                )
                                for mes in etiquetas
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
            boton.tooltip = self._datos_metricas[nombre]["grafica"]
            boton.bgcolor = COLOR_AZUL if seleccionado else "#F1F5FA"
            boton.border = ft.Border.all(
                1,
                COLOR_AZUL if seleccionado else "#E1E8F0",
            )
            boton.content.controls[0].color = (
                COLOR_BLANCO if seleccionado else COLOR_AZUL
            )
            boton.content.controls[1].value = self._datos_metricas[nombre]["etiqueta"]
            boton.content.controls[1].color = (
                COLOR_BLANCO if seleccionado else COLOR_BANNER
            )
        if self._page is not None:
            self._panel_grafica.update()

    def _crear_panel_recientes(self):
        return card(
            ft.Column(
                spacing=6,
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
                            ft.TextButton(
                                "Ver más reportes",
                                style=ft.ButtonStyle(color=COLOR_AZUL),
                                on_click=self.abrir_historial_completo,
                            ),
                        ],
                    ),
                    self._lista_informes_recientes(),
                ],
            ),
            padding=ft.Padding(8, 6, 8, 11),
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    def _lista_informes_recientes(self):
        if not self._informes_generados:
            return ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                content=ft.Text(
                    "Aún no se han generado informes.",
                    size=12,
                    color=COLOR_GRIS,
                ),
            )
        return ft.Row(
            spacing=9,
            controls=[
                ft.Container(
                    expand=True,
                    content=self._tarjeta_informe(informe),
                )
                for informe in self._informes_generados[:3]
            ],
        )

    def _tarjeta_informe(self, informe):
        formato = informe["formato"]
        color = informe["color"]
        icono_formato = (
            ft.Icons.PICTURE_AS_PDF_OUTLINED
            if formato == "PDF"
            else ft.Icons.TABLE_VIEW_OUTLINED
        )
        return ft.Container(
            padding=ft.Padding(10, 5, 10, 5),
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
                        tooltip="Descargar informe",
                        ink=True,
                        on_click=lambda e, item=informe: self._descargar_informe(item),
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
                    ft.IconButton(
                        icon=ft.Icons.DOWNLOAD_OUTLINED,
                        tooltip="Descargar informe",
                        icon_color=COLOR_AZUL,
                        on_click=lambda e, item=informe: self._descargar_informe(item),
                    ),
                ],
            ),
        )

    def abrir_historial_completo(self, e=None):
        self._dialogo_historial = ft.AlertDialog(
            modal=True,
            bgcolor="#F7FAFE",
            shape=ft.RoundedRectangleBorder(radius=18),
            title=ft.Row(
                spacing=8,
                controls=[
                    ft.Text(
                        "Ver más reportes",
                        size=19,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BANNER,
                        expand=True,
                    ),
                    ft.IconButton(
                        icon=ft.Icons.CLOSE,
                        tooltip="Cerrar",
                        icon_color=COLOR_GRIS,
                        on_click=lambda e: self._page.pop_dialog(),
                    ),
                ],
            ),
            content=ft.Container(
                width=560,
                height=300,
                content=ft.Column(
                    spacing=8,
                    controls=[
                        ft.Text(
                            "Informes generados durante esta sesión",
                            size=13,
                            color=COLOR_GRIS,
                        ),
                        ft.Column(
                            expand=True,
                            spacing=0,
                            scroll=ft.ScrollMode.AUTO,
                            controls=(
                                [
                                    self._fila_informe_historial(informe)
                                    for informe in self._informes_generados
                                ]
                                or [
                                    ft.Container(
                                        padding=12,
                                        content=ft.Text(
                                            "Todavía no hay informes generados.",
                                            size=12,
                                            color=COLOR_GRIS,
                                        ),
                                    )
                                ]
                            ),
                        ),
                    ],
                ),
            ),
            content_padding=ft.Padding(20, 0, 20, 10),
        )
        self._page.show_dialog(self._dialogo_historial)

    async def _descargar_informe(self, informe):
        try:
            selector = obtener_selector_archivos(self._page)
            contenido = leer_contenido_informe(informe)
            ruta = await selector.save_file(
                dialog_title="Descargar informe",
                file_name=informe["archivo"],
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=[informe["extension"]],
                src_bytes=contenido,
            )
        except (ft.FletException, OSError, ValueError) as error:
            self._mensaje_generacion.value = (
                f"No se pudo descargar el informe: {error}"
            )
            self._mensaje_generacion.visible = True
            reproducir_sonido(self._page, "error")
            self._page.update()
            return

        if ruta is not None or self._page.web:
            self._mensaje_generacion.value = "El informe se descargó correctamente."
            self._mensaje_generacion.visible = True
            reproducir_sonido(self._page, "documento")
            self._page.update()

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
                                        "El informe usará los registros del periodo y filtro seleccionados.",
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
                                "Elige periodo, filtro y formato de descarga.",
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
                                "El PDF incluye una gráfica; Excel agrega los datos y una hoja gráfica.",
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

    async def _generar_reporte_configurado(self, e):
        reporte = self._reporte_seleccionado["nombre"]
        periodo = self._selector_periodo_reporte.value
        filtro = self._selector_filtro_reporte.value
        formato = self._selector_formato_reporte.value
        self._page.pop_dialog()
        try:
            datos = self._servicio_reportes.obtener_informe(
                reporte, periodo, filtro
            )
            nombre_archivo = (
                f"{reporte.replace(' ', '_').replace('/', '-')}_"
                f"{periodo.replace(' ', '_')}"
            )
            if formato == "PDF":
                contenido = crear_pdf(
                    datos["rows"],
                    datos["columns"],
                    titulo=reporte,
                    subtitulo=(
                        f"Periodo: {periodo} · "
                        f"{datos['desde']:%d/%m/%Y} – {datos['hasta']:%d/%m/%Y}"
                    ),
                    metricas=datos["metrics"],
                    orientacion="landscape",
                    grafica=datos["chart"],
                )
                extension = "pdf"
                file_type = ft.FilePickerFileType.CUSTOM
            else:
                contenido = crear_excel_con_grafica(
                    datos["rows"],
                    datos["columns"],
                    nombre_hoja=reporte,
                    grafica=datos["chart"],
                )
                extension = "xlsx"
                file_type = ft.FilePickerFileType.CUSTOM

            archivo = f"{nombre_archivo}.{extension}"
            selector = obtener_selector_archivos(self._page)
            ruta = await selector.save_file(
                dialog_title=f"Exportar {reporte}",
                file_name=archivo,
                file_type=file_type,
                allowed_extensions=[extension],
                src_bytes=contenido,
            )
            if ruta is None and not self._page.web:
                return

            informe = {
                "nombre": reporte,
                "periodo": periodo,
                "generado": datetime.now().strftime("%d/%m/%Y · %H:%M"),
                "formato": formato,
                "color": COLOR_AZUL if formato == "PDF" else COLOR_VERDE,
                "archivo": archivo,
                "extension": extension,
            }
            informe = guardar_informe_generado(informe, contenido)
            self._informes_generados.insert(0, informe)
            lista_anterior = self._panel_recientes.content.controls[1]
            lista_nueva = self._lista_informes_recientes()
            indice = self._panel_recientes.content.controls.index(lista_anterior)
            self._panel_recientes.content.controls[indice] = lista_nueva
            self._mensaje_generacion.value = (
                f"{reporte} se exportó correctamente en {formato}."
            )
            self._mensaje_generacion.visible = True
            reproducir_sonido(self._page, "documento")
            self._page.update()
        except (SQLAlchemyError, ft.FletException, ValueError, OSError) as error:
            self._mensaje_generacion.value = f"No se pudo generar el informe: {error}"
            self._mensaje_generacion.visible = True
            reproducir_sonido(self._page, "error")
            self._page.update()

    def _cambiar_filtros(self, e):
        self._periodo = self._selector_periodo.value
        self._modulo = self._selector_modulo.value
        self._mensaje_generacion.visible = False
        try:
            self._resumen = self._servicio_reportes.obtener_resumen(
                self._periodo, self._modulo
            )
        except (SQLAlchemyError, ValueError) as error:
            self._mensaje_generacion.value = (
                f"No se pudieron actualizar los reportes: {error}"
            )
            self._mensaje_generacion.visible = True
            if self._page is not None:
                self._page.update()
            return
        self._datos_metricas = self._crear_datos_metricas()
        tarjetas_anteriores = self._tarjetas_metricas_row
        nuevas_tarjetas = self._tarjetas_metricas()
        tarjetas_anteriores.controls = nuevas_tarjetas.controls
        self._tarjetas_metricas_row = tarjetas_anteriores
        self._indicadores_clave.controls = [
            self._fila_indicador_clave(
                f"{self._resumen['aprobacion_periodo']}%",
                "Con anticipo, operación o liquidadas",
                COLOR_VERDE,
            ),
            self._fila_indicador_clave(
                f"{self._resumen['pendientes_periodo']:,}",
                "Pendientes",
                COLOR_NARANJA,
            ),
            self._fila_indicador_clave(
                f"{self._resumen['liquidadas_periodo']:,}",
                "Liquidadas",
                COLOR_AZUL,
            ),
        ]
        self._valor_periodo.value = (
            f"${self._resumen['monto_mxn_periodo']:,.0f} MXN"
        )
        self._resumen_periodo.value = f"Periodo: {self._periodo.lower()}"
        if self._page is not None:
            self._panel_indicadores.update()
        self._cambiar_metrica(self._metrica)
        if self._page is not None:
            self._page.update()

    def generar_reporte(self, e=None):
        self.abrir_selector_reportes(e)
