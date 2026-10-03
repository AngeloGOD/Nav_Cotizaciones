import flet as ft
from fuente.utilidades.Colores import COLOR_SIDEBAR, COLOR_NARANJA, COLOR_BLANCO, COLOR_GRIS

class MenuLateral(ft.Container):
    
    def __init__(self, on_cambiar_pantalla):
        super().__init__()
        self.on_cambiar_pantalla = on_cambiar_pantalla
        self.width = 250
        self.bgcolor = COLOR_SIDEBAR
        
        
        self.padding = ft.Padding(left=20, top=20, right=20, bottom=20)
        
        self.content = ft.Column([
            ft.Text("OPL PACÍFICO SUR", color=COLOR_BLANCO, weight=ft.FontWeight.BOLD, size=20),
            ft.Divider(color=ft.Colors.WHITE_24),
            ft.Container(height=10),
            ft.Text("NAVEGACIÓN", color=COLOR_GRIS, size=12),
            
            
            self.crear_item_menu(ft.Icons.HOME, "Dashboard", "ruta_dashboard", activo=True),
            self.crear_item_menu(ft.Icons.DESCRIPTION, "Cotizaciones", "ruta_cotizaciones"),
            self.crear_item_menu(ft.Icons.PEOPLE, "Clientes", "ruta_clientes"),
            self.crear_item_menu(ft.Icons.DIRECTIONS_BOAT, "Buques", "ruta_buques"),
            self.crear_item_menu(ft.Icons.SUPPORT_AGENT, "Servicios", "ruta_servicios"),
            self.crear_item_menu(ft.Icons.INSERT_CHART, "Reportes", "ruta_reportes"),
            self.crear_item_menu(ft.Icons.SETTINGS, "Configuración", "ruta_config"),
        ], spacing=10)

    def crear_item_menu(self, icono, texto, ruta, activo=False):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=COLOR_BLANCO if activo else ft.Colors.WHITE_54),
                ft.Text(texto, color=COLOR_BLANCO if activo else ft.Colors.WHITE_54, weight=ft.FontWeight.W_500 if activo else ft.FontWeight.NORMAL)
            ]),
            bgcolor=COLOR_NARANJA if activo else ft.Colors.TRANSPARENT,
            
           
            padding=ft.Padding(left=10, top=10, right=10, bottom=10),
            border_radius=8,
            
            
            on_click=lambda e: self.on_cambiar_pantalla(ruta)
        )