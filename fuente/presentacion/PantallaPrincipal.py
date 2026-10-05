import flet as ft

from fuente.presentacion.MenuLateral import MenuLateral
from fuente.presentacion.BarraSuperior import BarraSuperior
from fuente.presentacion.dashboard import dashboard
from fuente.presentacion.PantallaClientes import PantallaClientes
from fuente.utilidades.Colores import COLOR_FONDO


class PantallaPrincipal(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
            padding=0,
        )

        self.main_page = page

        self.content_area = ft.Container(
            expand=True,
            content=dashboard(),
        )

        self.menu_lateral = MenuLateral(
            on_cambiar_pantalla=self.cambiar_pantalla
        )

        self.content = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                self.menu_lateral,
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        BarraSuperior(),
                        self.content_area,
                    ],
                ),
            ],
        )

    def cambiar_pantalla(self, ruta):
        if ruta == "ruta_dashboard":
            self.content_area.content = dashboard()

        elif ruta == "ruta_clientes":
            self.content_area.content = PantallaClientes(
                self.main_page
            )

        if self.page is not None:
            self.content_area.update()