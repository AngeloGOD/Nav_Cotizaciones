import logging
import weakref

import flet as ft
import flet_audio as fta
from .Colores import *

_ARCHIVOS_AUDIO = {
    "exito": "Exito.mp3",
    "error": "Error.mp3",
    "eliminacion": "Eliminacion.mp3",
    "documento": "Documento.mp3",
    "confirmacion": "Confirmacion.mp3",
}
_AUDIO_POR_PAGINA = {}


def _obtener_sonidos_pagina(page):
    clave_pagina = id(page)
    registro = _AUDIO_POR_PAGINA.get(clave_pagina)
    if registro is not None and registro[0]() is page:
        return clave_pagina, registro[1]

    sonidos = {}
    referencia = weakref.ref(
        page,
        lambda _: _AUDIO_POR_PAGINA.pop(clave_pagina, None),
    )
    _AUDIO_POR_PAGINA[clave_pagina] = (referencia, sonidos)
    return clave_pagina, sonidos


def precargar_sonidos(page):
    if page is None:
        return
    try:
        _, sonidos = _obtener_sonidos_pagina(page)
        if sonidos:
            return
        for nombre, archivo in _ARCHIVOS_AUDIO.items():
            estado = {
                "listo": False,
                "precargando": True,
                "pendientes": 0,
            }
            audio = fta.Audio(
                src=f"audio/{archivo}",
                autoplay=False,
                volume=0,
                release_mode=fta.ReleaseMode.STOP,
                on_loaded=lambda e, tipo=nombre: _sonido_cargado(
                    page, tipo
                ),
            )
            page.services.append(audio)
            estado["audio"] = audio
            sonidos[nombre] = estado
        page.update()
    except Exception:
        logging.exception("No se pudieron precargar los sonidos de la aplicación.")


def _sonido_cargado(page, tipo):
    _, sonidos = _obtener_sonidos_pagina(page)
    estado = sonidos.get(tipo)
    if estado is not None and estado["precargando"]:
        page.run_task(_finalizar_precarga, estado)


async def _finalizar_precarga(estado):
    audio = estado["audio"]
    audio.volume = 0.65
    audio.update()
    estado["precargando"] = False
    estado["listo"] = True
    pendientes = estado["pendientes"]
    estado["pendientes"] = 0
    for _ in range(pendientes):
        await _reproducir_audio(estado)


async def _reproducir_audio(estado):
    try:
        await estado["audio"].play()
    except Exception:
        logging.exception("No se pudo reproducir el sonido %s.", estado["audio"].src)


def reproducir_sonido(page, tipo):
    nombre = (tipo or "").strip().lower()
    if page is None or nombre not in _ARCHIVOS_AUDIO:
        return

    try:
        _, sonidos = _obtener_sonidos_pagina(page)
        if not sonidos:
            precargar_sonidos(page)
            _, sonidos = _obtener_sonidos_pagina(page)
        estado = sonidos.get(nombre)
        if estado is None:
            return
        if not estado["listo"]:
            estado["pendientes"] += 1
            return
        page.run_task(_reproducir_audio, estado)
    except Exception:
        logging.exception("No se pudo reproducir el sonido %s.", nombre)


def dialogo_confirmacion(
    page,
    titulo,
    mensaje,
    on_confirmar,
    texto_confirmar="Confirmar",
    texto_cancelar="Cancelar",
    color_confirmar=COLOR_ROJO,
):
    reproducir_sonido(page, "confirmacion")

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


def mostrar_notificacion(page, mensaje, color=COLOR_VERDE, sonido=None):
    page.show_dialog(
        ft.SnackBar(
            content=ft.Text(mensaje, color=COLOR_BLANCO),
            bgcolor=color,
        )
    )
    page.update()
    if sonido is None:
        color_texto = str(color).lower()
        if color == COLOR_VERDE or "green" in color_texto:
            sonido = "exito"
        elif color == COLOR_ROJO or "red" in color_texto:
            sonido = "error"
    if sonido:
        reproducir_sonido(page, sonido)


def avisar_eliminacion_no_implementada(page):
    mostrar_notificacion(
        page,
        "La eliminación no está implementada; requiere autorización y verificación de permisos de usuario.",
        COLOR_NARANJA,
        sonido="error",
    )


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
    reproducir_sonido(page, "exito" if color == COLOR_VERDE else "error")
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
