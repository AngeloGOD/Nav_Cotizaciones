import flet as ft
import flet_datatable2 as ftd
from .Colores import *


def sombra_suave():
    return ft.BoxShadow(
        blur_radius=30,
        color="black12",
        offset=ft.Offset(0, 10),
    )


def agregar_panel_flotante(contenedor, panel):
    if panel not in contenedor.controls:
        contenedor.controls.append(panel)


def quitar_panel_flotante(contenedor, panel):
    if panel in contenedor.controls:
        contenedor.controls.remove(panel)


def estado_vacio(icono, titulo, descripcion):
    return ft.Container(
        expand=True,
        alignment=ft.Alignment(0, 0),
        content=ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=8,
            controls=[
                ft.Icon(icono, size=44, color=COLOR_GRIS),
                ft.Text(
                    titulo,
                    size=17,
                    font_family="Roboto",
                    weight=ft.FontWeight.W_600,
                    color=COLOR_BANNER,
                    text_align=ft.TextAlign.CENTER,
                ),
                ft.Text(
                    descripcion,
                    size=13,
                    font_family="Roboto",
                    color=COLOR_GRIS,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
        ),
    )


def menu_exportacion(
    descripcion,
    on_pdf,
    on_excel,
    descripcion_pdf="Genera un archivo PDF para guardar o compartir.",
    descripcion_excel="Descarga una hoja de cálculo con los datos.",
    top=52,
    right=0,
    width=280,
):
    texto_descripcion = (
        descripcion
        if isinstance(descripcion, ft.Text)
        else ft.Text(descripcion, size=11, color=COLOR_GRIS)
    )

    def opcion(icono, color, fondo, texto, detalle, on_click):
        return ft.Container(
            padding=ft.Padding(10, 8, 10, 8),
            border_radius=9,
            ink=True,
            on_click=on_click,
            content=ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=32,
                        height=32,
                        border_radius=7,
                        bgcolor=fondo,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(icono, color=color, size=19),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                texto,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Text(
                                detalle,
                                size=10,
                                color=COLOR_GRIS,
                                max_lines=2,
                            ),
                        ],
                    ),
                ],
            ),
        )

    return ft.Container(
        top=top,
        right=right,
        width=width,
        bgcolor=COLOR_BLANCO,
        border=ft.Border.all(1, "#DCEAF8"),
        border_radius=12,
        shadow=ft.BoxShadow(
            blur_radius=22,
            color="#263D5A30",
            offset=ft.Offset(0, 7),
        ),
        padding=ft.Padding(7, 7, 7, 7),
        on_click=lambda e: None,
        content=ft.Column(
            tight=True,
            spacing=1,
            controls=[
                ft.Container(
                    padding=ft.Padding(9, 4, 9, 6),
                    content=texto_descripcion,
                ),
                opcion(
                    ft.Icons.PICTURE_AS_PDF,
                    "#E53935",
                    "#FDECEC",
                    "Exportar a PDF",
                    descripcion_pdf,
                    on_pdf,
                ),
                opcion(
                    ft.Icons.GRID_ON,
                    "#168A59",
                    "#E5F4EB",
                    "Exportar a Excel",
                    descripcion_excel,
                    on_excel,
                ),
            ],
        ),
    )


def banner_imagen_desvanecida(
    src,
    content=None,
    altura=150,
    shadow=None,
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
        shadow=shadow,
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


def tarjeta_indicador(
    titulo,
    valor,
    descripcion,
    icono,
    color,
    fondo,
    borde,
    complemento=None,
    tooltip=None,
):
    controles = [
        ft.Container(
            width=48,
            height=48,
            alignment=ft.Alignment(0, 0),
            bgcolor=fondo,
            border_radius=24,
            content=ft.Icon(icono, size=25, color=color),
        ),
        ft.Column(
            expand=True,
            spacing=2,
            controls=[
                ft.Text(
                    titulo,
                    size=13,
                    color=COLOR_NEGRO,
                    weight=ft.FontWeight.W_600,
                    tooltip=tooltip,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    valor,
                    size=22,
                    color=COLOR_BANNER,
                    weight=ft.FontWeight.BOLD,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
                ft.Text(
                    descripcion,
                    size=10,
                    color=COLOR_GRIS,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
    ]
    if complemento is not None:
        controles.append(complemento)

    return card(
        ft.Row(
            spacing=10,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=controles,
        ),
        padding=12,
        border_color=borde,
        radius=12,
        shadow=sombra_suave(),
        expand=True,
    )


def seccion_opciones_filtro(
    titulo,
    opciones,
    seleccionados=None,
    on_change=None,
    icono=None,
):
    seleccionados = seleccionados or set()
    checkboxes = {}
    filas_opciones = []
    for valor, etiqueta in opciones:
        checkbox = ft.Checkbox(
            value=valor in seleccionados,
            active_color=COLOR_AZUL,
            check_color=COLOR_BLANCO,
            border_side=ft.BorderSide(1.5, "#7186A0"),
            shape=ft.RoundedRectangleBorder(radius=3),
            scale=1.2,
            width=30,
            height=32,
            on_change=on_change,
        )
        checkboxes[valor] = checkbox
        filas_opciones.append(
            ft.Row(
                tight=True,
                spacing=3,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    checkbox,
                    ft.Text(etiqueta, size=13, color="#415A77"),
                ],
            )
        )

    return (
        ft.Container(
            padding=ft.Padding(14, 8, 14, 6),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        spacing=7,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=(
                            [
                                ft.Icon(icono, size=16, color=COLOR_BANNER),
                                ft.Text(
                                    titulo,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                ),
                            ]
                            if icono
                            else [
                                ft.Text(
                                    titulo,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                )
                            ]
                        ),
                    ),
                    ft.Row(
                        spacing=8,
                        run_spacing=2,
                        wrap=True,
                        controls=filas_opciones,
                    ),
                ],
            ),
        ),
        checkboxes,
    )


def panel_filtros(
    titulo,
    secciones,
    resumen,
    on_limpiar,
    on_aplicar,
    on_cerrar,
    top=247,
    right=153,
    width=320,
    height=452,
):
    texto_resumen = ft.Text(
        resumen,
        size=11,
        color=COLOR_GRIS,
        expand=True,
        max_lines=1,
    )
    pie = ft.Container(
        padding=ft.Padding(12, 8, 12, 10),
        border=ft.Border(top=ft.BorderSide(1, "#E2EDF9")),
        content=ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.END,
            controls=[
                texto_resumen,
                ft.OutlinedButton(
                    "Limpiar",
                    on_click=on_limpiar,
                    style=ft.ButtonStyle(
                        color=COLOR_AZUL,
                        side=ft.BorderSide(1, "#C9DDF7"),
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding(10, 0, 10, 0),
                    ),
                    height=36,
                ),
                ft.FilledButton(
                    "Aplicar filtros",
                    on_click=on_aplicar,
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_NARANJA,
                        color=COLOR_BLANCO,
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding(12, 0, 12, 0),
                    ),
                    height=36,
                ),
            ],
        ),
    )
    panel = ft.Container(
        right=right,
        top=top,
        width=width,
        height=height,
        bgcolor=COLOR_BLANCO,
        border=ft.Border.all(1, "#DCEAF8"),
        border_radius=14,
        shadow=ft.BoxShadow(
            blur_radius=24,
            color="#263D5A30",
            offset=ft.Offset(0, 8),
        ),
        content=ft.Column(
            spacing=0,
            controls=[
                ft.Container(
                    padding=ft.Padding(14, 10, 10, 10),
                    border=ft.Border(bottom=ft.BorderSide(1, "#E2EDF9")),
                    content=ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.TUNE, size=18, color=COLOR_AZUL),
                            ft.Text(
                                titulo,
                                expand=True,
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=18,
                                icon_color="#6D89AB",
                                tooltip="Cerrar filtros",
                                on_click=on_cerrar,
                                width=30,
                                height=30,
                            ),
                        ],
                    ),
                ),
                ft.Column(
                    expand=True,
                    spacing=0,
                    scroll=ft.ScrollMode.AUTO,
                    controls=secciones,
                ),
                pie,
            ],
        ),
    )
    return panel, texto_resumen


def banner_modulo(
    src,
    categoria,
    titulo,
    descripcion,
    icono,
    altura=136,
    padding=ft.Padding(22, 8, 22, 8),
    tamano_icono=68,
    tamano_grafico=36,
    fondo_icono="#FFF0E5",
    tamano_titulo=29,
    tamano_descripcion=16,
    color_descripcion=COLOR_BANNER,
    overflow_descripcion=None,
):
    """Encabezado reutilizable para pantallas de módulos, con imagen, icono y descripción."""
    contenido = ft.Container(
        expand=True,
        padding=padding,
        content=ft.Row(
            spacing=18,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=tamano_icono,
                    height=tamano_icono,
                    border_radius=tamano_icono / 2,
                    bgcolor=fondo_icono,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        icono,
                        size=tamano_grafico,
                        color=COLOR_NARANJA,
                    ),
                ),
                ft.Column(
                    expand=True,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=4,
                    controls=[
                        ft.Text(
                            categoria.upper(),
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            titulo,
                            size=tamano_titulo,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            descripcion,
                            size=tamano_descripcion,
                            color=color_descripcion,
                            max_lines=2,
                            overflow=overflow_descripcion,
                        ),
                    ],
                ),
            ],
        ),
    )
    return card(
        banner_imagen_desvanecida(src, content=contenido, altura=altura),
        padding=0,
        border_color="#DCEAF8",
        radius=16,
        shadow=sombra_suave(),
    )


def avatar_inicial(texto, color=None, size=44, tooltip=None):
    """Avatar compacto con inicial y esquinas redondeadas."""
    inicial = (str(texto or "?").strip()[:1] or "?").upper()
    return ft.Container(
        width=size,
        height=size,
        border_radius=round(size * 0.25),
        bgcolor=color or COLOR_AZUL,
        alignment=ft.Alignment(0, 0),
        tooltip=tooltip,
        content=ft.Text(
            inicial,
            size=max(12, int(size * 0.4)),
            color=COLOR_BLANCO,
            weight=ft.FontWeight.BOLD,
        ),
    )


def badge_estado(texto, estado="activo"):
    """Etiqueta compacta de estado (activo, inactivo, pendiente o informativo)."""
    estilos = {
        "activo": ("#DDF7EF", "#009B82"),
        "inactivo": ("#FDE8EB", COLOR_ROJO),
        "pendiente": ("#FFF3D9", "#A66B00"),
        "info": ("#E8F2FF", COLOR_AZUL),
    }
    fondo, acento = estilos.get(str(estado).lower(), estilos["info"])
    return ft.Container(
        padding=ft.Padding(10, 5, 10, 5),
        bgcolor=fondo,
        border_radius=18,
        content=ft.Row(
            tight=True,
            spacing=6,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(width=7, height=7, bgcolor=acento, border_radius=4),
                ft.Text(
                    texto,
                    size=12,
                    color=acento,
                    weight=ft.FontWeight.BOLD,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
    )


def tarjeta_detalle(titulo, icono, contenido):
    return card(
        ft.Column(
            spacing=11,
            controls=[
                ft.Row(
                    spacing=9,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(icono, size=20, color=COLOR_NARANJA),
                        ft.Text(
                            titulo,
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                    ],
                ),
                contenido,
            ],
        ),
        padding=14,
        bgcolor=COLOR_BLANCO,
        border_color="#E4ECF5",
        radius=12,
    )


def campo_detalle(etiqueta, control, expand=False):
    return ft.Column(
        expand=expand,
        spacing=5,
        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        controls=[
            ft.Text(
                etiqueta,
                size=13,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BANNER,
            ),
            control,
        ],
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
    heading_row_color=None,
    heading_text_size=14,
    heading_text_color=None,
    vertical_lines=True,
    horizontal_lines=True,
    border_color=None,
    columnas_compactas=False,
):
    columnas_tabla = []

    for texto, ancho in columnas:
        contenido_encabezado = (
            texto
            if not isinstance(texto, str)
            else ft.Text(
                texto,
                size=heading_text_size,
                weight=ft.FontWeight.BOLD,
                color=heading_text_color or COLOR_NEGRO,
                text_align=ft.TextAlign.CENTER,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        )
        ancho_fijo = (
            not columnas_flexibles
            or ancho <= 60
            or (columnas_compactas and ancho <= 80)
        )
        encabezado = ft.Container(
            width=ancho if ancho_fijo else None,
            alignment=ft.Alignment(0, 0),
            content=contenido_encabezado,
        )

        if columnas_flexibles and not ancho_fijo:
            # El valor de ancho funciona como referencia proporcional. Las
            # columnas normales crecen hasta ocupar el espacio disponible;
            # las columnas pequeñas (checkboxes/acciones) conservan su ancho.
            if columnas_compactas and ancho <= 125:
                tamano = ftd.DataColumnSize.S
            else:
                tamano = ftd.DataColumnSize.M if ancho <= 145 else ftd.DataColumnSize.L
            columna = ftd.DataColumn2(label=encabezado, size=tamano)
        else:
            columna = ftd.DataColumn2(label=encabezado, fixed_width=ancho)

        columnas_tabla.append(columna)

    return ftd.DataTable2(
        expand=True,
        column_spacing=column_spacing,
        horizontal_margin=horizontal_margin,
        heading_row_height=heading_row_height,
        data_row_height=data_row_min_height,
        heading_row_color=heading_row_color or COLOR_FONDO,
        border=ft.Border.all(1, border_color or COLOR_GRIS_CLARO),
        vertical_lines=ft.BorderSide(1, border_color or COLOR_GRIS_CLARO) if vertical_lines else None,
        horizontal_lines=ft.BorderSide(1, border_color or COLOR_GRIS_CLARO) if horizontal_lines else None,
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
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


def etiqueta_categoria(nombre):
    """Etiqueta visual reutilizable para categorías de catálogo."""

    return ft.Container(
        padding=ft.Padding(8, 4, 8, 4),
        border_radius=20,
        bgcolor="#E0F7F4",
        content=ft.Row(
            spacing=5,
            tight=True,
            controls=[
                ft.Icon(
                    ft.Icons.ECO_OUTLINED,
                    size=14,
                    color="#079669",
                ),
                ft.Text(
                    nombre,
                    size=11,
                    color="#07865F",
                    weight=ft.FontWeight.W_600,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        ),
    )


def tarjeta_catalogo(
    titulo,
    descripcion,
    etiqueta,
    detalle,
    ruta_imagen=None,
    icono_secundario=ft.Icons.INVENTORY_2_OUTLINED,
    on_click=None,
):
    """Tarjeta reutilizable e interactiva para catálogos en cuadrícula."""

    control_imagen = ft.Container(
        height=72,
        border_radius=8,
        bgcolor="#EAF1F7",
        alignment=ft.Alignment(0, 0),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=(
            ft.Image(
                src=ruta_imagen,
                width=float("inf"),
                height=72,
                fit=ft.BoxFit.COVER,
            )
            if ruta_imagen
            else ft.Icon(
                ft.Icons.IMAGE_OUTLINED,
                size=28,
                color=COLOR_GRIS,
            )
        ),
    )

    controles = [
        control_imagen,
    ]
    if etiqueta is not None:
        controles.append(etiqueta)
    controles.append(
        ft.Text(
            titulo,
            size=14,
            weight=ft.FontWeight.BOLD,
            color=COLOR_AZUL,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
    )
    if descripcion:
        controles.append(
            ft.Text(
                descripcion,
                size=12,
                color=COLOR_GRIS,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
        )
    controles.append(
        ft.Row(
            spacing=7,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icono_secundario, size=19, color=COLOR_AZUL),
                ft.Text(
                    detalle or "",
                    size=12,
                    color=COLOR_GRIS,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        )
    )

    contenido = ft.Column(
        spacing=8,
        controls=controles,
    )

    tarjeta = card(
        contenido,
        padding=10,
        radius=11,
        shadow=sombra_suave(),
        border_color="#E3EAF2",
        expand=True,
    )
    return _hacer_tarjeta_catalogo_interactiva(tarjeta, on_click)


def _hacer_tarjeta_catalogo_interactiva(tarjeta, on_click):
    def actualizar_hover(e):
        esta_sobre_tarjeta = str(e.data).lower() in {
            "true",
            "enter",
            "entered",
            "hovered",
        }
        tarjeta.border = ft.Border.all(
            1.5,
            COLOR_AZUL if esta_sobre_tarjeta else ft.Colors.TRANSPARENT,
        )
        tarjeta.bgcolor = "#F5F9FF" if esta_sobre_tarjeta else COLOR_BLANCO
        tarjeta.shadow = (
            ft.BoxShadow(
                blur_radius=22,
                color="#2457D633",
                offset=ft.Offset(0, 8),
            )
            if esta_sobre_tarjeta
            else sombra_suave()
        )
        tarjeta.update()

    tarjeta.border = ft.Border.all(1.5, ft.Colors.TRANSPARENT)
    tarjeta.on_hover = actualizar_hover
    return ft.GestureDetector(
        expand=True,
        mouse_cursor=ft.MouseCursor.CLICK,
        on_tap=on_click,
        content=tarjeta,
    )


def fila_catalogo(
    titulo,
    descripcion,
    etiqueta,
    detalle,
    ruta_imagen=None,
    icono_secundario=ft.Icons.INVENTORY_2_OUTLINED,
    on_info=None,
):
    """Tarjeta compacta interactiva para catálogos en vista de lista."""

    if ruta_imagen:
        imagen_control = ft.Image(
            src=ruta_imagen,
            width=72,
            height=60,
            fit=ft.BoxFit.COVER,
            border_radius=8,
        )
    else:
        imagen_control = ft.Container(
            width=72,
            height=60,
            bgcolor="#EAF1F7",
            border_radius=8,
            alignment=ft.Alignment(0, 0),
            content=ft.Icon(
                ft.Icons.IMAGE_OUTLINED,
                color=COLOR_GRIS,
            ),
        )

    tarjeta = card(
        ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                imagen_control,
                ft.Column(
                    expand=True,
                    spacing=4,
                    controls=[
                        ft.Text(
                            titulo,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_AZUL,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            descripcion or "",
                            size=12,
                            color=COLOR_GRIS,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        etiqueta if etiqueta is not None else ft.Container(),
                    ],
                ),
                ft.Row(
                    width=120,
                    spacing=6,
                    controls=[
                        ft.Icon(
                            icono_secundario,
                            color=COLOR_AZUL,
                            size=18,
                        ),
                        ft.Text(
                            detalle or "",
                            size=12,
                            color=COLOR_GRIS,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                ),
            ],
        ),
        padding=10,
        radius=10,
        shadow=sombra_suave(),
        border_color="#E3EAF2",
        expand=True,
    )
    return _hacer_tarjeta_catalogo_interactiva(tarjeta, on_info)


def tarjeta_producto(producto, on_info=None):
    """Tarjeta de producto para la vista de cuadrícula."""

    return tarjeta_catalogo(
        titulo=producto["nombre"],
        descripcion=None,
        etiqueta=etiqueta_categoria(producto["categoria"]),
        detalle=producto["presentacion"],
        ruta_imagen=producto.get("imagen"),
        on_click=(lambda e, p=producto: on_info(p)) if on_info else None,
    )


def fila_producto(producto, on_info=None):
    """Fila de producto para la vista de lista."""

    return fila_catalogo(
        titulo=producto["nombre"],
        descripcion=producto["descripcion"],
        etiqueta=etiqueta_categoria(producto["categoria"]),
        detalle=producto["presentacion"],
        ruta_imagen=producto.get("imagen"),
        on_info=(lambda e, p=producto: on_info(p)) if on_info else None,
    )
