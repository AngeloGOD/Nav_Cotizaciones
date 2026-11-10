import flet as ft
from .Colores import *


class Herramientas:
    @staticmethod
    def limpiar_controles(controles, valores_iniciales=None):
        controles = list(controles)
        if valores_iniciales is not None and len(valores_iniciales) != len(controles):
            raise ValueError("Debe indicarse un valor inicial por cada control.")

        for indice, control in enumerate(controles):
            if isinstance(control, ft.TextField):
                valor = ""
            elif isinstance(control, ft.Dropdown):
                valor = None
            elif isinstance(control, (ft.Checkbox, ft.Switch)):
                valor = False
            elif isinstance(control, ft.DatePicker):
                valor = None
            else:
                raise TypeError(
                    f"No se puede limpiar el control {type(control).__name__}."
                )

            if valores_iniciales is not None:
                valor = valores_iniciales[indice]
            control.value = valor


def campo(
    hint,
    icono,
    expand=False,
    multiline=False,
    min_lines=None,
    max_lines=None,
):
    return ft.TextField(
        expand=expand,
        hint_text=hint,
        prefix_icon=icono,
        multiline=multiline,
        min_lines=min_lines,
        max_lines=max_lines,
        border=ft.InputBorder.OUTLINE,
        border_color=COLOR_GRIS_CLARO,
        focused_border_color=COLOR_NARANJA,
        border_radius=9,
        text_size=14,
        content_padding=14,
    )


def selector_catalogo(
    texto,
    icono,
    opciones,
    on_change=None,
    width=None,
):
    selector = ft.Dropdown(
        label=texto,
        options=[
            ft.dropdown.Option(
                key=valor,
                text=etiqueta,
            )
            for valor, etiqueta in opciones
        ],
    )

    selector.on_change = on_change

    return ft.Container(
        width=width,
        content=ft.Row(
            spacing=6,
            controls=[
                ft.Icon(
                    icono,
                    color=COLOR_AZUL,
                    size=20,
                ),
                ft.Container(
                    content=selector,
                    expand=True,
                ),
            ],
        ),
    )


def barra_busqueda(
    hint="Buscar...",
    on_change=None,
    expand=True,
    width=None,
):
    return ft.TextField(
        hint_text=hint,
        prefix_icon=ft.Icons.SEARCH,
        expand=expand,
        width=width,
        border=ft.InputBorder.OUTLINE,
        border_color=COLOR_GRIS_CLARO,
        focused_border_color=COLOR_AZUL,
        border_radius=8,
        text_size=14,
        content_padding=12,
        on_change=on_change,
    )


def boton(
    texto=None,
    on_click=None,
    icono=None,
    tipo="principal",
    width=None,
    height=None,
    tooltip=None,
    color=None,
    border_color=None,
):
    if tipo == "accion":
        return ft.IconButton(
            icon=icono,
            tooltip=tooltip or texto,
            icon_color=color or COLOR_AZUL,
            icon_size=19,
            width=width or 38,
            height=height or 38,
            padding=ft.Padding(2, 2, 2, 2),
            on_click=on_click,
        )

    if tipo == "secundario":
        return ft.OutlinedButton(
            width=width,
            height=height,
            content=ft.Row(
                tight=True,
                spacing=7,
                controls=[
                    ft.Icon(
                        icono,
                        size=18,
                        color=color or COLOR_AZUL,
                    ),
                    ft.Text(
                        texto,
                        size=14,
                        color=color or COLOR_AZUL,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            ),
            style=ft.ButtonStyle(
                color=color or COLOR_AZUL,
                side=ft.BorderSide(1, border_color or COLOR_GRIS_CLARO),
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding(14, 0, 14, 0),
            ),
            on_click=on_click,
        )

    return ft.FilledButton(
        width=width,
        height=height,
        content=ft.Row(
            tight=True,
            spacing=7,
            controls=[
                ft.Icon(
                    icono or ft.Icons.ADD,
                    size=19,
                    color=COLOR_BLANCO,
                ),
                ft.Text(
                    texto,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_BLANCO,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
        style=ft.ButtonStyle(
            bgcolor=color or COLOR_NARANJA,
            color=COLOR_BLANCO,
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(18, 0, 18, 0),
        ),
        on_click=on_click,
    )


def boton_exportacion(texto, on_click, width=None, height=44):
    etiqueta = (
        texto
        if isinstance(texto, ft.Text)
        else ft.Text(texto, size=14, color=COLOR_AZUL, max_lines=1)
    )
    etiqueta.max_lines = 1
    etiqueta.overflow = ft.TextOverflow.ELLIPSIS
    return ft.OutlinedButton(
        width=width,
        height=height,
        content=ft.Row(
            tight=True,
            spacing=7,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Icon(
                    ft.Icons.DOWNLOAD_OUTLINED,
                    size=18,
                    color=COLOR_AZUL,
                ),
                etiqueta,
            ],
        ),
        style=ft.ButtonStyle(
            color=COLOR_AZUL,
            side=ft.BorderSide(1, "#C9DDF7"),
            shape=ft.RoundedRectangleBorder(radius=9),
            padding=ft.Padding(14, 0, 14, 0),
        ),
        on_click=on_click,
    )


def boton_icono_enmarcado(
    icono,
    on_click=None,
    tooltip=None,
    color=None,
    border_color=None,
    size=40,
):
    """Botón de icono con borde suave para acciones de tablas y tarjetas."""
    color = color or COLOR_AZUL
    return ft.Container(
        width=size,
        height=size,
        alignment=ft.Alignment(0, 0),
        bgcolor=COLOR_BLANCO,
        border=ft.Border.all(1, border_color or "#CFE0F5"),
        border_radius=10,
        content=ft.IconButton(
            icon=icono,
            tooltip=tooltip,
            icon_color=color,
            icon_size=19,
            width=size,
            height=size,
            on_click=on_click,
        ),
    )


def boton_vista(icono, tooltip, seleccionado=False, on_click=None):
    """Botón para alternar entre cuadrícula y lista."""

    return ft.Container(
        width=44,
        height=44,
        alignment=ft.Alignment(0, 0),
        bgcolor=COLOR_AZUL if seleccionado else COLOR_BLANCO,
        border=ft.Border.all(
            1,
            COLOR_AZUL if seleccionado else COLOR_GRIS_CLARO,
        ),
        border_radius=9,
        tooltip=tooltip,
        ink=True,
        on_click=on_click,
        content=ft.Icon(
            icono,
            size=20,
            color=COLOR_BLANCO if seleccionado else COLOR_AZUL,
        ),
    )
