import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorRegistrarBuques import ControladorRegistrarBuques
from fuente.infraestructura.servicios_externos.ServicioPaises import ServicioPaises
from fuente.presentacion.SelectorCliente import SelectorCliente


class PantallaRegistrarBuque(ft.Container):
    def __init__(
        self, page: ft.Page, servicio_buque, servicio_cliente,
        vista_anterior=None, buque_a_editar=None
    ):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page
        self.vista_anterior = vista_anterior
        self.servicio_buque = servicio_buque
        self.servicio_cliente = servicio_cliente
        self.controlador = ControladorRegistrarBuques(servicio_buque)
        self.buque_a_editar = buque_a_editar
        self.modo_edicion = buque_a_editar is not None
        self.nombre = self._crear_campo_etiquetado(
            etiqueta="Nombre del buque *",
            ejemplo="Ej. Ocean Star",
            icono=ft.Icons.DIRECTIONS_BOAT_OUTLINED,
        )
        self.numero_imo = self._crear_campo_etiquetado(
            etiqueta="Número IMO",
            ejemplo="Ej.  IMO 9876543",
            icono=ft.Icons.NUMBERS_OUTLINED,
        )
        self.cliente_busqueda = SelectorCliente(self.servicio_cliente)
        self.paises = []
        try:
            self.paises = ServicioPaises.obtener_paises()
        except RuntimeError:
            self.paises = []

        self._opciones_paises_bandera = [
            ft.DropdownOption(key=pais["nombre"], text=f'{pais["emoji"]}  {pais["nombre"]}')
            for pais in self.paises
        ]
        self._busqueda_pais_registro = ft.TextField(
            hint_text="Buscar país...",
            prefix_icon=ft.Icons.SEARCH,
            height=38,
            text_size=12,
            content_padding=ft.Padding(9, 5, 9, 5),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=8,
            on_change=self._filtrar_paises_registro,
        )
        # Campo de bandera modificado con expand y height
        self.bandera_pais = ft.TextField(
            expand=True,
            height=58,
            label="Bandera / país",
            hint_text="Ej. México",
            prefix_icon=ft.Icons.FLAG_OUTLINED,
            suffix_icon=ft.Icons.ARROW_DROP_DOWN,
            read_only=True,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=ft.Padding(14, 12, 14, 12),
            on_click=self._abrir_selector_pais,
        )
        self._lista_paises_registro = ft.Column(
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
            height=250,
            controls=[],
        )
        self._dialogo_selector_pais = None
        self.subtipo_descripcion = self._crear_campo_etiquetado(
            etiqueta="Subtipo o descripción",
            ejemplo="Ej. Portacontenedores, carga general...",
            icono=ft.Icons.DESCRIPTION_OUTLINED,
        )

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
        self.trb_arqueo_bruto = self._crear_campo_etiquetado(
            etiqueta="Arqueo Bruto / TRB *",
            ejemplo="Ej. 12500.50",
            icono=ft.Icons.SCALE_OUTLINED,
            numerico=True,
        )

        self.eslora_metros = self._crear_campo_etiquetado(
            etiqueta="Eslora (m) *",
            ejemplo="Ej. 150.30",
            icono=ft.Icons.STRAIGHTEN_OUTLINED,
            numerico=True,
        )

        self.calado_metros = self._crear_campo_etiquetado(
            etiqueta="Calado (m)",
            ejemplo="Ej. 8.75",
            icono=ft.Icons.WATER_OUTLINED,
            numerico=True,
        )

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
            cliente_obj = getattr(self.buque_a_editar, "cliente", None)
            self.cliente_busqueda.establecer_cliente(cliente_obj)
            pais_actual = self.buque_a_editar.bandera_pais or ""
            nombres_paises = {p["nombre"] for p in self.paises}
            if pais_actual and pais_actual not in nombres_paises:
                opcion_anterior = ft.DropdownOption(
                    key=pais_actual, text=f"🌐  {pais_actual} (valor anterior)"
                )
                self._opciones_paises_bandera.append(opcion_anterior)
                self.bandera_pais.options.append(opcion_anterior)
            self.bandera_pais.value = pais_actual or ""
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

    def _abrir_selector_pais(self, e=None):
        self._busqueda_pais_registro.value = ""
        self._construir_lista_paises_registro()
        self._dialogo_selector_pais = ft.AlertDialog(
            modal=True,
            bgcolor="#F4F8FC",
            shape=ft.RoundedRectangleBorder(radius=16),
            title=ft.Text("Seleccionar bandera / país", size=17, weight=ft.FontWeight.BOLD),
            title_padding=ft.Padding(18, 14, 18, 8),
            content=ft.Container(
                width=420,
                content=ft.Column(
                    tight=True,
                    spacing=10,
                    controls=[self._busqueda_pais_registro, self._lista_paises_registro],
                ),
            ),
            content_padding=ft.Padding(16, 4, 16, 0),
            actions=[ft.TextButton("Cancelar", on_click=self._cerrar_selector_pais)],
            actions_alignment=ft.MainAxisAlignment.END,
            actions_padding=ft.Padding(12, 6, 12, 10),
        )
        self._page.show_dialog(self._dialogo_selector_pais)

    def _cerrar_selector_pais(self, e=None):
        if self._dialogo_selector_pais is not None:
            self._page.pop_dialog()
            self._dialogo_selector_pais = None

    def _construir_lista_paises_registro(self):
        termino = (self._busqueda_pais_registro.value or "").strip().casefold()
        opciones = [
            opcion for opcion in self._opciones_paises_bandera
            if termino in str(opcion.text).casefold()
        ]
        self._lista_paises_registro.controls = [
            ft.Container(
                border_radius=7,
                padding=ft.Padding(8, 7, 8, 7),
                bgcolor="#FFF0E5" if str(opcion.key) == str(self.bandera_pais.value) else None,
                content=ft.Row(
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.CHECK_CIRCLE if str(opcion.key) == str(self.bandera_pais.value) else ft.Icons.CIRCLE_OUTLINED,
                                color=COLOR_NARANJA if str(opcion.key) == str(self.bandera_pais.value) else COLOR_GRIS_CLARO, size=17),
                        ft.Text(str(opcion.text), size=12, color=COLOR_NEGRO, expand=True),
                    ],
                ),
                on_click=lambda e, valor=opcion.key: self._seleccionar_pais_registro(valor),
            )
            for opcion in opciones
        ]
        if not opciones:
            self._lista_paises_registro.controls = [
                ft.Container(padding=10, content=ft.Text("No se encontraron países", size=12, color=COLOR_GRIS_CLARO))
            ]

    def _filtrar_paises_registro(self, e=None):
        self._construir_lista_paises_registro()

    def _seleccionar_pais_registro(self, valor):
        self.bandera_pais.value = str(valor)
        self.bandera_pais.update()
        self._cerrar_selector_pais()

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
    
    def _crear_campo_etiquetado(self, etiqueta, ejemplo, icono=None, numerico=False):
        return ft.TextField(
            label=etiqueta,
            hint_text=ejemplo,
            prefix_icon=icono,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
            text_size=14,
            content_padding=ft.Padding(14, 12, 14, 12),
            height=58,
            input_filter=(
                ft.InputFilter(
                    allow=True,
                    regex_string=r"^[0-9.]*$",
                    replacement_string="",
                )
                if numerico else None
            ),
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

    # Nuevo método integrado para manejar el Stack y resultados superpuestos
    def crear_datos_generales(self):
        return ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    spacing=14,
                    controls=[
                        ft.Container(expand=True, content=self.nombre),
                        ft.Container(expand=True, content=self.numero_imo),
                        ft.Container(expand=True, content=self.cliente_busqueda),
                    ],
                ),
                ft.Row(
                    spacing=14,
                    controls=[
                        ft.Container(expand=True, content=self.categoria_buque),
                        ft.Container(expand=True, content=self.subtipo_descripcion),
                        ft.Container(expand=True, content=self.bandera_pais),
                    ],
                ),
            ],
        )


    def build_ui(self):
        formulario = card(
            ft.Stack(
                expand=True,
                clip_behavior=ft.ClipBehavior.NONE,
                controls=[
                    # Contenido principal del formulario
                    ft.Column(
                        expand=True,
                        spacing=24,
                        controls=[
                            self.seccion(
                                ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                                "Datos generales",
                                self.crear_datos_generales(),
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
                                                ft.Container(
                                                    expand=True,
                                                    content=self.trb_arqueo_bruto,
                                                ),
                                                ft.Container(
                                                    expand=True,
                                                    content=self.eslora_metros,
                                                ),
                                                ft.Container(
                                                    expand=True,
                                                    content=self.calado_metros,
                                                ),
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

                    # Desplegable de clientes por encima de todo el formulario
                    ft.Container(
                        top=96,
                        left=0,
                        right=0,
                        content=ft.Row(
                            spacing=14,
                            controls=[
                                ft.Container(expand=True),
                                ft.Container(expand=True),
                                ft.Container(
                                    expand=True,
                                    content=self.cliente_busqueda.contenido_resultados,
                                ),
                            ],
                        ),
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

        self.content = ft.Container(
            expand=True,
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
        try:
            datos_buque = self.controlador.obtener_datos(self)
            exito, mensaje = self.controlador.guardar_buque(
                datos=datos_buque,
                buque_a_editar=self.buque_a_editar,
            )

            self._page.show_dialog(
                ft.SnackBar(content=ft.Text(mensaje))
            )

            if exito and self.vista_anterior:
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