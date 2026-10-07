import flet as ft
from fuente.utilidades.Colores import COLOR_NARANJA, COLOR_BLANCO, COLOR_GRIS

COLOR_AZUL_OSCURO = "#0d1b2a"
COLOR_FONDO_CABECERA = "#f4f6f9" 
class PantallaNuevaCotizacion(ft.Container):
    def __init__(self, main_page):
        super().__init__()
        self.main_page = main_page
        self.expand = True
        self.padding = ft.Padding(20, 10, 20, 20)
        
        # ENCABEZADO DE LA PÁGINA
        encabezado_pagina = ft.Row([
            ft.Row([
                ft.Icon(ft.Icons.POST_ADD, color=COLOR_AZUL_OSCURO, size=28),
                ft.Text("Nueva Cotización", size=24, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO)
            ], spacing=15),
            # Botón de regresar
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.ARROW_BACK, size=16, color=COLOR_GRIS), ft.Text("Regresar al historial", color=COLOR_GRIS, size=13)]),
                padding=ft.Padding(10, 5, 10, 5),
                border=self.crear_borde_completo(1, ft.Colors.GREY_300),
                border_radius=6,
                ink=True,
                on_click=lambda e: self.volver_a_cotizaciones()
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # 2. SECCIÓN 1: DATOS GENERALES
        seccion_datos_generales = ft.Container(
            border=self.crear_borde_completo(1, ft.Colors.GREY_200),
            border_radius=10,
            bgcolor=COLOR_BLANCO,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column([
                # Cabecera de la sección (Estilo Imagen 2)
                ft.Container(
                    bgcolor=COLOR_FONDO_CABECERA,
                    padding=ft.Padding(20, 15, 20, 15),
                    border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
                    content=ft.Row([
                        self.crear_indicador_numero("1", COLOR_NARANJA),
                        ft.Icon(ft.Icons.ARTICLE_OUTLINED, color=COLOR_AZUL_OSCURO, size=20),
                        ft.Column([
                            ft.Text("Datos Generales", weight=ft.FontWeight.BOLD, size=15, color=COLOR_AZUL_OSCURO),
                            ft.Text("Completa la información básica de la cotización", size=12, color=COLOR_GRIS)
                        ], spacing=2)
                    ], spacing=15)
                ),
                # Formulario
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        # Fila 1
                        ft.Row([
                            self.crear_input("Nombre del Buque *", "Seleccione o escriba el nombre", ft.Icons.DIRECTIONS_BOAT_OUTLINED),
                            self.crear_input("ETA (Fecha y hora estimada) *", "dd/mm/aaaa --:--", ft.Icons.CALENDAR_TODAY_OUTLINED),
                            self.crear_input("Cliente *", "Buscar o seleccionar cliente", ft.Icons.PERSON_OUTLINE),
                        ], spacing=20),
                        ft.Container(height=5),
                        # Fila 2
                        ft.Row([
                            self.crear_input("Tipo de Operación *", "Seleccione el tipo", ft.Icons.SWAP_HORIZ),
                            self.crear_input("Puerto de Destino *", "Seleccione el puerto", ft.Icons.LOCATION_ON_OUTLINED),
                            self.crear_input("Moneda *", "MXN - Peso Mexicano", ft.Icons.ATTACH_MONEY),
                        ], spacing=20),
                        ft.Container(height=5),
                        # Fila 3
                        ft.Row([
                            self.crear_input("Vigencia de la Cotización *", "dd/mm/aaaa", ft.Icons.CALENDAR_MONTH_OUTLINED),
                            self.crear_input("Condiciones de Pago", "Seleccione las condiciones", ft.Icons.REQUEST_QUOTE_OUTLINED),
                            self.crear_input("Referencia / Folio Interno", "Ej. REF-2026-0012", ft.Icons.TAG),
                        ], spacing=20),
                    ])
                )
            ], spacing=0)
        )

        # SERVICIOS A COTIZAR
        boton_agregar_servicio = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.ADD, color=COLOR_NARANJA, size=16), ft.Text("Agregar Servicio", color=COLOR_NARANJA, weight=ft.FontWeight.W_600, size=13)], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            border=self.crear_borde_completo(1, COLOR_NARANJA),
            padding=ft.Padding(15, 5, 15, 5),
            border_radius=6, height=35, ink=True,
            on_click=lambda e: print("Añadiendo fila...")
        )

        seccion_servicios = ft.Container(
            border=self.crear_borde_completo(1, ft.Colors.GREY_200),
            border_radius=10,
            bgcolor=COLOR_BLANCO,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=ft.Column([
                # Cabecera
                ft.Container(
                    bgcolor=COLOR_FONDO_CABECERA,
                    padding=ft.Padding(20, 15, 20, 15),
                    border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
                    content=ft.Row([
                        ft.Row([
                            self.crear_indicador_numero("2", ft.Colors.TEAL_500),
                            ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, color=COLOR_AZUL_OSCURO, size=20),
                            ft.Column([
                                ft.Text("Servicios a Cotizar", weight=ft.FontWeight.BOLD, size=15, color=COLOR_AZUL_OSCURO),
                                ft.Text("Agrega los servicios que serán incluidos en esta cotización", size=12, color=COLOR_GRIS)
                            ], spacing=2)
                        ], spacing=15),
                        boton_agregar_servicio
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),
                # Tabla de servicios
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        # tabla simulada
                        ft.Row([
                            ft.Container(width=20, content=ft.Text("#", size=12, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
                            ft.Container(expand=2, content=ft.Text("Servicio", size=12, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
                            ft.Container(expand=3, content=ft.Text("Descripción", size=12, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
                            ft.Container(expand=1, content=ft.Text("Cantidad", size=12, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
                            ft.Container(expand=2, content=ft.Text("Costo Unit. (MXN)", size=12, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
                            ft.Container(expand=2, content=ft.Text("Importe (MXN)", size=12, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
                            ft.Container(width=50, content=ft.Text("Acciones", size=12, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
                        ]),
                        ft.Divider(height=10, color=ft.Colors.GREY_200),
                        
                        
                        self.crear_fila_servicio("1", "Practicaje", "Servicio de practicaje estándar", "1", "7500.00", "$7,500.00"),
                        
                        self.crear_fila_servicio("2", "Lanchaje", "Servicio de lanchaje", "1", "4200.00", "$4,200.00"),
                        
                        ft.Divider(height=20, color=ft.Colors.GREY_200),
                    
                        ft.Row([
                            
                            ft.Container(
                                bgcolor=ft.Colors.BLUE_50,
                                border=self.crear_borde_completo(1, ft.Colors.BLUE_100),
                                border_radius=6, padding=10,
                                content=ft.Row([
                                    ft.Icon(ft.Icons.INFO_OUTLINE, color=ft.Colors.BLUE_600, size=18),
                                    ft.Text("Los totales se calculan automáticamente.", color=ft.Colors.BLUE_700, size=12)
                                ])
                            ),
                            # Totales derecha
                            ft.Container(
                                width=300,
                                content=ft.Column([
                                    ft.Row([ft.Text("Subtotal", size=13, color=COLOR_GRIS), ft.Text("$11,700.00 MXN", size=13, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Row([ft.Text("IVA (16%)", size=13, color=COLOR_GRIS), ft.Text("$1,872.00 MXN", size=13, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                    ft.Divider(height=10, color=ft.Colors.GREY_200),
                                    ft.Row([ft.Text("Total", size=16, weight=ft.FontWeight.BOLD, color=COLOR_NARANJA), ft.Text("$13,572.00 MXN", size=18, weight=ft.FontWeight.W_900, color=COLOR_NARANJA)], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                                ])
                            )
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    ])
                )
            ], spacing=0)
        )

        # 4. BOTONES
        boton_cancelar = ft.Container(
            content=ft.Text("Cancelar", color=COLOR_GRIS, weight=ft.FontWeight.W_600, size=14),
            border=self.crear_borde_completo(1, ft.Colors.GREY_300),
            padding=ft.Padding(30, 10, 30, 10), border_radius=6, ink=True,
            on_click=lambda e: self.volver_a_cotizaciones()
        )
        
        boton_guardar = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.SAVE_OUTLINED, color=COLOR_BLANCO, size=18), ft.Text("Guardar Cotización", color=COLOR_BLANCO, weight=ft.FontWeight.W_600, size=14)], spacing=5),
            bgcolor=COLOR_NARANJA,
            padding=ft.Padding(30, 10, 30, 10), border_radius=6, ink=True,
            on_click=lambda e: print("Guardando en la base de datos...")
        )

        acciones_finales = ft.Row([boton_cancelar, boton_guardar], alignment=ft.MainAxisAlignment.END, spacing=15)

        self.content = ft.Column([
            encabezado_pagina,
            ft.Container(height=10),
            seccion_datos_generales,
            ft.Container(height=10),
            seccion_servicios,
            ft.Container(height=10),
            acciones_finales,
            ft.Container(height=20) # Espacio al final
        ], spacing=0, scroll=ft.ScrollMode.AUTO)

    # FUNCIONES AUXILIARES

    def crear_borde_completo(self, ancho, color):
        borde = ft.BorderSide(ancho, color)
        return ft.Border(top=borde, right=borde, bottom=borde, left=borde)

    def crear_indicador_numero(self, numero, color_fondo):
        return ft.Container(
            width=28, height=28,
            bgcolor=color_fondo,
            border_radius=14,
            alignment=ft.alignment.Alignment(0, 0),
            content=ft.Text(numero, color=COLOR_BLANCO, weight=ft.FontWeight.BOLD, size=14)
        )

    def crear_input(self, label, hint, icon):
        
        return ft.Container(
            expand=True,
            content=ft.Column([
                ft.Text(label, size=12, color=COLOR_AZUL_OSCURO, weight=ft.FontWeight.W_600),
                ft.TextField(
                    hint_text=hint,
                    prefix_icon=icon,
                    border_color=ft.Colors.GREY_300,
                    border_radius=6,
                    height=45,
                    content_padding=10,
                    text_size=13
                )
            ], spacing=5)
        )

    def crear_fila_servicio(self, numero, servicio, desc, cant, costo, importe):
        return ft.Container(
            padding=ft.Padding(0, 5, 0, 5),
            content=ft.Row([
                ft.Container(width=20, content=ft.Text(numero, size=13, color=COLOR_GRIS)),
                ft.Container(expand=2, content=ft.TextField(value=servicio, border_color=ft.Colors.GREY_300, border_radius=6, height=40, text_size=13, content_padding=10)),
                ft.Container(expand=3, content=ft.TextField(value=desc, border_color=ft.Colors.GREY_300, border_radius=6, height=40, text_size=13, content_padding=10)),
                ft.Container(expand=1, content=ft.TextField(value=cant, border_color=ft.Colors.GREY_300, border_radius=6, height=40, text_size=13, content_padding=10, text_align=ft.TextAlign.CENTER)),
                ft.Container(expand=2, content=ft.TextField(value=costo, prefix_icon=ft.Icons.ATTACH_MONEY, border_color=ft.Colors.GREY_300, border_radius=6, height=40, text_size=13, content_padding=10)),
                ft.Container(expand=2, content=ft.Text(importe, size=14, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO)),
                ft.Container(width=50, content=ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, icon_size=20, tooltip="Eliminar servicio"))
            ], alignment=ft.MainAxisAlignment.START)
        )

    def volver_a_cotizaciones(self):
        self.main_page.content_area.content = PantallaCotizaciones(self.main_page)
        self.main_page.update()