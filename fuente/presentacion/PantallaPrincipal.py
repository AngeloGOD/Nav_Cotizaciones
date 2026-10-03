import flet as ft

from fuente.presentacion.MenuLateral import MenuLateral
from fuente.presentacion.BarraSuperior import BarraSuperior
from fuente.presentacion.dashboard import Dashboard
from fuente.presentacion.PantallaClientes import PantallaClientes
from fuente.utilidades.Colores import COLOR_FONDO

class PantallaPrincipal(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__()
        self.main_page = page 
        self.expand = True
        self.bgcolor = COLOR_FONDO
        self.padding = 0

        
        vista_inicial = ft.Column(
            controls=[BarraSuperior(), Dashboard()],
            expand=True,
            spacing=0
        )

        
        self.contenido_dinamico = ft.Container(
            expand=True,
            content=vista_inicial
        )

        
        self.menu_lateral = MenuLateral(on_cambiar_pantalla=self.cambiar_pantalla)

       
        self.content = ft.Row(
            controls=[
                self.menu_lateral,
                self.contenido_dinamico
            ],
            expand=True,
            spacing=0
        )

    
    def cambiar_pantalla(self, ruta):
        if ruta == "ruta_dashboard":
            self.contenido_dinamico.content = ft.Column(
                controls=[BarraSuperior(), Dashboard()],
                expand=True,
                spacing=0
            )

        elif ruta == "ruta_clientes":
            self.contenido_dinamico.content = ft.Column(
                controls=[BarraSuperior(), PantallaClientes()],
                expand=True,
                spacing=0
            )

        self.contenido_dinamico.update()