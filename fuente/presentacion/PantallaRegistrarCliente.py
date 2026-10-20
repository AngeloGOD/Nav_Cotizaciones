import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorClientes import ControladorClientes


class PantallaRegistrarCliente(ft.Container):
    def __init__(self, page: ft.Page, servicio_cliente, vista_anterior=None):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page
        self.vista_anterior = vista_anterior
        self.servicio_cliente = servicio_cliente
        self.controlador = ControladorClientes(servicio_cliente)

        self.nombre = campo(
            "Nombre o razón social *",
            ft.Icons.BUSINESS_OUTLINED,
        )

        self.rfc = campo(
            "RFC",
            ft.Icons.BADGE_OUTLINED,
        )

        self.tipo_persona = ft.Dropdown(
            hint_text="Tipo de persona *",
            leading_icon=ft.Icons.GROUP_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            options=[
                ft.DropdownOption(
                    key="FISICA",
                    text="Persona Física",
                ),
                ft.DropdownOption(
                    key="MORAL",
                    text="Persona Moral",
                ),
                ft.DropdownOption(
                    key="EXTRANJERO",
                    text="Extranjero",
                ),
            ],
        )

        self.es_nuevo_cliente = ft.Switch(
            label="Es nuevo cliente",
            value=False,
            active_color=COLOR_NARANJA,
        )

        self.activo = ft.Switch(
            label="Cliente activo",
            value=True,
            active_color=COLOR_NARANJA,
        )

        self.telefono = campo(
            "Número telefónico",
            ft.Icons.PHONE_OUTLINED,
        )

        self.correo = campo(
            "Correo electrónico",
            ft.Icons.MAIL_OUTLINE,
        )

        self.direccion_fiscal = campo(
            "Dirección fiscal completa",
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
                                ft.Row(
                                    spacing=24,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            expand=True,
                                            content=self.tipo_persona,
                                        ),
                                        ft.Container(
                                            content=self.es_nuevo_cliente,
                                        ),
                                        ft.Container(
                                            content=self.activo,
                                        ),
                                    ],
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
        razon_social = (self.nombre.value or "").strip()
        rfc = (self.rfc.value or "").strip()
        direccion = (self.direccion_fiscal.value or "").strip()
        telefono = (self.telefono.value or "").strip()
        correo = (self.correo.value or "").strip()
        tipo_persona = (self.tipo_persona.value or "").strip()
        es_nuevo_cliente = bool(self.es_nuevo_cliente.value)
        activo = bool(self.activo.value)

        if not razon_social or not tipo_persona:
            self._page.show_dialog(
                ft.SnackBar(content=ft.Text("Completa todos los campos obligatorios."))
            )
            self._page.update()
            return

        try:
            self.controlador.registrar_cliente(
                razon_social=razon_social,
                tipo_persona=tipo_persona,
                direccion=direccion,
                rfc=rfc,
                telefono=telefono,
                correo_elect=correo,
                es_nuevo_cliente=es_nuevo_cliente,
                activo=activo,
            )
            self._page.show_dialog(
                ft.SnackBar(content=ft.Text("Cliente registrado correctamente."))
            )
            if self.vista_anterior:
                self.vista_anterior.build_ui()
                self.vista_anterior.actualizar_directorio()
            self._page.update()
        except Exception:
            self._page.show_dialog(
                ft.SnackBar(content=ft.Text("No se pudo guardar el cliente."))
            )
            self._page.update()
