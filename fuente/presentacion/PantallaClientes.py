import flet as ft
from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorClientes import ControladorClientes


class PantallaClientes(ft.Container):
    def __init__(self):
        super().__init__(
            expand=True,
            padding=24,
            bgcolor=COLOR_FONDO,
        )

        self.controlador = ControladorClientes()
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.total_clientes = 0
        self.busqueda = ""

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=18,
            controls=[
                self.encabezado(),
                self.barra_filtros(),
                self.directorio(),
            ],
        )

    def encabezado(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text(
                            "Gestión de Clientes",
                            size=27,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            "Administra la información fiscal y de contacto de agencias navieras, armadores y clientes.",
                            size=13,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                ft.FilledButton(
                    content=ft.Row(
                        tight=True,
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.ADD,
                                size=19,
                                color=COLOR_BLANCO,
                            ),
                            ft.Text(
                                "Registrar nuevo cliente",
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BLANCO,
                            ),
                        ],
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_NARANJA,
                        color=COLOR_BLANCO,
                        padding=ft.Padding(
                            left=18,
                            right=18,
                            top=16,
                            bottom=16,
                        ),
                        shape=ft.RoundedRectangleBorder(
                            radius=9
                        ),
                    ),
                ),
            ],
        )

    def barra_filtros(self):
        return card(
            ft.Row(
                spacing=10,
                controls=[
                    barra_busqueda(
                        hint="Buscar por nombre, RFC o contacto...",
                        on_change=self.buscar,
                    ),
                    boton_filtros(
                        on_click=self.abrir_filtros
                    ),
                ],
            ),
            padding=12,
        )

    def buscar(self, e):
        self.busqueda = e.control.value or ""
        self.pagina_actual = 1
        self.actualizar_directorio()

    def abrir_filtros(self, e):
        pass

    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        self.actualizar_directorio()

    def actualizar_directorio(self):
        self.content.controls[2] = self.directorio()
        self.update()

    def directorio(self):
        offset = (
            self.pagina_actual - 1
        ) * self.registros_por_pagina

        clientes, self.total_clientes = (
            self.controlador.obtener_clientes(
                texto=self.busqueda,
                limit=self.registros_por_pagina,
                offset=offset,
            )
        )

        filas = []

        for cliente in clientes:
            color_inicial = (
                COLOR_NARANJA
                if cliente.tipo_cliente == "Armador"
                else COLOR_AZUL
            )

            inicial = ft.Container(
                content=ft.Text(
                    cliente.nombre[:1],
                    color=COLOR_BLANCO,
                    weight=ft.FontWeight.BOLD,
                ),
                bgcolor=color_inicial,
                border_radius=9,
                width=35,
                height=35,
                alignment=ft.Alignment(0, 0),
            )

            info_contacto = ft.Column(
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=5,
                        controls=[
                            ft.Icon(
                                ft.Icons.PHONE_OUTLINED,
                                size=13,
                                color=COLOR_GRIS,
                            ),
                            ft.Text(
                                cliente.telefono,
                                size=11,
                                color=COLOR_NEGRO,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=5,
                        controls=[
                            ft.Icon(
                                ft.Icons.MAIL_OUTLINE,
                                size=13,
                                color=COLOR_GRIS,
                            ),
                            ft.Text(
                                cliente.correo_elect,
                                size=11,
                                color=COLOR_GRIS,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                        ],
                    ),
                ],
            )

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                width=245,
                                content=ft.Row(
                                    spacing=9,
                                    controls=[
                                        inicial,
                                        ft.Container(
                                            expand=True,
                                            content=ft.Text(
                                                cliente.nombre,
                                                size=12,
                                                color=COLOR_BANNER,
                                                weight=ft.FontWeight.BOLD,
                                                max_lines=2,
                                                overflow=ft.TextOverflow.ELLIPSIS,
                                            ),
                                        ),
                                    ],
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=120,
                                content=ft.Text(
                                    cliente.rfc,
                                    size=11,
                                    color=COLOR_GRIS,
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=240,
                                content=ft.Text(
                                    cliente.direccion_fiscal,
                                    size=11,
                                    color=COLOR_GRIS,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=135,
                                content=ft.Text(
                                    cliente.tipo_cliente,
                                    size=11,
                                    color=COLOR_GRIS,
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=230,
                                content=info_contacto,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=125,
                                content=ft.Row(
                                    spacing=0,
                                    controls=[
                                        boton_accion(
                                            ft.Icons.VISIBILITY_OUTLINED,
                                            "Ver cliente",
                                        ),
                                        boton_accion(
                                            ft.Icons.EDIT_OUTLINED,
                                            "Editar cliente",
                                        ),
                                        boton_accion(
                                            ft.Icons.DELETE_OUTLINE,
                                            "Eliminar cliente",
                                            COLOR_ROJO,
                                        ),
                                    ],
                                ),
                            )
                        ),
                    ],
                )
            )

        columnas = [
            ("Cliente", 245),
            ("RFC", 120),
            ("Dirección fiscal", 240),
            ("Tipo de cliente", 135),
            ("Información de contacto", 230),
            ("Acciones", 125),
        ]

        tabla_clientes = tabla(
            columnas=columnas,
            filas=filas,
        )

        titulo = ft.Row(
            spacing=12,
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.GROUPS_OUTLINED,
                        color=COLOR_AZUL,
                        size=24,
                    ),
                    bgcolor=COLOR_GRIS_CLARO,
                    border_radius=10,
                    padding=10,
                ),
                ft.Column(
                    expand=True,
                    spacing=3,
                    controls=[
                        ft.Text(
                            "Directorio de clientes",
                            size=17,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            f"{self.total_clientes} clientes registrados",
                            size=12,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                boton_exportar(
                    on_click=self.exportar_clientes
                ),
            ],
        )

        pie = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Mostrando {len(clientes)} de {self.total_clientes} clientes",
                    size=11,
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
                spacing=12,
                controls=[
                    titulo,
                    ft.Divider(
                        height=1,
                        color=COLOR_GRIS_CLARO,
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Row(
                            [tabla_clientes],
                            expand=True,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                    ),
                    ft.Divider(
                        height=1,
                        color=COLOR_GRIS_CLARO,
                    ),
                    pie,
                ],
            ),
            padding=16,
        )

    def exportar_clientes(self, e):
        pass