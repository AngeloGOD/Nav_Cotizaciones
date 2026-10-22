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
        return ft.Row(
            spacing=5,
            controls=[
                ft.Icon(
                    icono,
                    size=15,
                    color=COLOR_GRIS,
                ),
                ft.Text(
                    texto or "-",
                    size=14,
                    color=COLOR_NEGRO,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        )

    def editar_cliente(self, cliente):
        self.content = PantallaRegistrarCliente(
            self._page,
            self.servicio_cliente,
            vista_anterior=self,
            cliente=cliente,
        )
        self.update()

    def eliminar_cliente(self, cliente):
        dialogo = dialogo_confirmacion(
            page=self._page,
            titulo="Confirmar eliminación",
            mensaje=(
                f"¿Deseas eliminar el cliente "
                f"'{cliente.razon_social}'? Esta acción no se puede deshacer."
            ),
            on_confirmar=lambda: self._confirmar_eliminacion(cliente),
            texto_confirmar="Eliminar",
        )
        self._page.show_dialog(dialogo)

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
                            size=12,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
            )

            info_contacto = ft.Column(
                spacing=3,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.contacto(ft.Icons.PHONE_OUTLINED, cliente.telefono),
                    self.contacto(ft.Icons.MAIL_OUTLINE, cliente.correo_elect),
                ],
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
                            ),
                        ],
                    ),
                    ft.Text(
                        f"Nuevo cliente: {'Sí' if cliente.es_nuevo_cliente else 'No'}",
                        size=12,
                        color=COLOR_GRIS,
                    ),
                ],
            )

            acciones = ft.Row(
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    boton(
                        icono=ft.Icons.EDIT_OUTLINED,
                        tooltip="Editar cliente",
                        tipo="accion",
                        on_click=lambda e, c=cliente: self.editar_cliente(c),
                    ),
                    boton(
                        icono=ft.Icons.DELETE_OUTLINE,
                        tooltip="Eliminar cliente",
                        tipo="accion",
                        color=COLOR_ROJO,
                        on_click=lambda e, c=cliente: self.eliminar_cliente(c),
                    ),
                ],
            )

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Row(
                                spacing=9,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[inicial, nombre],
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                cliente.rfc or "-",
                                size=14,
                                color=COLOR_NEGRO,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                texto_tipo_persona,
                                size=14,
                                color=COLOR_NEGRO,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                cliente.direccion or "-",
                                size=14,
                                color=COLOR_NEGRO,
                                max_lines=2,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            )
                        ),
                        ft.DataCell(info_contacto),
                        ft.DataCell(estado_cliente),
                        ft.DataCell(acciones),
                    ],
                )
            )

        tabla_clientes = tabla(
            columnas=[
                ("Cliente", 230),
                ("RFC", 120),
                ("Tipo de persona", 145),
                ("Dirección", 220),
                ("Información de contacto", 240),
                ("Estado", 150),
                ("Acciones", 125),
            ],
            filas=filas,
            column_spacing=10,
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
