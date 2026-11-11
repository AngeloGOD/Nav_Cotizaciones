from __future__ import annotations

from decimal import Decimal
import flet as ft
import flet_datatable2 as ftd

from fuente.negocio.controlador.ControladorCotizacion import ControladorCotizacion
from fuente.negocio.modelo.ENUMs import EstadoCotizacion
from fuente.presentacion.PantallaNuevaCotizacion import PantallaNuevaCotizacion
from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_BANNER,
    COLOR_BLANCO,
    COLOR_FONDO,
    COLOR_GRIS,
    COLOR_NARANJA,
    COLOR_NEGRO,
    COLOR_ROJO,
    COLOR_VERDE,
)
from fuente.utilidades.Componentes import (
    badge_estado,
    banner_modulo,
    barra_busqueda,
    boton,
    boton_exportacion,
    card,
    paginacion,
    sombra_suave,
    tabla,
    tarjeta_indicador,
)
from fuente.utilidades.ExportacionExcel import exportar_excel
from fuente.utilidades.ExportacionPDF import exportar_pdf, exportar_proforma_pdf
from fuente.utilidades.contenedores import menu_exportacion
from fuente.utilidades.feedback import mostrar_notificacion, validar_registros_exportacion


class PantallaCotizaciones(ft.Container):
    def __init__(
        self,
        main_page,
        servicio_cotizacion=None,
        servicio_buque=None,
        servicio_cliente=None,
        servicio_servicio=None,
    ):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
            padding=0,
        )
        self.main_page = main_page
        self.servicio_cotizacion = servicio_cotizacion
        self.servicio_buque = servicio_buque
        self.servicio_cliente = servicio_cliente
        self.servicio_servicio = servicio_servicio

        self.controlador = (
            ControladorCotizacion(
                servicio_cotizacion=servicio_cotizacion,
                servicio_buque=servicio_buque,
                servicio_cliente=servicio_cliente,
                servicio_servicio=servicio_servicio,
            )
            if servicio_cotizacion is not None
            else None
        )
        if self.controlador is not None:
            self.servicio_buque = self.controlador.servicio_buque
            self.servicio_cliente = self.controlador.servicio_cliente
            self.servicio_servicio = self.controlador.servicio_servicio

        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.busqueda = ""
        self.registros_actuales: list = []
        self.total_registros = 0
        self._menu_exportacion_abierto = False
        self._clic_en_boton_menu = False

        self.build_ui()

    def build_ui(self) -> None:
        self._cargar_registros()
        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding(14, 8, 14, 16),
                    content=ft.Column(
                        spacing=10,
                        controls=[
                            self._encabezado(),
                            self._tarjetas_resumen(),
                            self._barra_herramientas(),
                            self._panel_historial(),
                        ],
                    ),
                )
            ],
        )

    def _cargar_registros(self) -> None:
        if self.controlador is not None:
            try:
                registros, total = self.controlador.obtener_historial_cotizaciones(
                    pagina=self.pagina_actual,
                    limite=self.registros_por_pagina,
                    texto=self.busqueda,
                )
                self.registros_actuales = registros
                self.total_registros = total
                return
            except Exception as error:
                print(f"Advertencia al consultar cotizaciones en BD: {error}")

        self.registros_actuales = []
        self.total_registros = 0

    def actualizar_historial(self) -> None:
        self.build_ui()
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

    def _encabezado(self):
        return banner_modulo(
            src="fondo_puerto.jpg",
            categoria="Gestión de cotizaciones",
            titulo="Cotizaciones",
            descripcion="Consulta el historial y prepara nuevas cotizaciones (PDA) para tus clientes y buques.",
            icono=ft.Icons.REQUEST_QUOTE_OUTLINED,
        )

    def _tarjetas_resumen(self):
        total_cot = self.total_registros
        aprobadas = sum(
            1
            for c in self.registros_actuales
            if getattr(
                getattr(c, "estado", None),
                "value",
                str(getattr(c, "estado", "")),
            ).upper()
            in (
                EstadoCotizacion.PROFORMA.value,
                EstadoCotizacion.BORRADOR.value,
                EstadoCotizacion.ANTICIPO_RECIBIDO.value,
                EstadoCotizacion.EN_OPERACION.value,
            )
        )
        canceladas = sum(
            1
            for c in self.registros_actuales
            if getattr(
                getattr(c, "estado", None),
                "value",
                str(getattr(c, "estado", "")),
            ).upper()
            == EstadoCotizacion.CANCELADA.value
        )
        suma_total = sum(
            (
                Decimal(str(getattr(c, "total", "0.00") or "0.00"))
                for c in self.registros_actuales
            ),
            Decimal("0.00"),
        )
        moneda_obj = (
            getattr(self.registros_actuales[0], "moneda", None)
            if self.registros_actuales
            else None
        )
        moneda = getattr(moneda_obj, "value", "MXN")
        monto_texto = f"$ {suma_total:,.2f} {moneda}"
        etiqueta_origen = "Registros en base de datos"

        resumenes = (
            (
                "Cotizaciones totales",
                str(total_cot),
                etiqueta_origen,
                ft.Icons.DESCRIPTION_OUTLINED,
                COLOR_AZUL,
                "#EAF2FF",
                "#D7E6FF",
            ),
            (
                "Proformas activas",
                str(aprobadas),
                etiqueta_origen,
                ft.Icons.CHECK_CIRCLE_OUTLINED,
                COLOR_VERDE,
                "#EAF8F0",
                "#D5F0E2",
            ),
            (
                "Cotizaciones canceladas",
                str(canceladas),
                etiqueta_origen,
                ft.Icons.CANCEL_OUTLINED,
                COLOR_ROJO,
                "#FDECEE",
                "#F8D9DD",
            ),
            (
                "Monto total cotizado",
                monto_texto,
                etiqueta_origen,
                ft.Icons.PAYMENTS_OUTLINED,
                COLOR_NARANJA,
                "#FFF2E8",
                "#FFE1C9",
            ),
        )
        return ft.Row(
            spacing=10,
            controls=[
                ft.Container(
                    expand=True,
                    content=self._tarjeta_resumen(*resumen),
                )
                for resumen in resumenes
            ],
        )

    @staticmethod
    def _tarjeta_resumen(
        titulo,
        valor,
        descripcion,
        icono,
        color,
        fondo,
        borde,
    ):
        return tarjeta_indicador(
            titulo,
            valor,
            descripcion,
            icono,
            color,
            fondo,
            borde,
        )

    def _al_buscar(self, e) -> None:
        self.busqueda = (e.control.value or "").strip()
        self.pagina_actual = 1
        self.actualizar_historial()

    def _cambiar_pagina(self, pagina: int) -> None:
        self.pagina_actual = pagina
        self.actualizar_historial()

    def _barra_herramientas(self):
        buscador = barra_busqueda(
            hint="Buscar por folio, buque o cliente...",
            on_change=self._al_buscar,
            expand=True,
        )
        buscador.value = self.busqueda
        buscador.height = 42
        boton_filtros = boton(
            texto="Filtros",
            icono=ft.Icons.TUNE,
            tipo="secundario",
            width=160,
            height=42,
        )
        return card(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    buscador,
                    boton_filtros,
                    self._boton_nueva_cotizacion(),
                ],
            ),
            padding=10,
            radius=10,
            border_color="#E0ECF9",
            shadow=sombra_suave(),
        )

    def _panel_historial(self):
        self._texto_resumen_exportacion = ft.Text(
            "Proformas coincidentes con la búsqueda actual",
            size=11,
            color=COLOR_GRIS,
        )
        self._boton_exportar = boton_exportacion(
            texto="Exportar",
            on_click=self.alternar_menu_exportacion,
            width=120,
            height=42,
        )
        self._menu_exportacion = menu_exportacion(
            descripcion=self._texto_resumen_exportacion,
            on_pdf=self._exportar_cotizaciones_pdf,
            on_excel=self._exportar_cotizaciones_excel,
            descripcion_pdf="Genera un PDF con las proformas del historial.",
            descripcion_excel="Descarga las proformas del historial en Excel.",
            top=52,
            right=0,
            width=280,
        )
        self._menu_exportacion.visible = False

        cantidad_mostrada = len(self.registros_actuales)
        total_mostrar = self.total_registros
        subtitulo = "Proformas PDA registradas en la base de datos"

        return card(
            ft.Stack(
                expand=True,
                clip_behavior=ft.ClipBehavior.NONE,
                controls=[
                    ft.GestureDetector(
                        expand=True,
                        on_tap_down=self._clic_fondo_exportacion,
                        content=ft.Column(
                            expand=True,
                            spacing=10,
                            controls=[
                                ft.Row(
                                    spacing=10,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Container(
                                            width=42,
                                            height=42,
                                            alignment=ft.Alignment(0, 0),
                                            bgcolor="#FFF2E8",
                                            border_radius=11,
                                            content=ft.Icon(
                                                ft.Icons.LIST_ALT_OUTLINED,
                                                size=23,
                                                color=COLOR_NARANJA,
                                            ),
                                        ),
                                        ft.Column(
                                            spacing=2,
                                            controls=[
                                                ft.Text(
                                                    "Historial de cotizaciones",
                                                    size=19,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=COLOR_BANNER,
                                                ),
                                                ft.Text(
                                                    subtitulo,
                                                    size=12,
                                                    color=COLOR_GRIS,
                                                ),
                                            ],
                                        ),
                                        ft.Container(expand=True),
                                        ft.GestureDetector(
                                            on_tap_down=self._marcar_clic_en_boton_menu,
                                            on_tap_up=self._limpiar_clic_en_boton_menu,
                                            on_tap_cancel=self._limpiar_clic_en_boton_menu,
                                            content=self._boton_exportar,
                                        ),
                                    ],
                                ),
                                ft.Container(
                                    expand=True,
                                    border=ft.Border.all(1, "#E2EDF9"),
                                    border_radius=12,
                                    bgcolor=COLOR_BLANCO,
                                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                                    content=(
                                        self._tabla_historial()
                                        if self.registros_actuales
                                        else ft.Container(
                                            height=190,
                                            alignment=ft.Alignment(0, 0),
                                            content=ft.Column(
                                                alignment=ft.MainAxisAlignment.CENTER,
                                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                                spacing=8,
                                                controls=[
                                                    ft.Icon(
                                                        ft.Icons.REQUEST_QUOTE_OUTLINED,
                                                        size=42,
                                                        color=COLOR_GRIS,
                                                    ),
                                                    ft.Text(
                                                        "No hay cotizaciones registradas",
                                                        size=16,
                                                        weight=ft.FontWeight.W_600,
                                                        color=COLOR_BANNER,
                                                    ),
                                                    ft.Text(
                                                        "Las proformas guardadas aparecerán aquí.",
                                                        size=12,
                                                        color=COLOR_GRIS,
                                                    ),
                                                ],
                                            ),
                                        )
                                    ),
                                ),
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        ft.Text(
                                            f"Mostrando {cantidad_mostrada} de {total_mostrar} cotizaciones",
                                            size=12,
                                            color=COLOR_GRIS,
                                        ),
                                        paginacion(
                                            total_registros=max(1, total_mostrar),
                                            registros_por_pagina=self.registros_por_pagina,
                                            pagina_actual=self.pagina_actual,
                                            on_change=self._cambiar_pagina,
                                        ),
                                    ],
                                ),
                            ],
                        ),
                    ),
                    self._menu_exportacion,
                ],
            ),
            padding=14,
            border_color="#E1EAF4",
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    def alternar_menu_exportacion(self, e=None):
        self._clic_en_boton_menu = False
        self._menu_exportacion_abierto = not self._menu_exportacion_abierto
        self._menu_exportacion.visible = self._menu_exportacion_abierto
        self._menu_exportacion.update()

    def cerrar_menu_exportacion(self, e=None):
        if not self._menu_exportacion_abierto:
            return
        self._menu_exportacion_abierto = False
        self._menu_exportacion.visible = False
        self._menu_exportacion.update()

    def _marcar_clic_en_boton_menu(self, e=None):
        self._clic_en_boton_menu = True

    def _limpiar_clic_en_boton_menu(self, e=None):
        self._clic_en_boton_menu = False

    def _clic_fondo_exportacion(self, e=None):
        if not self._clic_en_boton_menu:
            self.cerrar_menu_exportacion()

    def _obtener_registros_exportacion(self) -> list[dict[str, str]]:
        if self.controlador is None:
            return []

        registros = []
        pagina = 1
        total = 0
        while pagina == 1 or len(registros) < total:
            lote, total = self.controlador.obtener_historial_cotizaciones(
                pagina=pagina,
                limite=100,
                texto=self.busqueda,
            )
            if not lote:
                break
            registros.extend(self._normalizar_fila_tabla(item) for item in lote)
            pagina += 1
        return registros

    @staticmethod
    def _columnas_exportacion() -> dict[str, str]:
        return {
            "Folio": "folio",
            "Fecha": "fecha",
            "Nombre del buque": "buque",
            "Cliente": "cliente",
            "Monto total": "monto",
            "Estado": "estado",
        }

    async def _exportar_cotizaciones_excel(self, e=None):
        self.cerrar_menu_exportacion()
        try:
            filas = self._obtener_registros_exportacion()
            if not validar_registros_exportacion(
                self.main_page, filas, "cotizaciones"
            ):
                return
            guardado = await exportar_excel(
                self.main_page,
                filas,
                self._columnas_exportacion(),
                "proformas.xlsx",
                nombre_hoja="Proformas",
            )
            if guardado:
                mostrar_notificacion(
                    self.main_page,
                    f"Se exportaron {len(filas)} proformas a Excel.",
                    COLOR_VERDE,
                )
        except Exception as error:
            mostrar_notificacion(
                self.main_page,
                f"No se pudieron exportar las proformas a Excel: {error}",
                COLOR_ROJO,
            )

    async def _exportar_cotizaciones_pdf(self, e=None):
        self.cerrar_menu_exportacion()
        try:
            filas = self._obtener_registros_exportacion()
            if not validar_registros_exportacion(
                self.main_page, filas, "cotizaciones"
            ):
                return
            guardado = await exportar_pdf(
                self.main_page,
                filas,
                self._columnas_exportacion(),
                "proformas.pdf",
                titulo="Historial de proformas",
                subtitulo="Gestión de cotizaciones PDA",
                etiqueta_registros=f"Proformas registradas: {len(filas)}",
                orientacion="landscape",
                nombre_registro="proformas",
            )
            if guardado:
                mostrar_notificacion(
                    self.main_page,
                    f"Se exportaron {len(filas)} proformas a PDF.",
                    COLOR_VERDE,
                )
        except Exception as error:
            mostrar_notificacion(
                self.main_page,
                f"No se pudieron exportar las proformas a PDF: {error}",
                COLOR_ROJO,
            )

    @staticmethod
    def _valor_enum(valor, predeterminado=""):
        return getattr(valor, "value", valor) or predeterminado

    @staticmethod
    def _formatear_fecha(valor):
        return valor.strftime("%d/%m/%Y") if hasattr(valor, "strftime") else "—"

    @staticmethod
    def _formatear_importe(valor, moneda):
        return f"$ {Decimal(str(valor or '0.00')):,.2f} {moneda}"

    def _campo_detalle(self, etiqueta, valor):
        return ft.Container(
            width=210,
            padding=10,
            bgcolor=COLOR_BLANCO,
            border=ft.Border.all(1, "#E4ECF5"),
            border_radius=9,
            content=ft.Column(
                spacing=3,
                controls=[
                    ft.Text(
                        etiqueta,
                        size=10,
                        color=COLOR_GRIS,
                        weight=ft.FontWeight.W_600,
                    ),
                    ft.Text(
                        str(valor or "—"),
                        size=12,
                        color=COLOR_BANNER,
                        weight=ft.FontWeight.W_600,
                        selectable=True,
                    ),
                ],
            ),
        )

    def _tarjeta_detalle_proforma(self, cotizacion):
        cliente = getattr(cotizacion, "cliente", None)
        buque = getattr(cotizacion, "buque", None)
        categoria_buque = getattr(buque, "categoria_buque", None)
        moneda = self._valor_enum(getattr(cotizacion, "moneda", None), "MXN")
        filas_detalle = []
        for indice, detalle in enumerate(
            getattr(cotizacion, "detalles", None) or [], start=1
        ):
            concepto = getattr(detalle, "concepto", None)
            categoria = getattr(
                getattr(concepto, "categoria_pda", None), "nombre", "—"
            )
            proveedores = getattr(concepto, "proveedores", None) or []
            proveedor = ", ".join(
                p.nombre for p in proveedores if getattr(p, "nombre", None)
            ) or "—"
            descripcion = getattr(concepto, "nombre_es", None) or (
                f"Concepto #{getattr(detalle, 'concepto_id', '')}"
            )
            filas_detalle.append(
                ft.Container(
                    padding=12,
                    border=ft.Border.all(1, "#E1EAF4"),
                    border_radius=10,
                    bgcolor=COLOR_BLANCO,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Row(
                                spacing=10,
                                controls=[
                                    ft.Container(
                                        width=27,
                                        height=27,
                                        alignment=ft.Alignment(0, 0),
                                        bgcolor="#FFF2E8",
                                        border_radius=7,
                                        content=ft.Text(
                                            str(indice),
                                            size=12,
                                            weight=ft.FontWeight.BOLD,
                                            color=COLOR_NARANJA,
                                        ),
                                    ),
                                    ft.Column(
                                        expand=True,
                                        spacing=2,
                                        controls=[
                                            ft.Text(
                                                descripcion,
                                                size=13,
                                                weight=ft.FontWeight.BOLD,
                                                color=COLOR_BANNER,
                                            ),
                                            ft.Text(
                                                f"{categoria} · {proveedor}",
                                                size=10,
                                                color=COLOR_GRIS,
                                            ),
                                        ],
                                    ),
                                    ft.Text(
                                        self._formatear_importe(
                                            getattr(detalle, "total", 0), moneda
                                        ),
                                        size=13,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_AZUL,
                                    ),
                                ],
                            ),
                            ft.Row(
                                wrap=True,
                                spacing=8,
                                controls=[
                                    self._campo_detalle(
                                        "Cantidad",
                                        getattr(detalle, "cantidad", "—"),
                                    ),
                                    self._campo_detalle(
                                        "Precio unitario",
                                        self._formatear_importe(
                                            getattr(detalle, "precio_unitario", 0),
                                            moneda,
                                        ),
                                    ),
                                    self._campo_detalle(
                                        "Subtotal",
                                        self._formatear_importe(
                                            getattr(detalle, "subtotal", 0), moneda
                                        ),
                                    ),
                                    self._campo_detalle(
                                        "IVA / TAX",
                                        self._formatear_importe(
                                            getattr(detalle, "iva", 0), moneda
                                        ),
                                    ),
                                    self._campo_detalle(
                                        "Factura / Invoice",
                                        getattr(detalle, "factura", None),
                                    ),
                                    self._campo_detalle(
                                        "Observaciones / Observations",
                                        getattr(detalle, "observaciones", None),
                                    ),
                                ],
                            ),
                        ],
                    ),
                )
            )

        fecha_creacion = getattr(cotizacion, "creado_en", None)
        fecha = self._formatear_fecha(fecha_creacion or cotizacion.fecha_arribo)
        direccion = getattr(cliente, "direccion", None)
        tipo_buque = getattr(categoria_buque, "categoria", "—")
        subtipo = getattr(buque, "subtipo_descripcion", None)
        if subtipo:
            tipo_buque = f"{tipo_buque} · {subtipo}"
        return ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=560,
            spacing=12,
            controls=[
                ft.Row(
                    wrap=True,
                    spacing=10,
                    controls=[
                        self._campo_detalle(
                            "Cliente / Customer",
                            getattr(cliente, "razon_social", None),
                        ),
                        self._campo_detalle(
                            "Dirección / Address",
                            direccion,
                        ),
                        self._campo_detalle(
                            "Fecha / Date",
                            fecha,
                        ),
                        self._campo_detalle(
                            "Arribo / ETA",
                            self._formatear_fecha(
                                getattr(cotizacion, "fecha_arribo", None)
                            ),
                        ),
                        self._campo_detalle(
                            "Zarpe / ETD",
                            self._formatear_fecha(
                                getattr(cotizacion, "fecha_zarpe", None)
                            ),
                        ),
                    ],
                ),
                ft.Container(
                    padding=12,
                    bgcolor="#F4F8FC",
                    border=ft.Border.all(1, "#E1EAF4"),
                    border_radius=10,
                    content=ft.Column(
                        spacing=8,
                        controls=[
                            ft.Text(
                                "Información del buque / Vessel's Information",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Row(
                                wrap=True,
                                spacing=8,
                                controls=[
                                    self._campo_detalle(
                                        "Buque / Vessel",
                                        getattr(buque, "nombre", None),
                                    ),
                                    self._campo_detalle(
                                        "Tipo de buque / Type of vessel",
                                        tipo_buque,
                                    ),
                                    self._campo_detalle(
                                        "IMO",
                                        getattr(buque, "numero_imo", None),
                                    ),
                                    self._campo_detalle(
                                        "UAB / GRT",
                                        getattr(buque, "trb", None),
                                    ),
                                    self._campo_detalle(
                                        "Eslora / LOA (m)",
                                        getattr(buque, "eslora", None),
                                    ),
                                    self._campo_detalle(
                                        "Calado / Draft (m)",
                                        getattr(buque, "calado", None),
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
                ft.Text(
                    "Servicios y conceptos / Services and items",
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_BANNER,
                ),
                *filas_detalle,
                ft.Row(
                    alignment=ft.MainAxisAlignment.END,
                    controls=[
                        self._campo_detalle(
                            "Subtotal",
                            self._formatear_importe(
                                getattr(cotizacion, "subtotal", 0), moneda
                            ),
                        ),
                        self._campo_detalle(
                            "IVA / TAX",
                            self._formatear_importe(
                                getattr(cotizacion, "iva", 0), moneda
                            ),
                        ),
                        self._campo_detalle(
                            "Total / Total",
                            self._formatear_importe(
                                getattr(cotizacion, "total", 0), moneda
                            ),
                        ),
                        self._campo_detalle(
                            "Estado / Status",
                            self._valor_enum(
                                getattr(cotizacion, "estado", None)
                            ),
                        ),
                    ],
                ),
            ],
        )

    def ver_cotizacion(self, cotizacion):
        if isinstance(cotizacion, dict):
            mostrar_notificacion(
                self.main_page,
                "El detalle solo está disponible para proformas guardadas en la base de datos.",
                COLOR_ROJO,
            )
            return

        async def descargar(e=None):
            await self._descargar_proforma(cotizacion)

        self.dialogo_cotizacion = ft.AlertDialog(
            modal=True,
            bgcolor="#F4F8FC",
            shape=ft.RoundedRectangleBorder(radius=16),
            title=ft.Row(
                spacing=10,
                controls=[
                    ft.Icon(
                        ft.Icons.REQUEST_QUOTE_OUTLINED,
                        color=COLOR_NARANJA,
                    ),
                    ft.Column(
                        spacing=1,
                        controls=[
                            ft.Text(
                                "Proforma",
                                size=19,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Text(
                                getattr(cotizacion, "folio", ""),
                                size=12,
                                color=COLOR_GRIS,
                            ),
                        ],
                    ),
                ],
            ),
            content=ft.Container(
                width=1050,
                height=590,
                content=self._tarjeta_detalle_proforma(cotizacion),
            ),
            actions=[
                boton(
                    texto="Cerrar",
                    tipo="secundario",
                    on_click=lambda e: self.main_page.pop_dialog(),
                ),
                boton(
                    texto="Descargar proforma",
                    icono=ft.Icons.DOWNLOAD_OUTLINED,
                    tipo="principal",
                    on_click=descargar,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.main_page.show_dialog(self.dialogo_cotizacion)

    async def _descargar_proforma(self, cotizacion):
        try:
            guardado = await exportar_proforma_pdf(
                self.main_page,
                cotizacion,
            )
            if guardado:
                mostrar_notificacion(
                    self.main_page,
                    f"Se descargó la proforma {cotizacion.folio}.",
                    COLOR_VERDE,
                )
        except Exception as error:
            mostrar_notificacion(
                self.main_page,
                f"No se pudo descargar la proforma: {error}",
                COLOR_ROJO,
            )

    def _boton_nueva_cotizacion(self):
        return boton(
            texto="Nueva cotización",
            icono=ft.Icons.ADD,
            tipo="principal",
            height=42,
            on_click=lambda e: self.abrir_nueva_cotizacion(),
        )

    def _normalizar_fila_tabla(self, item) -> dict[str, str]:
        if isinstance(item, dict):
            return item
        fecha_obj = getattr(item, "creado_en", None) or getattr(
            item, "fecha_arribo", None
        )
        fecha_str = (
            fecha_obj.strftime("%d/%m/%Y")
            if hasattr(fecha_obj, "strftime")
            else str(fecha_obj or "")
        )
        buque_obj = getattr(item, "buque", None)
        buque_nombre = (
            getattr(buque_obj, "nombre", None)
            or f"Buque #{getattr(item, 'buque_id', '')}"
        )
        cliente_obj = getattr(item, "cliente", None)
        cliente_nombre = (
            getattr(cliente_obj, "razon_social", None)
            or f"Cliente #{getattr(item, 'cliente_id', '')}"
        )
        total_val = Decimal(str(getattr(item, "total", "0.00") or "0.00"))
        moneda_obj = getattr(item, "moneda", "MXN")
        moneda_str = getattr(moneda_obj, "value", str(moneda_obj or "MXN"))
        estado_obj = getattr(item, "estado", "PENDIENTE")
        estado_str = getattr(estado_obj, "value", str(estado_obj or "PENDIENTE"))

        return {
            "folio": getattr(item, "folio", ""),
            "fecha": fecha_str,
            "buque": buque_nombre,
            "cliente": cliente_nombre,
            "monto": f"$ {total_val:,.2f} {moneda_str}",
            "estado": estado_str,
        }

    def _tabla_historial(self):
        origen = self.registros_actuales
        filas = []
        for registro in origen:
            cotizacion = self._normalizar_fila_tabla(registro)
            filas.append(
                ftd.DataRow2(
                    cells=[
                        ft.DataCell(
                            ft.Text(
                                cotizacion["folio"],
                                size=13,
                                color=COLOR_AZUL,
                                weight=ft.FontWeight.W_600,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(cotizacion["fecha"], size=13, color=COLOR_GRIS)
                        ),
                        ft.DataCell(
                            ft.Text(
                                cotizacion["buque"],
                                size=13,
                                color=COLOR_BANNER,
                                weight=ft.FontWeight.W_600,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                cotizacion["cliente"],
                                size=13,
                                color=COLOR_GRIS,
                            )
                        ),
                        ft.DataCell(
                            ft.Text(
                                cotizacion["monto"],
                                size=13,
                                color=COLOR_BANNER,
                                weight=ft.FontWeight.BOLD,
                            )
                        ),
                        ft.DataCell(
                            badge_estado(
                                cotizacion["estado"],
                                self._estado_visual(cotizacion["estado"]),
                            )
                        ),
                        ft.DataCell(self._acciones_fila(registro)),
                    ],
                )
            )

        return tabla(
            columnas=[
                ("Folio", 155),
                ("Fecha", 110),
                ("Nombre del buque", 175),
                ("Cliente", 190),
                ("Monto total", 170),
                ("Estado", 125),
                ("Acciones", 58),
            ],
            filas=filas,
            column_spacing=6,
            horizontal_margin=8,
            heading_row_height=46,
            data_row_min_height=58,
            data_row_max_height=64,
            columnas_flexibles=True,
            heading_row_color="#EEF5FD",
            heading_text_size=14,
            heading_text_color=COLOR_NEGRO,
            vertical_lines=True,
            horizontal_lines=True,
            border_color="#E3EAF2",
            columnas_compactas=True,
        )

    @staticmethod
    def _estado_visual(estado):
        return {
            "Pendiente": "pendiente",
            "PENDIENTE": "pendiente",
            "BORRADOR": "pendiente",
            "PROFORMA": "activo",
            "APROBADA": "activo",
            "Aprobada": "activo",
            "RECHAZADA": "inactivo",
            "Rechazada": "inactivo",
            "Cancelada": "inactivo",
            "CANCELADA": "inactivo",
        }.get(str(estado), "info")

    def _acciones_fila(self, cotizacion):
        return boton(
            icono=ft.Icons.VISIBILITY_OUTLINED,
            texto="Ver cotización",
            tipo="accion",
            tooltip="Ver proforma",
            on_click=lambda e: self.ver_cotizacion(cotizacion),
        )

    def abrir_nueva_cotizacion(self):
        nueva_vista = PantallaNuevaCotizacion(
            self.main_page,
            vista_anterior=self,
            servicio_cotizacion=self.servicio_cotizacion,
            servicio_buque=self.servicio_buque,
            servicio_cliente=self.servicio_cliente,
            servicio_servicio=self.servicio_servicio,
            controlador=self.controlador,
        )
        if self.parent is not None:
            self.parent.content = nueva_vista
            self.parent.update()
        return nueva_vista
