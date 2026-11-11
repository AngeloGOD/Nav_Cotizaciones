from datetime import date as _date, datetime as _datetime
from decimal import Decimal as _Decimal, InvalidOperation as _InvalidOperation
import re as _re

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


def crear_mensaje_validacion(reservar_espacio=False):
    return ft.Text(
        " " if reservar_espacio else "",
        size=11,
        color=COLOR_ROJO,
        height=14 if reservar_espacio else None,
        visible=reservar_espacio,
        opacity=0 if reservar_espacio else 1,
        data={
            "reservar_espacio": reservar_espacio,
            "hay_error": False,
        },
    )


def campo_con_mensaje_error(control, mensaje_error):
    return ft.Column(
        spacing=2,
        controls=[control, mensaje_error],
    )


def validar_campo(
    control,
    mensaje_error,
    validador,
    controles_relacionados=(),
    marco=None,
):
    error = validador(control.value)
    reserva = (
        isinstance(mensaje_error.data, dict)
        and mensaje_error.data.get("reservar_espacio", False)
    )
    hay_error = bool(error)
    mensaje_error.value = error or (" " if reserva else "")
    mensaje_error.visible = hay_error or reserva
    mensaje_error.opacity = 1 if hay_error else 0
    if isinstance(mensaje_error.data, dict):
        mensaje_error.data["hay_error"] = hay_error
    color = COLOR_ROJO if error else COLOR_GRIS_CLARO
    if marco is not None:
        marco.border = ft.Border.all(1, color if error else "#C9DDF7")
    for campo_control in (control, *controles_relacionados):
        campo_control.border_color = color
        if hasattr(campo_control, "focused_border_color"):
            campo_control.focused_border_color = (
                COLOR_ROJO if error else COLOR_NARANJA
            )
    return not error


def limpiar_error_campo(
    control,
    mensaje_error,
    controles_relacionados=(),
    marco=None,
):
    data = mensaje_error.data
    hay_error = (
        data.get("hay_error", mensaje_error.visible)
        if isinstance(data, dict)
        else mensaje_error.visible
    )
    if not hay_error:
        return False
    reserva = (
        isinstance(data, dict)
        and data.get("reservar_espacio", False)
    )
    mensaje_error.value = " " if reserva else ""
    mensaje_error.visible = reserva
    mensaje_error.opacity = 0 if reserva else 1
    if isinstance(data, dict):
        data["hay_error"] = False
    if marco is not None:
        marco.border = ft.Border.all(1, "#C9DDF7")
    for campo_control in (control, *controles_relacionados):
        campo_control.border_color = COLOR_GRIS_CLARO
        if hasattr(campo_control, "focused_border_color"):
            campo_control.focused_border_color = COLOR_NARANJA
    return True


def vincular_validacion_campo(
    control,
    mensaje_error,
    validador,
    page=None,
    evento="on_change",
    controles_relacionados=(),
    marco=None,
):
    manejador_anterior = getattr(control, evento, None)
    manejador_blur_anterior = getattr(control, "on_blur", None)

    def cambio(e=None):
        if manejador_anterior:
            manejador_anterior(e)
        cambio_error = limpiar_error_campo(
            control,
            mensaje_error,
            controles_relacionados=controles_relacionados,
            marco=marco,
        )
        if cambio_error and page is not None:
            page.update()

    def validar_al_salir(e=None):
        if manejador_blur_anterior:
            manejador_blur_anterior(e)
        valido = validar_campo(
            control,
            mensaje_error,
            validador,
            controles_relacionados=controles_relacionados,
            marco=marco,
        )
        if page is not None:
            page.update()
        return valido

    setattr(control, evento, cambio)
    control.on_blur = validar_al_salir
    return validar_al_salir


def validar_campos(campos):
    valido = True
    for campo in campos.values():
        control, mensaje_error, validador, *relacionados = campo
        if not validar_campo(
            control,
            mensaje_error,
            validador,
            controles_relacionados=relacionados[0] if relacionados else (),
        ):
            valido = False
    return valido


def validador_requerido(etiqueta):
    def validar(valor):
        if valor is None or not str(valor).strip():
            return f"Completa {etiqueta}."
        return None

    return validar


def validador_correo():
    patron = _re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def validar(valor):
        if valor is None or not str(valor).strip():
            return "El correo electrónico es obligatorio."
        correo = str(valor).strip()
        if any(caracter.isspace() for caracter in correo):
            return "El correo no debe contener espacios."
        if correo.count("@") != 1:
            return "Escribe el nombre, una sola @ y el dominio."
        nombre, dominio = correo.split("@")
        if not nombre or not nombre[0].isalpha():
            return "Antes de @, el correo debe comenzar con una letra."
        if not dominio:
            return "Después de @, escribe el dominio, por ejemplo empresa.com."
        if "." not in dominio:
            return "Después de @, agrega un punto y la terminación del dominio."
        if dominio.startswith(".") or dominio.endswith(".") or ".." in dominio:
            return "Completa el dominio después del punto, por ejemplo empresa.com."
        if not patron.fullmatch(correo):
            return "Usa el formato nombre@empresa.com."
        return None

    return validar


def validador_telefono():
    def validar(valor):
        if valor is None or not str(valor).strip():
            return "El número telefónico es obligatorio."
        if not _re.fullmatch(r"\+?[\d\s().-]+", str(valor).strip()):
            return "Usa solo dígitos, espacios, paréntesis, guiones y el signo +."
        digitos = _re.sub(r"\D", "", str(valor))
        if not 7 <= len(digitos) <= 15:
            return "El teléfono debe contener entre 7 y 15 dígitos."
        return None

    return validar


def validador_numero(etiqueta, minimo=0, minimo_exclusivo=False):
    def validar(valor):
        if valor is None or not str(valor).strip():
            return f"{etiqueta} es obligatorio."
        try:
            numero = _Decimal(str(valor).strip())
        except _InvalidOperation:
            return f"{etiqueta} debe ser un número válido."
        if not numero.is_finite():
            return f"{etiqueta} debe ser un número válido."
        if numero < minimo or (minimo_exclusivo and numero == minimo):
            condicion = "mayor que" if minimo_exclusivo else "igual o mayor que"
            return f"{etiqueta} debe ser {condicion} {minimo}."
        return None

    return validar


def validar_rango_fechas(
    fecha_desde,
    fecha_hasta,
    formato="%d/%m/%Y",
    fecha_actual=None,
):
    fecha_actual = fecha_actual or _date.today()
    errores = {"fecha_desde": None, "fecha_hasta": None}
    fechas = {}

    for clave, valor in (
        ("fecha_desde", fecha_desde),
        ("fecha_hasta", fecha_hasta),
    ):
        if valor is None or not str(valor).strip():
            continue
        try:
            fecha = _datetime.strptime(str(valor).strip(), formato).date()
        except ValueError:
            formato_visible = (
                formato.replace("%d", "dd")
                .replace("%m", "mm")
                .replace("%Y", "aaaa")
            )
            errores[clave] = (
                f"Usa una fecha válida con formato {formato_visible}."
            )
            continue
        fechas[clave] = fecha
        if fecha < _date(1900, 1, 1):
            errores[clave] = "La fecha debe ser igual o posterior al 01/01/1900."
        if fecha > fecha_actual:
            errores[clave] = "La fecha no puede ser posterior a hoy."

    desde = fechas.get("fecha_desde")
    hasta = fechas.get("fecha_hasta")
    if desde and hasta and desde > hasta:
        errores["fecha_desde"] = (
            "La fecha inicial no puede ser posterior a la fecha final."
        )
        errores["fecha_hasta"] = (
            "La fecha final debe ser igual o posterior a la fecha inicial."
        )
    return errores


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
