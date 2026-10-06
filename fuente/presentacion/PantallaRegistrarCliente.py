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

        self.nombre = ft.TextField(
            hint_text="Nombre o razón social *",
            prefix_icon=ft.Icons.BUSINESS_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=14,
        )

        self.rfc = ft.TextField(
            hint_text="RFC *",
            prefix_icon=ft.Icons.BADGE_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=14,
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

        self.telefono = ft.TextField(
            hint_text="Número telefónico *",
            prefix_icon=ft.Icons.PHONE_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=14,
        )

        self.correo = ft.TextField(
            hint_text="Correo electrónico *",
            prefix_icon=ft.Icons.MAIL_OUTLINE,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=14,
        )

        self.direccion_fiscal = ft.TextField(
            expand=True,
            hint_text="Dirección fiscal completa *",
            prefix_icon=ft.Icons.LOCATION_ON_OUTLINED,
            multiline=True,
            min_lines=4,
            max_lines=5,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=14,
        )

        formulario = card(
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
                        ft.Row(
                            expand=True,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    content=self.direccion_fiscal,
                                )
                            ],
                        ),
                    ),

                    ft.Divider(
                        height=1,
                        color=COLOR_GRIS_CLARO,
                    ),

                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.OutlinedButton(
                                content=ft.Row(
                                    tight=True,
                                    spacing=7,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.ARROW_BACK,
                                            size=18,
                                            color=COLOR_GRIS,
                                        ),
                                        ft.Text(
                                            "Cancelar",
                                            size=14,
                                            color=COLOR_GRIS,
                                        ),
                                    ],
                                ),
                                style=ft.ButtonStyle(
                                    color=COLOR_GRIS,
                                    side=ft.BorderSide(
                                        1,
                                        COLOR_GRIS_CLARO,
                                    ),
                                    shape=ft.RoundedRectangleBorder(
                                        radius=9,
                                    ),
                                    padding=ft.Padding(
                                        left=18,
                                        right=18,
                                        top=12,
                                        bottom=12,
                                    ),
                                ),
                                on_click=self.cancelar,
                            ),

                            ft.FilledButton(
                                content=ft.Row(
                                    tight=True,
                                    spacing=8,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.SAVE_OUTLINED,
                                            size=19,
                                            color=COLOR_BLANCO,
                                        ),
                                        ft.Text(
                                            "Guardar cliente",
                                            size=14,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_BLANCO,
                                        ),
                                    ],
                                ),
                                style=ft.ButtonStyle(
                                    bgcolor=COLOR_NARANJA,
                                    color=COLOR_BLANCO,
                                    shape=ft.RoundedRectangleBorder(
                                        radius=9,
                                    ),
                                    padding=ft.Padding(
                                        left=22,
                                        right=22,
                                        top=12,
                                        bottom=12,
                                    ),
                                ),
                                on_click=self.guardar,
                            ),
                        ],
                    ),
                ],
            ),
            padding=24,
            radius=14,
            border_color=COLOR_GRIS_CLARO,
            shadow=sombra_suave(),
            expand=True,
        )

        encabezado = ft.Container(
            padding=ft.Padding(
                left=24,
                right=18,
                top=10,
                bottom=10,
            ),
            border_radius=14,
            shadow=sombra_suave(),
            bgcolor=COLOR_BLANCO,
            border=ft.Border.all(
                1,
                COLOR_GRIS_CLARO,
            ),
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

                    ft.Container(
                        width=330,
                        height=80,
                        border_radius=12,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(
                            src="fondo_PantallaRegistrarClientes.jpg",
                            width=330,
                            height=80,
                            fit=ft.BoxFit.COVER,
                        ),
                    ),
                ],
            ),
        )

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Container(
                    padding=ft.Padding(
                        left=24,
                        right=24,
                        top=20,
                        bottom=24,
                    ),
                    content=ft.Column(
                        expand=True,
                        spacing=16,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            encabezado,
                            formulario,
                        ],
                    ),
                )
            ],
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
            self.vista_anterior.update()

    def guardar(self, e):
        pass