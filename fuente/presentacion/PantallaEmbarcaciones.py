import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorEmbarcaciones import ControladorEmbarcaciones
from fuente.presentacion.PantallaRegistrarEmbarcacion import PantallaRegistrarEmbarcacion


class PantallaEmbarcaciones(ft.Container):
    def __init__(self, page: ft.Page):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page

        self.controlador = ControladorEmbarcaciones()
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.total_embarcaciones = 0
        self.busqueda = ""

        self.build_ui()

    def build_ui(self):
        contenido = ft.Column(
            spacing=12,
            controls=[
                self.encabezado(),
                self.barra_filtros(),
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
                            "Gestión de Embarcaciones",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            "Administra el directorio de buques, dimensiones y datos técnicos para proformas.",
                            size=14,
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
                                "Registrar embarcación",
                                size=14,
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
                            top=13,
                            bottom=13,
                        ),
                        shape=ft.RoundedRectangleBorder(
                            radius=8
                        ),
                    ),
                    on_click=self.ir_a_registro,
                ),
            ],
        )

    def barra_filtros(self):
        return card(
            ft.Row(
                spacing=10,
                controls=[
                    barra_busqueda(
                        hint="Buscar por nombre, IMO, matrícula o bandera...",
                        on_change=self.buscar,
                    ),
                    boton_filtros(
                        on_click=self.abrir_filtros
                    ),
                ],
            ),
            padding=10,
            radius=10,
        )

    def buscar(self, e):
        self.busqueda = e.control.value or ""
        self.pagina_actual = 1
        self.actualizar_directorio()

    def abrir_filtros(self, e):
        pass

    def ir_a_registro(self, e):
        self.content = PantallaRegistrarEmbarcacion(
            self._page,
            vista_anterior=self,
        )
        self.update()

    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        self.actualizar_directorio()

    def actualizar_directorio(self):
        self.content.controls[0].content.controls[2] = self.directorio()
        self.update()

    def directorio(self):
        offset = (
            self.pagina_actual - 1
        ) * self.registros_por_pagina

        embarcaciones, self.total_embarcaciones = (
            self.controlador.obtener_embarcaciones(
                texto=self.busqueda,
                limit=self.registros_por_pagina,
                offset=offset,
            )
        )

        filas = []

        for emb in embarcaciones:
            inicial = ft.Container(
                content=ft.Text(
                    emb.nombre[:1] if emb.nombre else "?",
                    size=14,
                    color=COLOR_BLANCO,
                    weight=ft.FontWeight.BOLD,
                ),
                bgcolor=COLOR_BANNER,
                border_radius=9,
                width=35,
                height=35,
                alignment=ft.Alignment(0, 0),
            )

            nombre = ft.Container(
                width=175,
                content=ft.Text(
                    emb.nombre,
                    size=14,
                    color=COLOR_NEGRO,
                    weight=ft.FontWeight.BOLD,
                    max_lines=2,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            )

            info_tecnica = ft.Container(
                width=260,
                content=ft.Column(
                    spacing=3,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Row(
                            spacing=5,
                            controls=[
                                ft.Icon(
                                    ft.Icons.STRAIGHTEN_OUTLINED,
                                    size=15,
                                    color=COLOR_GRIS,
                                ),
                                ft.Container(
                                    width=230,
                                    content=ft.Text(
                                        f"LOA: {emb.loa} m | Manga: {emb.manga} m",
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
                                    ft.Icons.SCALE_OUTLINED,
                                    size=15,
                                    color=COLOR_GRIS,
                                ),
                                ft.Container(
                                    width=230,
                                    content=ft.Text(
                                        f"TRB: {emb.trb} | GTR: {emb.gtr}",
                                        size=14,
                                        color=COLOR_NEGRO,
                                        max_lines=1,
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
                            "Ver embarcación",
                        ),
                        boton_accion(
                            ft.Icons.EDIT_OUTLINED,
                            "Editar embarcación",
                        ),
                        boton_accion(
                            ft.Icons.DELETE_OUTLINE,
                            "Eliminar embarcación",
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
                                width=120,
                                content=ft.Column(
                                    spacing=2,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(f"IMO: {emb.imo or 'N/A'}", size=13, color=COLOR_NEGRO, weight=ft.FontWeight.W_500),
                                        ft.Text(f"MAT: {emb.matricula or 'N/A'}", size=12, color=COLOR_GRIS),
                                    ]
                                ),
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=120,
                                content=ft.Row(
                                    spacing=5,
                                    controls=[
                                        ft.Icon(ft.Icons.FLAG_OUTLINED, size=16, color=COLOR_GRIS),
                                        ft.Text(
                                            emb.bandera or "N/A",
                                            size=14,
                                            color=COLOR_NEGRO,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS,
                                        )
                                    ]
                                )
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                width=155,
                                content=ft.Text(
                                    emb.tipo_embarcacion or "N/A",
                                    size=14,
                                    color=COLOR_NEGRO,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            )
                        ),
                        ft.DataCell(info_tecnica),
                        ft.DataCell(acciones),
                    ],
                )
            )

        columnas = [
            ("Embarcación", 235),
            ("Identificadores", 120),
            ("Bandera", 120),
            ("Tipo", 155),
            ("Especificaciones", 280),
            ("Acciones", 125),
        ]

        tabla_embarcaciones = tabla(
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
                        ft.Icons.DIRECTIONS_BOAT_OUTLINED,
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
                            "Directorio de embarcaciones",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_NEGRO,
                        ),
                        ft.Text(
                            f"{self.total_embarcaciones} embarcaciones registradas",
                            size=14,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                boton_exportar(
                    on_click=self.exportar_embarcaciones
                ),
            ],
        )

        pie = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Mostrando {len(embarcaciones)} de {self.total_embarcaciones} embarcaciones",
                    size=14,
                    color=COLOR_GRIS,
                ),
                paginacion(
                    total_registros=self.total_embarcaciones,
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
                    content=tabla_embarcaciones,
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
        )

    def exportar_embarcaciones(self, e):
        pass