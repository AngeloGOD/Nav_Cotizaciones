
import flet as ft
from .Colores import *
import flet_datatable2 as ftd


def sombra_suave():
    return ft.BoxShadow(
        blur_radius=30,
        color="black12",
        offset=ft.Offset(0, 10),
    )


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


def boton(
    texto=None,
    on_click=None,
    icono=None,
    tipo="principal",
    width=None,
    height=None,
    tooltip=None,
    color=None,
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
                    ),
                ],
            ),
            style=ft.ButtonStyle(
                color=color or COLOR_AZUL,
                side=ft.BorderSide(1, COLOR_GRIS_CLARO),
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


def banner_imagen_desvanecida(
    src,
    content=None,
    altura=150,
):
    imagen = ft.Container(
        expand=True,
        image=ft.DecorationImage(
            src=src,
            fit=ft.BoxFit.COVER,
            alignment=ft.Alignment(1, 0),
        ),
    )

    imagen = ft.ShaderMask(
        content=imagen,
        blend_mode=ft.BlendMode.DST_IN,
        border_radius=12,
        shader=ft.LinearGradient(
            begin=ft.Alignment(-1, 0),
            end=ft.Alignment(1, 0),
            colors=[
                ft.Colors.TRANSPARENT,
                ft.Colors.WHITE,
                ft.Colors.WHITE,
                ft.Colors.TRANSPARENT,
            ],
            stops=[0.0, 0.01, 0.99, 1.0],
        ),
    )

    imagen = ft.ShaderMask(
        content=imagen,
        blend_mode=ft.BlendMode.DST_IN,
        border_radius=12,
        shader=ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=[
                ft.Colors.TRANSPARENT,
                ft.Colors.WHITE,
                ft.Colors.WHITE,
                ft.Colors.TRANSPARENT,
            ],
            stops=[0.0, 0.01, 0.99, 1.0],
        ),
    )

    return ft.Container(
        height=altura,
        bgcolor=COLOR_BLANCO,
        border_radius=12,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=ft.Stack(
            expand=True,
            controls=[
                imagen,
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1, 0),
                        end=ft.Alignment(1, 0),
                        colors=[
                            ft.Colors.WHITE,
                            ft.Colors.WHITE_70,
                            ft.Colors.WHITE_54,
                            ft.Colors.TRANSPARENT,
                        ],
                        stops=[0.0, 0.38, 0.65, 1.0],
                    ),
                ),
                ft.Container(
                    expand=True,
                    content=content,
                ),
            ],
        ),
    )


def card(
    content,
    padding=16,
    bgcolor=COLOR_BLANCO,
    border_color=COLOR_GRIS_CLARO,
    radius=10,
    shadow=None,
    expand=False,
):
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        border=ft.Border.all(1, border_color),
        border_radius=radius,
        padding=padding,
        shadow=shadow,
        expand=expand,
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


def tabla(
    columnas,
    filas,
    column_spacing=10,
    horizontal_margin=6,
    heading_row_height=44,
    data_row_min_height=60,
    data_row_max_height=float("inf"),
    columnas_flexibles=False,
):
    columnas_tabla = []

    for texto, ancho in columnas:
        encabezado = ft.Container(
            width=None if columnas_flexibles else ancho,
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                texto,
                size=14,
                weight=ft.FontWeight.BOLD,
                color=COLOR_NEGRO,
                text_align=ft.TextAlign.CENTER,
            ),
        )

        if columnas_flexibles:
            # Las columnas grandes reciben más espacio.
            if ancho <= 140:
                tamano = ftd.DataColumnSize.S
            elif ancho <= 200:
                tamano = ftd.DataColumnSize.M
            else:
                tamano = ftd.DataColumnSize.L

            columna = ftd.DataColumn2(
                label=encabezado,
                size=tamano,
            )
        else:
            columna = ftd.DataColumn2(
                label=encabezado,
                fixed_width=ancho,
            )

        columnas_tabla.append(columna)

    return ftd.DataTable2(
        expand=True,
        column_spacing=column_spacing,
        horizontal_margin=horizontal_margin,
        heading_row_height=heading_row_height,
        data_row_height=data_row_min_height,
        heading_row_color=COLOR_FONDO,
        border=ft.Border.all(1, COLOR_GRIS_CLARO),
        vertical_lines=ft.BorderSide(1, COLOR_GRIS_CLARO),
        horizontal_lines=ft.BorderSide(1, COLOR_GRIS_CLARO),
        columns=columnas_tabla,
        rows=filas,
    )


def paginacion(
    total_registros,
    registros_por_pagina,
    pagina_actual,
    on_change,
):
    total_paginas = max(
        1,
        (total_registros // registros_por_pagina)
        + bool(total_registros % registros_por_pagina),
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

        paginas.extend(
            range(
                max(2, pagina_actual - 2),
                min(total_paginas - 1, pagina_actual + 2) + 1,
            )
        )

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
                        bgcolor=(
                            COLOR_AZUL
                            if pagina == pagina_actual
                            else "transparent"
                        ),
                        color=(
                            COLOR_BLANCO
                            if pagina == pagina_actual
                            else COLOR_AZUL
                        ),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda e, p=pagina: cambiar_pagina(p),
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

    botones.append(
        ft.TextField(
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
    )

    return ft.Row(
        controls=botones,
        spacing=5,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )