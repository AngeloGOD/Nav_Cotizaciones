
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



def banner_modulo(src, categoria, titulo, descripcion, icono, altura=174):
    """Encabezado reutilizable para pantallas de módulos, con imagen, icono y descripción."""
    contenido = ft.Container(
        expand=True,
        padding=ft.Padding(24, 16, 24, 16),
        content=ft.Row(
            spacing=18,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=88,
                    height=88,
                    border_radius=44,
                    bgcolor="#FFF5ED",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(icono, size=43, color=COLOR_NARANJA),
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
                            size=30,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            descripcion,
                            size=14,
                            color="#4F719B",
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
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
    """Avatar circular con inicial; reutilizable en directorios y fichas."""
    inicial = (str(texto or "?").strip()[:1] or "?").upper()
    return ft.Container(
        width=size,
        height=size,
        border_radius=size / 2,
        bgcolor=color or COLOR_AZUL,
        alignment=ft.Alignment(0, 0),
        tooltip=tooltip,
        content=ft.Text(
            inicial,
            size=max(12, int(size * 0.36)),
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


def etiqueta_categoria(nombre):
    """Etiqueta visual de la categoría de un producto."""

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
                ),
            ],
        ),
    )


def tarjeta_producto(producto, on_info=None):
    """Tarjeta de producto para la vista de cuadrícula."""

    imagen = ft.Container(
        height=120,
        border_radius=8,
        bgcolor="#EAF1F7",
        alignment=ft.Alignment(0, 0),
        clip_behavior=ft.ClipBehavior.HARD_EDGE,
        content=(
            ft.Image(
                src=producto.get("imagen", ""),
                width=float("inf"),
                height=120,
                fit=ft.BoxFit.COVER,
            )
            if producto.get("imagen")
            else ft.Icon(
                ft.Icons.IMAGE_OUTLINED,
                size=36,
                color=COLOR_GRIS,
            )
        ),
    )

    contenido = ft.Column(
        spacing=8,
        controls=[
            ft.Stack(
                controls=[
                    imagen,
                    ft.Container(
                        right=5,
                        top=5,
                        content=ft.IconButton(
                            icon=ft.Icons.INFO_OUTLINE,
                            tooltip="Ver información",
                            icon_color=COLOR_AZUL,
                            bgcolor=COLOR_BLANCO,
                            on_click=(
                                lambda e, p=producto: on_info(p)
                            ) if on_info else None,
                        ),
                    ),
                ],
            ),
            etiqueta_categoria(producto["categoria"]),
            ft.Text(
                producto["nombre"],
                size=14,
                weight=ft.FontWeight.BOLD,
                color=COLOR_AZUL,
                max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Text(
                producto["descripcion"],
                size=12,
                color=COLOR_GRIS,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            ),
            ft.Row(
                spacing=7,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.INVENTORY_2_OUTLINED,
                        size=19,
                        color=COLOR_AZUL,
                    ),
                    ft.Text(
                        producto["presentacion"],
                        size=12,
                        color=COLOR_GRIS,
                    ),
                ],
            ),
        ],
    )

    return card(
        contenido,
        padding=10,
        radius=11,
        shadow=sombra_suave(),
        expand=True,
    )


def fila_producto(producto, on_info=None):
    """Fila de producto para la vista de lista."""

    if producto.get("imagen"):
        imagen = ft.Image(
            src=producto["imagen"],
            width=86,
            height=72,
            fit=ft.BoxFit.COVER,
            border_radius=8,
        )
    else:
        imagen = ft.Container(
            width=86,
            height=72,
            bgcolor="#EAF1F7",
            border_radius=8,
            alignment=ft.Alignment(0, 0),
            content=ft.Icon(
                ft.Icons.IMAGE_OUTLINED,
                color=COLOR_GRIS,
            ),
        )

    return card(
        ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                imagen,
                ft.Column(
                    expand=True,
                    spacing=4,
                    controls=[
                        ft.Text(
                            producto["nombre"],
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_AZUL,
                        ),
                        ft.Text(
                            producto["descripcion"],
                            size=12,
                            color=COLOR_GRIS,
                            max_lines=2,
                        ),
                        etiqueta_categoria(producto["categoria"]),
                    ],
                ),
                ft.Row(
                    width=150,
                    spacing=6,
                    controls=[
                        ft.Icon(
                            ft.Icons.INVENTORY_2_OUTLINED,
                            color=COLOR_AZUL,
                            size=18,
                        ),
                        ft.Text(
                            producto["presentacion"],
                            size=12,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                ft.IconButton(
                    icon=ft.Icons.INFO_OUTLINE,
                    tooltip="Ver información",
                    icon_color=COLOR_AZUL,
                    on_click=(
                        lambda e, p=producto: on_info(p)
                    ) if on_info else None,
                ),
            ],
        ),
        padding=10,
        radius=10,
    )