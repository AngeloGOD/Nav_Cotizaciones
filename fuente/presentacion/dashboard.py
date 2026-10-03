import flet as ft
from fuente.utilidades.Colores import COLOR_BANNER, COLOR_BLANCO, COLOR_NARANJA, COLOR_VERDE, COLOR_ROJO, COLOR_AZUL, COLOR_NEGRO, COLOR_GRIS
from fuente.negocio.controlador.ControladorDashboard import ControladorDashboard

class Dashboard(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.Padding(left=20, top=0, right=20, bottom=20)
        
        # 1. Instanciamos el controlador que nos traerá los datos
        self.controlador = ControladorDashboard()
        
        # 2. Pedimos los datos al controlador
        metricas = self.controlador.obtener_metricas()
        lista_cotizaciones = self.controlador.obtener_ultimas_cotizaciones()
        
        banner = ft.Container(
            bgcolor=COLOR_BANNER,
            border_radius=15,
            padding=30,
            content=ft.Column([
                ft.Text("Bienvenido, José", size=32, weight=ft.FontWeight.BOLD, color=COLOR_BLANCO),
                ft.Text("Aquí tienes un resumen de tus cotizaciones.", size=16, color=ft.Colors.WHITE_70),
                ft.Container(height=15),
                ft.Text("OPL Pacífico Sur. Conectando puertos, impulsando oportunidades.", size=12, color=ft.Colors.WHITE_54),
            ])
        )

        # 3. Usamos los datos del controlador para llenar las tarjetas
        metrics_row = ft.Row(
            spacing=20,
            controls=[
                self.crear_tarjeta(ft.Icons.INSERT_DRIVE_FILE, COLOR_NARANJA, "Cotizaciones Pendientes", metricas["pendientes"], "↑ +33% vs. mes anterior", COLOR_VERDE),
                self.crear_tarjeta(ft.Icons.CHECK_CIRCLE, COLOR_VERDE, "Cotizaciones Aprobadas", metricas["aprobadas"], "↑ +17% vs. mes anterior", COLOR_VERDE),
                self.crear_tarjeta(ft.Icons.CANCEL, COLOR_ROJO, "Cotizaciones Rechazadas", metricas["rechazadas"], "↑ +20% vs. mes anterior", COLOR_VERDE),
                self.crear_tarjeta(ft.Icons.BAR_CHART, COLOR_AZUL, "Monto Mensual Cotizado", metricas["monto_mensual"], "↑ +42% vs. mes anterior", COLOR_VERDE),
            ]
        )

        # 4. Generamos las filas de la tabla dinámicamente según lo que traiga el controlador
        filas_tabla = []
        for cot in lista_cotizaciones:
            # Determinamos el color del estado
            color_txt = COLOR_NARANJA if cot["color_estado"] == "naranja" else COLOR_NEGRO
            
            filas_tabla.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(cot["folio"], color=COLOR_AZUL)),
                    ft.DataCell(ft.Text(cot["fecha"], color=COLOR_NEGRO)),
                    ft.DataCell(ft.Text(cot["buque"], weight=ft.FontWeight.BOLD, color=COLOR_NEGRO)),
                    ft.DataCell(ft.Text(cot["cliente"], color=COLOR_NEGRO)),
                    ft.DataCell(ft.Text(cot["monto"], weight=ft.FontWeight.BOLD, color=COLOR_NEGRO)),
                    ft.DataCell(ft.Text(cot["estado"], color=color_txt, weight=ft.FontWeight.BOLD))
                ])
            )

        table_section = ft.Container(
            bgcolor=COLOR_BLANCO,
            border_radius=10,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12),
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.ACCESS_TIME, color=COLOR_GRIS),
                        ft.Column([
                            ft.Text("Últimas 5 cotizaciones", weight=ft.FontWeight.BOLD, size=16, color=COLOR_NEGRO),
                            ft.Text("Cotizaciones enviadas recientemente a clientes o buques.", size=12, color=COLOR_GRIS)
                        ], spacing=2)
                    ]),
                    ft.TextButton("Ver historial →")
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.Divider(),
                ft.DataTable(
                    columns=[
                        ft.DataColumn(ft.Text("Folio", color=COLOR_GRIS)),
                        ft.DataColumn(ft.Text("Fecha", color=COLOR_GRIS)),
                        ft.DataColumn(ft.Text("Nombre del Buque", color=COLOR_GRIS)),
                        ft.DataColumn(ft.Text("Cliente", color=COLOR_GRIS)),
                        ft.DataColumn(ft.Text("Monto Total", color=COLOR_GRIS)),
                        ft.DataColumn(ft.Text("Estado", color=COLOR_GRIS)),
                    ],
                    rows=filas_tabla  # Le pasamos la lista de filas dinámicas
                )
            ])
        )

        self.content = ft.Column(
            controls=[banner, ft.Container(height=10), metrics_row, ft.Container(height=10), table_section],
            scroll=ft.ScrollMode.AUTO
        )

    def crear_tarjeta(self, icono, color_icono, titulo, valor, porcentaje, color_porcentaje):
        return ft.Container(
            bgcolor=COLOR_BLANCO,
            padding=20,
            border_radius=10,
            expand=True,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.Colors.BLACK_12), 
            content=ft.Column([
                ft.Icon(icono, color=color_icono, size=30),
                ft.Container(height=5),
                ft.Text(titulo, color=COLOR_GRIS, size=13),
                ft.Text(valor, size=24, weight=ft.FontWeight.BOLD, color=COLOR_NEGRO),
                ft.Text(porcentaje, color=color_porcentaje, size=12)
            ], spacing=2)
        )