import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorBuque import ControladorBuque


class PantallaRegistrarBuque(ft.Container):
    def __init__(
        self, page: ft.Page, servicio_buque,
        vista_anterior=None, buque_a_editar=None
    ):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page
        self.vista_anterior = vista_anterior
        self.servicio_buque = servicio_buque
        self.controlador = ControladorBuque(servicio_buque)
        self.buque_a_editar = buque_a_editar
        self.modo_edicion = buque_a_editar is not None

        self.nombre = self._crear_campo_texto("Nombre del buque *", ft.Icons.DIRECTIONS_BOAT_OUTLINED)
        self.numero_imo = self._crear_campo_texto("Número IMO", ft.Icons.NUMBERS_OUTLINED)
        self.cliente_id = self._crear_campo_entero("ID del cliente (opcional)", ft.Icons.PERSON_OUTLINE)
        self.bandera_pais = self._crear_campo_texto("Bandera / País", ft.Icons.FLAG_OUTLINED)
        self.subtipo_descripcion = self._crear_campo_texto("Subtipo o descripción", ft.Icons.DESCRIPTION_OUTLINED)

        self.categoria_buque = ft.Dropdown(
            hint_text="Categoría del buque *",
            leading_icon=ft.Icons.CATEGORY_OUTLINED,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            options=[
                ft.DropdownOption(key="COMERCIAL", text="Comercial (Carga general, portacontenedores, granelero)"),
                ft.DropdownOption(key="TURISTICO", text="Turístico (Cruceros)"),
                ft.DropdownOption(key="PESQUERO", text="Pesquero (Atuneros, camaroneros, etc.)"),
                ft.DropdownOption(key="PETROLERO", text="Petrolero (Tanqueros, gaseros, petroquímicos)"),
                ft.DropdownOption(key="RO_RO", text="Ro-Ro (Roll On - Roll Off)"),
                ft.DropdownOption(key="RECREO_MENOR", text="Recreo y Embarcación Menor (Yates, veleros)"),
            ],
        )

        # Campos numéricos para especificaciones técnicas
        self.trb_arqueo_bruto = self._crear_campo_numerico("Arqueo Bruto / TRB *")
        self.eslora_metros = self._crear_campo_numerico("Eslora (m) *")
        self.calado_metros = self._crear_campo_numerico("Calado (m)")

        # Controles booleanos de propulsión y estado
        self.es_autopropulsado = ft.Switch(
            label="Es autopropulsado",
            value=True,
            active_color=COLOR_NARANJA,
        )
        self.propulsores_proa_popa = ft.Switch(
            label="Propulsores proa/popa",
            value=False,
            active_color=COLOR_NARANJA,
        )
        self.activo = ft.Switch(
            label="Buque activo",
            value=True,
            active_color=COLOR_NARANJA,
        )
        if self.buque_a_editar is not None:
            self.nombre.value = self.buque_a_editar.nombre or ""
            self.numero_imo.value = self.buque_a_editar.numero_imo or ""
            self.cliente_id.value = (
                str(self.buque_a_editar.cliente_id)
                if self.buque_a_editar.cliente_id is not None else ""
            )
            self.bandera_pais.value = self.buque_a_editar.bandera_pais or ""
            self.subtipo_descripcion.value = (
                self.buque_a_editar.subtipo_descripcion or ""
            )

            categoria = self.buque_a_editar.categoria_buque
            self.categoria_buque.value = (
                categoria.value if hasattr(categoria, "value") else str(categoria)
            ) if categoria else None

            self.trb_arqueo_bruto.value = str(
                self.buque_a_editar.trb_arqueo_bruto or ""
            )
            self.eslora_metros.value = str(
                self.buque_a_editar.eslora_metros or ""
            )
            self.calado_metros.value = (
                str(self.buque_a_editar.calado_metros)
                if self.buque_a_editar.calado_metros is not None else ""
            )

            self.es_autopropulsado.value = bool(
                self.buque_a_editar.es_autopropulsado
            )
            self.propulsores_proa_popa.value = bool(
                self.buque_a_editar.propulsores_proa_popa
            )
            self.activo.value = bool(self.buque_a_editar.activo)

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

    def _crear_campo_entero(self, hint, icono):
        return ft.TextField(
            hint_text=hint,
            prefix_icon=icono,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=14,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string="")
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
                                            content=self.numero_imo,
                                        ),
                                        ft.Container(
                                            expand=True,
                                            content=self.cliente_id,
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    spacing=14,
                                    controls=[
                                        ft.Container(
                                            expand=True,
                                            content=self.categoria_buque,
                                        ),
                                        ft.Container(
                                            expand=True,
                                            content=self.subtipo_descripcion,
                                        ),
                                        ft.Container(
                                            expand=True,
                                            content=self.bandera_pais,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),

                    self.seccion(
                        ft.Icons.SQUARE_FOOT_OUTLINED,
                        "Especificaciones físicas, arqueo y propulsión",
                        ft.Column(
                            spacing=16,
                            controls=[
                                ft.Row(
                                    spacing=14,
                                    controls=[
                                        ft.Container(expand=True, content=self.trb_arqueo_bruto),
                                        ft.Container(expand=True, content=self.eslora_metros),
                                        ft.Container(expand=True, content=self.calado_metros),
                                    ],
                                ),
                                ft.Row(
                                    spacing=24,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(content=self.es_autopropulsado),
                                        ft.Container(content=self.propulsores_proa_popa),
                                        ft.Container(content=self.activo),
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
                                            "Guardar cambios" if self.modo_edicion else "Guardar buque",
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
                                "Editar buque" if self.modo_edicion else "Registrar nuevo buque",
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
        nombre = (self.nombre.value or "").strip()
        numero_imo = (self.numero_imo.value or "").strip()
        cliente_id = (self.cliente_id.value or "").strip()
        categoria_buque = (self.categoria_buque.value or "").strip()
        subtipo_descripcion = (self.subtipo_descripcion.value or "").strip()
        bandera_pais = (self.bandera_pais.value or "").strip()
        trb_arqueo_bruto = (self.trb_arqueo_bruto.value or "").strip()
        eslora_metros = (self.eslora_metros.value or "").strip()
        calado_metros = (self.calado_metros.value or "").strip()
        es_autopropulsado = bool(self.es_autopropulsado.value)
        propulsores_proa_popa = bool(self.propulsores_proa_popa.value)
        activo = bool(self.activo.value)

        if not nombre or not categoria_buque or not trb_arqueo_bruto or not eslora_metros:
            self._page.show_dialog(
                ft.SnackBar(content=ft.Text("Completa todos los campos obligatorios."))
            )
            self._page.update()
            return


        try:
            datos_buque = {
                "nombre": nombre,
                "categoria_buque": categoria_buque,
                "trb_arqueo_bruto": trb_arqueo_bruto,
                "eslora_metros": eslora_metros,
                "cliente_id": cliente_id,
                "numero_imo": numero_imo,
                "subtipo_descripcion": subtipo_descripcion,
                "calado_metros": calado_metros,
                "propulsores_proa_popa": propulsores_proa_popa,
                "es_autopropulsado": es_autopropulsado,
                "bandera_pais": bandera_pais,
                "activo": activo,
            }

            if self.modo_edicion:
                self.controlador.modificar_buque(
                    buque=self.buque_a_editar,
                    **datos_buque,
                )
                mensaje = "Buque modificado correctamente."
            else:
                self.controlador.registrar_buque(**datos_buque)
                mensaje = "Buque registrado correctamente."

            self._page.show_dialog(
                ft.SnackBar(content=ft.Text(mensaje))
            )

            if self.vista_anterior:
                self.vista_anterior.build_ui()
                self.vista_anterior.actualizar_directorio()

            self._page.update()

        except Exception as error:
            print(f"Error al guardar el buque: {error}")
            self._page.show_dialog(
                ft.SnackBar(
                    content=ft.Text(
                        "No se pudieron guardar los cambios del buque."
                    )
                )
            )
            self._page.update()

