import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorClientes import ControladorClientes
from fuente.presentacion.PantallaRegistrarCliente import PantallaRegistrarCliente


class PantallaClientes(ft.Container):
    def __init__(self, page: ft.Page, servicio_cliente):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page
        self.servicio_cliente = servicio_cliente
        self.controlador = ControladorClientes(servicio_cliente)
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.total_clientes = 0
        self.busqueda = ""

        self.build_ui()

    def build_ui(self):
        self._contenido = ft.Column(
            expand=True,
            spacing=10,
            controls=[
                self.cabecera_clientes(),
                self.directorio(),
            ],
        )

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding(14, 8, 14, 18),
                    content=self._contenido,
                )
            ],
        )

    def cabecera_clientes(self):
        return card(
            ft.Column(
                spacing=0,
                controls=[
                    banner_imagen_desvanecida(
                        "fondo_PantallaClientes.jpg",
                        altura=150,
                        content=ft.Container(
                            expand=True,
                            padding=ft.Padding(26, 20, 26, 20),
                            content=ft.Column(
                                expand=True,
                                alignment=ft.MainAxisAlignment.CENTER,
                                spacing=4,
                                controls=[
                                    ft.Text(
                                        "Gestión de Clientes",
                                        size=28,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_BANNER,
                                    ),
                                    ft.Text(
                                        "Administra la información fiscal y de contacto de agencias navieras, armadores y clientes.",
                                        size=14,
                                        color=COLOR_GRIS,
                                    ),
                                ],
                            ),
                        ),
                    ),
                    ft.Container(
                        padding=ft.Padding(10, 10, 10, 10),
                        content=ft.Row(
                            spacing=8,
                            controls=[
                                barra_busqueda(
                                    hint="Buscar por razón social, RFC, tipo de persona o contacto...",
                                    on_change=self.buscar,
                                ),
                                boton(
                                    texto="Filtros",
                                    icono=ft.Icons.TUNE,
                                    tipo="secundario",
                                    width=150,
                                    height=44,
                                    on_click=self.abrir_filtros,
                                ),
                                boton(
                                    texto="Registrar cliente",
                                    icono=ft.Icons.ADD,
                                    tipo="principal",
                                    width=200,
                                    height=44,
                                    on_click=self.ir_a_registro,
                                ),
                            ],
                        ),
                    ),
                ],
            ),
            padding=0,
            radius=12,
            shadow=sombra_suave(),
        )

    def buscar(self, e):
        self.busqueda = e.control.value or ""
        self.pagina_actual = 1
        self.actualizar_directorio()

    def abrir_filtros(self, e):
        pass

    def ir_a_registro(self, e):
        self.content = PantallaRegistrarCliente(
            self._page,
            self.servicio_cliente,
            vista_anterior=self,
        )
        self.update()

    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        self.actualizar_directorio()

    def actualizar_directorio(self):
        self._contenido.controls[1] = self.directorio()
        self.update()

    def contacto(self, icono, texto):
        return ft.Container(
            expand=True,
            content=ft.Row(
                expand=True,
                spacing=5,
                controls=[
                    ft.Icon(
                        icono,
                        size=15,
                        color=COLOR_GRIS,
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            texto or "-",
                            size=13,
                            color=COLOR_NEGRO,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                ],
            ),
        )

    def ver_cliente(self, cliente):
        self.cliente_seleccionado = cliente
        self.modo_edicion = False
        self.dialogo_cliente = self._crear_dialogo_cliente()
        self._page.show_dialog(self.dialogo_cliente)

    def _crear_dialogo_cliente(self):
        return ft.AlertDialog(
            modal=True,
            bgcolor="#F4F8FC",
            shape=ft.RoundedRectangleBorder(radius=18),
            title=self._encabezado_ficha(),
            title_padding=ft.Padding(22, 18, 22, 10),
            content=ft.Container(
                width=650,
                content=self._contenido_ficha_cliente(),
            ),
            content_padding=ft.Padding(18, 0, 18, 0),
            actions=self._acciones_ficha_cliente(),
            actions_alignment=ft.MainAxisAlignment.END,
            actions_padding=ft.Padding(18, 12, 18, 18),
            scrollable=True,
        )

    def _encabezado_ficha(self):
        es_edicion = self.modo_edicion
        return ft.Row(
            spacing=13,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=54,
                    height=54,
                    border_radius=27,
                    bgcolor="#FFF0E5",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.EDIT_OUTLINED if es_edicion else ft.Icons.GROUPS_OUTLINED,
                        size=28,
                        color=COLOR_NARANJA,
                    ),
                ),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text(
                            "Editar cliente" if es_edicion else "Ficha del cliente",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            "Actualiza los datos fiscales y de contacto"
                            if es_edicion
                            else "Información fiscal y de contacto",
                            size=13,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    tooltip="Cerrar",
                    icon_color=COLOR_BANNER,
                    on_click=self.cerrar_ficha,
                ),
            ],
        )

    def _contenido_ficha_cliente(self):
        cliente = self.cliente_seleccionado
        self.campos_ficha = {}

        tipo_persona = (
            cliente.tipo_persona.value
            if hasattr(cliente.tipo_persona, "value")
            else str(cliente.tipo_persona or "")
        )

        campo_tipo_persona = self._campo_ficha(
            "Tipo de persona",
            "tipo_persona",
            tipo_persona,
            tipo_persona=True,
            expand=True,
        )
        campo_cliente_nuevo = self._campo_ficha(
            "Cliente nuevo",
            "es_nuevo_cliente",
            cliente.es_nuevo_cliente,
            switch=True,
            expand=True,
        )
        campo_cliente_activo = self._campo_ficha(
            "Cliente activo",
            "activo",
            cliente.activo,
            switch=True,
            expand=True,
        )

        datos_generales = ft.Column(
            spacing=12,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        self._campo_ficha(
                            "Razón fiscal / nombre",
                            "razon_social",
                            cliente.razon_social,
                            expand=True,
                        ),
                        self._campo_ficha(
                            "RFC",
                            "rfc",
                            cliente.rfc,
                            expand=True,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.END,
                    controls=[
                        campo_tipo_persona,
                        *(
                            [campo_cliente_nuevo, campo_cliente_activo]
                            if self.modo_edicion
                            else []
                        ),
                    ],
                ),
            ],
        )

        contacto = ft.Row(
            spacing=12,
            controls=[
                self._campo_ficha(
                    "Teléfono",
                    "telefono",
                    cliente.telefono,
                    expand=True,
                ),
                self._campo_ficha(
                    "Correo electrónico",
                    "correo_elect",
                    cliente.correo_elect,
                    expand=True,
                ),
            ],
        )

        domicilio = self._campo_ficha(
            "Dirección fiscal",
            "direccion",
            cliente.direccion,
            expand=True,
            multiline=True,
        )

        estado = ft.Row(
            spacing=24,
            controls=[campo_cliente_nuevo, campo_cliente_activo],
        )

        tarjetas = [
            tarjeta_detalle(
                "Datos generales",
                ft.Icons.BUSINESS_OUTLINED,
                datos_generales,
            ),
            tarjeta_detalle(
                "Información de contacto",
                ft.Icons.PHONE_OUTLINED,
                contacto,
            ),
            tarjeta_detalle(
                "Domicilio fiscal",
                ft.Icons.LOCATION_ON_OUTLINED,
                domicilio,
            ),
        ]
        if not self.modo_edicion:
            tarjetas.append(
                tarjeta_detalle(
                    "Estado del cliente",
                    ft.Icons.VERIFIED_USER_OUTLINED,
                    estado,
                )
            )

        return ft.Column(
            tight=True,
            spacing=10,
            controls=tarjetas,
        )

    def _campo_ficha(
        self,
        etiqueta,
        nombre,
        valor,
        expand=False,
        tipo_persona=False,
        switch=False,
        multiline=False,
    ):
        if self.modo_edicion:
            if tipo_persona:
                control = ft.Dropdown(
                    value=valor,
                    options=[
                        ft.DropdownOption(key="FISICA", text="Persona Física"),
                        ft.DropdownOption(key="MORAL", text="Persona Moral"),
                        ft.DropdownOption(key="EXTRANJERO", text="Extranjero"),
                    ],
                    height=44,
                    text_size=14,
                    content_padding=ft.Padding(12, 8, 12, 8),
                    border=ft.InputBorder.OUTLINE,
                    border_color=COLOR_GRIS_CLARO,
                    focused_border_color=COLOR_NARANJA,
                    border_radius=9,
                )
                self.campos_ficha[nombre] = control
            elif switch:
                control = ft.Switch(
                    value=bool(valor),
                    active_color=COLOR_NARANJA,
                )
                self.campos_ficha[nombre] = control
            else:
                control = ft.TextField(
                    value=str(valor or ""),
                    multiline=multiline,
                    min_lines=2 if multiline else 1,
                    max_lines=3 if multiline else 1,
                    text_size=14,
                    content_padding=ft.Padding(12, 9, 12, 9),
                    border=ft.InputBorder.OUTLINE,
                    border_color=COLOR_GRIS_CLARO,
                    focused_border_color=COLOR_NARANJA,
                    border_radius=9,
                )
                self.campos_ficha[nombre] = control
        elif switch:
            color = COLOR_VERDE if valor else COLOR_ROJO
            control = ft.Container(
                bgcolor="#EAF7EF" if valor else "#FDECEC",
                border_radius=16,
                padding=ft.Padding(10, 5, 10, 5),
                content=ft.Row(
                    tight=True,
                    spacing=6,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE_OUTLINE
                            if valor
                            else ft.Icons.CANCEL_OUTLINED,
                            size=16,
                            color=color,
                        ),
                        ft.Text(
                            "Sí" if valor else "No",
                            color=color,
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            selectable=True,
                        ),
                    ],
                ),
            )
        else:
            texto = valor or "-"
            if nombre == "tipo_persona":
                texto = {
                    "FISICA": "Persona Física",
                    "MORAL": "Persona Moral",
                    "EXTRANJERO": "Extranjero",
                }.get(str(valor).upper(), texto)
            control = ft.Text(
                str(texto),
                color=COLOR_NEGRO,
                size=14,
                max_lines=3 if multiline else 1,
                overflow=ft.TextOverflow.ELLIPSIS,
                selectable=True,
            )

        if switch and self.modo_edicion:
            control = ft.Container(
                bgcolor="#F0F7FC",
                border_radius=10,
                padding=ft.Padding(10, 2, 10, 2),
                content=control,
            )

        return campo_detalle(etiqueta, control, expand=expand)

    def _acciones_ficha_cliente(self):
        if self.modo_edicion:
            return [
                ft.Row(
                    expand=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.OutlinedButton(
                            content=ft.Row(
                                tight=True,
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.DELETE_OUTLINE, color=COLOR_ROJO, size=18),
                                    ft.Text("Eliminar", color=COLOR_ROJO),
                                ],
                            ),
                            on_click=self.pedir_confirmacion_eliminacion,
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, COLOR_ROJO),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.Row(
                            spacing=9,
                            controls=[
                                ft.OutlinedButton(
                                    content=ft.Row(
                                        tight=True,
                                        spacing=6,
                                        controls=[
                                            ft.Icon(ft.Icons.CLOSE, color=COLOR_BANNER, size=18),
                                            ft.Text("Cancelar", color=COLOR_BANNER),
                                        ],
                                    ),
                                    on_click=self.cancelar_edicion,
                                    style=ft.ButtonStyle(
                                        side=ft.BorderSide(1, COLOR_GRIS_CLARO),
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                ),
                                ft.FilledButton(
                                    content=ft.Row(
                                        tight=True,
                                        spacing=6,
                                        controls=[
                                            ft.Icon(ft.Icons.SAVE_OUTLINED, color=COLOR_BLANCO, size=18),
                                            ft.Text("Guardar cambios", color=COLOR_BLANCO),
                                        ],
                                    ),
                                    on_click=self.guardar_cambios_cliente,
                                    style=ft.ButtonStyle(
                                        bgcolor=COLOR_VERDE,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            ]

        return [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.OutlinedButton(
                        content=ft.Row(
                            tight=True,
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.DELETE_OUTLINE, color=COLOR_ROJO, size=18),
                                ft.Text("Eliminar", color=COLOR_ROJO),
                            ],
                        ),
                        on_click=self.pedir_confirmacion_eliminacion,
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(1, COLOR_ROJO),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                    ft.Row(
                        spacing=9,
                        controls=[
                            ft.FilledButton(
                                content=ft.Row(
                                    tight=True,
                                    spacing=6,
                                    controls=[
                                        ft.Icon(ft.Icons.EDIT_OUTLINED, color=COLOR_BLANCO, size=18),
                                        ft.Text("Editar", color=COLOR_BLANCO),
                                    ],
                                ),
                                on_click=self.activar_edicion,
                                style=ft.ButtonStyle(
                                    bgcolor=COLOR_NARANJA,
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                        ],
                    ),
                ],
            ),
        ]

    def _actualizar_ficha(self):
        self.dialogo_cliente.title = self._encabezado_ficha()
        self.dialogo_cliente.content = self._contenido_ficha_cliente()
        self.dialogo_cliente.actions = self._acciones_ficha_cliente()
        self._page.update()

    def activar_edicion(self, e):
        self.modo_edicion = True
        self._actualizar_ficha()

    def cancelar_edicion(self, e):
        self.modo_edicion = False
        self._actualizar_ficha()

    def guardar_cambios_cliente(self, e):
        campos = self.campos_ficha
        razon_social = (campos["razon_social"].value or "").strip()
        tipo_persona = (campos["tipo_persona"].value or "").strip()
        if not razon_social or not tipo_persona:
            mostrar_notificacion(
                self._page,
                "La razón social y el tipo de persona son obligatorios.",
                COLOR_ROJO,
            )
            return

        try:
            self.controlador.modificar_cliente(
                cliente=self.cliente_seleccionado,
                razon_social=razon_social,
                tipo_persona=tipo_persona,
                direccion=campos["direccion"].value,
                rfc=campos["rfc"].value,
                telefono=campos["telefono"].value,
                correo_elect=campos["correo_elect"].value,
                es_nuevo_cliente=campos["es_nuevo_cliente"].value,
                activo=campos["activo"].value,
            )
        except Exception as error:
            mostrar_notificacion(
                self._page,
                f"No se pudieron guardar los cambios: {error}",
                COLOR_ROJO,
            )
            return

        self.modo_edicion = False
        self.actualizar_directorio()
        self._actualizar_ficha()
        mostrar_notificacion(
            self._page,
            "Cambios guardados correctamente.",
            COLOR_VERDE,
        )

    def pedir_confirmacion_eliminacion(self, e):
        cliente = self.cliente_seleccionado
        self._page.show_dialog(
            dialogo_confirmacion(
                page=self._page,
                titulo="Confirmar eliminación",
                mensaje=(
                    f"¿Deseas eliminar el cliente '{cliente.razon_social}'? "
                    "Esta acción no se puede deshacer."
                ),
                on_confirmar=lambda: self._confirmar_eliminacion(cliente),
                texto_confirmar="Eliminar",
            )
        )

    def _confirmar_eliminacion(self, cliente):
        try:
            self.controlador.eliminar_cliente(cliente)
        except Exception as error:
            mostrar_notificacion(
                self._page,
                f"No se pudo eliminar el cliente: {error}",
                COLOR_ROJO,
            )
            return

        self._page.pop_dialog()
        if self.pagina_actual > 1:
            clientes, _ = self.controlador.obtener_clientes(
                texto=self.busqueda,
                limit=self.registros_por_pagina,
                offset=(self.pagina_actual - 1) * self.registros_por_pagina,
            )
            if not clientes:
                self.pagina_actual -= 1
        self.actualizar_directorio()
        mostrar_notificacion(
            self._page,
            "Cliente eliminado correctamente.",
            COLOR_VERDE,
        )

    def cerrar_ficha(self, e):
        self._page.pop_dialog()

    def directorio(self):
        offset = (self.pagina_actual - 1) * self.registros_por_pagina

        clientes, self.total_clientes = self.controlador.obtener_clientes(
            texto=self.busqueda,
            limit=self.registros_por_pagina,
            offset=offset,
        )

        etiquetas_persona = {
            "FISICA": "Persona Física",
            "MORAL": "Persona Moral",
            "EXTRANJERO": "Extranjero",
        }

        filas = []
        for cliente in clientes:
            valor_tipo = (
                cliente.tipo_persona.value
                if hasattr(cliente.tipo_persona, "value")
                else str(cliente.tipo_persona or "")
            )
            texto_tipo_persona = etiquetas_persona.get(
                valor_tipo.upper(), valor_tipo or "-"
            )

            color_inicial = (
                COLOR_NARANJA if valor_tipo.upper() == "MORAL" else COLOR_AZUL
            )

            inicial = ft.Container(
                content=ft.Text(
                    (cliente.razon_social or "?")[:1].upper(),
                    size=14,
                    color=COLOR_BLANCO,
                    weight=ft.FontWeight.BOLD,
                ),
                bgcolor=color_inicial,
                border_radius=9,
                width=35,
                height=35,
                alignment=ft.Alignment(0, 0),
            )

            fecha_creacion = (
                cliente.creado_en.strftime("%d/%m/%Y")
                if getattr(cliente, "creado_en", None)
                else "-"
            )

            nombre = ft.Container(
                expand=True,
                content=ft.Column(
                    expand=True,
                    spacing=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Text(
                            cliente.razon_social or "-",
                            size=14,
                            color=COLOR_NEGRO,
                            weight=ft.FontWeight.BOLD,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                        ft.Text(
                            f"Registro: {fecha_creacion}",
                            size=11,
                            color=COLOR_GRIS,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                ),
            )

            info_contacto = ft.Container(
                expand=True,
                content=ft.Column(
                    expand=True,
                    spacing=3,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        self.contacto(ft.Icons.PHONE_OUTLINED, cliente.telefono),
                        self.contacto(ft.Icons.MAIL_OUTLINE, cliente.correo_elect),
                    ],
                ),
            )

            estado_cliente = ft.Column(
                spacing=3,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=5,
                        controls=[
                            ft.Icon(
                                ft.Icons.CIRCLE,
                                size=10,
                                color=COLOR_VERDE if cliente.activo else COLOR_ROJO,
                            ),
                            ft.Text(
                                "Activo" if cliente.activo else "Inactivo",
                                size=13,
                                color=COLOR_NEGRO,
                                weight=ft.FontWeight.W_500,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"Nuevo cliente: {'Sí' if cliente.es_nuevo_cliente else 'No'}",
                        size=11,
                        color=COLOR_GRIS,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            )

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                content=ft.Row(
                                    expand=True,
                                    spacing=9,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[inicial, nombre],
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    cliente.rfc or "-",
                                    size=13,
                                    color=COLOR_NEGRO,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    texto_tipo_persona,
                                    size=13,
                                    color=COLOR_NEGRO,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    cliente.direccion or "-",
                                    size=13,
                                    color=COLOR_NEGRO,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            )
                        ),
                        ft.DataCell(info_contacto),
                        ft.DataCell(
                            ft.Container(expand=True, content=estado_cliente)
                        ),
                        ft.DataCell(
                            ft.Container(
                                alignment=ft.Alignment(0, 0),
                                content=boton(
                                    icono=ft.Icons.VISIBILITY_OUTLINED,
                                    tooltip="Ver ficha del cliente",
                                    tipo="accion",
                                    on_click=lambda e, c=cliente: self.ver_cliente(c),
                                ),
                            )
                        ),
                    ],
                )
            )

        tabla_clientes = tabla(
            columnas=[
                ("Cliente", 210),
                ("RFC", 160),
                ("Tipo de persona", 150),
                ("Dirección", 210),
                ("Información de contacto", 210),
                ("Estado", 150),
                ("Detalles", 100),
            ],
            filas=filas,
            column_spacing=6,
            horizontal_margin=6,
            heading_row_height=44,
            data_row_min_height=60,
            data_row_max_height=float("inf"),
            columnas_flexibles=True,
        )

        titulo = ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.GROUPS_OUTLINED,
                        color=COLOR_BLANCO,
                        size=24,
                    ),
                    bgcolor=COLOR_NARANJA,
                    border_radius=10,
                    padding=10,
                ),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text(
                            "Directorio de clientes",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_NEGRO,
                        ),
                        ft.Text(
                            f"{self.total_clientes} clientes registrados",
                            size=14,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                boton(
                    texto="Exportar",
                    icono=ft.Icons.DOWNLOAD_OUTLINED,
                    tipo="secundario",
                    width=180,
                    height=44,
                    on_click=self.exportar_clientes,
                ),
            ],
        )

        pie = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Mostrando {len(clientes)} de {self.total_clientes} clientes",
                    size=14,
                    color=COLOR_GRIS,
                ),
                paginacion(
                    total_registros=self.total_clientes,
                    registros_por_pagina=self.registros_por_pagina,
                    pagina_actual=self.pagina_actual,
                    on_change=self.cambiar_pagina,
                ),
            ],
        )

        return card(
            ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    titulo,
                    ft.Divider(height=1, color=COLOR_GRIS_CLARO),
                    ft.Container(expand=True, content=tabla_clientes),
                    ft.Divider(height=1, color=COLOR_GRIS_CLARO),
                    pie,
                ],
            ),
            padding=16,
            radius=10,
            shadow=sombra_suave(),
            expand=True,
        )

    def exportar_clientes(self, e):
        pass
