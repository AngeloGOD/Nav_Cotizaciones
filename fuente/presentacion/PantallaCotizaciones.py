import flet as ft
from fuente.presentacion.PantallaNuevaCotizacion import PantallaNuevaCotizacion
from fuente.utilidades.Colores import COLOR_NARANJA, COLOR_BLANCO, COLOR_GRIS

COLOR_AZUL_OSCURO = "#0d1b2a" 
COLOR_FONDO_TABLA = "#f8f9fa"

class PantallaCotizaciones(ft.Container):
    
    def __init__(self, main_page):
        super().__init__()
        self.main_page = main_page 
        self.expand = True
        self.padding = ft.Padding(20, 20, 20, 20)
        
        # BANNER
        banner = ft.Container(
            height=130,
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            border=self.crear_borde_completo(1, ft.Colors.GREY_200),
            content=ft.Stack([
                ft.Container(
                    expand=True,
                    image=ft.DecorationImage(
                        src="fondo_puerto.jpg", 
                        fit="cover",
                        alignment=ft.alignment.Alignment(1, 0)
                    )
                ),
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.Alignment(-1, 0),
                        end=ft.alignment.Alignment(1, 0),
                        colors=[COLOR_BLANCO, COLOR_BLANCO, ft.Colors.with_opacity(0.6, COLOR_BLANCO), ft.Colors.TRANSPARENT],
                        stops=[0.0, 0.45, 0.7, 1.0]
                    )
                ),
                ft.Container(
                    padding=ft.Padding(30, 25, 30, 25),
                    content=ft.Column([
                    
                        ft.Text("Historial y Control de Cotizaciones", size=28, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO),
                        ft.Text("Administra, filtra y genera nuevas cotizaciones para la agencia.", size=14, color=COLOR_GRIS),
                    ], spacing=5)
                )
            ])
        )

        boton_nueva_cotizacion = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, color=COLOR_BLANCO, size=18),
                ft.Text("Nueva Cotización", color=COLOR_BLANCO, weight=ft.FontWeight.W_600, size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            bgcolor=COLOR_NARANJA,
            padding=ft.Padding(20, 5, 20, 5),
            border_radius=6,
            height=44, 
            ink=True, 
            on_click=lambda e: self.abrir_nueva_cotizacion()
        )

        # BARRA DE BÚSQUEDA Y FILTROS
        barra_herramientas = ft.Row([
            ft.Container(
                expand=True,
                content=ft.TextField(
                    hint_text="Buscar por folio, buque o cliente...",
                    prefix_icon=ft.Icons.SEARCH,
                    border_color=ft.Colors.GREY_300,
                    border_radius=6,
                    height=44, 
                    content_padding=10,
                    text_size=14 
                )
            ),
            ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.FILTER_LIST, size=18, color=ft.Colors.BLUE_600),
                    ft.Text("Filtros", size=14, color=ft.Colors.BLUE_600, weight=ft.FontWeight.W_500),
                ]),
                padding=ft.Padding(15, 5, 15, 5),
                border=self.crear_borde_completo(1, ft.Colors.GREY_300), 
                border_radius=6,
                height=44, 
                ink=True,
                on_click=lambda e: print("Abrir filtros")
            ),
            boton_nueva_cotizacion 
        ], spacing=15, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        tarjetas_resumen = ft.Row([
            self.crear_tarjeta_resumen("Total", "10", ft.Icons.DESCRIPTION_OUTLINED, ft.Colors.GREY_700, ft.Colors.GREY_100, borde_negro=True),
            self.crear_tarjeta_resumen("Pendientes", "3", ft.Icons.ACCESS_TIME, ft.Colors.ORANGE_500, ft.Colors.ORANGE_50),
            self.crear_tarjeta_resumen("Aprobadas", "5", ft.Icons.CHECK_CIRCLE_OUTLINE, ft.Colors.GREEN_500, ft.Colors.GREEN_50),
            self.crear_tarjeta_resumen("Rechazadas", "2", ft.Icons.CANCEL_OUTLINED, ft.Colors.RED_500, ft.Colors.RED_50),
        ], spacing=15)

        boton_exportar = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DOWNLOAD, color=ft.Colors.BLUE_600, size=16),
                ft.Text("Exportar", color=ft.Colors.BLUE_600, weight=ft.FontWeight.W_500, size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            border=self.crear_borde_completo(1, ft.Colors.GREY_300),
            padding=ft.Padding(15, 5, 15, 5),
            border_radius=6,
            height=44, 
            ink=True,
            on_click=lambda e: print("Exportando...")
        )

        # TABLA DE HISTORIAL 
        
        titulo_tabla = ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Icon(ft.Icons.REQUEST_QUOTE_OUTLINED, color=COLOR_BLANCO, size=24),
                    bgcolor=COLOR_NARANJA,
                    border_radius=10,
                    padding=10,
                ),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text("Historial de cotizaciones", size=19, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO),
                        ft.Text("10 cotizaciones registradas", size=14, color=COLOR_GRIS),
                    ],
                ),
                boton_exportar
            ],
        )

        tabla_cotizaciones = ft.ListView(
            expand=True,
            controls=[
                ft.DataTable(
                    heading_row_color=COLOR_FONDO_TABLA,
                    heading_row_height=45,
                    data_row_min_height=60,
                    data_row_max_height=80,
        
                    vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200),
                    border=self.crear_borde_completo(1, ft.Colors.GREY_200),
                    
                   columns=[
                        ft.DataColumn(ft.Text("Folio", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Fecha", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Nombre del Buque", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Cliente", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Monto Total", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Estado", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Acciones", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("COT-2026-0048", color=ft.Colors.BLUE_600, size=13)),
                            ft.DataCell(ft.Text("04/09/2026", size=13, color=COLOR_GRIS)),
                            ft.DataCell(ft.Text("MSC ORION", weight=ft.FontWeight.W_600, size=13)),
                            ft.DataCell(ft.Text("MSC Shipping S.A.", size=13, color=COLOR_GRIS)),
                            ft.DataCell(ft.Text("$245,800.00 MXN", weight=ft.FontWeight.BOLD, size=13)),
                            ft.DataCell(self.crear_badge_estado("Pendiente")),
                            ft.DataCell(ft.Row([
                                ft.IconButton(icon=ft.Icons.VISIBILITY_OUTLINED, icon_color=ft.Colors.BLUE_600, icon_size=18), 
                                ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, icon_size=18)
                            ]))
                        ])
                    ]
                )
            ]
        )

        pie_tabla = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Mostrando 1 de 10 cotizaciones", size=14, color=COLOR_GRIS),
                ft.Row([
                    ft.IconButton(icon=ft.Icons.FIRST_PAGE, icon_color=COLOR_GRIS, icon_size=18),
                    ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, icon_color=COLOR_GRIS, icon_size=18),
                    ft.Container(
                        content=ft.Text("1", color=COLOR_BLANCO, weight=ft.FontWeight.BOLD),
                        bgcolor=ft.Colors.BLUE_600, padding=ft.Padding(12, 6, 12, 6), border_radius=6
                    ),
                    ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, icon_color=COLOR_GRIS, icon_size=18),
                    ft.IconButton(icon=ft.Icons.LAST_PAGE, icon_color=COLOR_GRIS, icon_size=18),
                    ft.Container(
                        content=ft.Text("1", color=COLOR_GRIS),
                        border=self.crear_borde_completo(1, ft.Colors.GREY_300), padding=ft.Padding(12, 6, 12, 6), border_radius=6
                    )
                ], spacing=2)
            ],
        )

        tabla_datos = ft.Container(
            border=self.crear_borde_completo(1, ft.Colors.GREY_200), 
            border_radius=10,
            bgcolor=COLOR_BLANCO,
            padding=16,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
            expand=True,
            content=ft.Column([
                titulo_tabla,
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                tabla_cotizaciones,
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                pie_tabla
            ], spacing=10)
        )

        self.content = ft.Column([
            banner,
            ft.Container(height=15),
            barra_herramientas,
            ft.Container(height=15),
            tarjetas_resumen,
            ft.Container(height=15),
            tabla_datos
        ], spacing=0)

    def crear_borde_completo(self, ancho, color):
        borde_lado = ft.BorderSide(ancho, color)
        return ft.Border(top=borde_lado, right=borde_lado, bottom=borde_lado, left=borde_lado)

    def crear_tarjeta_resumen(self, titulo, cantidad, icono, color_icono, bg_icono, borde_negro=False):
        color_borde = COLOR_AZUL_OSCURO if borde_negro else ft.Colors.GREY_200
        ancho_borde = 1.5 if borde_negro else 1
        
        return ft.Container(
            expand=True,
            padding=15,
            border=self.crear_borde_completo(ancho_borde, color_borde), 
            border_radius=8,
            bgcolor=COLOR_BLANCO,
            content=ft.Row([
                ft.Container(
                    padding=10,
                    bgcolor=bg_icono,
                    border_radius=6,
                    content=ft.Icon(icono, color=color_icono, size=22)
                ),
                ft.Column([
                    ft.Text(titulo, size=12, color=COLOR_GRIS, weight=ft.FontWeight.W_500),
                    ft.Text(cantidad, size=18, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO)
                ], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(expand=True),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400, size=18)
            ])
        )

    def crear_badge_estado(self, estado):
        return ft.Container(
            padding=ft.Padding(10, 4, 10, 4),
            border=self.crear_borde_completo(1, ft.Colors.ORANGE_200), 
            border_radius=15,
            bgcolor=ft.Colors.ORANGE_50,
            content=ft.Row([
                ft.Icon(ft.Icons.CIRCLE, size=8, color=COLOR_NARANJA),
                ft.Text(estado, size=11, color=COLOR_NARANJA, weight=ft.FontWeight.W_600)
            ], spacing=5)
        )
        
    def abrir_nueva_cotizacion(self):
        self.parent.content = PantallaNuevaCotizacion(self.main_page, vista_anterior=self)
        self.parent.update()