import flet as ft
from fuente.utilidades.Colores import COLOR_SIDEBAR, COLOR_NARANJA, COLOR_BLANCO, COLOR_GRIS

class MenuLateral(ft.Container):
    
    def __init__(self, on_cambiar_pantalla):
        super().__init__()
        self.on_cambiar_pantalla = on_cambiar_pantalla
        self.width = 250
        self.bgcolor = COLOR_SIDEBAR
        
        self.image = ft.DecorationImage(
            src="fondo_menulateral.jpg",
            fit="contain",
            alignment=ft.alignment.Alignment(0, 1),
            opacity=0.3
        )
        
        self.padding = ft.Padding(left=20, top=20, right=20, bottom=20)
        
        self.content = ft.Column([
            ft.Container(
                content=ft.Image(src="logo_opl.png", width=190, fit="contain"),
                margin=ft.Margin(left=5, top=0, right=0, bottom=15)
            ),
            ft.Container(height=10),
            
            self.crear_item_menu(ft.Icons.HOME_OUTLINED, "Inicio", "ruta_dashboard", activo=True),
            self.crear_item_menu(ft.Icons.DESCRIPTION_OUTLINED, "Cotizaciones", "ruta_cotizaciones"),
            self.crear_item_menu(ft.Icons.PEOPLE_OUTLINE, "Clientes", "ruta_clientes"),
            self.crear_item_menu(ft.Icons.DIRECTIONS_BOAT_OUTLINED, "Buques", "ruta_buques"),
            self.crear_item_menu(ft.Icons.INVENTORY_2_OUTLINED, "Servicios", "ruta_servicios"),
            self.crear_item_menu(ft.Icons.INSERT_CHART_OUTLINED, "Reportes", "ruta_reportes"),
            self.crear_item_menu(ft.Icons.SETTINGS_OUTLINED, "Configuración", "ruta_config"),
            
            ft.Container(expand=True),
            ft.Text("Conectamos puertos, impulsamos oportunidades.", color=ft.Colors.WHITE_54, size=10)
        ], spacing=10)

    def crear_item_menu(self, icono, texto, ruta, activo=False):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=COLOR_BLANCO if activo else ft.Colors.WHITE_54, size=20),
                ft.Text(texto, color=COLOR_BLANCO if activo else ft.Colors.WHITE_54, weight=ft.FontWeight.W_500 if activo else ft.FontWeight.NORMAL)
            ]),
            bgcolor=COLOR_NARANJA if activo else ft.Colors.TRANSPARENT,
            padding=ft.Padding(left=15, top=10, right=15, bottom=10),
            border_radius=8,
            on_click=lambda e: self.on_cambiar_pantalla(ruta)
        )