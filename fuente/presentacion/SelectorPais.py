import asyncio
import flet as ft

from fuente.infraestructura.servicios_externos.ServicioPaises import ServicioPaises
from fuente.utilidades.Colores import (
    COLOR_GRIS,
    COLOR_GRIS_CLARO,
    COLOR_NARANJA,
    COLOR_NEGRO,
)


class SelectorPais(ft.Stack):

    def __init__(self):
        super().__init__(
            expand=True,
            height=58,
            clip_behavior=ft.ClipBehavior.NONE,
        )

        self.pais_seleccionado = None
        self._numero_busqueda = 0

        self.campo = ft.TextField(
            expand=True,
            label="Bandera / país",
            hint_text="Buscar país (mín. 2 caracteres)...",
            prefix_icon=ft.Icons.FLAG_OUTLINED,
            height=58,
            text_size=14,
            border=ft.InputBorder.OUTLINE,
            border_radius=9,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
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
    def value(self, valor):
        self._numero_busqueda += 1
        self.campo.value = "" if valor is None else str(valor)
        self._ocultar_resultados()

    def _al_cambiar_texto(self, e=None):
        self._numero_busqueda += 1
        numero_actual = self._numero_busqueda

        termino = (self.campo.value or "").strip()
        self.pais_seleccionado = None

        self._ocultar_resultados()
        self._actualizar()

        if len(termino) < 2:
            return

        try:
            self.page.run_task(
                self._buscar_paises,
                termino,
                numero_actual,
            )
        except RuntimeError:
            pass

    async def _buscar_paises(self, termino, numero_actual):
        await asyncio.sleep(0.25)

        if numero_actual != self._numero_busqueda:
            return

        try:
            paises = ServicioPaises.buscar_paises(termino)
        except Exception as error:
            print(f"Error al buscar países: {error}")

            if numero_actual == self._numero_busqueda:
                self._ocultar_resultados()
                self._actualizar()

            return

        if numero_actual != self._numero_busqueda:
            return

        if (self.campo.value or "").strip() != termino:
            return

        self._mostrar_resultados(paises)

    def _mostrar_resultados(self, paises):
        self.lista_resultados.controls.clear()

        if not paises:
            self.lista_resultados.controls.append(
                ft.Container(
                    padding=10,
                    content=ft.Text(
                        "No se encontraron países.",
                        size=12,
                        color=COLOR_GRIS,
                    ),
                )
            )
        else:
            for pais in paises:
                nombre = pais.get("nombre", "") or ""
                emoji = pais.get("emoji", "") or ""
                codigo = pais.get("codigo", "") or ""

                self.lista_resultados.controls.append(
                    ft.Container(
                        padding=ft.Padding(10, 9, 10, 9),
                        border_radius=7,
                        bgcolor="#F4F8FC",
                        on_click=lambda e, p=pais: self._seleccionar_pais(p),
                        content=ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    content=ft.Text(
                                        f'{emoji}  {nombre}',
                                        size=12,
                                        weight=ft.FontWeight.W_500,
                                        color=COLOR_NEGRO,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ),
                                ft.Text(
                                    codigo,
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
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

    def _seleccionar_pais(self, pais):
        self._numero_busqueda += 1

        nombre = pais["nombre"] if isinstance(pais, dict) else str(pais or "")
        self.pais_seleccionado = pais
        self.value = nombre

        self._ocultar_resultados()
        self._actualizar()

    def establecer_pais(self, nombre_pais):
        if not nombre_pais:
            self.limpiar()
            return

        self._numero_busqueda += 1

        self.pais_seleccionado = nombre_pais
        self.campo.value = str(nombre_pais)

        self._ocultar_resultados()
        self._actualizar()

    def limpiar(self):
        self._numero_busqueda += 1

        self.pais_seleccionado = None
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
