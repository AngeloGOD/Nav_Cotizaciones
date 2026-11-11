from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import flet as ft

from fuente.negocio.controlador.ControladorCotizacion import (
    ControladorCotizacion,
    ErrorCotizacion,
)
from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.Cliente import Cliente
from fuente.negocio.modelo.Cotizacion import DetalleCotizacion
from fuente.negocio.modelo.ENUMs import Moneda
from fuente.negocio.modelo.Servicio import Servicio
from fuente.presentacion.SelectorBuque import SelectorBuque
from fuente.presentacion.SelectorCliente import SelectorCliente
from fuente.presentacion.SelectorServicio import SelectorServicio
from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_BANNER,
    COLOR_BLANCO,
    COLOR_FONDO,
    COLOR_GRIS,
    COLOR_GRIS_CLARO,
    COLOR_NARANJA,
    COLOR_ROJO,
    COLOR_VERDE,
)
from fuente.utilidades.Componentes import (
    banner_modulo,
    boton,
    card,
    mostrar_notificacion,
    sombra_suave,
)

COLOR_AZUL_OSCURO = "#0d1b2a"


class PantallaNuevaCotizacion(ft.Container):
    """Pantalla para elaborar y guardar una nueva Proforma de Gastos Portuarios (PDA)."""

    def __init__(
        self,
        main_page: ft.Page | None = None,
        vista_anterior=None,
        servicio_cotizacion=None,
        servicio_buque=None,
        servicio_cliente=None,
        servicio_servicio=None,
        controlador: ControladorCotizacion | None = None,
    ):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
            padding=ft.Padding(16, 10, 16, 20),
        )
        self.main_page = main_page
        self.vista_anterior = vista_anterior

        self.servicio_cotizacion = servicio_cotizacion or getattr(
            vista_anterior, "servicio_cotizacion", None
        )
        self.servicio_buque = servicio_buque or getattr(
            vista_anterior, "servicio_buque", None
        )
        self.servicio_cliente = servicio_cliente or getattr(
            vista_anterior, "servicio_cliente", None
        )
        self.servicio_servicio = servicio_servicio or getattr(
            vista_anterior, "servicio_servicio", None
        )

        if controlador is not None:
            self.controlador = controlador
        elif self.servicio_cotizacion is not None:
            self.controlador = ControladorCotizacion(
                servicio_cotizacion=self.servicio_cotizacion,
                servicio_buque=self.servicio_buque,
                servicio_cliente=self.servicio_cliente,
                servicio_servicio=self.servicio_servicio,
            )
            self.servicio_buque = self.controlador.servicio_buque
            self.servicio_cliente = self.controlador.servicio_cliente
            self.servicio_servicio = self.controlador.servicio_servicio
        else:
            self.controlador = None

        self.buque_actual: Buque | None = None
        self.cliente_actual: Cliente | None = None
        self.filas_datos: list[dict] = []

        # Visibilidad de columnas opcionales (modo interno vs vista cliente PDA)
        self.ver_cantidad = True
        self.ver_precio_unitario = True
        self.ver_factura = True

        self.chk_cantidad = ft.Checkbox(
            label="Cantidad (Maniobras)",
            value=True,
            on_change=self.toggle_columnas,
            active_color=COLOR_AZUL,
        )
        self.chk_precio_unitario = ft.Checkbox(
            label="Precio Unitario",
            value=True,
            on_change=self.toggle_columnas,
            active_color=COLOR_AZUL,
        )
        self.chk_factura = ft.Checkbox(
            label="Factura / Invoice",
            value=True,
            on_change=self.toggle_columnas,
            active_color=COLOR_AZUL,
        )
        self.switch_cliente = ft.Switch(
            value=False,
            on_change=self.toggle_vista_cliente,
            active_color=COLOR_NARANJA,
        )

        self.input_activo_fecha: ft.TextField | None = None
        self.date_picker = ft.DatePicker(
            on_change=self.cambiar_fecha,
            help_text="Selecciona una fecha",
            cancel_text="Cancelar",
            confirm_text="Seleccionar",
        )

        self._inicializar_controles_encabezado()
        self._inicializar_tabla_detalles()
        self._inicializar_panel_totales()

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                self._encabezado(),
                ft.Row(
                    alignment=ft.MainAxisAlignment.START,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    spacing=16,
                    controls=[self._panel_izquierdo(), self._panel_derecho()],
                ),
                ft.Container(height=24),
            ],
        )

    def _obtener_folio_inicial(self) -> str:
        if self.controlador is not None:
            try:
                return self.controlador.obtener_folio_sugerido()
            except Exception as error:
                print(f"Advertencia al consultar siguiente folio PDA: {error}")
        return "PDA.-0001"

    def _inicializar_controles_encabezado(self) -> None:
        folio_inicial = self._obtener_folio_inicial()
        hoy_str = date.today().strftime("%d/%m/%Y")

        self.txt_folio = ft.TextField(
            label="Folio PDA",
            value=folio_inicial,
            read_only=True,
            prefix_icon=ft.Icons.TAG,
            height=48,
            text_size=13,
            text_style=ft.TextStyle(
                weight=ft.FontWeight.BOLD,
                color=COLOR_BANNER,
            ),
            bgcolor="#F4F8FC",
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            border_radius=8,
            content_padding=ft.Padding(12, 8, 12, 8),
            expand=True,
        )

        self.txt_fecha_emision = self._crear_campo_fecha(
            label="Fecha / Date *",
            valor_inicial=hoy_str,
        )
        self.txt_fecha_arribo = self._crear_campo_fecha(
            label="Arribo / ETA",
            valor_inicial="",
            hint_text="dd/mm/aaaa",
        )
        self.txt_fecha_zarpe = self._crear_campo_fecha(
            label="Zarpe / ETD",
            valor_inicial="",
            hint_text="dd/mm/aaaa",
        )

        # Buscador de Buque y campos informativos (Vessel's Information)
        self.selector_buque = SelectorBuque(
            servicio_buque=self.servicio_buque,
            on_buque_seleccionado=self._al_seleccionar_buque,
            label="Buque / Vessel *",
            hint_text="Buscar buque por nombre (ej. MT MTM HOUSTON)...",
            height=52,
        )

        self.txt_tipo_buque = self._crear_campo_solo_lectura(
            label="Tipo de buque / Type of vessel",
            icono=ft.Icons.CATEGORY_OUTLINED,
        )
        self.txt_imo_buque = self._crear_campo_solo_lectura(
            label="IMO",
            icono=ft.Icons.NUMBERS_OUTLINED,
        )
        self.txt_trb_buque = self._crear_campo_solo_lectura(
            label="UAB / GRT (TRB)",
            icono=ft.Icons.SCALE_OUTLINED,
        )
        self.txt_eslora_buque = self._crear_campo_solo_lectura(
            label="Eslora / LOA (m)",
            icono=ft.Icons.STRAIGHTEN_OUTLINED,
        )
        self.txt_calado_buque = self._crear_campo_solo_lectura(
            label="Calado / Draft (m)",
            icono=ft.Icons.WATER_OUTLINED,
        )

        # Buscador de Cliente y Dirección automática
        self.selector_cliente = SelectorCliente(
            servicio_cliente=self.servicio_cliente,
            on_cliente_seleccionado=self._al_seleccionar_cliente,
            label="Cliente / Customer *",
            hint_text="Buscar cliente por nombre o razón social...",
            height=52,
        )
        self.txt_direccion_cliente = self._crear_campo_solo_lectura(
            label="Dirección / Address",
            icono=ft.Icons.LOCATION_ON_OUTLINED,
        )

        # Estancia, Moneda y Tipo de Cambio
        self.txt_horas_estancia = ft.TextField(
            label="Horas de estancia *",
            value="32",
            prefix_icon=ft.Icons.ACCESS_TIME,
            height=48,
            text_size=12,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=8,
            content_padding=ft.Padding(12, 8, 12, 8),
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[0-9.]*$", replacement_string=""
            ),
            on_change=self._al_cambiar_horas_estancia,
            expand=True,
        )

        self.txt_dias_estancia = self._crear_campo_solo_lectura(
            label="Días de estancia (derivado)",
            icono=ft.Icons.CALENDAR_VIEW_DAY_OUTLINED,
            valor="2 días",
        )

        self.dd_moneda = ft.Dropdown(
            label="Moneda *",
            value=Moneda.MXN.value,
            options=[
                ft.dropdown.Option(key=Moneda.MXN.value, text="MXN - Peso Mexicano"),
                ft.dropdown.Option(key=Moneda.USD.value, text="USD - Dólar Americano"),
            ],
            height=48,
            text_size=12,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=8,
            content_padding=ft.Padding(12, 8, 12, 8),
            on_select=self._al_cambiar_moneda,
            expand=True,
        )

        self.txt_tipo_cambio = ft.TextField(
            label="Tipo de cambio",
            value="1.0000",
            disabled=True,
            prefix_icon=ft.Icons.CURRENCY_EXCHANGE,
            height=48,
            text_size=12,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=8,
            content_padding=ft.Padding(12, 8, 12, 8),
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[0-9.]*$", replacement_string=""
            ),
            on_change=self._al_cambiar_tipo_cambio,
            expand=True,
        )

        # Condiciones operativas de la escala (ContextoEscala)
        self.sw_mercancia_peligrosa = ft.Switch(
            label="Transporta mercancía peligrosa",
            value=False,
            active_color=COLOR_NARANJA,
        )
        self.sw_propulsores_danados = ft.Switch(
            label="Propulsores dañados / fuera de servicio",
            value=False,
            active_color=COLOR_NARANJA,
        )
        self.lbl_estado_propulsores = ft.Container(
            padding=ft.Padding(10, 5, 10, 5),
            border_radius=12,
            bgcolor="#EEF5FD",
            content=ft.Text(
                "Seleccione un buque para ver configuración de propulsores",
                size=11,
                color=COLOR_BANNER,
                weight=ft.FontWeight.W_500,
            ),
        )

    @staticmethod
    def _crear_campo_solo_lectura(
        label: str,
        icono,
        valor: str = "",
    ) -> ft.TextField:
        return ft.TextField(
            label=label,
            value=valor,
            read_only=True,
            prefix_icon=icono,
            height=48,
            text_size=12,
            bgcolor="#F4F8FC",
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            border_radius=8,
            content_padding=ft.Padding(12, 8, 12, 8),
            expand=True,
        )

    def _crear_campo_fecha(
        self,
        label: str,
        valor_inicial: str = "",
        hint_text: str = "dd/mm/aaaa",
    ) -> ft.TextField:
        txt_field = ft.TextField(
            label=label,
            value=valor_inicial,
            hint_text=hint_text,
            prefix_icon=ft.Icons.CALENDAR_TODAY_OUTLINED,
            height=48,
            text_size=12,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=8,
            content_padding=ft.Padding(12, 8, 12, 8),
            expand=True,
        )

        def abrir_picker(e):
            self.input_activo_fecha = txt_field
            pagina = e.page or self.main_page
            if pagina is not None:
                if self.date_picker not in pagina.overlay:
                    pagina.overlay.append(self.date_picker)
                self.date_picker.open = True
                pagina.update()

        txt_field.suffix = ft.IconButton(
            icon=ft.Icons.CALENDAR_MONTH,
            icon_size=16,
            icon_color=COLOR_NARANJA,
            on_click=abrir_picker,
            width=28,
            height=28,
            padding=0,
        )
        return txt_field

    def _inicializar_tabla_detalles(self) -> None:
        self.cabecera_tabla = self._construir_cabecera_tabla()
        self.lista_filas = ft.Column(spacing=4, controls=[])
        self.contenedor_resultados_servicio_activo = ft.Container(
            visible=False,
            padding=ft.Padding(110, 0, 120, 8),
        )

    def _inicializar_panel_totales(self) -> None:
        self.lbl_subtotal_general = ft.Text(
            "$ 0.00",
            size=13,
            weight=ft.FontWeight.BOLD,
            color=COLOR_AZUL_OSCURO,
        )
        self.lbl_iva_general = ft.Text(
            "$ 0.00",
            size=13,
            weight=ft.FontWeight.BOLD,
            color=COLOR_AZUL_OSCURO,
        )
        self.lbl_total_general = ft.Text(
            "$ 0.00",
            size=16,
            weight=ft.FontWeight.W_900,
            color=COLOR_NARANJA,
        )
        self.lbl_moneda_totales = ft.Text(
            "Importes expresados en MXN",
            size=11,
            color=COLOR_GRIS,
        )

    def _encabezado(self) -> ft.Control:
        return banner_modulo(
            src="fondo_puerto.jpg",
            categoria="Proforma de Gastos Portuarios (PDA)",
            titulo="Nueva Cotización",
            descripcion=(
                "Selecciona el buque y cliente, calcula los servicios portuarios "
                "obligatorios o agrega conceptos manualmente."
            ),
            icono=ft.Icons.REQUEST_QUOTE_OUTLINED,
        )

    def _panel_izquierdo(self) -> ft.Control:
        boton_cancelar = boton(
            texto="Volver a cotizaciones",
            icono=ft.Icons.ARROW_BACK,
            tipo="secundario",
            color=COLOR_BANNER,
            height=42,
            width=200,
            on_click=self.cancelar,
        )
        return ft.Column(
            expand=True,
            spacing=16,
            controls=[
                self._seccion_datos_generales(),
                self._seccion_servicios(),
                ft.Row(controls=[boton_cancelar]),
            ],
        )

    def _panel_derecho(self) -> ft.Control:
        tarjeta_columnas = card(
            ft.Column(
                spacing=8,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.VIEW_COLUMN_OUTLINED,
                                color=COLOR_AZUL_OSCURO,
                                size=18,
                            ),
                            ft.Text(
                                "Columnas visibles",
                                weight=ft.FontWeight.BOLD,
                                size=14,
                                color=COLOR_AZUL_OSCURO,
                            ),
                        ],
                    ),
                    ft.Text(
                        "Configura las columnas de edición u ocúltalas en vista cliente (formato PDA).",
                        size=11,
                        color=COLOR_GRIS,
                    ),
                    self.chk_cantidad,
                    self.chk_precio_unitario,
                    self.chk_factura,
                    ft.Divider(height=12, color=COLOR_GRIS_CLARO),
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.VISIBILITY_OUTLINED,
                                color=COLOR_GRIS,
                                size=16,
                            ),
                            ft.Text(
                                "Vista cliente (PDA)",
                                size=12,
                                weight=ft.FontWeight.W_500,
                                color=COLOR_AZUL_OSCURO,
                            ),
                            ft.Container(expand=True),
                            self.switch_cliente,
                        ],
                    ),
                ],
            ),
            padding=16,
            radius=12,
            border_color="#E1EAF4",
            shadow=sombra_suave(),
        )

        tarjeta_totales = card(
            ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        spacing=8,
                        controls=[
                            ft.Icon(
                                ft.Icons.CALCULATE_OUTLINED,
                                color=COLOR_AZUL,
                                size=20,
                            ),
                            ft.Text(
                                "Resumen de Proforma",
                                size=14,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_AZUL_OSCURO,
                            ),
                        ],
                    ),
                    self.lbl_moneda_totales,
                    ft.Divider(height=8, color=COLOR_GRIS_CLARO),
                    ft.Row(
                        controls=[
                            ft.Text("Subtotal", size=12, color=COLOR_GRIS),
                            ft.Container(expand=True),
                            self.lbl_subtotal_general,
                        ]
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("IVA / TAX", size=12, color=COLOR_GRIS),
                            ft.Container(expand=True),
                            self.lbl_iva_general,
                        ]
                    ),
                    ft.Divider(height=12, color=COLOR_GRIS_CLARO),
                    ft.Row(
                        controls=[
                            ft.Text(
                                "Total",
                                size=15,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_NARANJA,
                            ),
                            ft.Container(expand=True),
                            self.lbl_total_general,
                        ]
                    ),
                ],
            ),
            padding=16,
            radius=12,
            border_color="#E1EAF4",
            shadow=sombra_suave(),
        )

        self.boton_guardar = boton(
            texto="Guardar",
            icono=ft.Icons.SAVE_OUTLINED,
            tipo="principal",
            height=44,
            width=260,
            on_click=self.guardar_cotizacion,
        )

        return ft.Column(
            width=280,
            spacing=16,
            controls=[
                tarjeta_columnas,
                tarjeta_totales,
                self.boton_guardar,
            ],
        )

    def _seccion_datos_generales(self) -> ft.Control:
        cuerpo_formulario = ft.Column(
            spacing=14,
            controls=[
                # Bloque 1: Encabezado del Documento y Cliente (Folio PDA, Fecha, Cliente, Dirección)
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.Icons.BADGE_OUTLINED, size=18, color=COLOR_NARANJA),
                        ft.Text(
                            "Datos del Documento y Cliente / Customer",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                    ],
                ),
                # Fila 1 (top=30): Folio PDA | Fecha Emisión | Cliente (SelectorCliente)
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(expand=2, content=self.txt_folio),
                        ft.Container(expand=2, content=self.txt_fecha_emision),
                        ft.Container(expand=4, content=self.selector_cliente),
                    ],
                ),
                # Fila 2: Dirección del Cliente | Arribo (ETA) | Zarpe (ETD)
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(expand=4, content=self.txt_direccion_cliente),
                        ft.Container(expand=2, content=self.txt_fecha_arribo),
                        ft.Container(expand=2, content=self.txt_fecha_zarpe),
                    ],
                ),
                # Fila 3: Horas de Estancia | Días de Estancia | Moneda | Tipo de Cambio
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(expand=2, content=self.txt_horas_estancia),
                        ft.Container(expand=2, content=self.txt_dias_estancia),
                        ft.Container(expand=2, content=self.dd_moneda),
                        ft.Container(expand=2, content=self.txt_tipo_cambio),
                    ],
                ),
                ft.Divider(height=8, color=COLOR_GRIS_CLARO),
                # Bloque 2: Información del Buque / Vessel's Information
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                            size=18,
                            color=COLOR_NARANJA,
                        ),
                        ft.Text(
                            "Información del Buque / Vessel's Information",
                            size=13,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                    ],
                ),
                # Fila 4: SelectorBuque | Tipo de Buque | IMO
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(expand=4, content=self.selector_buque),
                        ft.Container(expand=2, content=self.txt_tipo_buque),
                        ft.Container(expand=2, content=self.txt_imo_buque),
                    ],
                ),
                # Fila 5: UAB / GRT (TRB) | Eslora / LOA (m) | Calado / Draft (m)
                ft.Row(
                    spacing=12,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(expand=2, content=self.txt_trb_buque),
                        ft.Container(expand=2, content=self.txt_eslora_buque),
                        ft.Container(expand=2, content=self.txt_calado_buque),
                    ],
                ),
                ft.Divider(height=8, color=COLOR_GRIS_CLARO),
                # Bloque 3: Condiciones Operativas de la Escala (ContextoEscala)
                ft.Container(
                    bgcolor="#F7FAFD",
                    border=ft.Border.all(1, "#E4ECF5"),
                    border_radius=9,
                    padding=ft.Padding(12, 8, 12, 8),
                    content=ft.Row(
                        spacing=16,
                        wrap=True,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Row(
                                spacing=6,
                                tight=True,
                                controls=[
                                    ft.Icon(
                                        ft.Icons.SETTINGS_OUTLINED,
                                        size=16,
                                        color=COLOR_BANNER,
                                    ),
                                    ft.Text(
                                        "Condiciones de la escala:",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_BANNER,
                                    ),
                                ],
                            ),
                            self.sw_mercancia_peligrosa,
                            self.sw_propulsores_danados,
                            self.lbl_estado_propulsores,
                        ],
                    ),
                ),
            ],
        )

        # Stack que superpone los desplegables flotantes de SelectorCliente y SelectorBuque
        stack_datos = ft.Stack(
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[
                cuerpo_formulario,
                # Resultados flotantes de SelectorCliente (debajo de Fila 1, columna derecha)
                ft.Container(
                    top=84,
                    left=0,
                    right=0,
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(expand=2),
                            ft.Container(expand=2),
                            ft.Container(
                                expand=4,
                                content=self.selector_cliente.contenido_resultados,
                            ),
                        ],
                    ),
                ),
                # Resultados flotantes de SelectorBuque (debajo de Fila 4, columna izquierda)
                ft.Container(
                    top=296,
                    left=0,
                    right=0,
                    content=ft.Row(
                        spacing=12,
                        controls=[
                            ft.Container(
                                expand=4,
                                content=self.selector_buque.contenido_resultados,
                            ),
                            ft.Container(expand=2),
                            ft.Container(expand=2),
                        ],
                    ),
                ),
            ],
        )

        return card(
            ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        padding=ft.Padding(18, 12, 18, 12),
                        border=ft.Border(bottom=ft.BorderSide(1, "#E8EEF5")),
                        content=ft.Row(
                            spacing=12,
                            controls=[
                                self._crear_indicador_numero("1", COLOR_AZUL),
                                ft.Column(
                                    spacing=1,
                                    controls=[
                                        ft.Text(
                                            "Encabezado de Proforma, Cliente y Buque",
                                            weight=ft.FontWeight.BOLD,
                                            size=15,
                                            color=COLOR_AZUL_OSCURO,
                                        ),
                                        ft.Text(
                                            "Selecciona el buque para autocompletar sus dimensiones y su cliente asociado.",
                                            size=11,
                                            color=COLOR_GRIS,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        padding=18,
                        content=stack_datos,
                    ),
                ],
            ),
            padding=0,
            radius=12,
            border_color="#E1EAF4",
            shadow=sombra_suave(),
        )

    def _seccion_servicios(self) -> ft.Control:
        self.boton_agregar_concepto = boton(
            texto="Agregar Concepto",
            icono=ft.Icons.ADD,
            tipo="secundario",
            color=COLOR_NARANJA,
            border_color=COLOR_NARANJA,
            height=38,
            on_click=self.agregar_fila,
        )

        self.boton_calcular_servicios = boton(
            texto="Calcular Servicios",
            icono=ft.Icons.CALCULATE_OUTLINED,
            tipo="principal",
            color=COLOR_NARANJA,
            height=38,
            on_click=self.calcular_servicios,
        )

        contenedor_tabla = ft.Container(
            width=1380,
            content=ft.Column(
                spacing=4,
                controls=[
                    self.cabecera_tabla,
                    ft.Divider(height=8, color=COLOR_GRIS_CLARO),
                    self.contenedor_resultados_servicio_activo,
                    self.lista_filas,
                    ft.Container(height=20),
                ],
            ),
        )

        tarjeta_desglose = card(
            ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        padding=ft.Padding(18, 12, 18, 12),
                        border=ft.Border(bottom=ft.BorderSide(1, "#E8EEF5")),
                        content=ft.Row(
                            spacing=14,
                            wrap=True,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Row(
                                    spacing=12,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        self._crear_indicador_numero("2", COLOR_AZUL),
                                        ft.Text(
                                            "Desglose de Servicios y Conceptos (Formato PDA)",
                                            weight=ft.FontWeight.BOLD,
                                            size=15,
                                            color=COLOR_AZUL_OSCURO,
                                        ),
                                    ],
                                ),
                                ft.Row(
                                    spacing=10,
                                    controls=[
                                        self.boton_agregar_concepto,
                                        self.boton_calcular_servicios,
                                    ],
                                ),
                            ],
                        ),
                    ),
                    ft.Container(
                        padding=18,
                        content=ft.Column(
                            spacing=10,
                            controls=[
                                contenedor_tabla,
                                ft.Container(
                                    bgcolor="#EEF5FD",
                                    border=ft.Border.all(1, "#D6E6FA"),
                                    border_radius=8,
                                    padding=10,
                                    content=ft.Row(
                                        spacing=8,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.INFO_OUTLINE,
                                                color=COLOR_AZUL,
                                                size=18,
                                            ),
                                            ft.Text(
                                                "El IVA se calcula automáticamente según la tasa del servicio (16%, 8% o 0%). Al modificar Cantidad o Precio Unitario se actualizan Subtotal, IVA y Total en tiempo real.",
                                                color=COLOR_BANNER,
                                                size=11,
                                            ),
                                        ],
                                    ),
                                ),
                            ],
                        ),
                    ),
                ],
            ),
            padding=0,
            radius=12,
            border_color="#E1EAF4",
            shadow=sombra_suave(),
        )
        return ft.Row(
            expand=True,
            scroll=ft.ScrollMode.ADAPTIVE,
            controls=[
                ft.Container(width=1420, content=tarjeta_desglose),
            ],
        )

    def _construir_cabecera_tabla(self) -> ft.Row:
        return ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=28,
                    content=ft.Text(
                        "#", size=11, color=COLOR_BANNER, weight=ft.FontWeight.BOLD
                    ),
                ),
                ft.Container(
                    width=130,
                    content=ft.Text(
                        "Categoría",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=235,
                    content=ft.Text(
                        "Descripción",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=175,
                    content=ft.Text(
                        "Proveedor",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=62,
                    visible=self.ver_cantidad,
                    content=ft.Text(
                        "Cant.",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=95,
                    visible=self.ver_precio_unitario,
                    content=ft.Text(
                        "Precio Unit.",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=95,
                    content=ft.Text(
                        "Subtotal",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=85,
                    content=ft.Text(
                        "IVA / TAX",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=95,
                    content=ft.Text(
                        "Total",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=85,
                    visible=self.ver_factura,
                    content=ft.Text(
                        "Factura",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=135,
                    content=ft.Text(
                        "Observaciones",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
                ft.Container(
                    width=50,
                    content=ft.Text(
                        "Acciones",
                        size=11,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.BOLD,
                    ),
                ),
            ],
        )

    # =========================================================================
    # MANEJADORES REACTIVOS DE ENCABEZADO (BUQUE, CLIENTE, ESTANCIA, MONEDA)
    # =========================================================================

    def _al_seleccionar_buque(self, buque: Buque | None) -> None:
        self.buque_actual = buque

        if buque is None:
            self.txt_tipo_buque.value = ""
            self.txt_imo_buque.value = ""
            self.txt_trb_buque.value = ""
            self.txt_eslora_buque.value = ""
            self.txt_calado_buque.value = ""
            self.lbl_estado_propulsores.bgcolor = "#EEF5FD"
            self.lbl_estado_propulsores.content.value = (
                "Seleccione un buque para ver configuración de propulsores"
            )
            self.lbl_estado_propulsores.content.color = COLOR_BANNER
            self._actualizar_ui()
            return

        categoria_obj = getattr(buque, "categoria_buque", None)
        nombre_cat = getattr(categoria_obj, "categoria", None) or ""
        subtipo = getattr(buque, "subtipo_descripcion", None) or ""
        if nombre_cat and subtipo and subtipo.upper() != nombre_cat.upper():
            self.txt_tipo_buque.value = f"{nombre_cat} ({subtipo})"
        else:
            self.txt_tipo_buque.value = nombre_cat or subtipo

        self.txt_imo_buque.value = str(getattr(buque, "numero_imo", "") or "")
        self.txt_trb_buque.value = (
            f"{Decimal(str(buque.trb)):,.2f}"
            if getattr(buque, "trb", None) is not None
            else ""
        )
        self.txt_eslora_buque.value = (
            f"{Decimal(str(buque.eslora)):,.2f}"
            if getattr(buque, "eslora", None) is not None
            else ""
        )
        self.txt_calado_buque.value = (
            f"{Decimal(str(buque.calado)):,.2f}"
            if getattr(buque, "calado", None) is not None
            else ""
        )

        # Indicador visual de propulsores proa/popa del buque
        tiene_propulsores = bool(getattr(buque, "propulsores_proa_popa", False))
        if tiene_propulsores:
            self.lbl_estado_propulsores.bgcolor = "#EAF8F0"
            self.lbl_estado_propulsores.content.value = (
                "Buque con propulsores en proa y popa"
            )
            self.lbl_estado_propulsores.content.color = COLOR_VERDE
        else:
            self.lbl_estado_propulsores.bgcolor = "#FFF3D9"
            self.lbl_estado_propulsores.content.value = (
                "Buque sin propulsores en proa y popa"
            )
            self.lbl_estado_propulsores.content.color = "#A66B00"

        # Autocarga editable del cliente asociado al buque
        cliente_buque = getattr(buque, "cliente", None)
        if cliente_buque is not None:
            self.selector_cliente.establecer_cliente(cliente_buque, notificar=False)
            self._al_seleccionar_cliente(cliente_buque)

        self._actualizar_ui()

    def _al_seleccionar_cliente(self, cliente: Cliente | None) -> None:
        self.cliente_actual = cliente
        if cliente is None:
            self.txt_direccion_cliente.value = ""
        else:
            self.txt_direccion_cliente.value = (
                getattr(cliente, "direccion", "") or ""
            )
        self._actualizar_ui()

    def _al_cambiar_horas_estancia(self, e=None) -> None:
        horas_txt = (self.txt_horas_estancia.value or "").strip()
        dias = ControladorCotizacion.calcular_dias_estancia(horas_txt)
        if dias > 0:
            sufijo = "día" if dias == 1 else "días"
            self.txt_dias_estancia.value = f"{dias} {sufijo}"
        else:
            self.txt_dias_estancia.value = "0 días"
        self._actualizar_ui()

    def _al_cambiar_moneda(self, e=None) -> None:
        moneda_sel = (self.dd_moneda.value or Moneda.MXN.value).upper()
        if moneda_sel == Moneda.MXN.value:
            self.txt_tipo_cambio.value = "1.0000"
            self.txt_tipo_cambio.disabled = True
        else:
            self.txt_tipo_cambio.disabled = False
            if (self.txt_tipo_cambio.value or "").strip() in ("", "1", "1.0", "1.00", "1.0000"):
                self.txt_tipo_cambio.value = "16.0000"
        self.lbl_moneda_totales.value = f"Importes expresados en {moneda_sel}"
        self._recalcular_filas_por_moneda()
        self._actualizar_ui()

    def _al_cambiar_tipo_cambio(self, e=None) -> None:
        self._recalcular_filas_por_moneda()
        self._actualizar_ui()

    def _obtener_parametros_contexto_actual(self) -> tuple[Decimal, Moneda, Decimal]:
        try:
            horas = Decimal((self.txt_horas_estancia.value or "24").strip())
            if horas <= Decimal("0"):
                horas = Decimal("24.00")
        except (InvalidOperation, ValueError):
            horas = Decimal("24.00")

        moneda = (
            Moneda.USD
            if (self.dd_moneda.value or "MXN").upper() == "USD"
            else Moneda.MXN
        )

        try:
            tc = (
                Decimal("1.0000")
                if moneda == Moneda.MXN
                else Decimal((self.txt_tipo_cambio.value or "16.0000").strip())
            )
            if tc <= Decimal("0"):
                tc = Decimal("1.0000")
        except (InvalidOperation, ValueError):
            tc = Decimal("1.0000")

        return horas, moneda, tc

    def _recalcular_filas_por_moneda(self) -> None:
        if not self.filas_datos or self.controlador is None:
            return
        horas, moneda, tc = self._obtener_parametros_contexto_actual()
        for estado_fila in self.filas_datos:
            servicio = estado_fila.get("servicio")
            if servicio is None:
                continue
            try:
                cant_actual = Decimal(
                    (estado_fila["txt_cantidad"].value or "1").strip()
                )
            except (InvalidOperation, ValueError):
                cant_actual = Decimal("1.00")

            datos_calc = self.controlador.calcular_detalle_para_servicio_manual(
                servicio=servicio,
                buque=self.buque_actual,
                horas_estancia=horas,
                moneda=moneda,
                tipo_cambio=tc,
                cantidad=cant_actual,
            )
            self._poblar_controles_fila(
                estado_fila, datos_calc, conservar_observaciones=True
            )
        self._recalcular_totales_generales()

    # =========================================================================
    # CÁLCULO AUTOMÁTICO Y GESTIÓN DE FILAS DE LA TABLA PDA
    # =========================================================================

    def calcular_servicios(self, e=None) -> list[DetalleCotizacion]:
        buque = self.buque_actual or self.selector_buque.buque_seleccionado
        if buque is None:
            self._notificar(
                "Selecciona un buque antes de calcular los servicios.",
                COLOR_ROJO,
            )
            return []

        try:
            horas_dec = ControladorCotizacion._a_decimal(
                self.txt_horas_estancia.value, "Las horas de estancia"
            )
            if horas_dec <= Decimal("0"):
                raise ValueError("Las horas de estancia deben ser mayores que 0.")
        except ValueError as error:
            self._notificar(str(error), COLOR_ROJO)
            return []

        if self.controlador is None:
            self._notificar(
                "El controlador de cotizaciones no está configurado.",
                COLOR_ROJO,
            )
            return []

        _, moneda, tc = self._obtener_parametros_contexto_actual()

        try:
            detalles = self.controlador.calcular_servicios_obligatorios(
                buque=buque,
                horas_estancia=horas_dec,
                moneda=moneda,
                tipo_cambio=tc,
                transporta_mercancia_peligrosa=bool(
                    self.sw_mercancia_peligrosa.value
                ),
                propulsores_danados=bool(self.sw_propulsores_danados.value),
            )
        except Exception as error:
            self._notificar(str(error), COLOR_ROJO)
            return []

        if not detalles:
            self._notificar(
                "No se encontraron servicios configurados para este buque. "
                "Se conservaron los conceptos que ya estaban en el desglose.",
                COLOR_NARANJA,
            )
            return []

        filas_manuales = [
            fila
            for fila in self.filas_datos
            if not fila.get("calculado_automaticamente", False)
        ]
        self.filas_datos = filas_manuales
        self.lista_filas.controls = [
            fila["contenedor"] for fila in filas_manuales
        ]
        self.contenedor_resultados_servicio_activo.visible = False

        for idx, detalle in enumerate(
            detalles, start=len(self.filas_datos) + 1
        ):
            estado_fila = self._crear_fila_desde_detalle(idx, detalle)
            estado_fila["calculado_automaticamente"] = True
            self.filas_datos.append(estado_fila)
            self.lista_filas.controls.append(estado_fila["contenedor"])

        for idx, fila in enumerate(self.filas_datos, start=1):
            fila["disc"] = idx
            fila["lbl_numero"].value = str(idx)

        self._recalcular_totales_generales()
        self._actualizar_ui()
        return detalles

    def agregar_fila(self, e=None) -> dict:
        siguiente_numero = len(self.filas_datos) + 1
        estado_fila = self._crear_estructura_fila(numero=siguiente_numero)
        self.filas_datos.append(estado_fila)
        self.lista_filas.controls.append(estado_fila["contenedor"])
        self._recalcular_totales_generales()
        self._actualizar_ui()
        return estado_fila

    def eliminar_fila(self, estado_fila: dict) -> None:
        if estado_fila in self.filas_datos:
            self.filas_datos.remove(estado_fila)
        if estado_fila["contenedor"] in self.lista_filas.controls:
            self.lista_filas.controls.remove(estado_fila["contenedor"])

        for idx, fila in enumerate(self.filas_datos, start=1):
            fila["disc"] = idx
            fila["lbl_numero"].value = str(idx)

        self._recalcular_totales_generales()
        self._actualizar_ui()

    def _al_abrir_resultados_servicio(
        self, selector: SelectorServicio, mostrar: bool
    ) -> None:
        if mostrar:
            self.contenedor_resultados_servicio_activo.content = (
                selector.contenido_resultados
            )
            self.contenedor_resultados_servicio_activo.visible = True
        else:
            if (
                self.contenedor_resultados_servicio_activo.content
                is selector.contenido_resultados
            ):
                self.contenedor_resultados_servicio_activo.visible = False
        self._actualizar_ui()

    def _crear_fila_desde_detalle(
        self, numero: int, detalle: DetalleCotizacion
    ) -> dict:
        servicio = getattr(detalle, "concepto", None)
        proveedores = getattr(servicio, "proveedores", None) or []
        proveedor_principal = proveedores[0] if proveedores else None
        estado_fila = self._crear_estructura_fila(
            numero=numero,
            servicio_inicial=servicio,
        )
        datos = {
            "concepto_id": detalle.concepto_id,
            "servicio": servicio,
            "categoria_pda": detalle.categoria_pda_nombre,
            "descripcion": detalle.descripcion,
            "proveedor": detalle.proveedor_nombre,
            "proveedor_id": (
                getattr(proveedor_principal, "id", None)
                if proveedor_principal is not None
                else None
            ),
            "proveedor_obj": proveedor_principal,
            "cantidad": detalle.cantidad,
            "precio_unitario": detalle.precio_unitario,
            "tasa_iva": detalle.tasa_iva,
            "subtotal": detalle.subtotal,
            "iva": detalle.iva,
            "total": detalle.total,
            "factura": detalle.factura or "",
            "observaciones": detalle.observaciones or "",
        }
        self._poblar_controles_fila(estado_fila, datos)
        return estado_fila

    def _crear_estructura_fila(
        self,
        numero: int,
        servicio_inicial: Servicio | None = None,
    ) -> dict:
        estado_fila: dict = {
            "disc": int(numero),
            "servicio": servicio_inicial,
            "concepto_id": (
                int(servicio_inicial.id)
                if servicio_inicial is not None
                and getattr(servicio_inicial, "id", None) is not None
                else None
            ),
            "proveedor_id": None,
            "proveedor_obj": None,
            "tasa_iva": (
                Decimal(str(servicio_inicial.tasa_iva))
                if servicio_inicial is not None
                and getattr(servicio_inicial, "tasa_iva", None) is not None
                else Decimal("0.1600")
            ),
            "subtotal": Decimal("0.00"),
            "iva": Decimal("0.00"),
            "total": Decimal("0.00"),
        }

        lbl_numero = ft.Text(
            str(numero),
            size=12,
            weight=ft.FontWeight.BOLD,
            color=COLOR_BANNER,
        )
        lbl_categoria = ft.Text(
            "",
            size=11,
            weight=ft.FontWeight.W_600,
            color=COLOR_AZUL_OSCURO,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
        lbl_proveedor = ft.Text(
            "",
            size=11,
            color=COLOR_GRIS,
            max_lines=2,
            overflow=ft.TextOverflow.ELLIPSIS,
        )

        selector_servicio = SelectorServicio(
            servicio_servicio=self.servicio_servicio,
            servicio_inicial=servicio_inicial,
            on_servicio_seleccionado=lambda serv, ef=estado_fila: self._al_seleccionar_servicio_en_fila(
                ef, serv
            ),
            on_abrir_resultados=self._al_abrir_resultados_servicio,
        )

        txt_cantidad = ft.TextField(
            value="1" if servicio_inicial is None else "1.00",
            height=34,
            text_size=11,
            dense=True,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=6,
            content_padding=ft.Padding(6, 4, 6, 4),
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[0-9.]*$", replacement_string=""
            ),
            on_change=lambda e, ef=estado_fila: self._al_editar_importe_fila(ef),
        )

        txt_precio_unitario = ft.TextField(
            value="0.00",
            height=34,
            text_size=11,
            dense=True,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=6,
            content_padding=ft.Padding(6, 4, 6, 4),
            input_filter=ft.InputFilter(
                allow=True, regex_string=r"^[0-9.]*$", replacement_string=""
            ),
            on_change=lambda e, ef=estado_fila: self._al_editar_importe_fila(ef),
        )

        lbl_subtotal = ft.Text(
            "$ 0.00",
            size=11,
            weight=ft.FontWeight.W_600,
            color=COLOR_AZUL_OSCURO,
        )
        lbl_iva = ft.Text(
            "$ 0.00",
            size=11,
            weight=ft.FontWeight.W_600,
            color=COLOR_AZUL_OSCURO,
        )
        lbl_total = ft.Text(
            "$ 0.00",
            size=11,
            weight=ft.FontWeight.BOLD,
            color=COLOR_AZUL_OSCURO,
        )

        txt_factura = ft.TextField(
            value="",
            hint_text="Factura",
            height=34,
            text_size=11,
            dense=True,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=6,
            content_padding=ft.Padding(6, 4, 6, 4),
        )

        txt_observaciones = ft.TextField(
            value="",
            hint_text="Observaciones",
            height=34,
            text_size=11,
            dense=True,
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=6,
            content_padding=ft.Padding(6, 4, 6, 4),
        )

        celda_cantidad = ft.Container(
            width=62,
            visible=self.ver_cantidad,
            content=txt_cantidad,
        )
        celda_precio = ft.Container(
            width=95,
            visible=self.ver_precio_unitario,
            content=txt_precio_unitario,
        )
        celda_factura = ft.Container(
            width=85,
            visible=self.ver_factura,
            content=txt_factura,
        )

        btn_borrar = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_size=17,
            icon_color=COLOR_ROJO,
            tooltip="Eliminar concepto",
            width=32,
            height=32,
            padding=0,
            on_click=lambda e, ef=estado_fila: self.eliminar_fila(ef),
        )

        contenedor_fila = ft.Container(
            padding=ft.Padding(0, 5, 0, 5),
            border=ft.Border(bottom=ft.BorderSide(1, "#EEF2F7")),
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(width=28, content=lbl_numero),
                    ft.Container(width=130, content=lbl_categoria),
                    ft.Container(width=235, content=selector_servicio),
                    ft.Container(width=175, content=lbl_proveedor),
                    celda_cantidad,
                    celda_precio,
                    ft.Container(width=95, content=lbl_subtotal),
                    ft.Container(width=85, content=lbl_iva),
                    ft.Container(width=95, content=lbl_total),
                    celda_factura,
                    ft.Container(width=135, content=txt_observaciones),
                    ft.Container(width=50, content=btn_borrar),
                ],
            ),
        )

        estado_fila.update(
            {
                "contenedor": contenedor_fila,
                "lbl_numero": lbl_numero,
                "lbl_categoria": lbl_categoria,
                "selector_servicio": selector_servicio,
                "lbl_proveedor": lbl_proveedor,
                "txt_cantidad": txt_cantidad,
                "txt_precio_unitario": txt_precio_unitario,
                "lbl_subtotal": lbl_subtotal,
                "lbl_iva": lbl_iva,
                "lbl_total": lbl_total,
                "txt_factura": txt_factura,
                "txt_observaciones": txt_observaciones,
                "celda_cantidad": celda_cantidad,
                "celda_precio": celda_precio,
                "celda_factura": celda_factura,
            }
        )
        return estado_fila

    def _poblar_controles_fila(
        self,
        estado_fila: dict,
        datos: dict,
        conservar_observaciones: bool = False,
    ) -> None:
        servicio = datos.get("servicio") or datos.get("concepto")
        estado_fila["servicio"] = servicio
        estado_fila["concepto_id"] = datos.get("concepto_id") or (
            getattr(servicio, "id", None) if servicio else None
        )
        estado_fila["proveedor_id"] = datos.get("proveedor_id")
        estado_fila["proveedor_obj"] = datos.get("proveedor_obj")
        estado_fila["tasa_iva"] = Decimal(
            str(datos.get("tasa_iva", Decimal("0.1600")))
        )
        estado_fila["subtotal"] = Decimal(str(datos.get("subtotal", Decimal("0.00"))))
        estado_fila["iva"] = Decimal(str(datos.get("iva", Decimal("0.00"))))
        estado_fila["total"] = Decimal(str(datos.get("total", Decimal("0.00"))))

        estado_fila["lbl_categoria"].value = datos.get("categoria_pda") or ""
        estado_fila["lbl_proveedor"].value = datos.get("proveedor") or ""
        if servicio is not None:
            estado_fila["selector_servicio"].establecer_servicio(servicio)

        cant_dec = Decimal(str(datos.get("cantidad", Decimal("1.00"))))
        estado_fila["txt_cantidad"].value = (
            str(int(cant_dec))
            if cant_dec == int(cant_dec)
            else f"{cant_dec:.2f}"
        )
        precio_dec = Decimal(str(datos.get("precio_unitario", Decimal("0.00"))))
        estado_fila["txt_precio_unitario"].value = f"{precio_dec:.2f}"

        estado_fila["lbl_subtotal"].value = ControladorCotizacion.formatear_moneda(
            estado_fila["subtotal"]
        )
        estado_fila["lbl_iva"].value = ControladorCotizacion.formatear_iva_celda(
            estado_fila["iva"], estado_fila["tasa_iva"]
        )
        estado_fila["lbl_total"].value = ControladorCotizacion.formatear_moneda(
            estado_fila["total"]
        )

        if not conservar_observaciones:
            estado_fila["txt_factura"].value = datos.get("factura") or ""
            estado_fila["txt_observaciones"].value = datos.get("observaciones") or ""

    def _al_seleccionar_servicio_en_fila(
        self, estado_fila: dict, servicio: Servicio
    ) -> None:
        if self.controlador is None:
            return
        horas, moneda, tc = self._obtener_parametros_contexto_actual()
        buque = self.buque_actual or self.selector_buque.buque_seleccionado
        try:
            datos_calculados = (
                self.controlador.calcular_detalle_para_servicio_manual(
                    servicio=servicio,
                    buque=buque,
                    horas_estancia=horas,
                    moneda=moneda,
                    tipo_cambio=tc,
                )
            )
            self._poblar_controles_fila(estado_fila, datos_calculados)
            self._recalcular_totales_generales()
            self._actualizar_ui()
        except Exception as error:
            self._notificar(str(error), COLOR_ROJO)

    def _al_editar_importe_fila(self, estado_fila: dict) -> None:
        cant_str = (estado_fila["txt_cantidad"].value or "0").strip()
        precio_str = (estado_fila["txt_precio_unitario"].value or "0").strip()
        tasa_iva = estado_fila.get("tasa_iva", Decimal("0.1600"))

        importes = ControladorCotizacion.recalcular_importes_fila(
            cantidad=cant_str or "0",
            precio_unitario=precio_str or "0",
            tasa_iva=tasa_iva,
        )
        estado_fila["subtotal"] = importes["subtotal"]
        estado_fila["iva"] = importes["iva"]
        estado_fila["total"] = importes["total"]

        estado_fila["lbl_subtotal"].value = ControladorCotizacion.formatear_moneda(
            importes["subtotal"]
        )
        estado_fila["lbl_iva"].value = ControladorCotizacion.formatear_iva_celda(
            importes["iva"], tasa_iva
        )
        estado_fila["lbl_total"].value = ControladorCotizacion.formatear_moneda(
            importes["total"]
        )

        self._recalcular_totales_generales()
        self._actualizar_ui()

    def _recalcular_totales_generales(self) -> tuple[Decimal, Decimal, Decimal]:
        acum_subtotal = Decimal("0.00")
        acum_iva = Decimal("0.00")

        for fila in self.filas_datos:
            acum_subtotal += Decimal(str(fila.get("subtotal", Decimal("0.00"))))
            acum_iva += Decimal(str(fila.get("iva", Decimal("0.00"))))

        subtotal = acum_subtotal.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        iva = acum_iva.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        total = (subtotal + iva).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        self.lbl_subtotal_general.value = ControladorCotizacion.formatear_moneda(
            subtotal
        )
        self.lbl_iva_general.value = ControladorCotizacion.formatear_moneda(iva)
        self.lbl_total_general.value = ControladorCotizacion.formatear_moneda(total)
        return subtotal, iva, total

    # =========================================================================
    # GUARDADO DE LA COTIZACIÓN EN BASE DE DATOS
    # =========================================================================

    def obtener_detalles_para_guardar(self) -> list[dict]:
        partidas: list[dict] = []
        for idx, fila in enumerate(self.filas_datos, start=1):
            servicio = fila.get("servicio") or getattr(
                fila.get("selector_servicio"), "servicio_seleccionado", None
            )
            concepto_id = fila.get("concepto_id") or (
                getattr(servicio, "id", None) if servicio is not None else None
            )
            if concepto_id is None:
                continue

            partidas.append(
                {
                    "disc": idx,
                    "concepto_id": int(concepto_id),
                    "servicio": servicio,
                    "proveedor_id": fila.get("proveedor_id"),
                    "proveedor_obj": fila.get("proveedor_obj"),
                    "cantidad": fila["txt_cantidad"].value,
                    "precio_unitario": fila["txt_precio_unitario"].value,
                    "tasa_iva": fila.get("tasa_iva", Decimal("0.1600")),
                    "subtotal": fila.get("subtotal", Decimal("0.00")),
                    "iva": fila.get("iva", Decimal("0.00")),
                    "factura": fila["txt_factura"].value,
                    "observaciones": fila["txt_observaciones"].value,
                }
            )
        return partidas

    def guardar_cotizacion(self, e=None):
        if self.controlador is None:
            self._notificar(
                "El controlador de cotizaciones no está disponible.",
                COLOR_ROJO,
            )
            return None

        buque = self.buque_actual or self.selector_buque.buque_seleccionado
        buque_id = (
            getattr(buque, "id", None)
            or self.selector_buque.buque_id_seleccionado
        )
        cliente = self.cliente_actual or self.selector_cliente.cliente_seleccionado
        cliente_id = (
            getattr(cliente, "id", None)
            or self.selector_cliente.cliente_id_seleccionado
        )

        partidas = self.obtener_detalles_para_guardar()

        try:
            cotizacion = self.controlador.guardar_nueva_cotizacion(
                cliente=cliente,
                cliente_id=cliente_id,
                buque=buque,
                buque_id=buque_id,
                detalles=partidas,
                folio=self.txt_folio.value,
                fecha_emision=self.txt_fecha_emision.value,
                fecha_arribo=self.txt_fecha_arribo.value,
                fecha_zarpe=self.txt_fecha_zarpe.value,
                horas_estancia=self.txt_horas_estancia.value,
                moneda=self.dd_moneda.value,
                tipo_cambio=self.txt_tipo_cambio.value,
                transporta_mercancia_peligrosa=bool(
                    self.sw_mercancia_peligrosa.value
                ),
                propulsores_danados=bool(self.sw_propulsores_danados.value),
            )
        except (ValueError, ErrorCotizacion) as error:
            self._notificar(str(error), COLOR_ROJO)
            return None

        self.txt_folio.value = cotizacion.folio
        self._notificar(
            f"Cotización {cotizacion.folio} registrada correctamente.",
            COLOR_VERDE,
        )

        if self.vista_anterior is not None:
            if hasattr(self.vista_anterior, "actualizar_historial"):
                self.vista_anterior.actualizar_historial()
            if self.parent is not None:
                self.parent.content = self.vista_anterior
                self.parent.update()
        return cotizacion

    # =========================================================================
    # VISIBILIDAD DE COLUMNAS Y NAVEGACIÓN
    # =========================================================================

    def toggle_vista_cliente(self, e) -> None:
        es_vista_cliente = bool(self.switch_cliente.value)
        self.chk_cantidad.value = not es_vista_cliente
        self.chk_precio_unitario.value = not es_vista_cliente
        self.toggle_columnas(None)

    def toggle_columnas(self, e) -> None:
        self.ver_cantidad = bool(self.chk_cantidad.value)
        self.ver_precio_unitario = bool(self.chk_precio_unitario.value)
        self.ver_factura = bool(self.chk_factura.value)

        self.cabecera_tabla.controls[4].visible = self.ver_cantidad
        self.cabecera_tabla.controls[5].visible = self.ver_precio_unitario
        self.cabecera_tabla.controls[9].visible = self.ver_factura

        for fila in self.filas_datos:
            fila["celda_cantidad"].visible = self.ver_cantidad
            fila["celda_precio"].visible = self.ver_precio_unitario
            fila["celda_factura"].visible = self.ver_factura

        self._actualizar_ui()

    def cancelar(self, e=None) -> None:
        if self.vista_anterior is not None and self.parent is not None:
            if hasattr(self.vista_anterior, "actualizar_historial"):
                self.vista_anterior.actualizar_historial()
            self.parent.content = self.vista_anterior
            self.parent.update()

    def cambiar_fecha(self, e) -> None:
        if self.date_picker.value and self.input_activo_fecha:
            fecha_formateada = self.date_picker.value.strftime("%d/%m/%Y")
            self.input_activo_fecha.value = fecha_formateada
            try:
                self.input_activo_fecha.update()
            except RuntimeError:
                pass

    @staticmethod
    def _crear_indicador_numero(numero: str, color_fondo: str) -> ft.Container:
        return ft.Container(
            width=26,
            height=26,
            bgcolor=color_fondo,
            border_radius=13,
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                numero,
                color=COLOR_BLANCO,
                weight=ft.FontWeight.BOLD,
                size=13,
            ),
        )

    def _notificar(self, mensaje: str, color: str = COLOR_VERDE) -> None:
        pagina = self.main_page
        if pagina is None:
            try:
                pagina = self.page
            except RuntimeError:
                pagina = None
        if pagina is not None:
            try:
                mostrar_notificacion(pagina, mensaje, color)
            except Exception:
                pass

    def _actualizar_ui(self) -> None:
        try:
            pagina = None
            try:
                pagina = self.page
            except RuntimeError:
                pagina = None
            if pagina is not None:
                pagina.update()
            elif self.main_page is not None:
                self.main_page.update()
            else:
                self.update()
        except RuntimeError:
            pass
