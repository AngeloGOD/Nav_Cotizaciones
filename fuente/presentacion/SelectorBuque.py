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
    from fuente.negocio.modelo.Buque import Buque


class SelectorBuque(ft.Stack):
    """Buscador autocompletable de buques con debounce y lista desplegable flotante."""

    def __init__(
        self,
        servicio_buque,
        on_buque_seleccionado: Callable[[Buque | None], None] | None = None,
        label: str = "Buque / Vessel *",
        hint_text: str = "Buscar buque por nombre...",
        height: int = 55,
    ):
        super().__init__(
            expand=True,
            height=height,
            clip_behavior=ft.ClipBehavior.NONE,
        )

        self.servicio_buque = servicio_buque
        self.on_buque_seleccionado = on_buque_seleccionado
        self.buque_seleccionado: Buque | None = None
        self.buque_id_seleccionado: int | None = None
        self._numero_busqueda = 0
        self._temporizador: threading.Timer | None = None

        self.boton_limpiar = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=16,
            icon_color=COLOR_GRIS,
            tooltip="Limpiar buque",
            width=28,
            height=28,
            padding=0,
            visible=False,
            on_click=self._al_limpiar_click,
        )

        self.campo = ft.TextField(
            expand=True,
            label=label,
            hint_text=hint_text,
            height=max(42, height - 3),
            text_size=12,
            border=ft.InputBorder.OUTLINE,
            border_radius=8,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            prefix_icon=ft.Icons.DIRECTIONS_BOAT_OUTLINED,
            suffix=self.boton_limpiar,
            content_padding=ft.Padding(12, 8, 12, 8),
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
            height=220,
            padding=5,
            bgcolor=ft.Colors.WHITE,
            border=ft.Border.all(1, "#DCE5EF"),
            border_radius=9,
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
        self.limpiar(notificar=True)

    def _al_cambiar_texto(self, e=None) -> None:
        self._cancelar_temporizador()
        self._numero_busqueda += 1
        numero_actual = self._numero_busqueda

        termino = (self.campo.value or "").strip()
        tenia_buque = self.buque_seleccionado is not None
        self.buque_seleccionado = None
        self.buque_id_seleccionado = None
        self.boton_limpiar.visible = bool(termino)

        self._ocultar_resultados()
        if tenia_buque and self.on_buque_seleccionado is not None:
            self.on_buque_seleccionado(None)
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
            if self.servicio_buque is not None:
                buques = self.servicio_buque.buscar_por_nombre(termino)
            else:
                buques = []
        except Exception as error:
            print(f"Error al buscar buques: {error}")
            if numero_actual == self._numero_busqueda:
                self._ocultar_resultados()
                self._actualizar()
            return

        if numero_actual != self._numero_busqueda:
            return

        if (self.campo.value or "").strip() != termino:
            return

        self._mostrar_resultados(buques)

    def _mostrar_resultados(self, buques) -> None:
        self.lista_resultados.controls.clear()

        if not buques:
            self.lista_resultados.controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Text(
                        "No se encontraron buques.",
                        size=12,
                        color=COLOR_GRIS,
                    ),
                )
            )
        else:
            for buque in buques:
                nombre_buque = getattr(buque, "nombre", "") or "Sin nombre"
                imo = getattr(buque, "numero_imo", None) or "S/N"
                categoria_obj = getattr(buque, "categoria_buque", None)
                categoria_txt = (
                    getattr(categoria_obj, "categoria", None)
                    or getattr(buque, "subtipo_descripcion", None)
                    or "N/D"
                )
                trb_val = getattr(buque, "trb", None)
                trb_txt = f"{trb_val:,.2f}" if trb_val is not None else "0.00"
                subtitulo = f"IMO: {imo} | Categoría: {categoria_txt} | TRB: {trb_txt}"

                self.lista_resultados.controls.append(
                    ft.Container(
                        padding=ft.Padding(10, 8, 10, 8),
                        border_radius=7,
                        bgcolor="#F4F8FC",
                        on_click=lambda e, b=buque: self._seleccionar_buque(b),
                        content=ft.Column(
                            spacing=2,
                            tight=True,
                            controls=[
                                ft.Text(
                                    nombre_buque,
                                    size=12,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_NEGRO,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    subtitulo,
                                    size=11,
                                    color=COLOR_GRIS,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    )
                )

        self.contenido_resultados.visible = True
        self._actualizar()

    def _seleccionar_buque(self, buque: Buque) -> None:
        self._cancelar_temporizador()
        self._numero_busqueda += 1

        self.buque_seleccionado = buque
        self.buque_id_seleccionado = (
            int(buque.id) if getattr(buque, "id", None) is not None else None
        )
        self.campo.value = getattr(buque, "nombre", "") or ""
        self.boton_limpiar.visible = bool(self.campo.value)

        self._ocultar_resultados()
        if self.on_buque_seleccionado is not None:
            self.on_buque_seleccionado(buque)
        self._actualizar()

    def establecer_buque(
        self, buque: Buque | None, notificar: bool = False
    ) -> None:
        if buque is None:
            self.limpiar(notificar=notificar)
            return

        self._cancelar_temporizador()
        self._numero_busqueda += 1

        self.buque_seleccionado = buque
        self.buque_id_seleccionado = (
            int(buque.id) if getattr(buque, "id", None) is not None else None
        )
        self.campo.value = getattr(buque, "nombre", "") or ""
        self.boton_limpiar.visible = bool(self.campo.value)

        self._ocultar_resultados()
        if notificar and self.on_buque_seleccionado is not None:
            self.on_buque_seleccionado(buque)
        self._actualizar()

    def limpiar(self, notificar: bool = True) -> None:
        self._cancelar_temporizador()
        self._numero_busqueda += 1

        self.buque_seleccionado = None
        self.buque_id_seleccionado = None
        self.campo.value = ""
        self.boton_limpiar.visible = False

        self._ocultar_resultados()
        if notificar and self.on_buque_seleccionado is not None:
            self.on_buque_seleccionado(None)
        self._actualizar()

    def _ocultar_resultados(self) -> None:
        self.contenido_resultados.visible = False
        self.lista_resultados.controls.clear()

    def _actualizar(self) -> None:
        try:
            if self.page:
                self.page.update()
            else:
                self.update()
        except RuntimeError:
            pass
