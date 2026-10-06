import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *


class PantallaRegistrarEmbarcacion(ft.Container):
    def __init__(self, page: ft.Page, vista_anterior=None):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page
        self.vista_anterior = vista_anterior

        self.nombre = self._crear_campo_texto("Nombre del buque *", ft.Icons.DIRECTIONS_BOAT_OUTLINED)
        self.matricula = self._crear_campo_texto("Matrícula *", ft.Icons.BADGE_OUTLINED)
        self.imo = self._crear_campo_texto("Número IMO", ft.Icons.NUMBERS_OUTLINED)
        self.bandera = self._crear_campo_texto("Bandera", ft.Icons.FLAG_OUTLINED)
        
        self.tipo_embarcacion = ft.Dropdown(
            hint_text="Tipo de embarcación *",
            leading_icon=ft.Icons.CATEGORY_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            options=[
                ft.DropdownOption(key="TUNA PURSE SEINER", text="Atunero (Tuna Purse Seiner)"),
                ft.DropdownOption(key="CARGO", text="Buque de Carga (Cargo)"),
                ft.DropdownOption(key="TANKER", text="Buque Tanque (Tanker)"),
                ft.DropdownOption(key="YACHT", text="Yate (Yacht)"),
                ft.DropdownOption(key="TUG", text="Remolcador (Tug)"),
                ft.DropdownOption(key="OTHER", text="Otro"),
            ],
        )

        # Campos numéricos para especificaciones técnicas
        self.loa = self._crear_campo_numerico("Eslora / LOA (m)")
        self.manga = self._crear_campo_numerico("Manga (m)")
        self.puntual = self._crear_campo_numerico("Puntal (m)")
        self.calado_draft = self._crear_campo_numerico("Calado / Draft (m)")
        
        self.gtr = self._crear_campo_numerico("Arqueo Bruto / GTR")
        self.trb = self._crear_campo_numerico("TRB")
        self.tonelaje = self._crear_campo_numerico("Tonelaje (t)")
        self.volumen_cubico = self._crear_campo_numerico("Vol. Cúbico (m³)")

        self.build_ui()

    def _crear_campo_texto(self, hint, icono):
        return ft.TextField(
            hint_text=hint,
            prefix_icon=icono,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=14,
        )

    def _crear_campo_numerico(self, hint):
        return ft.TextField(
            hint_text=hint,
            prefix_icon=ft.Icons.STRAIGHTEN_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=14,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9.]*$", replacement_string="")
        )

    def build_ui(self):
        formulario = card(
            ft.Column(
                spacing=24,
                controls=[
                    self.seccion(
                        ft.Icons.DIRECTIONS_BOAT_OUTLINED,
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
                                            content=self.matricula,
                                        ),
                                        ft.Container(
                                            expand=True,
                                            content=self.imo,
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    spacing=14,
                                    controls=[
                                        ft.Container(
                                            expand=True,
                                            content=self.tipo_embarcacion,
                                        ),
                                        ft.Container(
                                            expand=True,
                                            content=self.bandera,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),

                    self.seccion(
                        ft.Icons.SQUARE_FOOT_OUTLINED,
                        "Especificaciones físicas y arqueo",
                        ft.Column(
                            spacing=12,
                            controls=[
                                ft.Row(
                                    spacing=14,
                                    controls=[
                                        ft.Container(expand=True, content=self.loa),
                                        ft.Container(expand=True, content=self.manga),
                                        ft.Container(expand=True, content=self.puntual),
                                        ft.Container(expand=True, content=self.calado_draft),
                                    ],
                                ),
                                ft.Row(
                                    spacing=14,
                                    controls=[
                                        ft.Container(expand=True, content=self.gtr),
                                        ft.Container(expand=True, content=self.trb),
                                        ft.Container(expand=True, content=self.tonelaje),
                                        ft.Container(expand=True, content=self.volumen_cubico),
                                    ],
                                ),
                            ]
                        )
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
                                            "Guardar embarcación",
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
            shadow=ft.BoxShadow(
                blur_radius=18,
                color="black12",
                offset=ft.Offset(0, 4),
            ),
            expand=True,
        )

        encabezado = ft.Container(
            padding=ft.Padding(
                left=24,
                right=18,
                top=18,
                bottom=18,
            ),
            border_radius=14,
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
                        ft.Icons.SAILING_OUTLINED,
                        size=48,
                        color=COLOR_NARANJA,
                    ),

                    ft.Column(
                        expand=True,
                        spacing=5,
                        controls=[
                            ft.Text(
                                "Registrar nueva embarcación",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Text(
                                "Ingresa los datos de registro marítimo y características técnicas del buque.",
                                size=14,
                                color=COLOR_GRIS,
                            ),
                        ],
                    ),

                    ft.Container(
                        width=330,
                        height=105,
                        border_radius=12,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Image(
                            src="assets/barco_banner_opl.png",
                            width=330,
                            height=105,
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