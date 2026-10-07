import flet as ft
from fuente.utilidades.Colores import COLOR_SIDEBAR, COLOR_NARANJA, COLOR_BLANCO, COLOR_GRIS

class MenuLateral(ft.Container):
    
    def __init__(self, on_cambiar_pantalla):
        super().__init__()
        self.on_cambiar_pantalla = on_cambiar_pantalla
        self.width = 250
        self.bgcolor = COLOR_SIDEBAR
        self.animate = ft.Animation(300, ft.AnimationCurve.DECELERATE)
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.ruta_activa = "ruta_dashboard"
        self.is_expanded = True
        
        opciones = [
            (ft.Icons.HOME_OUTLINED, "Inicio", "ruta_dashboard"),
            (ft.Icons.DESCRIPTION_OUTLINED, "Cotizaciones", "ruta_cotizaciones"),
            (ft.Icons.PEOPLE_OUTLINE, "Clientes", "ruta_clientes"),
            (ft.Icons.DIRECTIONS_BOAT_OUTLINED, "Buques", "ruta_buques"),
            (ft.Icons.INVENTORY_2_OUTLINED, "Servicios", "ruta_servicios"),
            (ft.Icons.INSERT_CHART_OUTLINED, "Reportes", "ruta_reportes"),
            (ft.Icons.SETTINGS_OUTLINED, "Configuración", "ruta_config"),
        ]
        
        self.botones_menu = []
        
        for icono, texto, ruta in opciones:
            es_activo = (self.ruta_activa == ruta)
            btn_control = self.crear_item_menu(icono, texto, ruta, es_activo)
            
            self.botones_menu.append({
                "ruta": ruta, 
                "control": btn_control, 
                "icono": btn_control.content.controls[0], 
                "texto": btn_control.content.controls[1]
            })

        menu_items_container = ft.Column(
            controls=[item["control"] for item in self.botones_menu],
            spacing=10
        )
        
        self.logo = ft.Image(src="oplcompleto.png", width=140, fit="contain")
        self.btn_toggle = ft.IconButton(
            icon=ft.Icons.MENU_OPEN,
            icon_color=COLOR_BLANCO,
            tooltip="Cerrar menú",
            on_click=self.toggle_menu
        )
        
        fila_superior = ft.Row([
            self.logo,
            self.btn_toggle
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        self.texto_footer = ft.Text("Conectamos puertos, impulsamos oportunidades.", color=ft.Colors.WHITE_54, size=10)
        
        columna_interfaz = ft.Container(
            left=0, right=0, top=0, bottom=0,
            padding=ft.Padding(left=15, top=20, right=15, bottom=20),
            content=ft.Column([
                fila_superior,
                ft.Container(height=10),
                menu_items_container,
                ft.Container(expand=True),
                self.texto_footer
            ])
        )

        self.content = ft.Stack([
            # Capa 1: Fotografía de fondo (Alineación corregida a coordenadas)
            ft.Container(
                left=0, right=0, top=0, bottom=0,
                image=ft.DecorationImage(
                    src="fondo_menulateral.jpg",
                    fit="cover",
                    alignment=ft.alignment.Alignment(0, 1), # 0 en X (centro), 1 en Y (abajo)
                    opacity=0.35 
                )
            ),
            # Capa 2: Gradiente de Sólido a Transparente (Alineaciones corregidas)
            ft.Container(
                left=0, right=0, top=0, bottom=0,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.Alignment(0, -1), # Arriba al centro
                    end=ft.alignment.Alignment(0, 1),    # Abajo al centro
                    colors=[COLOR_SIDEBAR, ft.Colors.TRANSPARENT],
                    stops=[0.4, 0.9] 
                )
            ),
            # Capa 3: Tu interfaz
            columna_interfaz
        ])

    def toggle_menu(self, e):
        self.is_expanded = not self.is_expanded
        self.width = 250 if self.is_expanded else 75
        self.btn_toggle.icon = ft.Icons.MENU_OPEN if self.is_expanded else ft.Icons.MENU
        self.btn_toggle.tooltip = "Cerrar menú" if self.is_expanded else "Abrir menú"
        self.logo.visible = self.is_expanded
        self.texto_footer.visible = self.is_expanded
        
        for item in self.botones_menu:
            item["texto"].visible = self.is_expanded
            
        self.update()

    def manejar_click(self, ruta_seleccionada):
        self.ruta_activa = ruta_seleccionada
        
        for item in self.botones_menu:
            es_activo = (item["ruta"] == ruta_seleccionada)
            
            item["control"].bgcolor = COLOR_NARANJA if es_activo else ft.Colors.TRANSPARENT
            
            color_elementos = COLOR_BLANCO if es_activo else ft.Colors.WHITE_54
            item["icono"].color = color_elementos
            item["texto"].color = color_elementos
            item["texto"].weight = ft.FontWeight.W_500 if es_activo else ft.FontWeight.NORMAL
            
            item["control"].update()
            
        self.on_cambiar_pantalla(ruta_seleccionada)

    def crear_item_menu(self, icono, texto, ruta, activo=False):
        def on_hover(e):
            if self.ruta_activa != ruta:
                e.control.bgcolor = "#33FFFFFF" if str(e.data).lower() == "true" else ft.Colors.TRANSPARENT
                e.control.update()

        return ft.Container(
            content=ft.Row([
                ft.Icon(icono, color=COLOR_BLANCO if activo else ft.Colors.WHITE_54, size=20),
                ft.Text(texto, color=COLOR_BLANCO if activo else ft.Colors.WHITE_54, weight=ft.FontWeight.W_500 if activo else ft.FontWeight.NORMAL)
            ]),
            bgcolor=COLOR_NARANJA if activo else ft.Colors.TRANSPARENT,
            padding=ft.Padding(left=15, top=10, right=15, bottom=10),
            border_radius=8,
            ink=True, 
            tooltip=texto, 
            on_click=lambda e, r=ruta: self.manejar_click(r),
            on_hover=on_hover
        )