import flet as ft
from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_NARANJA,
    COLOR_BLANCO,
    COLOR_GRIS,
)
from fuente.utilidades.Componentes import (
    boton_vista,
    card,
    fila_catalogo,
    sombra_suave,
    tarjeta_catalogo,
)

COLOR_AZUL_OSCURO = "#0d1b2a" 

class PantallaServicios(ft.Container):
    
    def __init__(self, main_page):
        super().__init__()
        self.main_page = main_page 
        self.expand = True
        self.padding = ft.Padding(20, 20, 20, 20)
        
        self._menu_exportacion_abierto = False
        self._vista_servicios = "catalogo"
        self.registros_por_pagina = 8
        self.pagina_actual = 1
        self.servicios_demo = [
            {
                "nombre": "Manejo de Carga",
                "categoria": "Logística",
                "descripcion": "Coordinación integral de carga y descarga.",
                "detalle": "Por operación",
                "imagen": "photo-1494412519320-aa613dfb7738",
            },
            {
                "nombre": "Almacenaje en Puerto",
                "categoria": "Almacenaje",
                "descripcion": "Resguardo seguro de mercancía.",
                "detalle": "Por día",
                "imagen": "photo-1586528116311-ad8dd3c8310d",
            },
            {
                "nombre": "Transporte Terrestre",
                "categoria": "Transporte",
                "descripcion": "Traslado eficiente y seguro.",
                "detalle": "Por viaje",
                "imagen": "photo-1519003722824-194d4455a60c",
            },
            {
                "nombre": "Gestión Aduanera",
                "categoria": "Aduanero",
                "descripcion": "Trámites y asesoría aduanal.",
                "detalle": "Por trámite",
                "imagen": "photo-1450101499163-c8848c66ca85",
            },
            {
                "nombre": "Estiba y Desestiba",
                "categoria": "Operativo",
                "descripcion": "Operaciones portuarias especializadas.",
                "detalle": "Por tonelada",
                "imagen": "photo-1578575437130-527eed3abbec",
            },
            {
                "nombre": "Cadena de Frío",
                "categoria": "Especializado",
                "descripcion": "Control de temperatura en todo el proceso.",
                "detalle": "Por contenedor",
                "imagen": "photo-1581091226825-a6a2a5aee158",
            },
            {
                "nombre": "Agencia Marítima",
                "categoria": "Marítimo",
                "descripcion": "Representación y servicios marítimos.",
                "detalle": "Cuota fija",
                "imagen": "photo-1500375592092-40eb2168fd21",
            },
            {
                "nombre": "Distribución Nacional",
                "categoria": "Terrestre",
                "descripcion": "Entrega segura en todo México.",
                "detalle": "Por entrega",
                "imagen": "photo-1519003722824-194d4455a60c",
            },
        ]
        
        banner = ft.Container(
            height=174,
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            border=self.crear_borde_completo(1, ft.Colors.GREY_200),
            content=ft.Stack([
                ft.Container(
                    expand=True,
                    image=ft.DecorationImage(src="fondo_servicios.jpg", fit="cover", alignment=ft.alignment.Alignment(1, 0))
                ),
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.alignment.Alignment(-1, 0), end=ft.alignment.Alignment(1, 0),
                        colors=[COLOR_BLANCO, COLOR_BLANCO, ft.Colors.with_opacity(0.6, COLOR_BLANCO), ft.Colors.TRANSPARENT],
                        stops=[0.0, 0.45, 0.7, 1.0]
                    )
                ),
                ft.Container(
                    padding=ft.Padding(30, 25, 30, 25),
                    content=ft.Column([
                        ft.Text("Catálogo de Servicios", size=28, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO),
                        ft.Text("Administra y configura las tarifas y tipos de cobro para la agencia.", size=14, color=COLOR_GRIS),
                    ], spacing=5)
                )
            ])
        )

        boton_nuevo_servicio = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.ADD, color=COLOR_BLANCO, size=18),
                ft.Text("Nuevo Servicio", color=COLOR_BLANCO, weight=ft.FontWeight.W_600, size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            bgcolor=COLOR_NARANJA, padding=ft.Padding(20, 5, 20, 5), border_radius=6, height=44, ink=True, 
            # 1. CAMBIO: Se conecta el botón a la función de navegación
            on_click=self.abrir_nuevo_servicio 
        )

        # --- BARRA DE BÚSQUEDA Y FILTROS ---
        barra_herramientas = ft.Row([
            ft.Container(
                expand=True,
                content=ft.TextField(hint_text="Buscar por ID, nombre o categoría...", prefix_icon=ft.Icons.SEARCH, border_color=ft.Colors.GREY_300, border_radius=6, height=44, content_padding=10, text_size=14)
            ),
            ft.Container(
                content=ft.Row([ft.Icon(ft.Icons.FILTER_LIST, size=18, color=ft.Colors.BLUE_600), ft.Text("Filtros", size=14, color=ft.Colors.BLUE_600, weight=ft.FontWeight.W_500)]),
                padding=ft.Padding(15, 5, 15, 5), border=self.crear_borde_completo(1, ft.Colors.GREY_300), border_radius=6, height=44, ink=True,
                on_click=lambda e: print("Abrir filtros")
            ),
            boton_nuevo_servicio 
        ], spacing=15, alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        # --- TARJETAS RESUMEN ---
        tarjetas_resumen = ft.Row([
            self.crear_tarjeta_resumen("Total Servicios", "24", ft.Icons.FORMAT_LIST_BULLETED, ft.Colors.GREY_700, ft.Colors.GREY_100, borde_negro=True),
            self.crear_tarjeta_resumen("Cuota Fija", "10", ft.Icons.ATTACH_MONEY, ft.Colors.GREEN_500, ft.Colors.GREEN_50),
            self.crear_tarjeta_resumen("Factor Unitario", "8", ft.Icons.CALCULATE_OUTLINED, ft.Colors.BLUE_500, ft.Colors.BLUE_50),
            self.crear_tarjeta_resumen("Por Rangos/Días", "6", ft.Icons.LAYERS_OUTLINED, ft.Colors.PURPLE_500, ft.Colors.PURPLE_50),
        ], spacing=15)

        # =========================================================
        # COMPONENTES MANUALES CLONADOS DE CARLOS (Sin importar nada)
        # =========================================================
        self._boton_exportar = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.DOWNLOAD_OUTLINED, color=ft.Colors.BLUE_600, size=16),
                ft.Text("Exportar", color=ft.Colors.BLUE_600, weight=ft.FontWeight.W_600, size=14)
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            border=self.crear_borde_completo(1, "#C9DDF7"),
            border_radius=6, padding=ft.Padding(15, 5, 15, 5), height=44, width=150, ink=True,
            on_click=self.alternar_menu_exportacion
        )

        self._menu_exportacion = ft.Container(
            top=52, # Altura exacta de Carlos
            right=0, 
            width=280, # Ancho reducido (antes 320)
            visible=False,
            bgcolor=COLOR_BLANCO, border_radius=12, border=ft.Border.all(1, "#E3EAF2"),
            shadow=ft.BoxShadow(spread_radius=1, blur_radius=15, color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK)),
            padding=ft.Padding(16, 16, 16, 16), # Márgenes más compactos
            content=ft.Column([
                # Letra reducida a size=11
                ft.Text("Elige un formato para exportar los servicios encontrados.", size=11, color=COLOR_GRIS),
                ft.Container(height=2),
                ft.Container(
                    ink=True, padding=8, border_radius=8, on_click=lambda e: self.cerrar_menu_exportacion(),
                    content=ft.Row([
                        # Icono y fondo más pequeños
                        ft.Container(padding=8, bgcolor="#FDECEC", border_radius=8, content=ft.Icon(ft.Icons.PICTURE_AS_PDF, color=ft.Colors.RED_600, size=18)),
                        ft.Column([
                            ft.Text("Exportar a PDF", weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO, size=13),
                            ft.Text("Genera un archivo PDF en el directorio de servicios.", size=11, color=COLOR_GRIS)
                        ], spacing=2, expand=True)
                    ])
                ),
                ft.Container(
                    ink=True, padding=8, border_radius=8, on_click=lambda e: self.cerrar_menu_exportacion(),
                    content=ft.Row([
                        ft.Container(padding=8, bgcolor="#EAF7EF", border_radius=8, content=ft.Icon(ft.Icons.GRID_ON, color=ft.Colors.GREEN_600, size=18)),
                        ft.Column([
                            ft.Text("Exportar a Excel", weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO, size=13),
                            ft.Text("Descarga un archivo Excel con los datos de servicios.", size=11, color=COLOR_GRIS)
                        ], spacing=2, expand=True)
                    ])
                )
            ], spacing=4)
        )
        # =========================================================

        self._texto_total_servicios = ft.Text(
            f"{len(self.servicios_demo)} servicios en el catálogo",
            size=12,
            color=COLOR_GRIS,
        )
        self._contenido_servicios = ft.Container(
            expand=True,
            content=self._crear_vista_servicios(),
        )
        self._botones_vista = ft.Row(
            spacing=6,
            controls=self._crear_botones_vista(),
        )

        titulo_catalogo = ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=48,
                    height=48,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=COLOR_NARANJA,
                    border_radius=12,
                    content=ft.Icon(
                        ft.Icons.WORK_OUTLINE,
                        size=25,
                        color=COLOR_BLANCO,
                    ),
                ),
                ft.Column(
                    expand=True,
                    spacing=3,
                    controls=[
                        ft.Text(
                            "Listado de servicios",
                            size=18,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_AZUL_OSCURO,
                        ),
                        self._texto_total_servicios,
                    ],
                ),
                self._boton_exportar,
                self._botones_vista,
            ],
        )

        contenido_catalogo = ft.Column(
            expand=True,
            spacing=12,
            controls=[
                titulo_catalogo,
                ft.Divider(height=1, color=ft.Colors.GREY_200),
                self._contenido_servicios,
            ],
        )
        contenido_con_menu = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[contenido_catalogo, self._menu_exportacion],
        )
        catalogo_servicios = card(
            contenido_con_menu,
            padding=ft.Padding(12, 11, 12, 11),
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )
        pie_catalogo = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Mostrando 1–{len(self.servicios_demo)} de "
                    f"{len(self.servicios_demo)} servicios",
                    size=12,
                    color=COLOR_GRIS,
                ),
                ft.Row(
                    spacing=4,
                    controls=[
                        ft.Text(
                            "Página 1 de 1",
                            size=12,
                            color=COLOR_GRIS,
                        ),
                        ft.Container(
                            width=34,
                            height=34,
                            alignment=ft.Alignment(0, 0),
                            bgcolor=COLOR_AZUL,
                            border_radius=8,
                            content=ft.Text(
                                "1",
                                size=13,
                                color=COLOR_BLANCO,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ),
                    ],
                ),
            ],
        )

        self.content = ft.Column(
            expand=True,
            spacing=12,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                banner,
                barra_herramientas,
                tarjetas_resumen,
                catalogo_servicios,
                pie_catalogo,
            ],
        )

    def _crear_etiqueta_servicio(self, categoria):
        estilos = {
            "Logística": ("#FFF0C2", "#B26A00"),
            "Almacenaje": ("#F3F4A8", "#777A00"),
            "Transporte": ("#FFF0C2", "#B26A00"),
            "Aduanero": ("#DDF7E6", "#138A3D"),
            "Operativo": ("#DDF7E6", "#138A3D"),
            "Especializado": ("#E4E5FF", "#4C55C7"),
            "Marítimo": ("#D9ECFF", "#176FC1"),
            "Terrestre": ("#FFF0C2", "#B26A00"),
        }
        fondo, color = estilos[categoria]
        return ft.Container(
            padding=ft.Padding(8, 4, 8, 4),
            bgcolor=fondo,
            border_radius=18,
            content=ft.Text(
                categoria,
                size=11,
                color=color,
                weight=ft.FontWeight.W_600,
                max_lines=1,
            ),
        )

    def _crear_vista_servicios(self):
        servicios = self.servicios_demo[:self.registros_por_pagina]
        if self._vista_servicios == "lista":
            return ft.ListView(
                expand=True,
                spacing=8,
                padding=ft.Padding(2, 2, 2, 2),
                controls=[
                    fila_catalogo(
                        titulo=servicio["nombre"],
                        descripcion=servicio["descripcion"],
                        etiqueta=self._crear_etiqueta_servicio(
                            servicio["categoria"]
                        ),
                        detalle=servicio["detalle"],
                        ruta_imagen=(
                            "https://images.unsplash.com/"
                            f"{servicio['imagen']}?auto=format&fit=crop&w=700&q=80"
                        ),
                        icono_secundario=ft.Icons.ATTACH_MONEY,
                    )
                    for servicio in servicios
                ],
            )

        tarjetas = [
            tarjeta_catalogo(
                titulo=servicio["nombre"],
                descripcion=servicio["descripcion"],
                etiqueta=self._crear_etiqueta_servicio(
                    servicio["categoria"]
                ),
                detalle=servicio["detalle"],
                ruta_imagen=(
                    "https://images.unsplash.com/"
                    f"{servicio['imagen']}?auto=format&fit=crop&w=700&q=80"
                ),
                icono_secundario=ft.Icons.ATTACH_MONEY,
            )
            for servicio in servicios
        ]
        filas = []
        for inicio in range(0, len(tarjetas), 4):
            controles_fila = tarjetas[inicio:inicio + 4]
            controles_fila.extend(
                ft.Container(expand=True)
                for _ in range(4 - len(controles_fila))
            )
            filas.append(ft.Row(spacing=8, controls=controles_fila))
        return ft.Column(expand=True, spacing=8, controls=filas)

    def _crear_botones_vista(self):
        return [
            boton_vista(
                ft.Icons.GRID_VIEW,
                "Vista de tarjetas",
                self._vista_servicios == "catalogo",
                lambda e: self.cambiar_vista_servicios("catalogo"),
            ),
            boton_vista(
                ft.Icons.VIEW_LIST_OUTLINED,
                "Vista de lista",
                self._vista_servicios == "lista",
                lambda e: self.cambiar_vista_servicios("lista"),
            ),
        ]

    def cambiar_vista_servicios(self, vista):
        self._vista_servicios = vista
        self._contenido_servicios.content = self._crear_vista_servicios()
        self._botones_vista.controls = self._crear_botones_vista()
        if self.main_page is not None:
            self.main_page.update()

    # =========================================================
    # 2. CAMBIO: Función para hacer el cambio de pantalla
    # =========================================================
    def abrir_nuevo_servicio(self, e):
        # Guardar la vista de la tabla actual en memoria
        self.vista_catalogo = self.content 
        


    # --- LÓGICA DE EVENTOS ---
    def alternar_menu_exportacion(self, e=None):
        self._menu_exportacion_abierto = not self._menu_exportacion_abierto
        self._menu_exportacion.visible = self._menu_exportacion_abierto
        self._menu_exportacion.update()

    def cerrar_menu_exportacion(self, e=None):
        self._menu_exportacion_abierto = False
        self._menu_exportacion.visible = False
        self._menu_exportacion.update()

    # --- AYUDAS VISUALES ---
    def crear_borde_completo(self, ancho, color):
        return ft.Border(top=ft.BorderSide(ancho, color), right=ft.BorderSide(ancho, color), bottom=ft.BorderSide(ancho, color), left=ft.BorderSide(ancho, color))

    def crear_tarjeta_resumen(self, titulo, cantidad, icono, color_icono, bg_icono, borde_negro=False):
        color_borde = COLOR_AZUL_OSCURO if borde_negro else ft.Colors.GREY_200
        ancho_borde = 1.5 if borde_negro else 1
        return ft.Container(
            expand=True, padding=15, border=self.crear_borde_completo(ancho_borde, color_borde), border_radius=8, bgcolor=COLOR_BLANCO,
            content=ft.Row([
                ft.Container(padding=10, bgcolor=bg_icono, border_radius=6, content=ft.Icon(icono, color=color_icono, size=22)),
                ft.Column([ft.Text(titulo, size=12, color=COLOR_GRIS, weight=ft.FontWeight.W_500), ft.Text(cantidad, size=18, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO)], spacing=0, alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(expand=True), ft.Icon(ft.Icons.CHEVRON_RIGHT, color=ft.Colors.GREY_400, size=18)
            ])
        )
