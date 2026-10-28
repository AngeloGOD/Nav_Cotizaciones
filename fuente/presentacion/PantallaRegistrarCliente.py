import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorRegistrarCliente import (
    ControladorRegistrarCliente,
    ErrorRegistroCliente,
)


class PantallaRegistrarCliente(ft.Container):
    def __init__(self, page: ft.Page, servicio_cliente, vista_anterior=None):
        super().__init__(expand=True, bgcolor=COLOR_FONDO)

        self._page = page
        self.vista_anterior = vista_anterior
        self.servicio_cliente = servicio_cliente
        self.controlador = ControladorRegistrarCliente(servicio_cliente)

        # Campos de una sola línea: ancho completo de su columna y altura uniforme.
        self.nombre = self.ajustar_campo(campo("Ej. ABC Logistics S.A. de C.V.", None))
        self.rfc = self.ajustar_campo(campo("Ej. ABC010203XYZ", None))
        self.telefono = self.ajustar_campo(campo("Ej. +52 962 123 4567", None))
        self.correo = self.ajustar_campo(campo("Ej. cliente@empresa.com", None))

        self.tipo_persona = ft.Dropdown(
            hint_text="Selecciona un tipo de persona",
            options=[
                ft.DropdownOption(key="FISICA", text="Persona Física"),
                ft.DropdownOption(key="MORAL", text="Persona Moral"),
                ft.DropdownOption(key="EXTRANJERO", text="Extranjero"),
            ],
            width=360,
            menu_width=360,
            height=44,
            text_size=14,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
        )

        self.es_nuevo_cliente = ft.Switch(value=False, active_color=COLOR_NARANJA)
        self.activo = ft.Switch(value=True, active_color=COLOR_NARANJA)

        self.direccion_fiscal = campo(
            "Ej. Calle, número, colonia, ciudad, estado, código postal, país.",
            None,
            multiline=True,
            min_lines=2,
            max_lines=3,
        )
        self.direccion_fiscal.width = float("inf")
        self.direccion_fiscal.height = 66
        self.direccion_fiscal.content_padding = ft.Padding(12, 8, 12, 8)
        self.direccion_fiscal.text_size = 14

        # El encabezado permanece arriba y la zona de campos puede desplazarse.
        # Los botones están fuera de esa zona para permanecer siempre visibles.
        self.content = ft.Container(
            expand=True,
            padding=ft.Padding(24, 8, 24, 10),
            content=ft.Column(
                expand=True,
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[self.encabezado(), self.formulario()],
            ),
        )

    def ajustar_campo(self, control):
        control.width = float("inf")
        control.height = 44
        control.content_padding = ft.Padding(12, 8, 12, 8)
        control.text_size = 14
        return control

    def encabezado(self):
        return banner_imagen_desvanecida(
            "fondo_PantallaRegistrarClientes.jpg",
            altura=136,
            content=ft.Container(
                expand=True,
                padding=ft.Padding(22, 8, 22, 8),
                content=ft.Row(
                    spacing=18,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=68,
                            height=68,
                            border_radius=34,
                            bgcolor="#FFF0E5",
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(
                                ft.Icons.GROUPS_OUTLINED,
                                size=36,
                                color=COLOR_NARANJA,
                            ),
                        ),
                        ft.Column(
                            expand=True,
                            spacing=4,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    "REGISTRO DE CLIENTES",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                ),
                                ft.Text(
                                    "Registrar nuevo cliente",
                                    size=29,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                ),
                                ft.Text(
                                    "Completa la información fiscal y de contacto del cliente.",
                                    size=16,
                                    color=COLOR_BANNER,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )

    def formulario(self):
        datos_generales = ft.Column(
            spacing=10,
            controls=[
                ft.Row(
                    spacing=18,
                    controls=[
                        ft.Container(
                            expand=1,
                            content=self.campo_etiquetado(
                                "Nombre o razón social *", ft.Icons.PERSON_OUTLINED, self.nombre
                            ),
                        ),
                        ft.Container(
                            expand=1,
                            content=self.campo_etiquetado(
                                "RFC *", ft.Icons.BADGE_OUTLINED, self.rfc
                            ),
                        ),
                    ],
                ),
                ft.Row(
                    spacing=18,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            expand=4,
                            content=self.campo_etiquetado(
                                "Tipo de persona *", ft.Icons.PERSON_OUTLINE, self.tipo_persona
                            ),
                        ),
                        ft.Container(expand=7, content=self.panel_estados()),
                    ],
                ),
            ],
        )

        contacto = ft.Row(
            spacing=18,
            controls=[
                ft.Container(
                    expand=1,
                    content=self.campo_etiquetado(
                        "Número telefónico *", ft.Icons.PHONE_OUTLINED, self.telefono
                    ),
                ),
                ft.Container(
                    expand=1,
                    content=self.campo_etiquetado(
                        "Correo electrónico *", ft.Icons.MAIL_OUTLINE, self.correo
                    ),
                ),
            ],
        )

        domicilio = self.campo_etiquetado(
            "Dirección fiscal completa *", ft.Icons.LOCATION_ON_OUTLINED, self.direccion_fiscal
        )

        contenido_desplazable = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                self.seccion(ft.Icons.ASSIGNMENT_OUTLINED, "Datos generales", datos_generales),
                ft.Divider(height=1, color=COLOR_GRIS_CLARO),
                self.seccion(ft.Icons.PHONE_OUTLINED, "Información de contacto", contacto),
                self.seccion(ft.Icons.LOCATION_ON_OUTLINED, "Domicilio fiscal", domicilio),
            ],
        )

        pie_formulario = ft.Column(
            spacing=8,
            controls=[
                ft.Divider(height=1, color=COLOR_GRIS_CLARO),
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        boton(
                            texto="Cancelar",
                            icono=ft.Icons.ARROW_BACK,
                            tipo="secundario",
                            color=COLOR_BANNER,
                            height=42,
                            width=120,
                            on_click=self.cancelar,
                        ),
                        boton(
                            texto="Guardar cliente",
                            icono=ft.Icons.SAVE_OUTLINED,
                            tipo="principal",
                            height=44,
                            width=178,
                            on_click=self.guardar,
                        ),
                    ],
                ),
            ],
        )

        return card(
            ft.Column(
                expand=True,
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[contenido_desplazable, pie_formulario],
            ),
            padding=ft.Padding(18, 16, 18, 14),
            radius=14,
            shadow=sombra_suave(),
            expand=True,
        )

    def campo_etiquetado(self, titulo, icono, control):
        return ft.Column(
            width=float("inf"),
            spacing=5,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(icono, size=18, color=COLOR_BANNER),
                        ft.Text(
                            titulo,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                    ],
                ),
                control,
            ],
        )

    def panel_estados(self):
        return ft.Container(
            bgcolor="#F7FAFD",
            border_radius=10,
            padding=ft.Padding(12, 8, 12, 8),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        expand=True,
                        content=self.opcion_estado(
                            self.es_nuevo_cliente,
                            "Es nuevo cliente",
                            "Marca si es un cliente por primera vez.",
                        ),
                    ),
                    ft.Container(width=1, height=42, bgcolor=COLOR_GRIS_CLARO),
                    ft.Container(
                        expand=True,
                        content=self.opcion_estado(
                            self.activo,
                            "Cliente activo",
                            "El cliente puede ser utilizado en cotizaciones.",
                        ),
                    ),
                ],
            ),
        )

    def opcion_estado(self, control, titulo, descripcion):
        return ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                control,
                ft.Column(
                    expand=True,
                    spacing=3,
                    controls=[
                        ft.Text(
                            titulo,
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            descripcion,
                            size=12,
                            color=COLOR_GRIS,
                            max_lines=2,
                        ),
                    ],
                ),
            ],
        )

    def seccion(self, icono, titulo, contenido):
        return ft.Column(
            spacing=9,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(icono, size=22, color=COLOR_NARANJA),
                        ft.Text(
                            titulo,
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Container(expand=True, height=1, bgcolor=COLOR_GRIS_CLARO),
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
        razon_social = self.nombre.value
        rfc = self.rfc.value
        direccion = self.direccion_fiscal.value
        telefono = self.telefono.value
        correo = self.correo.value
        tipo_persona = self.tipo_persona.value
        es_nuevo_cliente = bool(self.es_nuevo_cliente.value)
        activo = bool(self.activo.value)

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
        except ValueError as error:
            mostrar_notificacion(self._page, str(error), COLOR_ROJO)
            return
        except ErrorRegistroCliente as error:
            mostrar_notificacion(self._page, str(error), COLOR_ROJO)
            return

        mostrar_notificacion(
            self._page,
            "Cliente registrado correctamente.",
            COLOR_VERDE,
        )
        if self.vista_anterior:
            self.vista_anterior.build_ui()
            self.vista_anterior.actualizar_directorio()
        self._page.update()
