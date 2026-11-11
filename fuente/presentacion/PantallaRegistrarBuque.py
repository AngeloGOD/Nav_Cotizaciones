import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.utilidades.feedback import reproducir_sonido
from fuente.negocio.controlador.ControladorBuque import ControladorBuque
from fuente.negocio.controlador.ControladorClientes import ControladorClientes
from fuente.negocio.controlador.ControladorRegistrarBuques import (
    ControladorRegistrarBuques,
    ErrorRegistroBuque,
)
from fuente.negocio.servicio.ServicioCategoriaBuque import ServicioCategoriaBuque
from fuente.presentacion.PantallaRegistrarCliente import PantallaRegistrarCliente
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
            width=58,
            height=58,
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
                width=58,
                height=58,
                padding=ft.Padding(0, 0, 0, 0),
                on_click=self.ir_a_registro_cliente,
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
            width=float("inf"),
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

    def ir_a_registro_cliente(self, e=None):
        self.cliente_busqueda._ocultar_resultados()
        self.bandera_pais._ocultar_resultados()
        self.content = PantallaRegistrarCliente(
            self._page,
            ControladorClientes(self.servicio_cliente),
            vista_anterior=self,
        )
        try:
            self.update()
        except RuntimeError:
            if self._page is not None:
                self._page.update()

    def actualizar_directorio(self):
        try:
            self.update()
        except RuntimeError:
            if self._page is not None:
                self._page.update()

    def _campo_con_error(self, control, clave_error):
        columna = campo_con_mensaje_error(
            control,
            self._errores_validacion[clave_error],
        )
        columna.tight = True
        columna.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        return columna

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
            expand=True,
            width=float("inf"),
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
                            content=self._campo_con_error(
                                self.nombre,
                                "nombre",
                            ),
                        ),
                        ft.Container(expand=True, content=self.numero_imo),
                        ft.Row(
                            expand=True,
                            spacing=8,
                            vertical_alignment=ft.CrossAxisAlignment.START,
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
                            content=self._campo_con_error(
                                self.categoria_buque,
                                "categoria_buque",
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
                                                    content=self._campo_con_error(
                                                        self.trb_arqueo_bruto,
                                                        "trb_arqueo_bruto",
                                                    ),
                                                ),
                                                ft.Container(
                                                    expand=True,
                                                    content=self._campo_con_error(
                                                        self.eslora_metros,
                                                        "eslora_metros",
                                                    ),
                                                ),
                                                ft.Container(
                                                    expand=True,
                                                    content=self._campo_con_error(
                                                        self.calado_metros,
                                                        "calado_metros",
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
            reproducir_sonido(self._page, "error")
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
