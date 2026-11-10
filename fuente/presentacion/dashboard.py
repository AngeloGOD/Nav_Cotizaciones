import flet as ft

from fuente.negocio.controlador.ControladorDashboard import ControladorDashboard
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
from fuente.utilidades.Componentes import (
    avatar_inicial,
    badge_estado,
    banner_modulo,
    card,
    sombra_suave,
)


class dashboard(ft.Container):
    ACTIVIDAD_DEMO = (
        {
            "icono": ft.Icons.DESCRIPTION_OUTLINED,
            "color": COLOR_AZUL,
            "fondo": "#EAF2FF",
            "titulo": "Cotización COT-2026-0048 registrada",
            "fecha": "04/11/2026 · 09:45 a. m.",
        },
        {
            "icono": ft.Icons.CHECK_CIRCLE_OUTLINED,
            "color": COLOR_VERDE,
            "fondo": "#EAF8F0",
            "titulo": "Cotización COT-2026-0046 aprobada",
            "fecha": "03/11/2026 · 04:20 p. m.",
        },
        {
            "icono": ft.Icons.PERSON_OUTLINE,
            "color": COLOR_AZUL,
            "fondo": "#EAF2FF",
            "titulo": "Cliente MSC Shipping S.A. actualizado",
            "fecha": "03/11/2026 · 11:15 a. m.",
        },
        {
            "icono": ft.Icons.INVENTORY_2_OUTLINED,
            "color": COLOR_NARANJA,
            "fondo": "#FFF2E8",
            "titulo": "Producto de servicio actualizado",
            "fecha": "02/11/2026 · 05:30 p. m.",
        },
    )
    CLIENTES_DEMO = (
        ("MSC Shipping S.A.", "04/11/2026"),
        ("Maersk México", "03/11/2026"),
        ("Navios South American", "01/11/2026"),
    )

    def __init__(self):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
            padding=ft.Padding(14, 6, 14, 8),
        )
        self.controlador = ControladorDashboard()
        self.metricas = self.controlador.obtener_metricas()
        self.lista_cotizaciones = self.controlador.obtener_ultimas_cotizaciones()

        self.content = ft.Column(
            expand=True,
            spacing=8,
            controls=[
                self._encabezado(),
                self._tarjetas_resumen(),
                ft.Row(
                    height=215,
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        ft.Container(
                            expand=2,
                            content=self._panel_estado_cotizaciones(),
                        ),
                        ft.Container(
                            expand=3,
                            content=self._panel_actividad(),
                        ),
                    ],
                ),
                ft.Row(
                    height=200,
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        ft.Container(
                            expand=3,
                            content=self._panel_cotizaciones(),
                        ),
                        ft.Container(
                            expand=2,
                            content=self._panel_clientes(),
                        ),
                    ],
                ),
            ],
        )

    def _encabezado(self):
        boton_nueva_cotizacion = ft.FilledButton(
            content=ft.Row(
                tight=True,
                spacing=7,
                controls=[
                    ft.Icon(ft.Icons.ADD, size=17, color=COLOR_BLANCO),
                    ft.Text(
                        "Nueva cotización",
                        size=13,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BLANCO,
                    ),
                ],
            ),
            height=42,
            style=ft.ButtonStyle(
                bgcolor=COLOR_NARANJA,
                shape=ft.RoundedRectangleBorder(radius=9),
                padding=ft.Padding(14, 0, 14, 0),
            ),
            on_click=lambda e: print("Nueva cotización clic"),
        )
        return ft.Stack(
            height=118,
            controls=[
                banner_modulo(
                    "fondo_puerto.jpg",
                    "OPL Pacífico Sur",
                    "Bienvenido, Alexis",
                    "Resumen de cotizaciones y actividad · datos ilustrativos.",
                    ft.Icons.HOME_OUTLINED,
                    altura=118,
                    padding=ft.Padding(18, 8, 18, 8),
                    tamano_icono=56,
                    tamano_grafico=30,
                    tamano_titulo=25,
                    tamano_descripcion=13,
                ),
                ft.Container(
                    alignment=ft.Alignment(1, 0),
                    padding=ft.Padding(0, 0, 18, 0),
                    content=boton_nueva_cotizacion,
                ),
            ],
        )

    def _tarjetas_resumen(self):
        resumenes = (
            (
                "Cotizaciones pendientes",
                self.metricas["pendientes"],
                ft.Icons.DESCRIPTION_OUTLINED,
                COLOR_AZUL,
                "#EAF2FF",
            ),
            (
                "Cotizaciones aprobadas",
                self.metricas["aprobadas"],
                ft.Icons.CHECK_CIRCLE_OUTLINED,
                COLOR_VERDE,
                "#EAF8F0",
            ),
            (
                "Cotizaciones canceladas",
                self.metricas["rechazadas"],
                ft.Icons.CANCEL_OUTLINED,
                COLOR_ROJO,
                "#FDECEE",
            ),
            (
                "Monto cotizado del mes",
                self.metricas["monto_mensual"],
                ft.Icons.PAYMENTS_OUTLINED,
                COLOR_NARANJA,
                "#FFF2E8",
            ),
        )
        return ft.Row(
            spacing=10,
            controls=[
                ft.Container(
                    expand=True,
                    content=self._tarjeta_resumen(
                        titulo,
                        valor,
                        icono,
                        color,
                        fondo,
                    ),
                )
                for titulo, valor, icono, color, fondo in resumenes
            ],
        )

    @staticmethod
    def _tarjeta_resumen(titulo, valor, icono, color, fondo):
        return card(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        alignment=ft.Alignment(0, 0),
                        bgcolor=fondo,
                        border_radius=24,
                        content=ft.Icon(icono, size=25, color=color),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                titulo,
                                size=12,
                                font_family="Roboto",
                                color=COLOR_BANNER,
                                weight=ft.FontWeight.W_600,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                valor,
                                size=22,
                                color=COLOR_BANNER,
                                weight=ft.FontWeight.BOLD,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                "Periodo actual · demo",
                                size=10,
                                color=COLOR_GRIS,
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

    def _panel_estado_cotizaciones(self):
        estados = (
            ("Pendientes", int(self.metricas["pendientes"]), COLOR_AZUL),
            ("Aprobadas", int(self.metricas["aprobadas"]), COLOR_VERDE),
            ("Canceladas", int(self.metricas["rechazadas"]), COLOR_ROJO),
        )
        total = sum(cantidad for _, cantidad, _ in estados)
        total_con_anillo = ft.Stack(
            width=132,
            height=132,
            alignment=ft.Alignment(0, 0),
            controls=[
                ft.ProgressRing(
                    value=cantidad / total if total else 0,
                    width=126 - indice * 30,
                    height=126 - indice * 30,
                    stroke_width=11,
                    color=color,
                    bgcolor="#DCE7F4",
                    tooltip=f"{nombre}: {cantidad}",
                )
                for indice, (nombre, cantidad, color) in enumerate(estados)
            ]
            + [
                ft.Column(
                    tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    controls=[
                        ft.Text("Total", size=11, color=COLOR_GRIS),
                        ft.Text(
                            str(total),
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                    ],
                )
            ],
        )
        segmentos = ft.Row(
            height=14,
            spacing=3,
            controls=[
                ft.Container(
                    expand=max(cantidad, 1),
                    bgcolor=color,
                    border_radius=6,
                )
                for _, cantidad, color in estados
            ],
        )
        filas = ft.Column(
            spacing=8,
            controls=[
                self._fila_estado(nombre, cantidad, color, total)
                for nombre, cantidad, color in estados
            ],
        )
        return card(
            ft.Column(
                spacing=10,
                controls=[
                    self._titulo_panel(
                        ft.Icons.DONUT_SMALL,
                        "Estado de cotizaciones",
                    ),
                    ft.Row(
                        expand=True,
                        spacing=18,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            total_con_anillo,
                            ft.Column(
                                expand=True,
                                spacing=12,
                                controls=[segmentos, filas],
                            ),
                        ],
                    ),
                ],
            ),
            padding=10,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    @staticmethod
    def _fila_estado(nombre, cantidad, color, total):
        porcentaje = cantidad / total * 100 if total else 0
        return ft.Row(
            spacing=7,
            controls=[
                ft.Container(
                    width=9,
                    height=9,
                    border_radius=5,
                    bgcolor=color,
                ),
                ft.Text(
                    nombre,
                    size=13,
                    font_family="Roboto",
                    color=COLOR_BANNER,
                    expand=True,
                ),
                ft.Text(
                    str(cantidad),
                    size=13,
                    font_family="Roboto",
                    color=COLOR_BANNER,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    f"{porcentaje:.1f}%",
                    size=12,
                    font_family="Roboto",
                    color=COLOR_GRIS,
                    width=43,
                    text_align=ft.TextAlign.RIGHT,
                ),
            ],
        )

    def _panel_actividad(self):
        return card(
            ft.Column(
                expand=True,
                spacing=8,
                controls=[
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self._titulo_panel(
                                ft.Icons.BOLT,
                                "Actividad reciente",
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                "Ver historial →",
                                style=ft.ButtonStyle(color=COLOR_AZUL),
                            ),
                        ],
                    ),
                    ft.Column(
                        expand=True,
                        spacing=3,
                        controls=[
                            self._fila_actividad(actividad)
                            for actividad in self.ACTIVIDAD_DEMO
                        ],
                    ),
                ],
            ),
            padding=10,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    @staticmethod
    def _fila_actividad(actividad):
        return ft.Row(
            spacing=9,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=32,
                    height=32,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=actividad["fondo"],
                    border_radius=16,
                    content=ft.Icon(
                        actividad["icono"],
                        size=17,
                        color=actividad["color"],
                    ),
                ),
                ft.Column(
                    expand=True,
                    spacing=1,
                    controls=[
                        ft.Text(
                            actividad["titulo"],
                            size=13,
                            font_family="Roboto",
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            actividad["fecha"],
                            size=11,
                            font_family="Roboto",
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
            ],
        )

    def _panel_cotizaciones(self):
        encabezados = ("Folio", "Fecha", "Buque", "Cliente", "Monto", "Estado")
        tabla = ft.Column(
            spacing=0,
            controls=[
                self._fila_tabla_cotizacion(encabezados, encabezado=True),
                ft.Divider(height=1, color="#E7EEF6"),
                *[
                    self._fila_tabla_cotizacion(
                        (
                            cot["folio"],
                            cot["fecha"],
                            cot["buque"],
                            cot["cliente"],
                            cot["monto"],
                            cot["estado"],
                        ),
                        estado=cot["estado"],
                    )
                    for cot in self.lista_cotizaciones
                ],
            ],
        )
        return card(
            ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self._titulo_panel(
                                ft.Icons.REQUEST_QUOTE_OUTLINED,
                                "Cotizaciones recientes",
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                "Ver historial →",
                                style=ft.ButtonStyle(color=COLOR_AZUL),
                            ),
                        ],
                    ),
                    ft.Text(
                        "Muestra de registros · datos ilustrativos",
                        size=10,
                        color=COLOR_GRIS,
                    ),
                    tabla,
                ],
            ),
            padding=14,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    @staticmethod
    def _fila_tabla_cotizacion(valores, encabezado=False, estado=None):
        proporciones = (135, 100, 115, 145, 120, 100)
        controles = []
        for indice, (valor, proporcion) in enumerate(zip(valores, proporciones)):
            if estado and indice == 5:
                estado_normalizado = estado.lower()
                estado_badge = (
                    "pendiente"
                    if "pendiente" in estado_normalizado
                    else "activo"
                    if "aprob" in estado_normalizado
                    else "inactivo"
                    if "cancel" in estado_normalizado
                    else "info"
                )
                contenido = badge_estado(valor, estado_badge)
            else:
                contenido = ft.Text(
                    valor,
                    size=10 if encabezado else 11,
                    font_family="Roboto",
                    color=COLOR_BANNER if encabezado else COLOR_GRIS,
                    weight=ft.FontWeight.BOLD if encabezado else None,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                    tooltip=valor,
                )
            controles.append(
                ft.Container(
                    expand=proporcion,
                    alignment=ft.Alignment(-1, 0),
                    padding=ft.Padding(5, 8, 3, 8),
                    content=contenido,
                )
            )
        return ft.Container(
            bgcolor="#F3F7FD" if encabezado else None,
            border_radius=6 if encabezado else None,
            content=ft.Row(
                spacing=2,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=controles,
            ),
        )

    def _panel_clientes(self):
        clientes = [
            (nombre, f"Registro demo · {fecha}")
            for nombre, fecha in self.CLIENTES_DEMO
        ]

        return card(
            ft.Column(
                expand=True,
                spacing=5,
                controls=[
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self._titulo_panel(
                                ft.Icons.GROUPS_OUTLINED,
                                "Clientes recientes",
                            ),
                            ft.Container(expand=True),
                            ft.TextButton(
                                "Ver todos →",
                                style=ft.ButtonStyle(color=COLOR_AZUL),
                            ),
                        ],
                    ),
                    ft.Container(
                        padding=ft.Padding(8, 4, 8, 4),
                        bgcolor="#F3F7FD",
                        border_radius=6,
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    "Cliente",
                                    size=11,
                                    font_family="Roboto",
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                    expand=True,
                                ),
                                ft.Text(
                                    "Actividad",
                                    size=11,
                                    font_family="Roboto",
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                    width=160,
                                ),
                            ],
                            spacing=8,
                        ),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=0,
                        controls=[
                            self._fila_cliente(nombre, detalle)
                            for nombre, detalle in clientes
                        ],
                    ),
                ],
            ),
            padding=10,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    @staticmethod
    def _fila_cliente(nombre, detalle):
        return ft.Container(
            padding=ft.Padding(0, 2, 0, 2),
            border=ft.Border(
                bottom=ft.BorderSide(1, "#EDF1F6"),
            ),
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    avatar_inicial(nombre, color=COLOR_BANNER, size=26),
                    ft.Text(
                        nombre,
                        size=12,
                        font_family="Roboto",
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.W_600,
                        expand=True,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        detalle,
                        size=10,
                        font_family="Roboto",
                        color=COLOR_GRIS,
                        width=160,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            ),
        )

    @staticmethod
    def _titulo_panel(icono, titulo):
        return ft.Row(
            tight=True,
            spacing=7,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icono, size=18, color=COLOR_NARANJA),
                ft.Text(
                    titulo,
                    size=15,
                    font_family="Roboto",
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_BANNER,
                ),
            ],
        )
