import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *


class PantallaRegistrarCliente(ft.Container):
    def __init__(self, page: ft.Page, vista_anterior=None):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page
        self.vista_anterior = vista_anterior

        self.nombre = campo(
            "Nombre o razón social *",
            ft.Icons.BUSINESS_OUTLINED,
        )

        self.rfc = campo(
            "RFC *",
            ft.Icons.BADGE_OUTLINED,
        )

        self.tipo_cliente = ft.Dropdown(
            hint_text="Tipo de cliente *",
            leading_icon=ft.Icons.GROUP_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            options=[
                ft.DropdownOption(
                    key="Agencia",
                    text="Agencia naviera",
                ),
                ft.DropdownOption(
                    key="Armador",
                    text="Armador",
                ),
                ft.DropdownOption(
                    key="Cliente",
                    text="Cliente",
                ),
            ],
        )

        self.telefono = campo(
            "Número telefónico *",
            ft.Icons.PHONE_OUTLINED,
        )

        self.correo = campo(
            "Correo electrónico *",
            ft.Icons.MAIL_OUTLINE,
        )

        self.direccion_fiscal = campo(
            "Dirección fiscal completa *",
            ft.Icons.LOCATION_ON_OUTLINED,
            expand=True,
            multiline=True,
            min_lines=4,
            max_lines=5,
        )

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Container(
                    padding=ft.Padding(24, 20, 24, 24),
                    content=ft.Column(
                        expand=True,
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            self.encabezado(),
                            self.formulario(),
                        ],
                    ),
                )
            ],
        )

    def formulario(self):
        return card(
            ft.Column(
                spacing=24,
                controls=[
                    self.seccion(
                        ft.Icons.BUSINESS_OUTLINED,
                        "Datos generales",
                        ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    spacing=14,
                                    controls=[
                                        ft.Container(
                                            expand=True,
                                            content=self.nombre,
                                        ),
                                        ft.Container(
                                            expand=True,
                                            content=self.rfc,
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    width=560,
                                    content=self.tipo_cliente,
                                ),
                            ],
                        ),
                    ),

                    self.seccion(
                        ft.Icons.PHONE_OUTLINED,
                        "Información de contacto",
                        ft.Row(
                            spacing=14,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    content=self.telefono,
                                ),
                                ft.Container(
                                    expand=True,
                                    content=self.correo,
                                ),
                            ],
                        ),
                    ),

                    self.seccion(
                        ft.Icons.LOCATION_ON_OUTLINED,
                        "Domicilio fiscal",
                        self.direccion_fiscal,
                    ),

                    ft.Divider(
                        height=1,
                        color=COLOR_GRIS_CLARO,
                    ),

                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            boton(
                                texto="Cancelar",
                                icono=ft.Icons.ARROW_BACK,
                                tipo="secundario",
                                color=COLOR_GRIS,
                                height=44,
                                width=125,
                                on_click=self.cancelar,
                            ),
                            boton(
                                texto="Guardar cliente",
                                icono=ft.Icons.SAVE_OUTLINED,
                                tipo="principal",
                                height=44,
                                width=175,
                                on_click=self.guardar,
                            ),
                        ],
                    ),
                ],
            ),
            padding=24,
            radius=14,
            shadow=sombra_suave(),
            expand=True,
        )

    def encabezado(self):
        return banner_imagen_desvanecida(
            "fondo_PantallaRegistrarClientes.jpg",
            altura=120,
            content=ft.Container(
                expand=True,
                padding=ft.Padding(24, 10, 24, 10),
                content=ft.Row(
                    expand=True,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=18,
                    controls=[
                        ft.Icon(
                            ft.Icons.PERSON_ADD_OUTLINED,
                            size=48,
                            color=COLOR_NARANJA,
                        ),

                        ft.Column(
                            expand=True,
                            spacing=5,
                            controls=[
                                ft.Text(
                                    "Registrar nuevo cliente",
                                    size=28,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                ),
                                ft.Text(
                                    "Completa la información fiscal y de contacto del cliente.",
                                    size=14,
                                    color=COLOR_GRIS,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )

    def seccion(self, icono, titulo, contenido):
        return ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            icono,
                            size=23,
                            color=COLOR_NARANJA,
                        ),
                        ft.Text(
                            titulo,
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Container(
                            expand=True,
                            height=1,
                            bgcolor=COLOR_GRIS_CLARO,
                        ),
                    ],
                ),
                contenido,
            ],
        )

    def cancelar(self, e):
        if self.vista_anterior:
            self.vista_anterior.build_ui()
            self._page.update()

    def guardar(self, e):
        pass