import flet as ft
from fuente.utilidades.Colores import COLOR_BANNER, COLOR_BLANCO, COLOR_NARANJA, COLOR_VERDE, COLOR_ROJO, COLOR_AZUL, COLOR_NEGRO, COLOR_GRIS
from fuente.negocio.controlador.ControladorDashboard import ControladorDashboard

class dashboard(ft.Container):
    def __init__(self):
        super().__init__()
        self.expand = True
        self.padding = ft.Padding(left=20, top=0, right=20, bottom=20)
        
        self.controlador = ControladorDashboard()
        
        metricas = self.controlador.obtener_metricas()
        lista_cotizaciones = self.controlador.obtener_ultimas_cotizaciones()
        
        banner = ft.Container(
            height=200,
            border_radius=15,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Stack([
                ft.Container(
                    expand=True,
                    image=ft.DecorationImage(
                        src="fondo_puerto.jpg",
                        fit="cover",
                        alignment=ft.alignment.Alignment(1, 0)
                    )
                ),
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.Alignment(-1, 0),
                        end=ft.alignment.Alignment(1, 0),
                        colors=[COLOR_BLANCO, COLOR_BLANCO, ft.Colors.TRANSPARENT],
                        stops=[0.0, 0.45, 1.0]
                    )
                ),
                ft.Container(
                    padding=30,
                    content=ft.Column([
                        ft.Text("OPL PACÍFICO SUR", size=10, color=COLOR_GRIS, weight=ft.FontWeight.BOLD),
                        ft.Text("Bienvenido, José", size=32, weight=ft.FontWeight.BOLD, color=COLOR_AZUL),
                        ft.Text("Aquí tienes un resumen de tus cotizaciones.", size=16, color=COLOR_GRIS),
                        ft.Container(height=10),
                        ft.Text('"Conectamos puertos, impulsamos oportunidades"', size=12, color=COLOR_GRIS, italic=True),
                    ])
                )
            ])
        )
        
        metrics_row = ft.Row(
            spacing=20,
            controls=[
                self.crear_tarjeta(ft.Icons.INSERT_DRIVE_FILE, COLOR_NARANJA, "Cotizaciones Pendientes", metricas["pendientes"], "↑ +33% vs. mes anterior", COLOR_VERDE),
                self.crear_tarjeta(ft.Icons.CHECK_CIRCLE, COLOR_VERDE, "Cotizaciones Aprobadas", metricas["aprobadas"], "↑ +17% vs. mes anterior", COLOR_VERDE),
                self.crear_tarjeta(ft.Icons.CANCEL, COLOR_ROJO, "Cotizaciones Rechazadas", metricas["rechazadas"], "↑ +20% vs. mes anterior", COLOR_VERDE),
                self.crear_tarjeta(ft.Icons.BAR_CHART, COLOR_AZUL, "Monto Mensual Cotizado", metricas["monto_mensual"], "↑ +42% vs. mes anterior", COLOR_VERDE),
            ]
        )
        
        filas_tabla = []
        for cot in lista_cotizaciones:
            if cot["color_estado"] == "naranja":
                color_dot = COLOR_NARANJA
            elif cot["color_estado"] == "rojo":
                color_dot = COLOR_ROJO
            else:
                color_dot = COLOR_VERDE
                
            estado_con_punto = ft.Row([
                ft.Icon(ft.Icons.CIRCLE, color=color_dot, size=10),
                ft.Text(cot["estado"], color=COLOR_GRIS)
            ], spacing=5)
            
            filas_tabla.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(cot["folio"], color=COLOR_GRIS)),
                    ft.DataCell(ft.Text(cot["fecha"], color=COLOR_GRIS)),
                    ft.DataCell(ft.Text(cot["buque"], color=COLOR_GRIS)),
                    ft.DataCell(ft.Text(cot["cliente"], color=COLOR_GRIS)),
                    ft.DataCell(ft.Text(cot["monto"], color=COLOR_GRIS)),
                    ft.DataCell(estado_con_punto),
                    ft.DataCell(ft.Text("•••", color=COLOR_GRIS, weight=ft.FontWeight.BOLD))
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
                        ft.DataColumn(ft.Text("Acciones", color=COLOR_GRIS)),
                    ],
                    rows=filas_tabla  
                )
            ])
        )

        footer = ft.Row([
            ft.Text("OPL Pacífico Sur | Agente naviero y operador logístico", size=12, color=COLOR_GRIS),
            ft.Row([
                ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=14, color=COLOR_GRIS),
                ft.Text("Tapachula, Chiapas, México", size=12, color=COLOR_GRIS),
                ft.Container(width=20),
                # Botón nueva cotizacion
                ft.Container(
                    content=ft.Text("+ Nueva Cotización", color=COLOR_BLANCO, weight=ft.FontWeight.BOLD),
                    bgcolor=COLOR_NARANJA,
                    padding=ft.Padding(left=20, top=10, right=20, bottom=10),
                    border_radius=8,
                    on_click=lambda e: print("Nueva cotización clic")
                )
            ], spacing=2, alignment=ft.MainAxisAlignment.END)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        self.content = ft.Column(
            controls=[banner, ft.Container(height=10), metrics_row, ft.Container(height=10), table_section, footer],
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