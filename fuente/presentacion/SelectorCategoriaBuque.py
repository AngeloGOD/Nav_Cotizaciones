import asyncio
import flet as ft

from fuente.utilidades.Colores import (
    COLOR_GRIS,
    COLOR_GRIS_CLARO,
    COLOR_NEGRO,
    COLOR_NARANJA,
)


class SelectorCategoriaBuque(ft.Stack):

    def __init__(self, servicio_categoria_buque, height=58):
        super().__init__(
            expand=True,
            height=height,
            clip_behavior=ft.ClipBehavior.NONE,
        )

        self.servicio_categoria_buque = servicio_categoria_buque
        self.categoria_buque_id_seleccionada = None
        self.categoria_seleccionada = None
        self._numero_busqueda = 0

        self.campo = ft.TextField(
            expand=True,
            label="Categoría del buque *",
            hint_text="Buscar categoría del buque...",
            height=height,
            text_size=14,
            border_radius=9,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            prefix_icon=ft.Icons.CATEGORY_OUTLINED,
            content_padding=ft.Padding(14, 12, 14, 12),
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
    def value(self):
        return self.campo.value

    @value.setter
    def value(self, val):
        self.campo.value = val

    def _al_cambiar_texto(self, e=None):
        self._numero_busqueda += 1
        numero_actual = self._numero_busqueda

        termino = (self.campo.value or "").strip()
        self.categoria_buque_id_seleccionada = None
        self.categoria_seleccionada = None

        self._ocultar_resultados()
        self._actualizar()

        if len(termino) < 1:
            return

        try:
            self.page.run_task(
                self._buscar_categorias,
                termino,
                numero_actual,
            )
        except RuntimeError:
            pass

    async def _buscar_categorias(self, termino, numero_actual):
        await asyncio.sleep(0.40)

        if numero_actual != self._numero_busqueda:
            return

        try:
            if hasattr(self.servicio_categoria_buque, "obtener_pagina"):
                categorias = self.servicio_categoria_buque.obtener_pagina(
                    1, limite=10, filtros={"nombre": termino}
                )
            elif hasattr(self.servicio_categoria_buque, "obtener_categorias_buque"):
                categorias = self.servicio_categoria_buque.obtener_categorias_buque(
                    1, limite=10, filtros={"nombre": termino}
                )
            else:
                categorias = []
        except Exception as error:
            print(f"Error al buscar categorías de buque: {error}")

            if numero_actual == self._numero_busqueda:
                self._ocultar_resultados()
                self._actualizar()

            return

        if numero_actual != self._numero_busqueda:
            return

        if (self.campo.value or "").strip() != termino:
            return

        self._mostrar_resultados(categorias)

    def _mostrar_resultados(self, categorias):
        self.lista_resultados.controls.clear()

        if not categorias:
            self.lista_resultados.controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Text(
                        "No se encontraron categorías de buque.",
                        size=12,
                        color=COLOR_GRIS,
                    ),
                )
            )
        else:
            for categoria in categorias:
                nombre_cat = (
                    getattr(categoria, "categoria", "")
                    or "Sin categoría"
                )
                id_cat = getattr(categoria, "id", "")

                self.lista_resultados.controls.append(
                    ft.Container(
                        padding=ft.Padding(10, 9, 10, 9),
                        border_radius=7,
                        bgcolor="#F4F8FC",
                        on_click=lambda e, cat=categoria: self._seleccionar_categoria(cat),
                        content=ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    content=ft.Text(
                                        nombre_cat,
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
                                            "ID",
                                            size=10,
                                            color=COLOR_GRIS,
                                            weight=ft.FontWeight.BOLD,
                                        ),
                                        ft.Text(
                                            str(id_cat),
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

    def _seleccionar_categoria(self, categoria):
        self._numero_busqueda += 1

        self.categoria_buque_id_seleccionada = int(categoria.id)
        self.categoria_seleccionada = categoria
        self.campo.value = categoria.categoria or ""

        self._ocultar_resultados()
        self._actualizar()

    def establecer_categoria(self, categoria):
        if categoria is None:
            self.limpiar()
            return

        self._numero_busqueda += 1

        self.categoria_buque_id_seleccionada = int(categoria.id)
        self.categoria_seleccionada = categoria
        self.campo.value = getattr(categoria, "categoria", "") or ""

        self._ocultar_resultados()
        self._actualizar()

    def limpiar(self):
        self._numero_busqueda += 1

        self.categoria_buque_id_seleccionada = None
        self.categoria_seleccionada = None
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
