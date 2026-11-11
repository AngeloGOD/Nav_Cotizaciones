from __future__ import annotations

import threading
from typing import Callable, TYPE_CHECKING
import flet as ft

from fuente.utilidades.Colores import (
    COLOR_GRIS,
    COLOR_GRIS_CLARO,
    COLOR_NARANJA,
    COLOR_NEGRO,
)

if TYPE_CHECKING:
    from fuente.negocio.modelo.Servicio import Servicio


class SelectorServicio(ft.Stack):
    """Buscador compacto autocompletable de servicios portuarios para celdas de la tabla PDA."""

    def __init__(
        self,
        servicio_servicio,
        on_servicio_seleccionado: Callable[[Servicio], None] | None = None,
        on_abrir_resultados: Callable[["SelectorServicio", bool], None] | None = None,
        servicio_inicial: Servicio | None = None,
        hint_text: str = "Buscar servicio por nombre...",
        height: int = 36,
    ):
        super().__init__(
            expand=True,
            height=height,
            clip_behavior=ft.ClipBehavior.NONE,
        )

        self.servicio_servicio = servicio_servicio
        self.on_servicio_seleccionado = on_servicio_seleccionado
        self.on_abrir_resultados = on_abrir_resultados
        self.servicio_seleccionado: Servicio | None = None
        self.servicio_id_seleccionado: int | None = None
        self._numero_busqueda = 0
        self._temporizador: threading.Timer | None = None

        self.boton_limpiar = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=14,
            icon_color=COLOR_GRIS,
            tooltip="Limpiar servicio",
            width=24,
            height=24,
            padding=0,
            visible=False,
            on_click=self._al_limpiar_click,
        )

        self.campo = ft.TextField(
            expand=True,
            hint_text=hint_text,
            height=height,
            text_size=11,
            border=ft.InputBorder.OUTLINE,
            border_radius=6,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            prefix_icon=ft.Icons.SEARCH,
            suffix=self.boton_limpiar,
            content_padding=ft.Padding(8, 4, 8, 4),
            dense=True,
            on_change=self._al_cambiar_texto,
        )

        self.lista_resultados = ft.Column(
            spacing=3,
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            tight=True,
        )

        self.contenido_resultados = ft.Container(
            visible=False,
            height=200,
            padding=5,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, "#DCE5EF"),
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            shadow=ft.BoxShadow(
                blur_radius=14,
                spread_radius=1,
                color="#35000000",
                offset=ft.Offset(0, 5),
            ),
            content=self.lista_resultados,
        )

        self.controls = [
            self.campo,
        ]

        if servicio_inicial is not None:
            self.establecer_servicio(servicio_inicial)

    @property
    def value(self) -> str:
        return self.campo.value or ""

    @value.setter
    def value(self, val: str | None) -> None:
        self.campo.value = "" if val is None else str(val)

    def _cancelar_temporizador(self) -> None:
        if self._temporizador is not None:
            self._temporizador.cancel()
            self._temporizador = None

    def _al_limpiar_click(self, e=None) -> None:
        self.limpiar()

    def _al_cambiar_texto(self, e=None) -> None:
        self._cancelar_temporizador()
        self._numero_busqueda += 1
        numero_actual = self._numero_busqueda

        termino = (self.campo.value or "").strip()
        self.servicio_seleccionado = None
        self.servicio_id_seleccionado = None
        self.boton_limpiar.visible = bool(termino)

        self._ocultar_resultados()
        self._actualizar()

        if len(termino) < 2:
            return

        self._temporizador = threading.Timer(
            0.35,
            self._ejecutar_busqueda,
            args=(termino, numero_actual),
        )
        self._temporizador.daemon = True
        self._temporizador.start()

    def _ejecutar_busqueda(self, termino: str, numero_actual: int) -> None:
        if numero_actual != self._numero_busqueda:
            return

        try:
            if self.servicio_servicio is not None:
                servicios = self.servicio_servicio.buscar_por_nombre(termino)
            else:
                servicios = []
        except Exception as error:
            print(f"Error al buscar servicios: {error}")
            if numero_actual == self._numero_busqueda:
                self._ocultar_resultados()
                self._actualizar()
            return

        if numero_actual != self._numero_busqueda:
            return

        if (self.campo.value or "").strip() != termino:
            return

        self._mostrar_resultados(servicios)

    def _mostrar_resultados(self, servicios) -> None:
        self.lista_resultados.controls.clear()

        if not servicios:
            self.lista_resultados.controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Text(
                        "No se encontraron servicios.",
                        size=11,
                        color=COLOR_GRIS,
                    ),
                )
            )
        else:
            for servicio in servicios:
                nombre_es = getattr(servicio, "nombre_es", "") or "Sin descripción"
                cat_pda_obj = getattr(servicio, "categoria_pda", None)
                cat_pda_nombre = getattr(cat_pda_obj, "nombre", None) or "SIN CATEGORÍA"
                proveedores = getattr(servicio, "proveedores", None) or []
                prov_nombre = (
                    getattr(proveedores[0], "nombre", None)
                    if proveedores
                    else "Sin proveedor"
                ) or "Sin proveedor"

                self.lista_resultados.controls.append(
                    ft.Container(
                        padding=ft.Padding(8, 7, 8, 7),
                        border_radius=6,
                        bgcolor="#F4F8FC",
                        on_click=lambda e, s=servicio: self._seleccionar_servicio(s),
                        content=ft.Column(
                            spacing=2,
                            tight=True,
                            controls=[
                                ft.Text(
                                    nombre_es,
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_NEGRO,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    f"Categoría: {cat_pda_nombre} | Proveedor: {prov_nombre}",
                                    size=10,
                                    color=COLOR_GRIS,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    )
                )

        self.contenido_resultados.visible = True
        if self.on_abrir_resultados is not None:
            self.on_abrir_resultados(self, True)
        self._actualizar()

    def _seleccionar_servicio(self, servicio: Servicio) -> None:
        self._cancelar_temporizador()
        self._numero_busqueda += 1

        self.servicio_seleccionado = servicio
        self.servicio_id_seleccionado = (
            int(servicio.id) if getattr(servicio, "id", None) is not None else None
        )
        self.campo.value = getattr(servicio, "nombre_es", "") or ""
        self.boton_limpiar.visible = bool(self.campo.value)

        self._ocultar_resultados()
        if self.on_servicio_seleccionado is not None:
            self.on_servicio_seleccionado(servicio)
        self._actualizar()

    def establecer_servicio(self, servicio: Servicio | None) -> None:
        if servicio is None:
            self.limpiar()
            return

        self._cancelar_temporizador()
        self._numero_busqueda += 1

        self.servicio_seleccionado = servicio
        self.servicio_id_seleccionado = (
            int(servicio.id) if getattr(servicio, "id", None) is not None else None
        )
        self.campo.value = getattr(servicio, "nombre_es", "") or ""
        self.boton_limpiar.visible = bool(self.campo.value)

        self._ocultar_resultados()
        self._actualizar()

    def limpiar(self) -> None:
        self._cancelar_temporizador()
        self._numero_busqueda += 1

        self.servicio_seleccionado = None
        self.servicio_id_seleccionado = None
        self.campo.value = ""
        self.boton_limpiar.visible = False

        self._ocultar_resultados()
        self._actualizar()

    def _ocultar_resultados(self) -> None:
        estaba_visible = self.contenido_resultados.visible
        self.contenido_resultados.visible = False
        self.lista_resultados.controls.clear()
        if estaba_visible and self.on_abrir_resultados is not None:
            self.on_abrir_resultados(self, False)

    def _actualizar(self) -> None:
        try:
            if self.page:
                self.page.update()
            else:
                self.update()
        except RuntimeError:
            pass
