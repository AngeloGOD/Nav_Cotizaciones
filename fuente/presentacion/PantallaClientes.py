import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorClientes import ControladorClientes
from fuente.presentacion.PantallaRegistrarCliente import PantallaRegistrarCliente


class PantallaClientes(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page

        self.controlador = ControladorClientes()
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.total_clientes = 0
        self.busqueda = ""

        self.build_ui()

    def build_ui(self):
        contenido = ft.Column(
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
                    padding=ft.Padding(
                        left=14,
                        right=14,
                        top=8,
                        bottom=18,
                    ),
                    content=contenido,
                )
            ],
        )
    def cabecera_clientes(self):
        return card(
            ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        height=150,
                        border_radius=12,
                        clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        content=ft.Stack(
                            expand=True,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    image=ft.DecorationImage(
                                        src="fondo_PantallaClientes.jpg",
                                        fit=ft.BoxFit.COVER,
                                        alignment=ft.Alignment(1, 0),
                                    ),
                                ),

                                ft.Container(
                                    expand=True,
                                    gradient=ft.LinearGradient(
                                        begin=ft.Alignment(-1, 0),
                                        end=ft.Alignment(1, 0),
                                        colors=[
                                            ft.Colors.WHITE,
                                            ft.Colors.WHITE_70,
                                            ft.Colors.WHITE_54,
                                            ft.Colors.TRANSPARENT,
                                        ],
                                        stops=[
                                            0.0,
                                            0.38,
                                            0.65,
                                            1.0,
                                        ],
                                    ),
                                ),

                                ft.Container(
                                    expand=True,
                                    padding=ft.Padding(
                                        left=26,
                                        right=26,
                                        top=20,
                                        bottom=20,
                                    ),
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
                            ],
                        ),
                    ),

                    ft.Container(
                        padding=ft.Padding(
                            left=10,
                            right=10,
                            top=10,
                            bottom=10,
                        ),
                        content=ft.Row(
                            spacing=8,
                            controls=[
                                ft.Container(
                                    expand=True,
                                    content=barra_busqueda(
                                        hint="Buscar por nombre, RFC o contacto...",
                                        on_change=self.buscar,
                                    ),
                                ),

                                boton_filtros(
                                    on_click=self.abrir_filtros,
                                ),

                                ft.FilledButton(
                                    width=185,
                                    content=ft.Row(
                                        tight=True,
                                        spacing=7,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.ADD,
                                                size=18,
                                                color=COLOR_BLANCO,
                                            ),
                                            ft.Text(
                                                "Registrar cliente",
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
                                            radius=8,
                                        ),
                                        padding=ft.Padding(
                                            left=18,
                                            right=18,
                                            top=12,
                                            bottom=12,
                                        ),
                                    ),
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
            vista_anterior=self,
        )
        self.update()

    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        self.actualizar_directorio()

    def actualizar_directorio(self):
        self.content.controls[0].content.controls[1] = self.directorio()
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

            nombre = ft.Container(
                width=175,
                content=ft.Text(
                    cliente.nombre,
                    size=14,
                    color=COLOR_NEGRO,
                    weight=ft.FontWeight.BOLD,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            )

            info_contacto = ft.Container(
                width=260,
                content=ft.Column(
                    spacing=3,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.Icon(
                                    ft.Icons.PHONE_OUTLINED,
                                    size=15,
                                    color=COLOR_GRIS,
                                ),
                                ft.Container(
                                    width=230,
                                    content=ft.Text(
                                        cliente.telefono,
                                        size=14,
                                        color=COLOR_NEGRO,
                                        max_lines=1,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ),
                            ],
                        ),
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.Icon(
                                    ft.Icons.MAIL_OUTLINE,
                                    size=15,
                                    color=COLOR_GRIS,
                                ),
                                ft.Container(
                                    width=230,
                                    content=ft.Text(
                                        cliente.correo_elect,
                                        size=14,
                                        color=COLOR_NEGRO,
                                        max_lines=2,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
            )

            acciones = ft.Container(
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

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                width=230,
                                content=ft.Row(
                                    spacing=9,
                                    controls=[
                                        inicial,
                                        nombre,
                                    ],
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=115,
                                content=ft.Text(
                                    cliente.rfc,
                                    size=14,
                                    color=COLOR_NEGRO,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=250,
                                content=ft.Text(
                                    cliente.direccion_fiscal,
                                    size=14,
                                    color=COLOR_NEGRO,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=155,
                                content=ft.Text(
                                    cliente.tipo_cliente,
                                    size=14,
                                    color=COLOR_NEGRO,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            )
                        ),
                        ft.DataCell(info_contacto),
                        ft.DataCell(acciones),
                    ],
                )
            )

        columnas = [
            ("Cliente", 235),
            ("RFC", 120),
            ("Dirección fiscal", 250),
            ("Tipo de cliente", 155),
            ("Información de contacto", 280),
            ("Acciones", 125),
        ]

        tabla_clientes = tabla(
            columnas=columnas,
            filas=filas,
            column_spacing=10,
            horizontal_margin=6,
            heading_row_height=44,
            data_row_min_height=60,
            data_row_max_height=float("inf"),
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

        tabla_contenedor = ft.Row(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    content=tabla_clientes,
                    expand=True,
                    expand_loose=True,
                )
            ],
        )

        return card(
            ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    titulo,
                    ft.Divider(
                        height=1,
                        color=COLOR_GRIS_CLARO,
                    ),
                    tabla_contenedor,
                    ft.Divider(
                        height=1,
                        color=COLOR_GRIS_CLARO,
                    ),
                    pie,
                ],
            ),
            padding=16,
            radius=10,
            shadow=sombra_suave(),
        )

    def exportar_clientes(self, e):
        pass