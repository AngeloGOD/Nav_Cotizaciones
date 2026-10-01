import flet as ft

def main(page: ft.Page):
    
    page.bgcolor = "#F4F6F8"
    page.padding = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    BG_SIDEBAR = "#0A1A2F"
    COLOR_NARANJA = "#FF6B00"
    BG_BANNER = "#1A3A5F"

    page.floating_action_button = ft.FloatingActionButton(
        content=ft.Row(
            controls=[
                ft.Icon(ft.Icons.ADD, color=ft.Colors.WHITE),
                ft.Text("Nueva Cotización", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5
        ),
        bgcolor=COLOR_NARANJA,
        width=180
    )

    # --- MENÚ LATERAL ---
    def crear_item_menu(icono, texto, activo=False):
        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=ft.Colors.WHITE if activo else ft.Colors.WHITE_54),
                ft.Text(texto, color=ft.Colors.WHITE if activo else ft.Colors.WHITE_54, weight=ft.FontWeight.W_500 if activo else ft.FontWeight.NORMAL)
            ]),
            bgcolor=COLOR_NARANJA if activo else ft.Colors.TRANSPARENT,
            padding=10,
            border_radius=8
        )

    sidebar = ft.Container(
        width=250,
        bgcolor=BG_SIDEBAR,
        padding=20,
        content=ft.Column([
            ft.Text("OPL PACÍFICO SUR", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=20),
            ft.Divider(color=ft.Colors.WHITE_24),
            ft.Container(height=10),
            ft.Text("NAVEGACIÓN", color=ft.Colors.GREY, size=12),
            crear_item_menu(ft.Icons.HOME, "Dashboard", activo=True),
            crear_item_menu(ft.Icons.DESCRIPTION, "Cotizaciones"),
            crear_item_menu(ft.Icons.PEOPLE, "Clientes"),
            crear_item_menu(ft.Icons.DIRECTIONS_BOAT, "Buques"),
            crear_item_menu(ft.Icons.SUPPORT_AGENT, "Servicios"),
            crear_item_menu(ft.Icons.INSERT_CHART, "Reportes"),
            crear_item_menu(ft.Icons.SETTINGS, "Configuración"),
        ], spacing=10)
    )

   
    top_bar = ft.Container(
        padding=20,
        content=ft.Row([
            ft.TextField(
                prefix_icon=ft.Icons.SEARCH,
                hint_text="Buscar buque, cliente o folio...",
                border_radius=8,
                bgcolor=ft.Colors.WHITE,
                height=40,
                width=400,
                content_padding=10
            ),
            ft.Row([
                ft.Container(content=ft.Icon(ft.Icons.NOTIFICATIONS_OUTLINED, color=ft.Colors.GREY_700), padding=5),
                ft.Container(content=ft.Icon(ft.Icons.HELP_OUTLINE, color=ft.Colors.GREY_700), padding=5),
                ft.Container(width=10),
                ft.Column([
                    ft.Text("Carlos Daniels", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                    ft.Text("Gerente Administrativo", size=12, color=ft.Colors.GREY_600)
                ], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                ft.CircleAvatar(content=ft.Text("CD", color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD), bgcolor=BG_SIDEBAR)
            ])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
    )

    
    banner = ft.Container(
        bgcolor=BG_BANNER,
        border_radius=15,
        padding=30,
        content=ft.Column([
            ft.Text("Bienvenido, Carlos", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            ft.Text("Aquí tienes un resumen de tus cotizaciones.", size=16, color=ft.Colors.WHITE_70),
            ft.Container(height=15),
            ft.Text("OPL Pacífico Sur. Conectando puertos, impulsando oportunidades.", size=12, color=ft.Colors.WHITE_54),
        ])
    )

    def crear_tarjeta(icono, color_icono, titulo, valor, porcentaje):
        return ft.Container(
            bgcolor=ft.Colors.WHITE,
            padding=20,
            border_radius=10,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12), 
            content=ft.Column([
                ft.Icon(icono, color=color_icono, size=30),
                ft.Container(height=5),
                ft.Text(titulo, color=ft.Colors.GREY_600, size=13),
                ft.Text(valor, size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK),
                ft.Text(porcentaje, color=ft.Colors.GREEN, size=12)
            ], spacing=2)
        )

    metrics_row = ft.Row(
        spacing=20,
        controls=[
            crear_tarjeta(ft.Icons.INSERT_DRIVE_FILE, ft.Colors.ORANGE, "Cotizaciones Pendientes", "12", "↑ +33% vs. mes anterior"),
            crear_tarjeta(ft.Icons.CHECK_CIRCLE, ft.Colors.GREEN, "Cotizaciones Aprobadas", "28", "↑ +17% vs. mes anterior"),
            crear_tarjeta(ft.Icons.CANCEL, ft.Colors.RED, "Cotizaciones Rechazadas", "6", "↑ +20% vs. mes anterior"),
            crear_tarjeta(ft.Icons.BAR_CHART, ft.Colors.BLUE, "Monto Mensual Cotizado", "$1,286,500 MXN", "↑ +42% vs. mes anterior"),
        ]
    )

    table_section = ft.Container(
        bgcolor=ft.Colors.WHITE,
        border_radius=10,
        padding=20,
        shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12),
        content=ft.Column([
            ft.Row([
                ft.Row([
                    ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.GREY),
                    ft.Column([
                        ft.Text("Últimas 5 cotizaciones", weight=ft.FontWeight.BOLD, size=16, color=ft.Colors.BLACK),
                        ft.Text("Cotizaciones enviadas recientemente a clientes o buques.", size=12, color=ft.Colors.GREY)
                    ], spacing=2)
                ]),
                ft.TextButton("Ver historial →")
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            ft.Divider(),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Folio", color=ft.Colors.GREY)),
                    ft.DataColumn(ft.Text("Fecha", color=ft.Colors.GREY)),
                    ft.DataColumn(ft.Text("Nombre del Buque", color=ft.Colors.GREY)),
                    ft.DataColumn(ft.Text("Cliente", color=ft.Colors.GREY)),
                    ft.DataColumn(ft.Text("Monto Total", color=ft.Colors.GREY)),
                    ft.DataColumn(ft.Text("Estado", color=ft.Colors.GREY)),
                ],
                rows=[
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text("COT-2026-0048", color=ft.Colors.BLUE)),
                        ft.DataCell(ft.Text("04/09/2026", color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text("MSC ORION", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text("MSC Shipping S.A.", color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text("$245,800.00", weight=ft.FontWeight.BOLD, color=ft.Colors.BLACK)),
                        ft.DataCell(ft.Text("Pendiente", color=ft.Colors.ORANGE, weight=ft.FontWeight.BOLD))
                    ])
                ]
            )
        ])
    )

    main_content = ft.Container(
        expand=True,
        content=ft.Column(
            controls=[
                top_bar,
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        banner,
                        ft.Container(height=10),
                        metrics_row,
                        ft.Container(height=10),
                        table_section
                    ], spacing=10)
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )
    )

    layout = ft.Row(
        controls=[sidebar, main_content],
        expand=True,
        spacing=0
    )
    
    page.add(layout)

if __name__ == "__main__":
    ft.run(main)
