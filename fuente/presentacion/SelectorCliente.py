import asyncio
import flet as ft

from fuente.utilidades.Colores import (
    COLOR_GRIS,
    COLOR_GRIS_CLARO,
    COLOR_NEGRO,
    COLOR_NARANJA,
)


class SelectorCliente(ft.Stack):

    def __init__(self, servicio_cliente):
        super().__init__(
            expand=True,
            height=58,
            clip_behavior=ft.ClipBehavior.NONE,
        )

        self.servicio_cliente = servicio_cliente
        self.cliente_id_seleccionado = None
        self._numero_busqueda = 0

        # Campo de búsqueda con expand=True
        self.campo = ft.TextField(
            expand=True,
            width=float("inf"),
            label="Cliente (opcional)",
            hint_text="Buscar cliente por razón social...",
            height=58,
            text_size=14,
            border=ft.InputBorder.OUTLINE,
            border_radius=9,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            prefix_icon=ft.Icons.PERSON_SEARCH,
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

    def _al_cambiar_texto(self, e=None):
        self._numero_busqueda += 1
        numero_actual = self._numero_busqueda

        termino = (self.campo.value or "").strip()
        self.cliente_id_seleccionado = None

        # Ocultar inmediatamente los resultados anteriores.
        self._ocultar_resultados()
        self._actualizar()

        # Buscar desde dos caracteres.
        if len(termino) < 2:
            return

        try:
            self.page.run_task(
                self._buscar_clientes,
                termino,
                numero_actual,
            )
        except RuntimeError:
            pass

    async def _buscar_clientes(self, termino, numero_actual):
        # Pequeña pausa para evitar consultas excesivas.
        await asyncio.sleep(0.30)

        if numero_actual != self._numero_busqueda:
            return

        try:
            clientes = self.servicio_cliente.buscar_por_nombre(termino)

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

    def _mostrar_resultados(self, clientes):
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
                    getattr(cliente, "razon_social", "")
                    or "Sin razón social"
                )

                rfc = (
                    getattr(cliente, "rfc", None)
                    or "No registrado"
                )

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

    def _seleccionar_cliente(self, cliente):
        self._numero_busqueda += 1

        self.cliente_id_seleccionado = int(cliente.id)
        self.campo.value = cliente.razon_social or ""

        self._ocultar_resultados()
        self._actualizar()

    def establecer_cliente(self, cliente):
        if cliente is None:
            self.limpiar()
            return

        self._numero_busqueda += 1

        try:
            cliente_id = getattr(cliente, "id", None)
            razon_social = getattr(cliente, "razon_social", "") or ""
        except Exception:
            cliente_id = None
            razon_social = ""

        self.cliente_id_seleccionado = (
            int(cliente_id) if cliente_id is not None else None
        )
        self.campo.value = razon_social

        self._ocultar_resultados()
        self._actualizar()

    def limpiar(self):
        self._numero_busqueda += 1

        self.cliente_id_seleccionado = None
        self.campo.value = ""

        self._ocultar_resultados()
        self._actualizar()

    def _ocultar_resultados(self):
        self.contenido_resultados.visible = False
        self.lista_resultados.controls.clear()

    def _actualizar(self):
        try:
            if self.page:
                self.page.update()
            else:
                self.update()
        except RuntimeError:
            pass