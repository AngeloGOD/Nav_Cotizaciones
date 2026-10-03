import flet as ft
from fuente.presentacion.PantallaPrincipal import PantallaPrincipal
from fuente.utilidades.Colores import *

def main(page: ft.Page):
    page.bgcolor = COLOR_FONDO
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    expand=True,
                    bgcolor=COLOR_FONDO,
                    content=PantallaPrincipal(page),
                )
            ],
            expand=True,
            spacing=0,
        )
    )

if __name__ == "__main__":
    ft.run(main)