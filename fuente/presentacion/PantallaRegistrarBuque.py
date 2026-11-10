import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorBuque import ControladorBuque
from fuente.negocio.controlador.ControladorClientes import ControladorClientes
from fuente.negocio.controlador.ControladorRegistrarBuques import (
    ControladorRegistrarBuques,
    ErrorRegistroBuque,
)
from fuente.negocio.controlador.ControladorRegistrarCliente import (
    ErrorRegistroCliente,
)
from fuente.negocio.servicio.ServicioCategoriaBuque import ServicioCategoriaBuque
from fuente.presentacion.SelectorCliente import SelectorCliente
from fuente.presentacion.SelectorPais import SelectorPais


class PantallaRegistrarBuque(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_buque,
        servicio_cliente,
        vista_anterior=None,
        buque_a_editar=None,
        servicio_categoria_buque=None,
    ):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page
        self.vista_anterior = vista_anterior
        self.servicio_buque = servicio_buque
        self.servicio_cliente = servicio_cliente
        self.servicio_categoria_buque = (
            servicio_categoria_buque
            if servicio_categoria_buque is not None
            else ServicioCategoriaBuque(servicio_buque.uow)
        )
        self.controlador = ControladorRegistrarBuques(
            servicio_buque,
            servicio_categoria_buque=self.servicio_categoria_buque,
        )
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
        self._boton_nuevo_cliente = ft.Container(
            width=52,
            height=52,
            bgcolor="#FFF0E5",
            border=ft.Border.all(1, COLOR_NARANJA),
            border_radius=9,
            alignment=ft.Alignment(0, 0),
            tooltip="Registrar nuevo cliente",
            content=ft.IconButton(
                icon=ft.Icons.PERSON_ADD_ALT_1_OUTLINED,
                icon_color=COLOR_NARANJA,
                icon_size=22,
                tooltip="Registrar nuevo cliente",
                width=52,
                height=52,
                on_click=self._abrir_dialogo_nuevo_cliente,
            ),
        )
        self.bandera_pais = SelectorPais()
        self.subtipo_descripcion = self._crear_campo_etiquetado(
            etiqueta="Subtipo o descripción",
            ejemplo="Ej. Portacontenedores, carga general...",
            icono=ft.Icons.DESCRIPTION_OUTLINED,
        )

        self.categoria_buque = ft.Dropdown(
            expand=True,
            height=58,
            label="Tipo / categoría del buque *",
            hint_text="Selecciona un tipo de buque",
            leading_icon=ft.Icons.CATEGORY_OUTLINED,
            options=self._obtener_opciones_categoria(),
            text_size=14,
            content_padding=ft.Padding(14, 12, 14, 12),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
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
            self.bandera_pais.establecer_pais(pais_actual)
            self.subtipo_descripcion.value = (
                self.buque_a_editar.subtipo_descripcion or ""
            )

            categoria_obj = getattr(self.buque_a_editar, "categoria_buque", None)
            categoria_id = getattr(
                self.buque_a_editar, "categoria_buque_id", None
            ) or getattr(categoria_obj, "id", None)
            if categoria_id is not None:
                self.categoria_buque.value = str(categoria_id)

            self.trb_arqueo_bruto.value = str(
                self.buque_a_editar.trb_arqueo_bruto or ""
            )
            self.eslora_metros.value = str(
                self.buque_a_editar.eslora_metros or ""
            )
            self.calado_metros.value = (
                str(self.buque_a_editar.calado_metros)
                if self.buque_a_editar.calado_metros is not None
                else ""
            )

            self.es_autopropulsado.value = bool(
                self.buque_a_editar.es_autopropulsado
            )
            self.propulsores_proa_popa.value = bool(
                self.buque_a_editar.propulsores_proa_popa
            )
            self.activo.value = bool(self.buque_a_editar.activo)

        self._errores_validacion = {
            campo: crear_mensaje_validacion()
            for campo in (
                "nombre",
                "categoria_buque",
                "trb_arqueo_bruto",
                "eslora_metros",
                "calado_metros",
            )
        }
        self._validaciones = {
            "nombre": (
                self.nombre,
                self._errores_validacion["nombre"],
                validador_requerido("el nombre del buque"),
            ),
            "categoria_buque": (
                self.categoria_buque,
                self._errores_validacion["categoria_buque"],
                validador_requerido("una categoría de buque"),
            ),
            "trb_arqueo_bruto": (
                self.trb_arqueo_bruto,
                self._errores_validacion["trb_arqueo_bruto"],
                validador_numero(
                    "El arqueo bruto (TRB)",
                    minimo=0,
                    minimo_exclusivo=True,
                ),
            ),
            "eslora_metros": (
                self.eslora_metros,
                self._errores_validacion["eslora_metros"],
                validador_numero(
                    "La eslora",
                    minimo=0,
                    minimo_exclusivo=True,
                ),
            ),
            "calado_metros": (
                self.calado_metros,
                self._errores_validacion["calado_metros"],
                self._validar_calado,
            ),
        }
        for clave, (control, mensaje_error, validador) in self._validaciones.items():
            vincular_validacion_campo(
                control,
                mensaje_error,
                validador,
                page=self._page,
                evento="on_select" if clave == "categoria_buque" else "on_change",
            )

        self.build_ui()

    @staticmethod
    def _validar_calado(valor):
        if valor is None or not str(valor).strip():
            return None
        return validador_numero(
            "El calado",
            minimo=0,
            minimo_exclusivo=True,
        )(valor)

    def _obtener_opciones_categoria(self):
        try:
            if hasattr(self.servicio_categoria_buque, "obtener_todas"):
                categorias = self.servicio_categoria_buque.obtener_todas()
            else:
                categorias = self.servicio_categoria_buque.obtener_pagina(
                    1, limite=100
                )
        except Exception:
            categorias = []

        opciones = []
        for cat in categorias or []:
            etiqueta_legible = ControladorBuque.etiqueta_categoria(cat)
            opciones.append(
                ft.DropdownOption(key=str(cat.id), text=etiqueta_legible)
            )
        return opciones

    def _campo_dialogo_cliente(
        self,
        titulo,
        icono,
        control,
        mensaje_error=None,
        expand=True,
    ):
        return ft.Container(
            expand=expand,
            content=ft.Column(
                spacing=4,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Row(
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(icono, size=16, color=COLOR_BANNER),
                            ft.Text(
                                titulo,
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                        ],
                    ),
                    (
                        campo_con_mensaje_error(control, mensaje_error)
                        if mensaje_error is not None
                        else control
                    ),
                ],
            ),
        )

    def _abrir_dialogo_nuevo_cliente(self, e=None):
        self._cliente_rapido_nombre = ft.TextField(
            hint_text="Ej. ABC Logistics S.A. de C.V.",
            height=42,
            text_size=13,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
        )
        self._cliente_rapido_rfc = ft.TextField(
            hint_text="Ej. ABC010203XYZ",
            height=42,
            text_size=13,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
        )
        self._cliente_rapido_tipo_persona = ft.Dropdown(
            hint_text="Selecciona un tipo de persona",
            options=[
                ft.DropdownOption(key="FISICA", text="Persona Física"),
                ft.DropdownOption(key="MORAL", text="Persona Moral"),
                ft.DropdownOption(key="EXTRANJERO", text="Extranjero"),
            ],
            expand=True,
            height=42,
            text_size=13,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
        )
        self._cliente_rapido_es_nuevo = ft.Switch(
            value=True,
            active_color=COLOR_NARANJA,
        )
        self._cliente_rapido_activo = ft.Switch(
            value=True,
            active_color=COLOR_NARANJA,
        )
        self._cliente_rapido_telefono = ft.TextField(
            hint_text="Ej. +52 962 123 4567",
            height=42,
            text_size=13,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
        )
        self._cliente_rapido_correo = ft.TextField(
            hint_text="Ej. cliente@empresa.com",
            height=42,
            text_size=13,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
        )
        self._cliente_rapido_direccion = ft.TextField(
            hint_text="Ej. Calle, número, colonia, ciudad, estado, código postal, país.",
            multiline=True,
            min_lines=2,
            max_lines=2,
            height=64,
            text_size=13,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
        )

        panel_switches = ft.Container(
            bgcolor="#F7FAFD",
            border=ft.Border.all(1, "#E4ECF5"),
            border_radius=9,
            padding=ft.Padding(10, 6, 10, 6),
            content=ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        expand=True,
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self._cliente_rapido_es_nuevo,
                            ft.Text(
                                "Es nuevo cliente",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                        ],
                    ),
                    ft.Container(width=1, height=28, bgcolor=COLOR_GRIS_CLARO),
                    ft.Row(
                        expand=True,
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            self._cliente_rapido_activo,
                            ft.Text(
                                "Cliente activo",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                        ],
                    ),
                ],
            ),
        )

        encabezado_dialogo = ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=48,
                    height=48,
                    border_radius=24,
                    bgcolor="#FFF0E5",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.PERSON_ADD_ALT_1_OUTLINED,
                        size=24,
                        color=COLOR_NARANJA,
                    ),
                ),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text(
                            "Registrar nuevo cliente",
                            size=20,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            "Completa la información fiscal y de contacto del cliente.",
                            size=12,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    tooltip="Cerrar",
                    icon_color=COLOR_BANNER,
                    on_click=self._cerrar_dialogo_nuevo_cliente,
                ),
            ],
        )

        self._feedback_cliente_rapido = crear_feedback_dialogo(self._page)
        self._errores_cliente_rapido = {
            campo: crear_mensaje_validacion()
            for campo in (
                "nombre",
                "rfc",
                "tipo_persona",
                "telefono",
                "correo",
                "direccion",
            )
        }
        self._validaciones_cliente_rapido = {
            "nombre": (
                self._cliente_rapido_nombre,
                self._errores_cliente_rapido["nombre"],
                validador_requerido("el nombre o razón social"),
            ),
            "rfc": (
                self._cliente_rapido_rfc,
                self._errores_cliente_rapido["rfc"],
                validador_requerido("el RFC"),
            ),
            "tipo_persona": (
                self._cliente_rapido_tipo_persona,
                self._errores_cliente_rapido["tipo_persona"],
                validador_requerido("un tipo de persona"),
            ),
            "telefono": (
                self._cliente_rapido_telefono,
                self._errores_cliente_rapido["telefono"],
                validador_telefono(),
            ),
            "correo": (
                self._cliente_rapido_correo,
                self._errores_cliente_rapido["correo"],
                validador_correo(),
            ),
            "direccion": (
                self._cliente_rapido_direccion,
                self._errores_cliente_rapido["direccion"],
                validador_requerido("la dirección fiscal"),
            ),
        }
        for clave, (control, mensaje_error, validador) in (
            self._validaciones_cliente_rapido.items()
        ):
            vincular_validacion_campo(
                control,
                mensaje_error,
                validador,
                page=self._page,
                evento="on_select" if clave == "tipo_persona" else "on_change",
            )

        contenido_dialogo = ft.Column(
            tight=True,
            spacing=10,
            controls=[
                self._feedback_cliente_rapido,
                tarjeta_detalle(
                    "Datos generales",
                    ft.Icons.ASSIGNMENT_OUTLINED,
                    ft.Column(
                        spacing=10,
                        controls=[
                            ft.Row(
                                spacing=12,
                                controls=[
                                    self._campo_dialogo_cliente(
                                        "Nombre o razón social *",
                                        ft.Icons.PERSON_OUTLINED,
                                        self._cliente_rapido_nombre,
                                        self._errores_cliente_rapido["nombre"],
                                    ),
                                    self._campo_dialogo_cliente(
                                        "RFC *",
                                        ft.Icons.BADGE_OUTLINED,
                                        self._cliente_rapido_rfc,
                                        self._errores_cliente_rapido["rfc"],
                                    ),
                                ],
                            ),
                            ft.Row(
                                spacing=12,
                                vertical_alignment=ft.CrossAxisAlignment.END,
                                controls=[
                                    self._campo_dialogo_cliente(
                                        "Tipo de persona *",
                                        ft.Icons.PERSON_OUTLINE,
                                        self._cliente_rapido_tipo_persona,
                                        self._errores_cliente_rapido[
                                            "tipo_persona"
                                        ],
                                        expand=4,
                                    ),
                                    ft.Container(
                                        expand=6,
                                        content=panel_switches,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                tarjeta_detalle(
                    "Información de contacto",
                    ft.Icons.PHONE_OUTLINED,
                    ft.Row(
                        spacing=12,
                        controls=[
                            self._campo_dialogo_cliente(
                                "Número telefónico *",
                                ft.Icons.PHONE_OUTLINED,
                                self._cliente_rapido_telefono,
                                self._errores_cliente_rapido["telefono"],
                            ),
                            self._campo_dialogo_cliente(
                                "Correo electrónico *",
                                ft.Icons.MAIL_OUTLINE,
                                self._cliente_rapido_correo,
                                self._errores_cliente_rapido["correo"],
                            ),
                        ],
                    ),
                ),
                tarjeta_detalle(
                    "Domicilio fiscal",
                    ft.Icons.LOCATION_ON_OUTLINED,
                    self._campo_dialogo_cliente(
                        "Dirección fiscal completa *",
                        ft.Icons.LOCATION_ON_OUTLINED,
                        self._cliente_rapido_direccion,
                        self._errores_cliente_rapido["direccion"],
                    ),
                ),
            ],
        )

        self._dialogo_nuevo_cliente = ft.AlertDialog(
            modal=True,
            bgcolor="#F4F8FC",
            shape=ft.RoundedRectangleBorder(radius=16),
            scrollable=True,
            title=encabezado_dialogo,
            title_padding=ft.Padding(18, 14, 18, 8),
            content=ft.Container(
                width=620,
                content=contenido_dialogo,
            ),
            content_padding=ft.Padding(16, 4, 16, 4),
            actions=[
                ft.Row(
                    expand=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        boton(
                            texto="Cancelar",
                            icono=ft.Icons.CLOSE,
                            tipo="secundario",
                            color=COLOR_BANNER,
                            height=40,
                            width=120,
                            on_click=self._cerrar_dialogo_nuevo_cliente,
                        ),
                        boton(
                            texto="Guardar cliente",
                            icono=ft.Icons.SAVE_OUTLINED,
                            tipo="principal",
                            height=40,
                            width=165,
                            on_click=self._guardar_nuevo_cliente_rapido,
                        ),
                    ],
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            actions_padding=ft.Padding(16, 8, 16, 14),
        )
        self._page.show_dialog(self._dialogo_nuevo_cliente)

    def _cerrar_dialogo_nuevo_cliente(self, e=None):
        self._page.pop_dialog()

    def _guardar_nuevo_cliente_rapido(self, e=None):
        if not validar_campos(self._validaciones_cliente_rapido):
            self._page.update()
            return

        controlador_clientes = ControladorClientes(self.servicio_cliente)
        try:
            cliente = controlador_clientes.registrar_cliente(
                razon_social=self._cliente_rapido_nombre.value,
                tipo_persona=self._cliente_rapido_tipo_persona.value,
                direccion=self._cliente_rapido_direccion.value,
                rfc=self._cliente_rapido_rfc.value,
                telefono=self._cliente_rapido_telefono.value,
                correo_elect=self._cliente_rapido_correo.value,
                es_nuevo_cliente=bool(self._cliente_rapido_es_nuevo.value),
                activo=bool(self._cliente_rapido_activo.value),
            )
        except (ValueError, ErrorRegistroCliente) as error:
            mostrar_feedback_dialogo(
                self._feedback_cliente_rapido,
                str(error),
                COLOR_ROJO,
                page=self._page,
            )
            return

        if getattr(cliente, "id", None) is not None:
            self.cliente_busqueda.establecer_cliente(cliente)
        self._page.pop_dialog()
        mostrar_notificacion(
            self._page,
            "Cliente registrado correctamente.",
            COLOR_VERDE,
        )

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
                if numerico
                else None
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
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[0-9.]*$", replacement_string=""
            ),
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
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[0-9]*$", replacement_string=""
            ),
        )

    # Nuevo método integrado para manejar el Stack y resultados superpuestos
    def crear_datos_generales(self):
        return ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=campo_con_mensaje_error(
                                self.nombre,
                                self._errores_validacion["nombre"],
                            ),
                        ),
                        ft.Container(expand=True, content=self.numero_imo),
                        ft.Row(
                            expand=True,
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    content=self.cliente_busqueda,
                                ),
                                self._boton_nuevo_cliente,
                            ],
                        ),
                    ],
                ),
                ft.Row(
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            expand=True,
                            content=campo_con_mensaje_error(
                                self.categoria_buque,
                                self._errores_validacion["categoria_buque"],
                            ),
                        ),
                        ft.Container(
                            expand=True, content=self.subtipo_descripcion
                        ),
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
                                            vertical_alignment=ft.CrossAxisAlignment.START,
                                            controls=[
                                                ft.Container(
                                                    expand=True,
                                                    content=campo_con_mensaje_error(
                                                        self.trb_arqueo_bruto,
                                                        self._errores_validacion[
                                                            "trb_arqueo_bruto"
                                                        ],
                                                    ),
                                                ),
                                                ft.Container(
                                                    expand=True,
                                                    content=campo_con_mensaje_error(
                                                        self.eslora_metros,
                                                        self._errores_validacion[
                                                            "eslora_metros"
                                                        ],
                                                    ),
                                                ),
                                                ft.Container(
                                                    expand=True,
                                                    content=campo_con_mensaje_error(
                                                        self.calado_metros,
                                                        self._errores_validacion[
                                                            "calado_metros"
                                                        ],
                                                    ),
                                                ),
                                            ],
                                        ),
                                        ft.Row(
                                            spacing=24,
                                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                            controls=[
                                                ft.Container(
                                                    content=self.es_autopropulsado
                                                ),
                                                ft.Container(
                                                    content=self.propulsores_proa_popa
                                                ),
                                                ft.Container(
                                                    content=self.activo
                                                ),
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
                                                    "Guardar cambios"
                                                    if self.modo_edicion
                                                    else "Guardar buque",
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
                    # Desplegable de bandera / país por encima del formulario
                    ft.Container(
                        top=166,
                        left=0,
                        right=0,
                        content=ft.Row(
                            spacing=14,
                            controls=[
                                ft.Container(expand=True),
                                ft.Container(expand=True),
                                ft.Container(
                                    expand=True,
                                    content=self.bandera_pais.contenido_resultados,
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
                                "Editar buque"
                                if self.modo_edicion
                                else "Registrar nuevo buque",
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
            self._page.update()

    def guardar(self, e):
        if not validar_campos(self._validaciones):
            self._page.update()
            return

        datos_buque = self.controlador.obtener_datos(self)
        try:
            if self.buque_a_editar is not None:
                self.controlador.modificar_buque(
                    buque=self.buque_a_editar,
                    **datos_buque,
                )
                mensaje_exito = "Buque modificado correctamente."
            else:
                self.controlador.registrar_buque(**datos_buque)
                mensaje_exito = "Buque registrado correctamente."
        except ValueError as error:
            mostrar_notificacion(self._page, str(error), COLOR_ROJO)
            return
        except ErrorRegistroBuque as error:
            mostrar_notificacion(self._page, str(error), COLOR_ROJO)
            return

        mostrar_notificacion(
            self._page,
            mensaje_exito,
            COLOR_VERDE,
        )
        if self.vista_anterior:
            self.vista_anterior.build_ui()
            self.vista_anterior.actualizar_directorio()
        self._page.update()
