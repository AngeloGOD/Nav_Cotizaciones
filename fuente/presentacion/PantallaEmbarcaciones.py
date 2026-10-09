
import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorEmbarcaciones import (
    ControladorEmbarcaciones,
)
from fuente.presentacion.PantallaRegistrarEmbarcacion import (
    PantallaRegistrarEmbarcacion,
)


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
            expand=True,
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
                    expand=True,
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
                            "Administra el directorio de buques, "
                            "dimensiones y datos técnicos para proformas.",
                            size=14,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                boton(
                    texto="Registrar embarcación",
                    icono=ft.Icons.ADD,
                    tipo="principal",
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
                    boton(
                        texto="Filtros",
                        icono=ft.Icons.TUNE,
                        tipo="secundario",
                        on_click=self.abrir_filtros,
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
        self.content.controls[0].content.controls[2] = (
            self.directorio()
        )
        self.update()

    def crear_tabla_embarcaciones(self, embarcaciones):
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

            nombre = ft.Row(
                spacing=9,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    inicial,
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            emb.nombre or "Sin nombre",
                            size=14,
                            color=COLOR_NEGRO,
                            weight=ft.FontWeight.BOLD,
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                ],
            )

            identificadores = ft.Column(
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        f"IMO: {emb.imo or 'N/A'}",
                        size=13,
                        color=COLOR_NEGRO,
                        weight=ft.FontWeight.W_500,
                    ),
                    ft.Text(
                        f"MAT: {emb.matricula or 'N/A'}",
                        size=12,
                        color=COLOR_GRIS,
                    ),
                ],
            )

            bandera = ft.Row(
                spacing=5,
                controls=[
                    ft.Icon(
                        ft.Icons.FLAG_OUTLINED,
                        size=16,
                        color=COLOR_GRIS,
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            emb.bandera or "N/A",
                            size=14,
                            color=COLOR_NEGRO,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                ],
            )

            tipo = ft.Text(
                emb.tipo_embarcacion or "N/A",
                size=14,
                color=COLOR_NEGRO,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
            )

            especificaciones = ft.Column(
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
                                expand=True,
                                content=ft.Text(
                                    f"LOA: {emb.loa} m | "
                                    f"Manga: {emb.manga} m",
                                    size=13,
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
                                expand=True,
                                content=ft.Text(
                                    f"TRB: {emb.trb} | GTR: {emb.gtr}",
                                    size=13,
                                    color=COLOR_NEGRO,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ),
                        ],
                    ),
                ],
            )

            acciones = ft.Row(
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    boton(
                        icono=ft.Icons.VISIBILITY_OUTLINED,
                        tooltip="Ver embarcación",
                        tipo="accion",
                    ),
                    boton(
                        icono=ft.Icons.EDIT_OUTLINED,
                        tooltip="Editar embarcación",
                        tipo="accion",
                    ),
                    boton(
                        icono=ft.Icons.DELETE_OUTLINE,
                        tooltip="Eliminar embarcación",
                        color=COLOR_ROJO,
                        tipo="accion",
                    ),
                ],
            )

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(nombre),
                        ft.DataCell(identificadores),
                        ft.DataCell(bandera),
                        ft.DataCell(tipo),
                        ft.DataCell(especificaciones),
                        ft.DataCell(acciones),
                    ],
                )
            )

        columnas = [
            ("Embarcación", 270),
            ("Identificadores", 140),
            ("Bandera", 140),
            ("Tipo", 175),
            ("Especificaciones", 300),
            ("Acciones", 125),
        ]

        return tabla(
            columnas=columnas,
            filas=filas,
            column_spacing=15,
            horizontal_margin=10,
            heading_row_height=44,
            data_row_min_height=60,
            data_row_max_height=float("inf"),
            columnas_flexibles=True,
        )

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

        tabla_embarcaciones = self.crear_tabla_embarcaciones(
            embarcaciones
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
                            f"{self.total_embarcaciones} "
                            "embarcaciones registradas",
                            size=14,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                boton(
                    texto="Exportar",
                    icono=ft.Icons.DOWNLOAD_OUTLINED,
                    tipo="secundario",
                    on_click=self.exportar_embarcaciones,
                ),
            ],
        )

        pie = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Mostrando {len(embarcaciones)} de "
                    f"{self.total_embarcaciones} embarcaciones",
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
                    ft.Container(
                        expand=True,
                        content=tabla_embarcaciones,
                    ),
                    ft.Divider(
                        height=1,
                        color=COLOR_GRIS_CLARO,
                    ),
                    pie,
                ],
            ),
            padding=16,
            radius=10,
            expand=True,
        )

    def exportar_embarcaciones(self, e):
        pass