from datetime import datetime

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
        self.clientes_seleccionados = {}
        self.filtros_seleccionados = {
            "tipos_persona": set(),
            "estados": set(),
            "tipos_cliente": set(),
            "fecha_desde": None,
            "fecha_hasta": None,
        }
        self._checks_filtros = {}
        self._campo_fecha_filtro_activo = None
        self._panel_filtros_abierto = False
        self._menu_exportacion_abierto = False
        self._date_picker_filtros = ft.DatePicker(
            on_change=self._fecha_seleccionada,
            first_date=datetime(1900, 1, 1),
            last_date=datetime.now(),
            help_text="Selecciona una fecha de registro",
            cancel_text="Cancelar",
            confirm_text="Seleccionar",
        )

        self.build_ui()

    def build_ui(self):
        self._columna_contenido = ft.Column(
            expand=True,
            spacing=10,
            controls=[
                self.cabecera_clientes(),
                self.directorio(),
            ],
        )
        self._contenido = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[self._columna_contenido],
        )

        contenido_desplazable = ft.Column(
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
        self._layout_principal = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[contenido_desplazable],
        )
        self.content = self._layout_principal

    def cabecera_clientes(self):
        buscador = barra_busqueda(
            hint="Buscar por razón social...",
            on_change=self._con_cierre_de_menus(self.buscar),
        )
        buscador.height = 48
        buscador.on_focus = self.cerrar_menus

        self._boton_filtros = boton(
            texto="Filtros",
            icono=ft.Icons.TUNE,
            tipo="secundario",
            width=160,
            height=48,
            border_color="#C9DDF7",
            on_click=self.abrir_filtros,
        )
        self._actualizar_indicador_filtros()

        barra_herramientas = card(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    buscador,
                    self._boton_filtros,
                    boton(
                        texto="Registrar cliente",
                        icono=ft.Icons.ADD,
                        tipo="principal",
                        width=210,
                        height=48,
                        on_click=self._con_cierre_de_menus(self.ir_a_registro),
                    ),
                ],
            ),
            padding=12,
            radius=14,
            border_color="#E0ECF9",
            shadow=sombra_suave(),
        )

        banner = banner_modulo(
            src="fondo_PantallaClientes.jpg",
            categoria="Gestión de clientes",
            titulo="Clientes",
            descripcion=(
                "Administra la información fiscal y de contacto de agencias navieras, "
                "armadores y clientes."
            ),
            icono=ft.Icons.GROUPS_OUTLINED,
            altura=174,
        )
        banner.on_click = self.cerrar_menus

        return ft.Column(
            spacing=12,
            controls=[
                banner,
                barra_herramientas,
            ],
        )

    def buscar(self, e):
        self.busqueda = e.control.value or ""
        self.pagina_actual = 1
        self.clientes_seleccionados.clear()
        self.actualizar_directorio()

    def abrir_filtros(self, e):
        self.cerrar_menu_exportacion()
        if self._panel_filtros_abierto:
            self.cerrar_filtros()
            return

        self._checks_filtros = {}
        self._campo_fecha_desde = ft.TextField(
            value=self._formatear_fecha_filtro(self.filtros_seleccionados["fecha_desde"]),
            hint_text="dd/mm/aaaa",
            height=38,
            text_size=13,
            content_padding=ft.Padding(9, 0, 4, 8),
            border=ft.InputBorder.NONE,
            border_color="#C9DDF7",
            focused_border_color=COLOR_AZUL,
            border_radius=8,
            keyboard_type=ft.KeyboardType.DATETIME,
            on_change=self._cambio_fecha_filtro,
        )
        self._campo_fecha_hasta = ft.TextField(
            value=self._formatear_fecha_filtro(self.filtros_seleccionados["fecha_hasta"]),
            hint_text="dd/mm/aaaa",
            height=38,
            text_size=13,
            content_padding=ft.Padding(9, 0, 4, 8),
            border=ft.InputBorder.NONE,
            border_color="#C9DDF7",
            focused_border_color=COLOR_AZUL,
            border_radius=8,
            keyboard_type=ft.KeyboardType.DATETIME,
            on_change=self._cambio_fecha_filtro,
        )
        self._panel_filtros = self._crear_panel_filtros()
        self._contenido.controls.append(self._panel_filtros)
        self._panel_filtros_abierto = True
        self.update()

    def _actualizar_indicador_filtros(self):
        cantidad = self._contar_filtros(self.filtros_seleccionados)
        controles = [
            ft.Icon(ft.Icons.TUNE, size=18, color=COLOR_AZUL),
            ft.Text("Filtros", size=14, color=COLOR_AZUL, max_lines=1),
        ]
        if cantidad:
            controles.append(
                ft.Container(
                    width=20,
                    height=20,
                    alignment=ft.Alignment(0, 0),
                    bgcolor="#E8F2FF",
                    border_radius=10,
                    content=ft.Text(
                        str(cantidad),
                        size=11,
                        color=COLOR_AZUL,
                        weight=ft.FontWeight.BOLD,
                    ),
                )
            )
        self._boton_filtros.content = ft.Row(
            tight=True,
            spacing=7,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=controles,
        )

    def _contar_filtros(self, filtros):
        return (
            len(filtros["tipos_persona"])
            + len(filtros["estados"])
            + len(filtros["tipos_cliente"])
            + int(bool(filtros["fecha_desde"]))
            + int(bool(filtros["fecha_hasta"]))
        )

    def _formatear_fecha_filtro(self, valor):
        if isinstance(valor, str):
            return valor
        return valor.strftime("%d/%m/%Y") if valor else ""

    def _seccion_filtro(self, titulo, opciones, clave):
        seleccionados = self.filtros_seleccionados[clave]
        seccion, checkboxes = seccion_opciones_filtro(
            titulo,
            opciones,
            seleccionados,
            self._cambio_checkbox_filtro,
        )
        self._checks_filtros.update(
            {(clave, valor): checkbox for valor, checkbox in checkboxes.items()}
        )
        return seccion

    def _crear_panel_filtros(self):
        cantidad_filtros = self._contar_filtros(self.filtros_seleccionados)
        resumen_filtros = (
            "1 filtro seleccionado"
            if cantidad_filtros == 1
            else f"{cantidad_filtros} filtros seleccionados"
        )
        self._panel_filtros, self._texto_resumen_filtros = panel_filtros(
            titulo="Filtrar clientes",
            secciones=[
                self._seccion_filtro(
                    "Tipo de persona",
                    [
                        ("FISICA", "Persona Física"),
                        ("MORAL", "Persona Moral"),
                        ("EXTRANJERO", "Extranjero"),
                    ],
                    "tipos_persona",
                ),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_filtro(
                    "Estado del cliente",
                    [("ACTIVO", "Activo"), ("INACTIVO", "Inactivo")],
                    "estados",
                ),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_filtro(
                    "Tipo de cliente",
                    [("NUEVO", "Nuevo"), ("EXISTENTE", "Existente")],
                    "tipos_cliente",
                ),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_fechas_filtro(),
            ],
            resumen=resumen_filtros,
            on_limpiar=self.limpiar_filtros,
            on_aplicar=self.aplicar_filtros,
            on_cerrar=self.cerrar_filtros,
        )
        return self._panel_filtros

    def _seccion_fechas_filtro(self):
        return ft.Container(
            padding=ft.Padding(14, 8, 14, 12),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Text(
                        "Fecha de registro",
                        size=12,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BANNER,
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Column(
                                expand=True,
                                spacing=3,
                                controls=[
                                    ft.Text("Desde", size=11, color=COLOR_GRIS),
                                    self._envoltura_campo_fecha(
                                        self._campo_fecha_desde, "fecha_desde"
                                    ),
                                ],
                            ),
                            ft.Column(
                                expand=True,
                                spacing=3,
                                controls=[
                                    ft.Text("Hasta", size=11, color=COLOR_GRIS),
                                    self._envoltura_campo_fecha(
                                        self._campo_fecha_hasta, "fecha_hasta"
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _boton_calendario_filtro(self, campo):
        return ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
            icon_size=16,
            icon_color=COLOR_AZUL,
            tooltip="Seleccionar fecha",
            on_click=lambda e: self.abrir_calendario_filtro(campo),
            width=34,
            height=34,
            padding=0,
            alignment=ft.Alignment(0, 0),
        )

    def _envoltura_campo_fecha(self, campo_fecha, campo):
        return ft.Container(
            height=42,
            padding=ft.Padding(4, 1, 4, 1),
            border=ft.Border.all(1, "#C9DDF7"),
            border_radius=8,
            content=ft.Row(
                spacing=2,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(expand=True, content=campo_fecha),
                    self._boton_calendario_filtro(campo),
                ],
            ),
        )

    def abrir_calendario_filtro(self, campo):
        self._campo_fecha_filtro_activo = (
            self._campo_fecha_desde if campo == "fecha_desde" else self._campo_fecha_hasta
        )
        valor = self._campo_fecha_filtro_activo.value
        if valor:
            try:
                fecha = datetime.strptime(valor.strip(), "%d/%m/%Y")
                self._date_picker_filtros.value = fecha
            except ValueError:
                self._date_picker_filtros.value = None
        else:
            self._date_picker_filtros.value = None
        if self._date_picker_filtros not in self._page.overlay:
            self._page.overlay.append(self._date_picker_filtros)
        self._date_picker_filtros.open = True
        self._page.update()

    def _fecha_seleccionada(self, e):
        if self._date_picker_filtros.value and self._campo_fecha_filtro_activo:
            self._campo_fecha_filtro_activo.value = (
                self._date_picker_filtros.value.strftime("%d/%m/%Y")
            )
            self._campo_fecha_filtro_activo.update()
            self._actualizar_resumen_filtros()
            self._texto_resumen_filtros.update()

    def limpiar_filtros(self, e=None):
        Herramientas.limpiar_controles(
            [
                *self._checks_filtros.values(),
                self._campo_fecha_desde,
                self._campo_fecha_hasta,
                self._date_picker_filtros,
            ]
        )
        self.filtros_seleccionados = {
            "tipos_persona": set(),
            "estados": set(),
            "tipos_cliente": set(),
            "fecha_desde": None,
            "fecha_hasta": None,
        }
        if self._date_picker_filtros in self._page.overlay:
            self._date_picker_filtros.update()
        self._actualizar_indicador_filtros()
        self._actualizar_resumen_filtros()
        self._panel_filtros.update()

    def _cambio_checkbox_filtro(self, e):
        self._actualizar_resumen_filtros()
        self._texto_resumen_filtros.update()

    def _cambio_fecha_filtro(self, e):
        self._actualizar_resumen_filtros()
        self._texto_resumen_filtros.update()

    def _actualizar_resumen_filtros(self):
        cantidad = sum(bool(checkbox.value) for checkbox in self._checks_filtros.values())
        cantidad += int(bool(self._campo_fecha_desde.value))
        cantidad += int(bool(self._campo_fecha_hasta.value))
        self._texto_resumen_filtros.value = (
            "1 filtro seleccionado"
            if cantidad == 1
            else f"{cantidad} filtros seleccionados"
        )

    def aplicar_filtros(self, e=None):
        self.filtros_seleccionados = {
            "tipos_persona": set(),
            "estados": set(),
            "tipos_cliente": set(),
            "fecha_desde": (self._campo_fecha_desde.value or "").strip() or None,
            "fecha_hasta": (self._campo_fecha_hasta.value or "").strip() or None,
        }
        for (grupo, valor), checkbox in self._checks_filtros.items():
            if checkbox.value:
                self.filtros_seleccionados[grupo].add(valor)
        self._actualizar_indicador_filtros()
        self.cerrar_filtros()

    def cerrar_filtros(self, e=None):
        if self._panel_filtros_abierto:
            self._contenido.controls = [self._columna_contenido]
            self._panel_filtros_abierto = False
            self.update()

    def ir_a_registro(self, e):
        if self._panel_filtros_abierto:
            self.cerrar_filtros()
        self.content = PantallaRegistrarCliente(
            self._page,
            self.servicio_cliente,
            vista_anterior=self,
        )
        self.update()

    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        self.clientes_seleccionados.clear()
        self.actualizar_directorio()

    def actualizar_directorio(self):
        self._columna_contenido.controls[1] = self.directorio()
        self.update()

    def contacto(self, icono, texto, max_lines=1):
        return ft.Container(
            expand=True,
            content=ft.Row(
                expand=True,
                spacing=5,
                controls=[
                    ft.Icon(
                        icono,
                        size=14,
                        color="#6D89AB",
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            texto or "-",
                            size=13,
                            color=COLOR_NEGRO,
                            max_lines=max_lines,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                ],
            ),
        )

    def _insignia_tabla(self, texto, icono, fondo, color):
        return ft.Container(
            padding=ft.Padding(7, 4, 7, 4),
            bgcolor=fondo,
            border_radius=18,
            content=ft.Row(
                tight=True,
                spacing=5,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icono, size=14, color=color),
                    ft.Text(
                        texto,
                        size=12,
                        color=color,
                        weight=ft.FontWeight.BOLD,
                        max_lines=1,
                        text_align=ft.TextAlign.CENTER,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            ),
        )

    def _encabezado_columna(self, texto, icono):
        return ft.Row(
            tight=True,
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icono, size=15, color="#6684A8"),
                ft.Text(
                    texto,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_NEGRO,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
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
                        campo_cliente_nuevo,
                        campo_cliente_activo,
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
        self.dialogo_cliente.content = ft.Container(
            width=650,
            content=self._contenido_ficha_cliente(),
        )
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

    def _clave_cliente(self, cliente):
        return getattr(cliente, "id_cliente", getattr(cliente, "id", id(cliente)))

    def seleccionar_cliente(self, cliente, seleccionado):
        clave = self._clave_cliente(cliente)
        if seleccionado:
            self.clientes_seleccionados[clave] = cliente
        else:
            self.clientes_seleccionados.pop(clave, None)
        self._actualizar_vista_seleccion({clave})

    def seleccionar_pagina(self, clientes, seleccionado):
        claves = set()
        for cliente in clientes:
            clave = self._clave_cliente(cliente)
            claves.add(clave)
            if seleccionado:
                self.clientes_seleccionados[clave] = cliente
            else:
                self.clientes_seleccionados.pop(clave, None)
        self._actualizar_vista_seleccion(claves)

    def _actualizar_vista_seleccion(self, claves_actualizadas):
        for clave in claves_actualizadas:
            checkbox = self._checkboxes_seleccion_clientes.get(clave)
            fila = self._filas_seleccion_clientes.get(clave)
            seleccionado = clave in self.clientes_seleccionados
            if checkbox is not None:
                checkbox.value = seleccionado
            if fila is not None:
                fila.selected = seleccionado
                fila.update()

        claves_pagina = self._claves_clientes_pagina
        self._checkbox_seleccionar_pagina.value = bool(claves_pagina) and all(
            clave in self.clientes_seleccionados for clave in claves_pagina
        )
        self._checkbox_seleccionar_pagina.update()

        cantidad = len(self.clientes_seleccionados)
        self._texto_seleccionados.value = (
            f"{cantidad} cliente seleccionado"
            if cantidad == 1
            else f"{cantidad} clientes seleccionados"
        )
        self._barra_seleccion.visible = cantidad > 0
        self._barra_seleccion.update()

        self._boton_exportar.width = 230 if cantidad else 150
        self._boton_exportar.content.controls[1].value = (
            f"Exportar seleccionados ({cantidad})" if cantidad else "Exportar"
        )
        self._boton_exportar.update()

    def cancelar_seleccion(self, e=None):
        claves = set(self.clientes_seleccionados)
        self.clientes_seleccionados.clear()
        self._actualizar_vista_seleccion(claves)

    def confirmar_eliminar_seleccionados(self, e=None):
        cantidad = len(self.clientes_seleccionados)
        if not cantidad:
            return
        self._page.show_dialog(
            dialogo_confirmacion(
                page=self._page,
                titulo="Eliminar clientes seleccionados",
                mensaje=(
                    f"¿Deseas eliminar {cantidad} cliente(s) seleccionado(s)? "
                    "Esta acción no se puede deshacer."
                ),
                on_confirmar=self._eliminar_seleccionados,
                texto_confirmar="Eliminar",
                texto_cancelar="Cancelar",
                color_confirmar=COLOR_ROJO,
            )
        )

    def _eliminar_seleccionados(self):
        seleccionados = list(self.clientes_seleccionados.values())
        eliminados = 0
        try:
            for cliente in seleccionados:
                self.controlador.eliminar_cliente(cliente)
                eliminados += 1
        except Exception as error:
            # No se modifica el controlador; se informa el fallo desde la pantalla.
            for cliente in seleccionados[:eliminados]:
                self.clientes_seleccionados.pop(self._clave_cliente(cliente), None)
            self.actualizar_directorio()
            mostrar_notificacion(
                self._page,
                f"Se eliminaron {eliminados}; ocurrió un error: {error}",
                COLOR_ROJO,
            )
            return

        self.clientes_seleccionados.clear()
        paginas = max(
            1,
            (max(0, self.total_clientes - eliminados) + self.registros_por_pagina - 1)
            // self.registros_por_pagina,
        )
        self.pagina_actual = min(self.pagina_actual, paginas)
        self.actualizar_directorio()
        mostrar_notificacion(
            self._page,
            f"Se eliminaron {eliminados} cliente(s).",
            COLOR_VERDE,
        )

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
        colores_avatar = [COLOR_AZUL, COLOR_NARANJA, "#08AFAE", "#7040D7"]
        claves_pagina = [self._clave_cliente(c) for c in clientes]
        pagina_completa_seleccionada = bool(clientes) and all(
            clave in self.clientes_seleccionados for clave in claves_pagina
        )
        self._claves_clientes_pagina = claves_pagina
        self._checkboxes_seleccion_clientes = {}
        self._filas_seleccion_clientes = {}
        encabezado_seleccion = ft.Container(
            width=52,
            alignment=ft.Alignment(0, 0),
            content=ft.Checkbox(
                value=pagina_completa_seleccionada,
                active_color=COLOR_AZUL,
                check_color=COLOR_BLANCO,
                border_side=ft.BorderSide(1.5, "#7186A0"),
                shape=ft.RoundedRectangleBorder(radius=3),
                on_change=self._con_cierre_de_menus(
                    lambda e, cs=list(clientes): self.seleccionar_pagina(
                        cs, bool(e.control.value)
                    )
                ),
            ),
        )
        self._checkbox_seleccionar_pagina = encabezado_seleccion.content

        filas = []
        for indice, cliente in enumerate(clientes):
            valor_tipo = (
                cliente.tipo_persona.value
                if hasattr(cliente.tipo_persona, "value")
                else str(cliente.tipo_persona or "")
            )
            texto_tipo = etiquetas_persona.get(valor_tipo.upper(), valor_tipo or "—")
            nombre_cliente = cliente.razon_social or "—"
            fecha = (
                cliente.creado_en.strftime("%d/%m/%Y")
                if getattr(cliente, "creado_en", None)
                else "—"
            )
            clave = self._clave_cliente(cliente)
            seleccionado = clave in self.clientes_seleccionados

            avatar = avatar_inicial(
                nombre_cliente,
                color=colores_avatar[indice % len(colores_avatar)],
                size=44,
            )
            celda_cliente = ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    avatar,
                    ft.Column(
                        expand=True,
                        spacing=3,
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Text(
                                nombre_cliente,
                                size=14,
                                color=COLOR_NEGRO,
                                weight=ft.FontWeight.BOLD,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text(
                                f"Registro: {fecha}",
                                size=12,
                                color=COLOR_GRIS,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ],
            )

            contacto = ft.Column(
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.contacto(ft.Icons.PHONE_OUTLINED, cliente.telefono),
                    self.contacto(
                        ft.Icons.MAIL_OUTLINE,
                        cliente.correo_elect,
                        max_lines=2,
                    ),
                ],
            )
            direccion = ft.Text(
                cliente.direccion or "—",
                size=13,
                color=COLOR_NEGRO,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            )
            insignias_tipo = {
                "FISICA": ("#E8F2FF", "#1875D1"),
                "MORAL": ("#FFF1E5", "#D96900"),
                "EXTRANJERO": ("#E5EEFF", "#315F9B"),
            }
            fondo_tipo, color_tipo = insignias_tipo.get(
                valor_tipo.upper(), ("#EEF2F7", "#5E718A")
            )
            insignia_tipo = self._insignia_tabla(
                texto_tipo,
                {
                    "FISICA": ft.Icons.PERSON_OUTLINED,
                    "MORAL": ft.Icons.BUSINESS_OUTLINED,
                    "EXTRANJERO": ft.Icons.PUBLIC_OUTLINED,
                }.get(valor_tipo.upper(), ft.Icons.BADGE_OUTLINED),
                fondo_tipo,
                color_tipo,
            )
            insignia_estado = self._insignia_tabla(
                "Activo" if cliente.activo else "Inactivo",
                ft.Icons.CHECK_CIRCLE_OUTLINE if cliente.activo else ft.Icons.CLOSE,
                "#DDF7EF" if cliente.activo else "#FDE8EB",
                "#009B82" if cliente.activo else COLOR_ROJO,
            )
            insignia_novedad = self._insignia_tabla(
                "Nuevo" if cliente.es_nuevo_cliente else "Existente",
                ft.Icons.AUTO_AWESOME
                if cliente.es_nuevo_cliente
                else ft.Icons.HOW_TO_REG_OUTLINED,
                "#FFF0E1" if cliente.es_nuevo_cliente else "#EEF2F7",
                "#D96900" if cliente.es_nuevo_cliente else "#5E718A",
            )
            estado = ft.Column(
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    insignia_estado,
                    insignia_novedad,
                ],
            )

            checkbox_seleccion_cliente = ft.Checkbox(
                value=seleccionado,
                active_color=COLOR_AZUL,
                check_color=COLOR_BLANCO,
                border_side=ft.BorderSide(1.5, "#7186A0"),
                shape=ft.RoundedRectangleBorder(radius=3),
                on_change=self._con_cierre_de_menus(
                    lambda e, c=cliente: self.seleccionar_cliente(
                        c, bool(e.control.value)
                    )
                ),
            )
            fila_cliente = ft.DataRow(
                selected=seleccionado,
                cells=[
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                alignment=ft.Alignment(0, 0),
                                content=checkbox_seleccion_cliente,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                padding=ft.Padding(8, 0, 0, 0),
                                content=celda_cliente,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                cliente.rfc or "—",
                                size=13,
                                color=COLOR_NEGRO,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                alignment=ft.Alignment(0, 0),
                                content=insignia_tipo,
                            )
                        ),
                        ft.DataCell(ft.Container(expand=True, content=direccion)),
                        ft.DataCell(ft.Container(expand=True, content=contacto)),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                alignment=ft.Alignment(0, 0),
                                content=estado,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                alignment=ft.Alignment(0, 0),
                                content=boton_icono_enmarcado(
                                    ft.Icons.VISIBILITY_OUTLINED,
                                    tooltip="Ver ficha del cliente",
                                    on_click=self._con_cierre_de_menus(
                                        lambda e, c=cliente: self.ver_cliente(c)
                                    ),
                                    color=COLOR_AZUL,
                                    border_color="#C9DDF7",
                                    size=38,
                                ),
                            )
                        ),
                    ],
            )
            filas.append(fila_cliente)
            self._checkboxes_seleccion_clientes[clave] = checkbox_seleccion_cliente
            self._filas_seleccion_clientes[clave] = fila_cliente

        encabezado_tipo_persona = ft.Row(
            tight=True,
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.BUSINESS_OUTLINED, size=14, color="#6684A8"),
                ft.Text(
                    "Tipo de\npersona",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_NEGRO,
                    max_lines=2,
                ),
            ],
        )

        tabla_clientes = tabla(
            columnas=[
                (encabezado_seleccion, 52),
                (self._encabezado_columna("Cliente", ft.Icons.PERSON_OUTLINED), 285),
                (self._encabezado_columna("RFC", ft.Icons.BADGE_OUTLINED), 135),
                (
                    encabezado_tipo_persona,
                    120,
                ),
                (
                    self._encabezado_columna(
                        "Dirección", ft.Icons.LOCATION_ON_OUTLINED
                    ),
                    172,
                ),
                (
                    self._encabezado_columna(
                        "Contacto", ft.Icons.CONTACT_PHONE_OUTLINED
                    ),
                    202,
                ),
                (self._encabezado_columna("Estado", ft.Icons.CHECK_CIRCLE_OUTLINE), 125),
                ("Acciones", 76),
            ],
            filas=filas,
            column_spacing=6,
            horizontal_margin=6,
            heading_row_height=46,
            data_row_min_height=80,
            data_row_max_height=float("inf"),
            columnas_flexibles=True,
            heading_row_color="#EEF5FD",
            heading_text_size=14,
            heading_text_color=COLOR_NEGRO,
            vertical_lines=True,
            horizontal_lines=True,
            border_color="#E3EAF2",
            columnas_compactas=True,
        )

        self._texto_seleccionados = ft.Text(
            (
                f"{len(self.clientes_seleccionados)} cliente seleccionado"
                if len(self.clientes_seleccionados) == 1
                else f"{len(self.clientes_seleccionados)} clientes seleccionados"
            ),
            size=12,
            color=COLOR_NEGRO,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
        )
        self._barra_seleccion = ft.Row(
            visible=bool(self.clientes_seleccionados),
            spacing=7,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(
                    ft.Icons.CHECK_CIRCLE_OUTLINED,
                    size=18,
                    color=COLOR_AZUL,
                ),
                self._texto_seleccionados,
                boton(
                    texto="Eliminar",
                    icono=ft.Icons.DELETE_OUTLINE,
                    tipo="secundario",
                    color=COLOR_ROJO,
                    border_color="#FFC8CF",
                    height=36,
                    on_click=self._con_cierre_de_menus(
                        self.confirmar_eliminar_seleccionados
                    ),
                ),
                ft.TextButton(
                    "Cancelar",
                    on_click=self._con_cierre_de_menus(self.cancelar_seleccion),
                    style=ft.ButtonStyle(color=COLOR_BANNER),
                ),
            ],
        )
        self._boton_exportar = boton(
            texto=(
                f"Exportar seleccionados ({len(self.clientes_seleccionados)})"
                if self.clientes_seleccionados
                else "Exportar"
            ),
            icono=ft.Icons.DOWNLOAD_OUTLINED,
            tipo="secundario",
            width=230 if self.clientes_seleccionados else 150,
            height=44,
            border_color="#C9DDF7",
            on_click=self.alternar_menu_exportacion,
        )
        self._texto_resumen_exportacion = ft.Text(
            self._descripcion_exportacion(),
            size=11,
            color=COLOR_GRIS,
        )
        self._menu_exportacion = menu_exportacion(
            descripcion=self._texto_resumen_exportacion,
            on_pdf=self.cerrar_menu_exportacion,
            on_excel=self.cerrar_menu_exportacion,
            descripcion_pdf="Genera un archivo PDF en el directorio de clientes.",
            descripcion_excel="Descarga un archivo Excel con los datos de clientes.",
            top=52,
            right=0,
            width=280,
        )
        self._menu_exportacion.visible = False

        cabecera_directorio = ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=52,
                    height=52,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=COLOR_NARANJA,
                    border_radius=13,
                    on_click=self.cerrar_menus,
                    content=ft.Icon(
                        ft.Icons.CONTACTS_OUTLINED,
                        color=COLOR_BLANCO,
                        size=27,
                    ),
                ),
                ft.Container(
                    expand=True,
                    on_click=self.cerrar_menus,
                    content=ft.Column(
                        expand=True,
                        spacing=3,
                        controls=[
                            ft.Text(
                                "Directorio de clientes",
                                size=20,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_NEGRO,
                            ),
                            ft.Text(
                                f"{self.total_clientes} clientes registrados",
                                size=13,
                                color=COLOR_GRIS,
                            ),
                        ],
                    ),
                ),
                self._barra_seleccion,
                self._boton_exportar,
            ],
        )

        controles = [
            cabecera_directorio,
            ft.Divider(height=1, color="#E2EDF9"),
            ft.Container(
                expand=True,
                border=ft.Border.all(1, "#E2EDF9"),
                border_radius=12,
                bgcolor=COLOR_BLANCO,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
                on_click=self.cerrar_menus,
                content=tabla_clientes,
            ),
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        f"Mostrando {len(clientes)} de {self.total_clientes} clientes",
                        size=12,
                        color=COLOR_GRIS,
                    ),
                    paginacion(
                        total_registros=self.total_clientes,
                        registros_por_pagina=self.registros_por_pagina,
                        pagina_actual=self.pagina_actual,
                        on_change=self._con_cierre_de_menus(
                            self.cambiar_pagina
                        ),
                    ),
                ],
            ),
        ]

        self._contenido_directorio = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=controles,
                ),
                self._menu_exportacion,
            ],
        )
        return card(
            self._contenido_directorio,
            padding=14,
            radius=16,
            border_color="#E0ECF9",
            shadow=sombra_suave(),
            expand=True,
        )

    def alternar_menu_exportacion(self, e=None):
        self.cerrar_filtros()
        self._menu_exportacion_abierto = not self._menu_exportacion_abierto
        self._actualizar_menu_exportacion()

    def cerrar_menus(self, e=None):
        self.cerrar_menu_exportacion()
        self.cerrar_filtros()

    def cerrar_menu_exportacion(self, e=None):
        if not self._menu_exportacion_abierto:
            return
        self._menu_exportacion_abierto = False
        self._actualizar_menu_exportacion()

    def _actualizar_menu_exportacion(self):
        if self._menu_exportacion_abierto:
            self._texto_resumen_exportacion.value = self._descripcion_exportacion()
        self._menu_exportacion.visible = self._menu_exportacion_abierto
        self._menu_exportacion.update()

    def _con_cierre_de_menus(self, accion):
        def ejecutar(*args, **kwargs):
            try:
                return accion(*args, **kwargs)
            finally:
                self.cerrar_menus()

        return ejecutar

    def _descripcion_exportacion(self):
        if self.clientes_seleccionados:
            return "Elige un formato para exportar los clientes seleccionados."

        filtros_activos = any(
            self.filtros_seleccionados.get(grupo)
            for grupo in ("tipos_persona", "estados", "tipos_cliente")
        ) or any(
            self.filtros_seleccionados.get(campo)
            for campo in ("fecha_desde", "fecha_hasta")
        )
        if self.busqueda.strip() or filtros_activos:
            return "Elige un formato para exportar los clientes filtrados."
        return "Elige un formato para exportar los clientes encontrados."