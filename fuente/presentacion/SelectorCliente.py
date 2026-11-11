from __future__ import annotations

import threading
from typing import Callable, TYPE_CHECKING
import flet as ft

from fuente.utilidades.Colores import (
    COLOR_GRIS,
    COLOR_GRIS_CLARO,
    COLOR_NEGRO,
    COLOR_NARANJA,
)

if TYPE_CHECKING:
    from fuente.negocio.modelo.Cliente import Cliente


class SelectorCliente(ft.Stack):
    """Buscador autocompletable de clientes con debounce y lista desplegable flotante."""

    def __init__(
        self,
        servicio_cliente,
        on_cliente_seleccionado: Callable[[Cliente | None], None] | None = None,
        label: str = "Cliente (opcional)",
        hint_text: str = "Buscar cliente por razón social...",
        height: int = 58,
    ):
        super().__init__(
            expand=True,
            height=height,
            clip_behavior=ft.ClipBehavior.NONE,
        )

        self.servicio_cliente = servicio_cliente
        self.on_cliente_seleccionado = on_cliente_seleccionado
        self.cliente_seleccionado: Cliente | None = None
        self.cliente_id_seleccionado: int | None = None
        self._numero_busqueda = 0
        self._temporizador: threading.Timer | None = None

        self.boton_limpiar = ft.IconButton(
            icon=ft.Icons.CLOSE,
            icon_size=16,
            icon_color=COLOR_GRIS,
            tooltip="Limpiar selección",
            width=28,
            height=28,
            padding=0,
            visible=False,
            on_click=self._al_limpiar_click,
        )

        # Campo de búsqueda con expand=True
        self.campo = ft.TextField(
            expand=True,
            width=float("inf"),
            label=label,
            hint_text=hint_text,
            height=height,
            text_size=14,
            border=ft.InputBorder.OUTLINE,
            border_radius=9,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            prefix_icon=ft.Icons.PERSON_SEARCH,
            suffix=self.boton_limpiar,
            content_padding=ft.Padding(14, 12, 14, 12),
            on_change=self._al_cambiar_texto,
        )

        # Lista donde se mostrarán los resultados
        self.lista_resultados = ft.Column(
            spacing=3,
            controls=[],
            scroll=ft.ScrollMode.AUTO,
            tight=True,
        )

        # Contenedor flotante de resultados
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

        # Stack: el campo ocupa el espacio normal y los resultados
        # se posicionan debajo sin modificar la altura del control
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
        tenia_cliente = self.cliente_seleccionado is not None
        self.cliente_seleccionado = None
        self.cliente_id_seleccionado = None
        self.boton_limpiar.visible = bool(termino)

        # Ocultar inmediatamente los resultados anteriores.
        self._ocultar_resultados()
        if tenia_cliente and self.on_cliente_seleccionado is not None:
            self.on_cliente_seleccionado(None)
        self._actualizar()

        # Buscar desde dos caracteres.
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
            if self.servicio_cliente is not None:
                clientes = self.servicio_cliente.buscar_por_nombre(termino)
            else:
                clientes = []
        except Exception as error:
            print(f"Error al buscar clientes: {error}")

            if numero_actual == self._numero_busqueda:
                self._ocultar_resultados()
                self._actualizar()

            return

        # Comprobar que el usuario no haya seguido escribiendo.
        if numero_actual != self._numero_busqueda:
            return

        if (self.campo.value or "").strip() != termino:
            return

        self._mostrar_resultados(clientes)

    def _mostrar_resultados(self, clientes) -> None:
        self.lista_resultados.controls.clear()

        if not clientes:
            self.lista_resultados.controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Text(
                        "No se encontraron clientes.",
                        size=12,
                        color=COLOR_GRIS,
                    ),
                )
            )
        else:
            for cliente in clientes:
                razon_social = (
                    getattr(cliente, "razon_social", "") or "Sin razón social"
                )
                rfc = getattr(cliente, "rfc", None) or "No registrado"

                self.lista_resultados.controls.append(
                    ft.Container(
                        padding=ft.Padding(10, 9, 10, 9),
                        border_radius=7,
                        bgcolor="#F4F8FC",
                        on_click=lambda e, c=cliente: self._seleccionar_cliente(c),
                        content=ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    content=ft.Text(
                                        razon_social,
                                        size=12,
                                        weight=ft.FontWeight.W_500,
                                        color=COLOR_NEGRO,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ),
                                ft.Column(
                                    spacing=1,
                                    horizontal_alignment=ft.CrossAxisAlignment.END,
                                    controls=[
                                        ft.Text(
                                            "RFC",
                                            size=10,
                                            color=COLOR_GRIS,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            rfc,
                                            size=11,
                                            color=COLOR_NEGRO,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    )
                )

        self.contenido_resultados.visible = True
        self._actualizar()

    def _seleccionar_cliente(self, cliente: Cliente) -> None:
        self._cancelar_temporizador()
        self._numero_busqueda += 1

        try:
            cliente_id = getattr(cliente, "id", None)
            razon_social = getattr(cliente, "razon_social", "") or ""
        except Exception:
            cliente_id = None
            razon_social = ""

        self.cliente_seleccionado = cliente
        self.cliente_id_seleccionado = (
            int(cliente_id) if cliente_id is not None else None
        )
        self.campo.value = razon_social
        self.boton_limpiar.visible = bool(self.campo.value)

        self._ocultar_resultados()
        if self.on_cliente_seleccionado is not None:
            self.on_cliente_seleccionado(cliente)
        self._actualizar()

    def establecer_cliente(
        self, cliente: Cliente | None, notificar: bool = False
    ) -> None:
        if cliente is None:
            self.limpiar(notificar=notificar)
            return

        self._cancelar_temporizador()
        self._numero_busqueda += 1

        try:
            cliente_id = getattr(cliente, "id", None)
            razon_social = getattr(cliente, "razon_social", "") or ""
        except Exception:
            cliente_id = None
            razon_social = ""

        self.cliente_seleccionado = cliente
        self.cliente_id_seleccionado = (
            int(cliente_id) if cliente_id is not None else None
        )
        self.campo.value = razon_social
        self.boton_limpiar.visible = bool(self.campo.value)

        self._ocultar_resultados()
        if notificar and self.on_cliente_seleccionado is not None:
            self.on_cliente_seleccionado(cliente)
        self._actualizar()

    def limpiar(self, notificar: bool = False) -> None:
        self._cancelar_temporizador()
        self._numero_busqueda += 1

        self.cliente_seleccionado = None
        self.cliente_id_seleccionado = None
        self.campo.value = ""
        self.boton_limpiar.visible = False

        self._ocultar_resultados()
        if notificar and self.on_cliente_seleccionado is not None:
            self.on_cliente_seleccionado(None)
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
