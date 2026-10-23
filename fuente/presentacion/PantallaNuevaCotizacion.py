import flet as ft
from fuente.utilidades.Colores import COLOR_NARANJA, COLOR_BLANCO, COLOR_GRIS

COLOR_AZUL_OSCURO = "#0d1b2a"
COLOR_FONDO_CABECERA = "#f4f6f9" 
COLOR_FONDO_APP = "#f8f9fa" 

class PantallaNuevaCotizacion(ft.Container):
    def __init__(self, main_page, vista_anterior=None):
        super().__init__(
            expand=True,
            padding=ft.Padding(20, 10, 20, 20)
        )
        self.main_page = main_page
        self.vista_anterior = vista_anterior

        self.ver_costo = True
        self.ver_ganancia = True
        self.ver_iva = True
        
        self.chk_costo = ft.Checkbox(label="Costo Unitario (MXN)", value=True, on_change=self.toggle_columnas, active_color=ft.Colors.BLUE_600)
        self.chk_ganancia = ft.Checkbox(label="Ganancia (%)", value=True, on_change=self.toggle_columnas, active_color=ft.Colors.BLUE_600)
        self.chk_iva = ft.Checkbox(label="IVA (%)", value=True, on_change=self.toggle_columnas, active_color=ft.Colors.BLUE_600)
        self.switch_cliente = ft.Switch(label="Vista de la cotización (cliente)", value=False, on_change=self.toggle_vista_cliente, active_color=COLOR_NARANJA)

        self.input_activo_fecha = None 
        self.date_picker = ft.DatePicker(
            on_change=self.cambiar_fecha,
            help_text="Selecciona una fecha",
            cancel_text="Cancelar",
            confirm_text="Seleccionar"
        )

        self.cabecera_tabla = self._construir_cabecera_tabla()
        self.lista_filas = ft.Column(
            spacing=0,
            controls=[
                self.crear_fila_servicio("1", "Tomate rojo fresco", "Reja", "1", "$300.00", "10%", "16%", "$382.80", "$382.80"),
                self.crear_fila_servicio("2", "Agua embotellada", "Caja", "2", "$120.00", "5%", "0%", "$126.00", "$252.00"),
                self.crear_fila_servicio("3", "Servicio de amarre", "Servicio", "1", "$3,800.00", "0%", "16%", "$4,408.00", "$4,408.00"),
            ]
        )

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=20,
            controls=[
                self.encabezado(),
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=20,
                    controls=[self.panel_izquierdo(), self.panel_derecho()]
                ),
                ft.Container(height=30)
            ]
        )

    def encabezado(self):
        return ft.Container(
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE, 
            image=ft.DecorationImage(src="assets/fondo_puerto.jpg", fit="cover"),
            content=ft.Container(
                padding=ft.Padding(30, 20, 30, 20),
                gradient=ft.LinearGradient(
                    begin=ft.alignment.Alignment(-1.0, 0.0), 
                    end=ft.alignment.Alignment(1.0, 0.0),    
                    colors=[COLOR_BLANCO, ft.Colors.with_opacity(0, COLOR_BLANCO)],
                    stops=[0.25, 0.85] 
                ),
                content=ft.Row([
                    ft.Row([
                        ft.Container(
                            content=ft.Icon(ft.Icons.POST_ADD, color=COLOR_BLANCO, size=30),
                            bgcolor=ft.Colors.BLUE_800, padding=10, border_radius=8
                        ),
                        ft.Column([
                            ft.Text("Nueva Cotización", size=26, weight=ft.FontWeight.W_900, color=COLOR_AZUL_OSCURO),
                            ft.Text("Completa la información básica de la cotización y agrega los productos y servicios.", size=13, color=COLOR_GRIS)
                        ], spacing=2)
                    ], spacing=15)
                ], alignment=ft.MainAxisAlignment.START)
            )
        )

    def panel_izquierdo(self):
        boton_cancelar = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.CHEVRON_LEFT, size=18, color=COLOR_GRIS), ft.Text("Cancelar", color=COLOR_GRIS, weight=ft.FontWeight.W_600, size=13)], spacing=2),
            padding=ft.Padding(10, 8, 15, 8), border=self.crear_borde_completo(1, ft.Colors.GREY_300), border_radius=6, ink=True,
            on_click=self.cancelar
        )
        return ft.Column([self.seccion_datos(), self.seccion_servicios(), boton_cancelar], expand=True, spacing=20)

    def panel_derecho(self):
        tarjeta_columnas = ft.Container(
            border=self.crear_borde_completo(1, ft.Colors.GREY_200), border_radius=10, bgcolor=COLOR_BLANCO, padding=20,
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.VIEW_COLUMN_OUTLINED, color=COLOR_AZUL_OSCURO, size=18), ft.Text("Columnas", weight=ft.FontWeight.BOLD, size=14, color=COLOR_AZUL_OSCURO)]),
                ft.Text("Selecciona qué ver en la tabla.", size=11, color=COLOR_GRIS),
                ft.Container(height=5),
                self.chk_costo, self.chk_ganancia, self.chk_iva,
                ft.Divider(height=20, color=ft.Colors.GREY_200),
                ft.Row([ft.Icon(ft.Icons.VISIBILITY_OUTLINED, color=COLOR_GRIS, size=16), ft.Text("Vista cliente", size=12, weight=ft.FontWeight.W_500, color=COLOR_AZUL_OSCURO), ft.Container(expand=True), self.switch_cliente]),
            ], spacing=10)
        )

        tarjeta_totales = ft.Container(
            border=self.crear_borde_completo(1, ft.Colors.GREY_200), border_radius=10, bgcolor=COLOR_BLANCO, padding=20,
            content=ft.Column([
                ft.Row([ft.Icon(ft.Icons.CALCULATE_OUTLINED, color=ft.Colors.BLUE_400, size=20), ft.Text("Subtotal", size=12, color=COLOR_GRIS), ft.Container(expand=True), ft.Text("$10,998.60", size=12, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO)]),
                ft.Row([ft.Container(width=28), ft.Text("IVA total", size=12, color=COLOR_GRIS), ft.Container(expand=True), ft.Text("$1,574.00", size=12, weight=ft.FontWeight.BOLD, color=COLOR_AZUL_OSCURO)]),
                ft.Divider(height=20, color=ft.Colors.GREY_200),
                ft.Row([ft.Text("Total", size=14, weight=ft.FontWeight.BOLD, color=COLOR_NARANJA), ft.Container(expand=True), ft.Text("$12,572.60", size=14, weight=ft.FontWeight.W_900, color=COLOR_NARANJA)]),
            ])
        )

        boton_guardar = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.SAVE_OUTLINED, color=COLOR_BLANCO, size=18), ft.Text("Guardar", color=COLOR_BLANCO, weight=ft.FontWeight.W_600, size=14)], alignment=ft.MainAxisAlignment.CENTER), 
            bgcolor=COLOR_NARANJA, padding=ft.Padding(0, 12, 0, 12), border_radius=6, ink=True
        )

        return ft.Column([tarjeta_columnas, tarjeta_totales, boton_guardar], width=240, spacing=20)

    def seccion_datos(self):
        return ft.Container(
            border=self.crear_borde_completo(1, ft.Colors.GREY_200), border_radius=10, bgcolor=COLOR_BLANCO,
            content=ft.Column([
                ft.Container(
                    bgcolor=COLOR_BLANCO, padding=ft.Padding(20, 15, 20, 15), border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                    content=ft.Row([self.crear_indicador_numero("1", ft.Colors.BLUE_600), ft.Text("Datos Generales", weight=ft.FontWeight.BOLD, size=15, color=COLOR_AZUL_OSCURO)], spacing=15)
                ),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        ft.Row([
                            self.crear_dropdown("Nombre del Buque *", "Ej. MV Ocean Star", ft.Icons.DIRECTIONS_BOAT_OUTLINED, ["MV Ocean Star", "CMA CGM Marco Polo"]), 
                            self.crear_input_fecha("ETA (Fecha y hora) *", "25/10/2026", ft.Icons.CALENDAR_TODAY_OUTLINED), 
                            self.crear_dropdown("Cliente *", "ABC Logística S.A. de C.V.", ft.Icons.PERSON_OUTLINE, ["ABC Logística S.A. de C.V.", "Maersk Line"])
                        ], spacing=20),
                        ft.Row([
                            self.crear_dropdown("Tipo de Operación *", "Importación", ft.Icons.SWAP_HORIZ, ["Importación", "Exportación", "Transbordo"]), 
                            self.crear_dropdown("Puerto de Destino *", "Manzanillo, Colima", ft.Icons.LOCATION_ON_OUTLINED, ["Manzanillo, Colima", "Lázaro Cárdenas", "Veracruz"]), 
                            self.crear_dropdown("Moneda *", "MXN - Peso Mexicano", ft.Icons.ATTACH_MONEY, ["MXN - Peso Mexicano", "USD - Dólar Americano"])
                        ], spacing=20),
                        ft.Row([
                            self.crear_input_fecha("Vigencia de la Cotización *", "25/10/2026", ft.Icons.DATE_RANGE), 
                            self.crear_dropdown("Condiciones de Pago", "30% anticipo - 70% contra entrega", ft.Icons.REQUEST_QUOTE_OUTLINED, ["30% anticipo - 70% contra entrega", "100% anticipo", "Crédito 30 días"]), 
                            self.crear_input("Referencia / Folio Interno", "Ej. REF-2026-0012", ft.Icons.TAG)
                        ], spacing=20),
                    ], spacing=15)
                )
            ], spacing=0)
        )

    def seccion_servicios(self):
        boton_agregar_menu = ft.PopupMenuButton(
            content=ft.Container(
                content=ft.Row([
                    ft.Icon(ft.Icons.ADD, color=COLOR_NARANJA, size=16), 
                    ft.Text("Agregar...", color=COLOR_NARANJA, weight=ft.FontWeight.W_600, size=13),
                    ft.Icon(ft.Icons.ARROW_DROP_DOWN, color=COLOR_NARANJA, size=18)
                ], spacing=5), 
                border=self.crear_borde_completo(1, COLOR_NARANJA), padding=ft.Padding(15, 5, 10, 5), border_radius=6, ink=True
            ),
            items=[
                ft.PopupMenuItem(content=ft.Row([ft.Icon(ft.Icons.TABLE_ROWS_OUTLINED, color=COLOR_GRIS, size=18), ft.Text("Agregar Producto (Nueva Fila)", color=COLOR_AZUL_OSCURO)]), on_click=self.agregar_fila),
                ft.PopupMenuItem(content=ft.Row([ft.Icon(ft.Icons.VIEW_COLUMN_OUTLINED, color=COLOR_GRIS, size=18), ft.Text("Agregar Campo (Nueva Columna)", color=COLOR_AZUL_OSCURO)]), on_click=self.mostrar_dialogo_columna)
            ]
        )

        return ft.Container(
            border=self.crear_borde_completo(1, ft.Colors.GREY_200), border_radius=10, bgcolor=COLOR_BLANCO,
            content=ft.Column([
                ft.Container(
                    bgcolor=COLOR_BLANCO, padding=ft.Padding(20, 15, 20, 15), border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)),
                    content=ft.Row([
                        ft.Row([self.crear_indicador_numero("2", ft.Colors.BLUE_600), ft.Column([ft.Text("Productos y servicios cotizados", weight=ft.FontWeight.BOLD, size=15, color=COLOR_AZUL_OSCURO), ft.Text("Agrega los productos y servicios que serán incluidos en esta cotización.", size=11, color=COLOR_GRIS)], spacing=0)], spacing=15),
                        ft.Row([boton_agregar_menu], alignment=ft.MainAxisAlignment.END)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                ),
                ft.Container(
                    padding=20,
                    content=ft.Column([
                        self.cabecera_tabla,
                        ft.Divider(height=20, color=ft.Colors.GREY_200),
                        self.lista_filas,
                        ft.Container(height=10),
                        ft.Container(
                            bgcolor=ft.Colors.BLUE_50, border=self.crear_borde_completo(1, ft.Colors.BLUE_100), border_radius=6, padding=12,
                            content=ft.Row([ft.Icon(ft.Icons.INFO, color=ft.Colors.BLUE_500, size=18), ft.Text("El IVA y la ganancia se configuran por producto. Usa el panel derecho para ocultar columnas internas.", color=ft.Colors.BLUE_700, size=12)], spacing=10)
                        )
                    ])
                )
            ], spacing=0)
        )

    def _construir_cabecera_tabla(self):
        return ft.Row([
            ft.Container(width=20, content=ft.Text("#", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
            ft.Container(expand=5, content=ft.Text("Producto / Servicio", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)), 
            ft.Container(expand=2, content=ft.Text("Unidad", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
            ft.Container(expand=1, content=ft.Text("Cant.", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
            ft.Container(expand=2, content=ft.Text("Costo Unit.", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD), visible=self.ver_costo),
            ft.Container(expand=2, content=ft.Text("Ganancia", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD), visible=self.ver_ganancia),
            ft.Container(expand=2, content=ft.Text("IVA", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD), visible=self.ver_iva),
            ft.Container(expand=2, content=ft.Text("Precio Final", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
            ft.Container(expand=2, content=ft.Text("Importe", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
            ft.Container(width=70, content=ft.Text("Acciones", size=11, color=COLOR_GRIS, weight=ft.FontWeight.BOLD)),
        ])

    def agregar_fila(self, e):
        siguiente_numero = str(len(self.lista_filas.controls) + 1)
        nueva_fila = self.crear_fila_servicio(siguiente_numero, "Seleccione un producto", "Servicio", "1", "$0.00", "0%", "16%", "$0.00", "$0.00")
        self.lista_filas.controls.append(nueva_fila)
        self.update()

    def eliminar_fila(self, fila_a_borrar):
        if fila_a_borrar in self.lista_filas.controls:
            self.lista_filas.controls.remove(fila_a_borrar)
        for index, fila in enumerate(self.lista_filas.controls):
            fila.content.controls[0].content.value = str(index + 1)
        self.update()

    def mostrar_dialogo_columna(self, e):
        print("¡Clic en agregar nueva columna! Preparando Pop-up...")

    def toggle_vista_cliente(self, e):
        es_vista = e.control.value
        self.chk_costo.value = not es_vista
        self.chk_ganancia.value = not es_vista
        self.chk_iva.value = not es_vista
        self.toggle_columnas(None)

    def toggle_columnas(self, e):
        self.ver_costo = self.chk_costo.value
        self.ver_ganancia = self.chk_ganancia.value
        self.ver_iva = self.chk_iva.value
        
        self.cabecera_tabla.controls[4].visible = self.ver_costo
        self.cabecera_tabla.controls[5].visible = self.ver_ganancia
        self.cabecera_tabla.controls[6].visible = self.ver_iva

        for fila in self.lista_filas.controls:
            celdas = fila.content.controls
            celdas[4].visible = self.ver_costo
            celdas[5].visible = self.ver_ganancia
            celdas[6].visible = self.ver_iva
            
        self.update()

    def cancelar(self, e=None):
        if self.vista_anterior:
            self.parent.content = self.vista_anterior
            self.parent.update()
        else:
            print("Error: No se configuró una vista anterior para regresar.")

    def cambiar_fecha(self, e):
        if self.date_picker.value and self.input_activo_fecha:
            fecha_formateada = self.date_picker.value.strftime("%d/%m/%Y")
            self.input_activo_fecha.value = fecha_formateada
            self.input_activo_fecha.update()

    # --- HELPERS UI ---
    def crear_borde_completo(self, ancho, color):
        return ft.Border(top=ft.BorderSide(ancho, color), right=ft.BorderSide(ancho, color), bottom=ft.BorderSide(ancho, color), left=ft.BorderSide(ancho, color))

    def crear_indicador_numero(self, numero, color_fondo):
        return ft.Container(width=26, height=26, bgcolor=color_fondo, border_radius=13, alignment=ft.alignment.Alignment(0, 0), content=ft.Text(numero, color=COLOR_BLANCO, weight=ft.FontWeight.BOLD, size=13))

    def crear_input(self, label, hint, icon):
        return ft.Container(
            expand=True,
            content=ft.Column([
                ft.Text(label, size=11, color=COLOR_AZUL_OSCURO, weight=ft.FontWeight.W_600),
                ft.TextField(hint_text=hint, prefix_icon=icon, border_color=ft.Colors.GREY_300, border_radius=6, height=38, content_padding=10, text_size=12)
            ], spacing=5)
        )

    def crear_input_fecha(self, label, hint, icon):
        def abrir_picker(e):
            self.input_activo_fecha = txt_field
            if self.date_picker not in e.page.overlay:
                e.page.overlay.append(self.date_picker)
            self.date_picker.open = True
            e.page.update()

        btn_calendario = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, icon_size=16, icon_color=COLOR_NARANJA, on_click=abrir_picker, width=30, height=30)
        txt_field = ft.TextField(hint_text=hint, prefix_icon=icon, suffix=btn_calendario, border_color=ft.Colors.GREY_300, border_radius=6, height=38, content_padding=10, text_size=12)
        
        return ft.Container(
            expand=True,
            content=ft.Column([
                ft.Text(label, size=11, color=COLOR_AZUL_OSCURO, weight=ft.FontWeight.W_600), txt_field
            ], spacing=5)
        )

    def crear_dropdown(self, label, hint, icon, opciones):
        elementos = [ft.dropdown.Option(opt) for opt in opciones]
        return ft.Container(
            expand=True,
            content=ft.Column([
                ft.Row([ft.Icon(icon, size=14, color=COLOR_AZUL_OSCURO), ft.Text(label, size=11, color=COLOR_AZUL_OSCURO, weight=ft.FontWeight.W_600)], spacing=5),
                ft.Dropdown(hint_text=hint, border_color=ft.Colors.GREY_300, border_radius=6, height=38, content_padding=10, text_size=12, options=elementos)
            ], spacing=5)
        )

    def crear_dropdown_tabla(self, valor, opciones):
        elementos = [ft.dropdown.Option(opt) for opt in opciones]
        return ft.Dropdown(value=valor, border_color=ft.Colors.GREY_300, border_radius=6, height=32, content_padding=ft.Padding(8, 0, 8, 0), text_size=11, dense=True, options=elementos)

    def crear_input_tabla(self, valor):
        return ft.TextField(value=valor, border_color=ft.Colors.GREY_300, border_radius=6, height=32, content_padding=ft.Padding(8, 0, 8, 0), text_size=11, dense=True)

    def crear_fila_servicio(self, numero, producto, unidad, cant, costo, ganancia, iva, precio_fin, importe):
        fila = ft.Container(padding=ft.Padding(0, 5, 0, 5), border=ft.Border(bottom=ft.BorderSide(1, ft.Colors.GREY_100)))
        btn_borrar = ft.Container(content=ft.Icon(ft.Icons.DELETE_OUTLINE, size=16, color=ft.Colors.RED_400), ink=True, padding=4, border_radius=4, on_click=lambda e: self.eliminar_fila(fila))
        
        fila.content = ft.Row([
            ft.Container(width=20, content=ft.Text(numero, size=12, color=COLOR_GRIS)),
            ft.Container(expand=5, content=self.crear_dropdown_tabla(producto, [producto, "Lanchaje", "Practicaje", "Agua", "Comida", "Seleccione un producto"])),
            ft.Container(expand=2, content=self.crear_dropdown_tabla(unidad, ["Reja", "Caja", "Servicio"])),
            ft.Container(expand=1, content=self.crear_input_tabla(cant)),
            ft.Container(expand=2, content=self.crear_input_tabla(costo), visible=self.ver_costo),
            ft.Container(expand=2, content=self.crear_dropdown_tabla(ganancia, ["0%", "5%", "10%", "15%"]), visible=self.ver_ganancia),
            ft.Container(expand=2, content=self.crear_dropdown_tabla(iva, ["0%", "8%", "16%"]), visible=self.ver_iva),
            ft.Container(expand=2, content=ft.Text(precio_fin, size=12, weight=ft.FontWeight.W_600, color=COLOR_AZUL_OSCURO)),
            ft.Container(expand=2, content=ft.Text(importe, size=12, weight=ft.FontWeight.W_600, color=COLOR_AZUL_OSCURO)),
            ft.Container(width=70, content=ft.Row([ft.Icon(ft.Icons.EDIT_OUTLINED, size=16, color=COLOR_GRIS), btn_borrar], spacing=10))
        ])
        
        return fila