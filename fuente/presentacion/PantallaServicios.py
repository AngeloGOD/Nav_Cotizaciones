import flet as ft
from fuente.utilidades.Colores import COLOR_NARANJA, COLOR_BLANCO, COLOR_GRIS
from fuente.presentacion.PantallaNuevoServicio import PantallaNuevoServicio

COLOR_AZUL_OSCURO = "#0d1b2a" 
COLOR_FONDO_TABLA = "#f8f9fa"

class PantallaServicios(ft.Container):
    
    def __init__(self, main_page):
        super().__init__()
        self.main_page = main_page 
        self.expand = True
        self.padding = ft.Padding(20, 20, 20, 20)
        
        self._menu_exportacion_abierto = False
        
        banner = ft.Container(
            height=174,
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            border=self.crear_borde_completo(1, ft.Colors.GREY_200),
            content=ft.Stack([
                ft.Container(
                    expand=True,
                    image=ft.DecorationImage(src="fondo_servicios.jpg", fit="cover", alignment=ft.alignment.Alignment(1, 0))
                ),
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.Alignment(-1, 0), end=ft.alignment.Alignment(1, 0),
                        colors=[COLOR_BLANCO, COLOR_BLANCO, ft.Colors.with_opacity(0.6, COLOR_BLANCO), ft.Colors.TRANSPARENT],
                        stops=[0.0, 0.45, 0.7, 1.0]
                    )
                ),
                ft.Container(
                    padding=ft.Padding(30, 25, 30, 25),
                    content=ft.Column([
                        ft.Text("Catálogo de Servicios", size=28, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO),
                        ft.Text("Administra y configura las tarifas y tipos de cobro para la agencia.", size=14, color=COLOR_GRIS),
                    ], spacing=5)
                )
            ])
        )

        boton_nuevo_servicio = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, color=COLOR_BLANCO, size=18),
                ft.Text("Nuevo Servicio", color=COLOR_BLANCO, weight=ft.FontWeight.W_600, size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            bgcolor=COLOR_NARANJA, padding=ft.Padding(20, 5, 20, 5), border_radius=6, height=44, ink=True, 
            # 1. CAMBIO: Se conecta el botón a la función de navegación
            on_click=self.abrir_nuevo_servicio 
        )

        # --- BARRA DE BÚSQUEDA Y FILTROS ---
        barra_herramientas = ft.Row([
            ft.Container(
                expand=True,
                content=ft.TextField(hint_text="Buscar por ID, nombre o categoría...", prefix_icon=ft.Icons.SEARCH, border_color=ft.Colors.GREY_300, border_radius=6, height=44, content_padding=10, text_size=14)
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.FILTER_LIST, size=18, color=ft.Colors.BLUE_600), ft.Text("Filtros", size=14, color=ft.Colors.BLUE_600, weight=ft.FontWeight.W_500)]),
                padding=ft.Padding(15, 5, 15, 5), border=self.crear_borde_completo(1, ft.Colors.GREY_300), border_radius=6, height=44, ink=True,
                on_click=lambda e: print("Abrir filtros")
            ),
            boton_nuevo_servicio 
        ], spacing=15, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # --- TARJETAS RESUMEN ---
        tarjetas_resumen = ft.Row([
            self.crear_tarjeta_resumen("Total Servicios", "24", ft.Icons.FORMAT_LIST_BULLETED, ft.Colors.GREY_700, ft.Colors.GREY_100, borde_negro=True),
            self.crear_tarjeta_resumen("Cuota Fija", "10", ft.Icons.ATTACH_MONEY, ft.Colors.GREEN_500, ft.Colors.GREEN_50),
            self.crear_tarjeta_resumen("Factor Unitario", "8", ft.Icons.CALCULATE_OUTLINED, ft.Colors.BLUE_500, ft.Colors.BLUE_50),
            self.crear_tarjeta_resumen("Por Rangos/Días", "6", ft.Icons.LAYERS_OUTLINED, ft.Colors.PURPLE_500, ft.Colors.PURPLE_50),
        ], spacing=15)

        # =========================================================
        # COMPONENTES MANUALES CLONADOS DE CARLOS (Sin importar nada)
        # =========================================================
        self._boton_exportar = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, color=ft.Colors.BLUE_600, size=16),
                ft.Text("Exportar", color=ft.Colors.BLUE_600, weight=ft.FontWeight.W_600, size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            border=self.crear_borde_completo(1, "#C9DDF7"),
            border_radius=6, padding=ft.Padding(15, 5, 15, 5), height=44, width=150, ink=True,
            on_click=self.alternar_menu_exportacion
        )

        self._menu_exportacion = ft.Container(
            top=52, # Altura exacta de Carlos
            right=0, 
            width=280, # Ancho reducido (antes 320)
            visible=False,
            bgcolor=COLOR_BLANCO, border_radius=12, border=ft.Border.all(1, "#E3EAF2"),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            padding=ft.Padding(16, 16, 16, 16), # Márgenes más compactos
            content=ft.Column([
                # Letra reducida a size=11
                ft.Text("Elige un formato para exportar los servicios encontrados.", size=11, color=COLOR_GRIS),
                ft.Container(height=2),
                ft.Container(
                    ink=True, padding=8, border_radius=8, on_click=lambda e: self.cerrar_menu_exportacion(),
                    content=ft.Row([
                        # Icono y fondo más pequeños
                        ft.Container(padding=8, bgcolor="#FDECEC", border_radius=8, content=ft.Icon(ft.Icons.PICTURE_AS_PDF, color=ft.Colors.RED_600, size=18)),
                        ft.Column([
                            ft.Text("Exportar a PDF", weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO, size=13),
                            ft.Text("Genera un archivo PDF en el directorio de servicios.", size=11, color=COLOR_GRIS)
                        ], spacing=2, expand=True)
                    ])
                ),
                ft.Container(
                    ink=True, padding=8, border_radius=8, on_click=lambda e: self.cerrar_menu_exportacion(),
                    content=ft.Row([
                        ft.Container(padding=8, bgcolor="#EAF7EF", border_radius=8, content=ft.Icon(ft.Icons.GRID_ON, color=ft.Colors.GREEN_600, size=18)),
                        ft.Column([
                            ft.Text("Exportar a Excel", weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO, size=13),
                            ft.Text("Descarga un archivo Excel con los datos de servicios.", size=11, color=COLOR_GRIS)
                        ], spacing=2, expand=True)
                    ])
                )
            ], spacing=4)
        )
        # =========================================================

        # --- TABLA ---
        titulo_tabla = ft.Row(
            spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(content=ft.Icon(ft.Icons.LOCAL_OFFER_OUTLINED, color=COLOR_BLANCO, size=24), bgcolor=COLOR_NARANJA, border_radius=10, padding=10),
                ft.Column(expand=True, spacing=2, controls=[
                    ft.Text("Servicios Activos", size=19, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO),
                    ft.Text("Configuración de tarifas base", size=14, color=COLOR_GRIS),
                ]),
                self._boton_exportar # Se coloca el botón manual
            ],
        )

        tabla_servicios = ft.ListView(
            expand=True,
            controls=[
                ft.DataTable(
                    heading_row_color=COLOR_FONDO_TABLA, heading_row_height=45, data_row_min_height=60, data_row_max_height=80,
                    vertical_lines=ft.BorderSide(1, ft.Colors.GREY_200), border=self.crear_borde_completo(1, ft.Colors.GREY_200),
                    columns=[
                        ft.DataColumn(ft.Text("ID", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Nombre del Servicio", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Categoría / Unidad", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Tipo de Cobro", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Tasa IVA", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                        ft.DataColumn(ft.Text("Acciones", size=14, color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)),
                    ],
                    rows=[
                        ft.DataRow(cells=[
                            ft.DataCell(ft.Text("SRV-001", color=ft.Colors.BLUE_600, size=13)),
                            ft.DataCell(ft.Text("Lanchaje de Buques", weight=ft.FontWeight.W_600, size=13)),
                            ft.DataCell(ft.Text("Lanchaje / Servicio", size=13, color=COLOR_GRIS)),
                            ft.DataCell(self.crear_badge_tipo_cobro("Factor Unitario", ft.Colors.BLUE_600, ft.Colors.BLUE_50)),
                            ft.DataCell(ft.Text("16.0%", size=13, color=COLOR_GRIS)),
                            ft.DataCell(ft.Row([ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color=ft.Colors.BLUE_600, icon_size=18), ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, icon_size=18)]))
                        ])
                    ]
                )
            ]
        )

        # --- ENSAMBLAJE FINAL CON STACK ---
        controles_tabla = ft.Column(
            expand=True, spacing=10,
            controls=[
                titulo_tabla,
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                tabla_servicios,
            ]
        )
        
        contenido_con_menu = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE, 
            controls=[
                controles_tabla,
                self._menu_exportacion 
            ]
        )

        tabla_datos = ft.Container(
            border=self.crear_borde_completo(1, ft.Colors.GREY_200), border_radius=10, bgcolor=COLOR_BLANCO, padding=16,
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=5, color=ft.Colors.with_opacity(0.05, ft.Colors.BLACK), offset=ft.Offset(0, 2)),
            expand=True,
            content=contenido_con_menu
        )

        self.content = ft.Column([
            banner, ft.Container(height=15), barra_herramientas, ft.Container(height=15),
            tarjetas_resumen, ft.Container(height=15), tabla_datos
        ], spacing=0)

    # =========================================================
    # 2. CAMBIO: Función para hacer el cambio de pantalla
    # =========================================================
    def abrir_nuevo_servicio(self, e):
        # Guardar la vista de la tabla actual en memoria
        self.vista_catalogo = self.content 
        
        # Cargar el nuevo formulario pasándole la referencia actual (self)
        self.content = PantallaNuevoServicio(vista_anterior=self)
        self.update()

    # --- LÓGICA DE EVENTOS ---
    def alternar_menu_exportacion(self, e=None):
        self._menu_exportacion_abierto = not self._menu_exportacion_abierto
        self._menu_exportacion.visible = self._menu_exportacion_abierto
        self._menu_exportacion.update()

    def cerrar_menu_exportacion(self, e=None):
        self._menu_exportacion_abierto = False
        self._menu_exportacion.visible = False
        self._menu_exportacion.update()

    # --- AYUDAS VISUALES ---
    def crear_borde_completo(self, ancho, color):
        return ft.Border(top=ft.BorderSide(ancho, color), right=ft.BorderSide(ancho, color), bottom=ft.BorderSide(ancho, color), left=ft.BorderSide(ancho, color))

    def crear_tarjeta_resumen(self, titulo, cantidad, icono, color_icono, bg_icono, borde_negro=False):
        color_borde = COLOR_AZUL_OSCURO if borde_negro else ft.Colors.GREY_200
        ancho_borde = 1.5 if borde_negro else 1
        return ft.Container(
            expand=True, padding=15, border=self.crear_borde_completo(ancho_borde, color_borde), border_radius=8, bgcolor=COLOR_BLANCO,
            content=ft.Row([
                ft.Container(padding=10, bgcolor=bg_icono, border_radius=6, content=ft.Icon(icono, color=color_icono, size=22)),
                ft.Column([ft.Text(titulo, size=12, color=COLOR_GRIS, weight=ft.FontWeight.W_500), ft.Text(cantidad, size=18, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO)], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(expand=True), ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400, size=18)
            ])
        )

    def crear_badge_tipo_cobro(self, texto, color_borde_texto, color_fondo):
        return ft.Container(
            padding=ft.Padding(10, 4, 10, 4), border=self.crear_borde_completo(1, ft.Colors.with_opacity(0.3, color_borde_texto)), border_radius=15, bgcolor=color_fondo,
            content=ft.Row([ft.Icon(ft.Icons.CIRCLE, size=8, color=color_borde_texto), ft.Text(texto, size=11, color=color_borde_texto, weight=ft.FontWeight.W_600)], spacing=5)
        )