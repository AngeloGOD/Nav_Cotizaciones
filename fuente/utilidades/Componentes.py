import flet as ft
from .Colores import *

def sombra_suave():
    return ft.BoxShadow(
        blur_radius=30,
        color="black12",
        offset=ft.Offset(0, 10),
    )

def card(content, padding=16, bgcolor=COLOR_BLANCO, border_color=COLOR_GRIS_CLARO, radius=10, shadow=None, expand=False):
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        border=ft.Border.all(1, border_color),
        border_radius=radius,
        padding=padding,
        shadow=shadow,
        expand=expand,
    )


def barra_busqueda(hint="Buscar...", on_change=None, expand=True, width=None):
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


def boton_filtros(texto="Filtros", on_click=None, icono=ft.Icons.TUNE):
    return ft.OutlinedButton(
        content=ft.Row(
            tight=True,
            spacing=7,
            controls=[
                ft.Icon(icono, size=17, color=COLOR_AZUL),
                ft.Text(texto, size=14, color=COLOR_AZUL),
            ],
        ),
        style=ft.ButtonStyle(
            color=COLOR_AZUL,
            side=ft.BorderSide(1, COLOR_GRIS_CLARO),
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(left=14, right=14, top=13, bottom=13),
        ),
        on_click=on_click,
    )


def boton_exportar(texto="Exportar", on_click=None, icono=ft.Icons.DOWNLOAD_OUTLINED):
    return ft.OutlinedButton(
        content=ft.Row(
            tight=True,
            spacing=6,
            controls=[
                ft.Icon(icono, size=17, color=COLOR_AZUL),
                ft.Text(texto, size=14, color=COLOR_AZUL),
            ],
        ),
        style=ft.ButtonStyle(
            color=COLOR_AZUL,
            side=ft.BorderSide(1, COLOR_GRIS_CLARO),
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding(left=14, right=14, top=12, bottom=12),
        ),
        on_click=on_click,
    )


def boton_accion(icono, tooltip, color=COLOR_AZUL, on_click=None):
    return ft.IconButton(
        icon=icono,
        tooltip=tooltip,
        icon_color=color,
        icon_size=19,
        width=38,
        height=38,
        padding=ft.Padding(left=2, right=2, top=2, bottom=2),
        on_click=on_click,
    )


def tabla(
    columnas,
    filas,
    column_spacing=10,
    horizontal_margin=6,
    heading_row_height=44,
    data_row_min_height=60,
    data_row_max_height=float("inf"),
):
    return ft.DataTable(
        expand=True,
        column_spacing=column_spacing,
        horizontal_margin=horizontal_margin,
        heading_row_height=heading_row_height,
        data_row_min_height=data_row_min_height,
        data_row_max_height=data_row_max_height,
        heading_row_color=COLOR_FONDO,
        border=ft.Border.all(1, COLOR_GRIS_CLARO),
        vertical_lines=ft.BorderSide(1, COLOR_GRIS_CLARO),
        horizontal_lines=ft.BorderSide(1, COLOR_GRIS_CLARO),
        columns=[
            ft.DataColumn(
                ft.Container(
                    width=ancho,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        texto,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_NEGRO,
                        text_align=ft.TextAlign.CENTER,
                    ),
                )
            )
            for texto, ancho in columnas
        ],
        rows=filas,
    )


def paginacion(total_registros, registros_por_pagina, pagina_actual, on_change):
    total_paginas = max(
        1,
        (total_registros // registros_por_pagina)
        + (1 if total_registros % registros_por_pagina else 0),
    )

    def cambiar_pagina(pagina):
        if 1 <= pagina <= total_paginas:
            on_change(pagina)

    botones = [
        ft.IconButton(
            icon=ft.Icons.FIRST_PAGE,
            icon_color=COLOR_GRIS,
            tooltip="Primera página",
            on_click=lambda e: cambiar_pagina(1),
        ),
        ft.IconButton(
            icon=ft.Icons.CHEVRON_LEFT,
            icon_color=COLOR_GRIS,
            tooltip="Página anterior",
            on_click=lambda e: cambiar_pagina(pagina_actual - 1),
        ),
    ]

    if total_paginas <= 7:
        paginas = list(range(1, total_paginas + 1))
    else:
        paginas = [1]

        if pagina_actual > 3:
            paginas.append("...")

        inicio = max(2, pagina_actual - 2)
        fin = min(total_paginas - 1, pagina_actual + 2)

        for pagina in range(inicio, fin + 1):
            paginas.append(pagina)

        if pagina_actual < total_paginas - 2:
            paginas.append("...")

        paginas.append(total_paginas)

    for pagina in paginas:
        if pagina == "...":
            botones.append(
                ft.Text(
                    "...",
                    size=14,
                    color=COLOR_GRIS,
                )
            )
        else:
            botones.append(
                ft.TextButton(
                    content=ft.Text(
                        str(pagina),
                        size=14,
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_AZUL if pagina == pagina_actual else "transparent",
                        color=COLOR_BLANCO if pagina == pagina_actual else COLOR_AZUL,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda e, pagina=pagina: cambiar_pagina(pagina),
                )
            )

    botones.extend([
        ft.IconButton(
            icon=ft.Icons.CHEVRON_RIGHT,
            icon_color=COLOR_GRIS,
            tooltip="Página siguiente",
            on_click=lambda e: cambiar_pagina(pagina_actual + 1),
        ),
        ft.IconButton(
            icon=ft.Icons.LAST_PAGE,
            icon_color=COLOR_GRIS,
            tooltip="Última página",
            on_click=lambda e: cambiar_pagina(total_paginas),
        ),
    ])

    entrada = ft.TextField(
        width=55,
        height=35,
        value=str(pagina_actual),
        text_align=ft.TextAlign.CENTER,
        content_padding=5,
        border_radius=8,
        border_color=COLOR_GRIS_CLARO,
        focused_border_color=COLOR_AZUL,
        color=COLOR_GRIS,
        text_size=13,
        on_submit=lambda e: cambiar_pagina(
            int(e.control.value)
            if e.control.value.isdigit()
            else pagina_actual
        ),
    )

    botones.append(entrada)

    return ft.Row(
        controls=botones,
        spacing=5,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )