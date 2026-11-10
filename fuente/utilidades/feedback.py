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


def crear_feedback_dialogo(page=None):
    feedback = ft.Container(
        visible=False,
        padding=ft.Padding(10, 8, 8, 8),
        border_radius=9,
    )
    feedback.content = ft.Row(
        spacing=8,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        controls=[
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE, size=18),
            ft.Text("", size=12, expand=True, selectable=True),
            ft.IconButton(
                icon=ft.Icons.CLOSE,
                icon_size=15,
                tooltip="Cerrar mensaje",
                on_click=lambda e: ocultar_feedback_dialogo(feedback, page),
                width=28,
                height=28,
            ),
        ],
    )
    return feedback


def mostrar_feedback_dialogo(feedback, mensaje, color=COLOR_VERDE, page=None):
    es_exito = color == COLOR_VERDE
    icono, texto, _ = feedback.content.controls
    texto.value = mensaje
    texto.color = color
    icono.icon = (
        ft.Icons.CHECK_CIRCLE_OUTLINE if es_exito else ft.Icons.ERROR_OUTLINE
    )
    icono.color = color
    feedback.bgcolor = "#EAF7EF" if es_exito else "#FDECEC"
    feedback.border = ft.Border.all(1, color)
    feedback.visible = True
    if page is not None:
        page.update()


def ocultar_feedback_dialogo(feedback, page=None):
    feedback.visible = False
    if page is not None:
        page.update()


def validar_registros_exportacion(page, registros, entidad):
    if registros:
        return True
    mostrar_notificacion(
        page,
        f"No hay {entidad} para exportar con los criterios seleccionados.",
        COLOR_ROJO,
    )
    return False
