import flet as ft
from fuente.utilidades.Colores import *


class PantallaClientes(ft.Container):
    def __init__(self):
        super().__init__(expand=True, padding=24, bgcolor=COLOR_FONDO)
        
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

    def card(self, content, padding=16):
        return ft.Container(
            content=content,
            bgcolor=COLOR_BLANCO,
            border=ft.Border.all(1, COLOR_GRIS_CLARO),
            border_radius=14,
            padding=padding,
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
                        ft.Text("Clientes", size=13, color=COLOR_GRIS),
                        ft.Text("Gestión de Clientes", size=27, weight=ft.FontWeight.BOLD, color=COLOR_BANNER),
                        ft.Text(
                            "Administra la información fiscal y de contacto de agencias navieras, armadores y clientes.",
                            size=13, color=COLOR_GRIS,
                        ),
                    ],
                ),
                ft.FilledButton(
                    content=ft.Row(
                        tight=True,
                        spacing=8,
                        controls=[ft.Icon(ft.Icons.ADD, size=19), ft.Text("Registrar nuevo cliente", weight=ft.FontWeight.BOLD)],
                    ),
                    style=ft.ButtonStyle(
                        bgcolor=COLOR_NARANJA,
                        color=COLOR_BLANCO,
                        padding=ft.Padding(left=18, right=18, top=16, bottom=16),
                        shape=ft.RoundedRectangleBorder(radius=9),
                    ),
                ),
            ],
        )

    def barra_filtros(self):
        busqueda = ft.TextField(
            hint_text="Buscar por razón social, RFC o contacto...",
            prefix_icon=ft.Icons.SEARCH,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_AZUL,
            border_radius=9,
            text_size=13,
            content_padding=12,
            expand=True,
        )

        return self.card(
            ft.Row(
                spacing=10,
                controls=[
                    busqueda,
                    ft.OutlinedButton(
                        content=ft.Row(tight=True, spacing=7, controls=[ft.Icon(ft.Icons.TUNE, size=17), ft.Text("Filtros")]),
                        style=ft.ButtonStyle(
                            color=COLOR_AZUL,
                            side=ft.BorderSide(1, COLOR_GRIS_CLARO),
                            shape=ft.RoundedRectangleBorder(radius=9),
                            padding=ft.Padding(left=15, right=15, top=17, bottom=17),
                        ),
                    ),
                ],
            ),
            padding=12,
        )

    def estado(self, activo=True):
        color = COLOR_VERDE if activo else COLOR_ROJO
        return ft.Container(
            content=ft.Row(
                tight=True,
                spacing=6,
                controls=[
                    ft.Container(width=7, height=7, bgcolor=color, border_radius=5),
                    ft.Text("Activo" if activo else "Inactivo", size=11, color=color, weight=ft.FontWeight.W_600),
                ],
            ),
            bgcolor=COLOR_GRIS_CLARO,
            border=ft.Border.all(1, COLOR_GRIS_CLARO),
            border_radius=20,
            padding=ft.Padding(left=10, right=10, top=5, bottom=5),
        )

    def icono_accion(self, icono, tooltip, color=None):
        return ft.IconButton(
            icon=icono,
            tooltip=tooltip,
            icon_color=color or COLOR_AZUL,
            icon_size=18,
        )

    def directorio(self):
        clientes = [
            ("MSC Shipping S.A.", "MSC Shipping", "MSH180624KQ2", "Agencia naviera", "Mariana López", "+52 833 210 4580", "operaciones@mscshipping.mx", "03/04/2022", True, "M"),
            ("Maersk Line México, S.A. de C.V.", "Maersk México", "MLM920815A71", "Agencia naviera", "Roberto García", "+52 833 210 9080", "contacto@maersk.mx", "01/05/2022", True, "M"),
            ("Navios Maritime Holdings", "Navios Maritime", "NMH0503118D4", "Armador", "Ana Martínez", "+52 833 260 1442", "navios@empresa.mx", "03/05/2022", True, "N"),
            ("Oceanic Traders, S.A. de C.V.", "Oceanic Traders", "OTA190423P32", "Cliente comercial", "Carlos Hernández", "+52 833 198 7620", "administracion@oceanic.mx", "04/09/2022", False, "O"),
        ]

        filas = []
        for razon, comercial, rfc, tipo, contacto, telefono, correo, fecha, activo, inicial in clientes:
            inicial_color = COLOR_NARANJA if tipo == "Armador" else COLOR_AZUL
            info_contacto = ft.Column(
                spacing=4,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(spacing=5, controls=[ft.Icon(ft.Icons.PHONE_OUTLINED, size=13, color=COLOR_GRIS), ft.Text(telefono, size=11, color=COLOR_NEGRO)]),
                    ft.Row(spacing=5, controls=[ft.Icon(ft.Icons.MAIL_OUTLINE, size=13, color=COLOR_GRIS), ft.Text(correo, size=11, color=COLOR_GRIS, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS)]),
                ],
            )
            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Row(spacing=9, controls=[
                            ft.Container(content=ft.Text(inicial, color=COLOR_BLANCO, weight=ft.FontWeight.BOLD), bgcolor=inicial_color, border_radius=9, width=35, height=35, alignment=ft.Alignment(0, 0)),
                            ft.Column(spacing=3, width=190, controls=[
                                ft.Text(razon, size=12, color=COLOR_BANNER, weight=ft.FontWeight.BOLD, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                                ft.Text(comercial, size=11, color=COLOR_GRIS, max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            ]),
                        ])),
                        ft.DataCell(ft.Text(rfc, size=11, color=COLOR_GRIS)),
                        ft.DataCell(ft.Text(tipo, size=11, color=COLOR_GRIS)),
                        ft.DataCell(ft.Text(contacto, size=11, color=COLOR_NEGRO)),
                        ft.DataCell(ft.Container(content=info_contacto, width=225)),
                        ft.DataCell(ft.Text(fecha, size=11, color=COLOR_GRIS)),
                        ft.DataCell(self.estado(activo)),
                        ft.DataCell(ft.Row(spacing=0, controls=[
                            self.icono_accion(ft.Icons.VISIBILITY_OUTLINED, "Ver cliente"),
                            self.icono_accion(ft.Icons.EDIT_OUTLINED, "Editar cliente"),
                            self.icono_accion(ft.Icons.DELETE_OUTLINE, "Eliminar cliente", COLOR_ROJO),
                        ])),
                    ]
                )
            )

        columnas = [
            "Cliente / Razón social", "RFC", "Tipo de cliente",
            "Contacto principal", "Información de contacto",
            "Fecha de registro", "Estado", "Acciones",
        ]

        tabla = ft.DataTable(
            expand=True,
            column_spacing=45,
            horizontal_margin=14,
            heading_row_height=46,
            data_row_min_height=68,
            data_row_max_height=76,
            heading_row_color=COLOR_FONDO,
            border=ft.Border.all(1, COLOR_GRIS_CLARO),
            vertical_lines=ft.BorderSide(0.5, COLOR_GRIS_CLARO),
            horizontal_lines=ft.BorderSide(1, COLOR_GRIS_CLARO),
            columns=[ft.DataColumn(ft.Text(t, size=11, weight=ft.FontWeight.BOLD, color=COLOR_GRIS)) for t in columnas],
            rows=filas,
        )

        titulo = ft.Row(
            spacing=12,
            controls=[
                ft.Container(content=ft.Icon(ft.Icons.GROUPS_OUTLINED, color=COLOR_AZUL, size=24), bgcolor=COLOR_GRIS_CLARO, border_radius=10, padding=10),
                ft.Column(expand=True, spacing=3, controls=[
                    ft.Text("Directorio de clientes", size=17, weight=ft.FontWeight.BOLD, color=COLOR_BANNER),
                    ft.Text("Clientes registrados en el sistema", size=12, color=COLOR_GRIS),
                ]),
                ft.Text("24 clientes registrados", size=11, color=COLOR_GRIS),
                ft.Text("/", size=11, color=COLOR_GRIS_CLARO),
                ft.Text("18 activos", size=11, color=COLOR_VERDE, weight=ft.FontWeight.W_600),
                ft.OutlinedButton(
                    content=ft.Row(tight=True, spacing=6, controls=[
                        ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, size=16, color=COLOR_AZUL),
                        ft.Text("Exportar", size=12, color=COLOR_AZUL),
                    ]),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1, COLOR_GRIS_CLARO),
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),

            ],
        )

        pie = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Mostrando 1–4 de 24 clientes", size=11, color=COLOR_GRIS),
                ft.Row(spacing=5, controls=[
                    ft.OutlinedButton("‹", style=ft.ButtonStyle(color=COLOR_GRIS, side=ft.BorderSide(1, COLOR_GRIS_CLARO))),
                    ft.FilledButton("1", style=ft.ButtonStyle(bgcolor=COLOR_NARANJA, color=COLOR_BLANCO, shape=ft.RoundedRectangleBorder(radius=6))),
                    ft.OutlinedButton("2", style=ft.ButtonStyle(color=COLOR_AZUL, side=ft.BorderSide(1, COLOR_GRIS_CLARO))),
                    ft.OutlinedButton("3", style=ft.ButtonStyle(color=COLOR_AZUL, side=ft.BorderSide(1, COLOR_GRIS_CLARO))),
                    ft.OutlinedButton("4", style=ft.ButtonStyle(color=COLOR_AZUL, side=ft.BorderSide(1, COLOR_GRIS_CLARO))),
                    ft.OutlinedButton("5", style=ft.ButtonStyle(color=COLOR_AZUL, side=ft.BorderSide(1, COLOR_GRIS_CLARO))),
                    ft.OutlinedButton("›", style=ft.ButtonStyle(color=COLOR_AZUL, side=ft.BorderSide(1, COLOR_GRIS_CLARO))),
                ]),
            ],
        )

        return self.card(
            ft.Column(
                expand=True,
                spacing=12,
                controls=[
                    titulo,
                    ft.Divider(height=1, color=COLOR_GRIS_CLARO),
                    ft.Container(
                        expand=True,
                        content=ft.Row(
                            [tabla],
                            expand=True
                        )
                    ),
                    ft.Divider(height=1, color=COLOR_GRIS_CLARO),
                    pie,
                ],
            ),
            padding=16,
        )