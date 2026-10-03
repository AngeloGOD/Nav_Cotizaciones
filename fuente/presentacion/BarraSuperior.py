import flet as ft
from fuente.utilidades.Colores import COLOR_GRIS, COLOR_NEGRO, COLOR_BLANCO, COLOR_SIDEBAR

class BarraSuperior(ft.Container):
    def __init__(self):
        super().__init__()
        
        self.padding = ft.Padding(left=20, top=20, right=20, bottom=20)
        
        self.content = ft.Row([
            
            # --- NUEVOS BOTONES DE HERRAMIENTAS ---
            ft.Row([
                # Idioma y Tema
                ft.IconButton(icon=ft.Icons.LANGUAGE, icon_color=COLOR_GRIS, tooltip="Cambiar Idioma (ES/EN)"),
                ft.IconButton(icon=ft.Icons.DARK_MODE_OUTLINED, icon_color=COLOR_GRIS, tooltip="Modo Oscuro"),
                
                # Notificaciones de la agencia
                ft.IconButton(icon=ft.Icons.NOTIFICATIONS_OUTLINED, icon_color=COLOR_GRIS, tooltip="Alertas y Notificaciones"),
                
                ft.Container(width=10), 
                
               
                ft.IconButton(icon=ft.Icons.SETTINGS_OUTLINED, icon_color=COLOR_GRIS, tooltip="Ajustes"),
                ft.IconButton(icon=ft.Icons.HELP_OUTLINE, icon_color=COLOR_GRIS, tooltip="Ayuda"),
            ], spacing=5),
            
            ft.Container(width=20), 
            
        
            ft.Row([
                ft.Column([
                    ft.Text("José Aguilar", weight=ft.FontWeight.BOLD, color=COLOR_NEGRO),
                    ft.Text("Gerente Administrativo", size=12, color=COLOR_GRIS)
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.END),
                
                ft.Container(width=5),
                ft.CircleAvatar(content=ft.Text("JA", color=COLOR_BLANCO, weight=ft.FontWeight.BOLD), bgcolor=COLOR_SIDEBAR)
            ])
            
        ], alignment=ft.MainAxisAlignment.END) 