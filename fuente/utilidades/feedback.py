import flet as ft
from .Colores import *


def dialogo_confirmacion(
    page,
    titulo,
    mensaje,
    on_confirmar,
    texto_confirmar="Confirmar",
    texto_cancelar="Cancelar",
    color_confirmar=COLOR_ROJO,
):
    def cancelar(e):
        page.pop_dialog()

    def confirmar(e):
        page.pop_dialog()
        on_confirmar()

    return ft.AlertDialog(
        modal=True,
        bgcolor=COLOR_BLANCO,
        shape=ft.RoundedRectangleBorder(radius=12),
        title=ft.Text(
            titulo,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BANNER,
        ),
        content=ft.Text(mensaje, color=COLOR_NEGRO),
        actions=[
            ft.TextButton(texto_cancelar, on_click=cancelar),
            ft.TextButton(
                texto_confirmar,
                on_click=confirmar,
                style=ft.ButtonStyle(color=color_confirmar),
            ),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )


def mostrar_notificacion(page, mensaje, color=COLOR_VERDE):
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(mensaje, color=COLOR_BLANCO),
            bgcolor=color,
        )
    )
    page.update()
