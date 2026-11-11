from __future__ import annotations

import asyncio
from datetime import datetime, time
from decimal import Decimal
import flet as ft
import flet_datatable2 as ftd

from fuente.negocio.controlador.ControladorCotizacion import ControladorCotizacion
from fuente.negocio.modelo.ENUMs import EstadoCotizacion, Moneda
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
    agregar_panel_flotante,
    crear_mensaje_validacion,
    limpiar_error_campo,
    paginacion,
    panel_filtros,
    quitar_panel_flotante,
    seccion_opciones_filtro,
    sombra_suave,
    tabla,
    tarjeta_indicador,
    validar_campo,
    validar_rango_fechas,
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
        self.cotizaciones_seleccionadas = {}
        self._checkboxes_seleccion_cotizaciones = {}
        self._filas_seleccion_cotizaciones = {}
        self._claves_cotizaciones_pagina = []
        self._tarea_busqueda = None
        self._texto_busqueda_pendiente = ""
        self.filtros_seleccionados = {
            "estados": set(),
            "monedas": set(),
            "fecha_desde": None,
            "fecha_hasta": None,
        }
        self.cotizaciones_seleccionadas.clear()
        self._checks_filtros = {}
        self._panel_filtros_abierto = False
        self._clic_en_boton_filtros = False
        self._menu_exportacion_abierto = False
        self._clic_en_boton_menu = False

        self.build_ui()

    def build_ui(self) -> None:
        self._cargar_registros()
        contenido_principal = ft.Column(
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
                            self._contenedor_tarjetas_resumen(),
                            self._barra_herramientas(),
                            self._panel_historial(),
                        ],
                    ),
                )
            ],
        )
        self._layout_principal = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[
                ft.GestureDetector(
                    expand=True,
                    on_tap_down=self._clic_fondo_filtros,
                    content=contenido_principal,
                )
            ],
        )
        self.content = self._layout_principal

    def _cargar_registros(self) -> None:
        if self.controlador is not None:
            try:
                registros, total = self.controlador.obtener_historial_cotizaciones(
                    pagina=self.pagina_actual,
                    limite=self.registros_por_pagina,
                    filtros=self._filtros_repositorio(),
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
        self._cargar_registros()
        self._contenido_tarjetas_resumen.content = self._tarjetas_resumen()
        self._contenedor_tabla_historial.content = self._contenido_tabla_historial()
        self._texto_total_historial.value = (
            f"Mostrando {len(self.registros_actuales)} de "
            f"{self.total_registros} cotizaciones"
        )
        self._contenedor_paginacion_historial.content = paginacion(
            total_registros=max(1, self.total_registros),
            registros_por_pagina=self.registros_por_pagina,
            pagina_actual=self.pagina_actual,
            on_change=self._cambiar_pagina,
        )
        self._actualizar_descripcion_exportacion()
        if hasattr(self, "_boton_exportar"):
            self._boton_exportar.update()
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

    def _contenedor_tarjetas_resumen(self):
        self._contenido_tarjetas_resumen = ft.Container(
            content=self._tarjetas_resumen()
        )
        return self._contenido_tarjetas_resumen

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
        self.cerrar_filtros()
        texto = (e.control.value or "").strip()
        self._texto_busqueda_pendiente = texto
        if self._tarea_busqueda is not None:
            self._tarea_busqueda.cancel()
            self._tarea_busqueda = None

        if len(texto) < 3:
            if self.busqueda:
                self.busqueda = ""
                self.cotizaciones_seleccionadas.clear()
                self.pagina_actual = 1
                self.actualizar_historial()
            return

        if self.main_page is None:
            self._aplicar_busqueda(texto)
            return
        self._tarea_busqueda = self.main_page.run_task(
            self._buscar_con_demora,
            texto,
        )

    async def _buscar_con_demora(self, texto):
        await asyncio.sleep(0.2)
        if texto != self._texto_busqueda_pendiente:
            return
        self._tarea_busqueda = None
        self._aplicar_busqueda(texto)

    def _aplicar_busqueda(self, texto):
        self.busqueda = texto
        self.pagina_actual = 1
        self.cotizaciones_seleccionadas.clear()
        self.actualizar_historial()

    def _cambiar_pagina(self, pagina: int) -> None:
        self.pagina_actual = pagina
        self.actualizar_historial()

    def _filtros_repositorio(self):
        filtros = {
            "estados": self.filtros_seleccionados["estados"],
            "monedas": self.filtros_seleccionados["monedas"],
        }
        for clave in ("fecha_desde", "fecha_hasta"):
            valor = self.filtros_seleccionados[clave]
            if valor:
                fecha = datetime.strptime(valor, "%d/%m/%Y").date()
                filtros[clave] = (
                    datetime.combine(fecha, time.min)
                    if clave == "fecha_desde"
                    else datetime.combine(fecha, time.max)
                )
        return filtros

    def abrir_filtros(self, e=None):
        if self._panel_filtros_abierto:
            self.cerrar_filtros()
            return
        self.cerrar_menu_exportacion()
        self._checks_filtros = {}
        self._campo_fecha_desde = self._crear_campo_fecha_filtro("fecha_desde")
        self._campo_fecha_hasta = self._crear_campo_fecha_filtro("fecha_hasta")
        self._errores_fecha_filtro = {
            "fecha_desde": crear_mensaje_validacion(),
            "fecha_hasta": crear_mensaje_validacion(),
        }
        self._marcos_fecha_filtro = {}
        self._date_picker_filtros = ft.DatePicker(
            on_change=self._fecha_seleccionada,
            first_date=datetime(1900, 1, 1),
            last_date=datetime(2099, 12, 31),
            help_text="Selecciona una fecha de arribo",
            cancel_text="Cancelar",
            confirm_text="Seleccionar",
        )
        secciones = [
            self._seccion_filtro(
                "Estado de la cotización",
                [
                    (estado.value, self._etiqueta_estado(estado))
                    for estado in (
                        EstadoCotizacion.BORRADOR,
                        EstadoCotizacion.PROFORMA,
                        EstadoCotizacion.ANTICIPO_RECIBIDO,
                        EstadoCotizacion.EN_OPERACION,
                        EstadoCotizacion.LIQUIDADA_FDA,
                        EstadoCotizacion.CANCELADA,
                    )
                ],
                "estados",
                ft.Icons.CHECK_CIRCLE_OUTLINED,
            ),
            ft.Divider(height=1, color="#E2EDF9"),
            self._seccion_filtro(
                "Moneda",
                [(moneda.value, moneda.value) for moneda in Moneda],
                "monedas",
                ft.Icons.PAYMENTS_OUTLINED,
            ),
            ft.Divider(height=1, color="#E2EDF9"),
            self._seccion_fechas_filtro(),
        ]
        self._panel_filtros, self._texto_resumen_filtros = panel_filtros(
            titulo="Filtrar cotizaciones",
            secciones=secciones,
            resumen=self._resumen_filtros(),
            on_limpiar=self.limpiar_filtros,
            on_aplicar=self.aplicar_filtros,
            on_cerrar=self.cerrar_filtros,
            top=210,
            right=155,
            width=360,
            height=500,
        )
        agregar_panel_flotante(self._layout_principal, self._panel_filtros)
        self._panel_filtros_abierto = True
        self.update()

    @staticmethod
    def _etiqueta_estado(estado):
        return {
            EstadoCotizacion.BORRADOR: "Borrador",
            EstadoCotizacion.PROFORMA: "Proforma",
            EstadoCotizacion.ANTICIPO_RECIBIDO: "Anticipo recibido",
            EstadoCotizacion.EN_OPERACION: "En operación",
            EstadoCotizacion.LIQUIDADA_FDA: "Liquidada FDA",
            EstadoCotizacion.CANCELADA: "Cancelada",
        }[estado]

    def _seccion_filtro(self, titulo, opciones, clave, icono):
        seccion, checkboxes = seccion_opciones_filtro(
            titulo,
            opciones,
            self.filtros_seleccionados[clave],
            self._cambio_checkbox_filtro,
            icono=icono,
        )
        self._checks_filtros.update(
            {(clave, valor): checkbox for valor, checkbox in checkboxes.items()}
        )
        return seccion

    def _crear_campo_fecha_filtro(self, clave):
        return ft.TextField(
            value=self.filtros_seleccionados[clave] or "",
            hint_text="dd/mm/aaaa",
            height=38,
            text_size=13,
            content_padding=ft.Padding(9, 0, 4, 8),
            border=ft.InputBorder.NONE,
            border_color="#C9DDF7",
            focused_border_color=COLOR_AZUL,
            border_radius=8,
            keyboard_type=ft.KeyboardType.DATETIME,
            on_change=self._cambio_fecha_filtro,
            on_blur=self._salir_campo_fecha_filtro,
        )

    def _seccion_fechas_filtro(self):
        return ft.Container(
            padding=ft.Padding(14, 8, 14, 12),
            content=ft.Column(
                spacing=6,
                controls=[
                    ft.Row(
                        spacing=7,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.CALENDAR_MONTH_OUTLINED,
                                size=16,
                                color=COLOR_BANNER,
                            ),
                            ft.Text(
                                "Fecha de arribo",
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=8,
                        controls=[
                            self._columna_campo_fecha("Desde", "fecha_desde"),
                            self._columna_campo_fecha("Hasta", "fecha_hasta"),
                        ],
                    ),
                ],
            ),
        )

    def _columna_campo_fecha(self, etiqueta, clave):
        campo = (
            self._campo_fecha_desde
            if clave == "fecha_desde"
            else self._campo_fecha_hasta
        )
        marco = ft.Container(
            height=42,
            padding=ft.Padding(4, 1, 4, 1),
            border=ft.Border.all(1, "#C9DDF7"),
            border_radius=8,
            content=ft.Row(
                spacing=2,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(expand=True, content=campo),
                    ft.IconButton(
                        icon=ft.Icons.CALENDAR_MONTH_OUTLINED,
                        icon_size=16,
                        icon_color=COLOR_AZUL,
                        tooltip="Seleccionar fecha",
                        on_click=lambda e, k=clave: self._abrir_calendario_filtro(k),
                        width=34,
                        height=34,
                        padding=0,
                    ),
                ],
            ),
        )
        self._marcos_fecha_filtro[clave] = marco
        return ft.Column(
            expand=True,
            spacing=3,
            controls=[
                ft.Text(etiqueta, size=11, color=COLOR_GRIS),
                marco,
                self._errores_fecha_filtro[clave],
            ],
        )

    def _abrir_calendario_filtro(self, clave):
        self._campo_fecha_filtro_activo = (
            self._campo_fecha_desde
            if clave == "fecha_desde"
            else self._campo_fecha_hasta
        )
        valor = self._campo_fecha_filtro_activo.value
        try:
            self._date_picker_filtros.value = (
                datetime.strptime(valor, "%d/%m/%Y") if valor else None
            )
        except ValueError:
            self._date_picker_filtros.value = None
        if self._date_picker_filtros not in self.main_page.overlay:
            self.main_page.overlay.append(self._date_picker_filtros)
        self._date_picker_filtros.open = True
        self.main_page.update()

    def _fecha_seleccionada(self, e):
        if self._date_picker_filtros.value and self._campo_fecha_filtro_activo:
            self._campo_fecha_filtro_activo.value = (
                self._date_picker_filtros.value.strftime("%d/%m/%Y")
            )
            self._campo_fecha_filtro_activo.update()
            self._validar_fechas_filtro()
            self._actualizar_resumen_filtros()
            self._panel_filtros.update()

    def _cambio_checkbox_filtro(self, e=None):
        self._actualizar_resumen_filtros()

    def _cambio_fecha_filtro(self, e=None):
        for clave, campo in (
            ("fecha_desde", self._campo_fecha_desde),
            ("fecha_hasta", self._campo_fecha_hasta),
        ):
            limpiar_error_campo(
                campo,
                self._errores_fecha_filtro[clave],
                marco=self._marcos_fecha_filtro[clave],
            )
        self._actualizar_resumen_filtros()
        self._panel_filtros.update()

    def _salir_campo_fecha_filtro(self, e=None):
        self._validar_fechas_filtro()
        self._panel_filtros.update()

    def _validar_fechas_filtro(self):
        errores = validar_rango_fechas(
            self._campo_fecha_desde.value,
            self._campo_fecha_hasta.value,
            fecha_actual=datetime(2099, 12, 31).date(),
        )
        valido = True
        for clave, campo in (
            ("fecha_desde", self._campo_fecha_desde),
            ("fecha_hasta", self._campo_fecha_hasta),
        ):
            valido = validar_campo(
                campo,
                self._errores_fecha_filtro[clave],
                lambda valor, error=errores[clave]: error,
                marco=self._marcos_fecha_filtro[clave],
            ) and valido
        return valido

    def _resumen_filtros(self):
        cantidad = self._contar_filtros()
        return (
            "Sin filtros seleccionados"
            if cantidad == 0
            else "1 filtro seleccionado"
            if cantidad == 1
            else f"{cantidad} filtros seleccionados"
        )

    def _contar_filtros(self):
        return (
            sum(len(self.filtros_seleccionados[clave]) for clave in ("estados", "monedas"))
            + int(bool(self.filtros_seleccionados["fecha_desde"]))
            + int(bool(self.filtros_seleccionados["fecha_hasta"]))
        )

    def _actualizar_indicador_filtros(self):
        cantidad = self._contar_filtros()
        controles = [
            ft.Icon(ft.Icons.TUNE, size=18, color=COLOR_AZUL),
            ft.Text("Filtros", size=14, color=COLOR_AZUL, max_lines=1),
        ]
        if cantidad:
            controles.append(
                ft.Container(
                    width=20,
                    height=20,
                    alignment=ft.Alignment(0, 0),
                    bgcolor="#E8F2FF",
                    border_radius=10,
                    content=ft.Text(
                        str(cantidad),
                        size=11,
                        color=COLOR_AZUL,
                        weight=ft.FontWeight.BOLD,
                    ),
                )
            )
        self._boton_filtros.content = ft.Row(
            tight=True,
            spacing=7,
            alignment=ft.MainAxisAlignment.CENTER,
            controls=controles,
        )

    def _actualizar_resumen_filtros(self):
        cantidad = sum(
            bool(checkbox.value) for checkbox in self._checks_filtros.values()
        )
        cantidad += int(bool(self._campo_fecha_desde.value))
        cantidad += int(bool(self._campo_fecha_hasta.value))
        self._texto_resumen_filtros.value = (
            "Sin filtros seleccionados"
            if cantidad == 0
            else "1 filtro seleccionado"
            if cantidad == 1
            else f"{cantidad} filtros seleccionados"
        )
        self._texto_resumen_filtros.update()

    def limpiar_filtros(self, e=None):
        for checkbox in self._checks_filtros.values():
            checkbox.value = False
        self._campo_fecha_desde.value = ""
        self._campo_fecha_hasta.value = ""
        self.filtros_seleccionados = {
            "estados": set(),
            "monedas": set(),
            "fecha_desde": None,
            "fecha_hasta": None,
        }
        self.cotizaciones_seleccionadas.clear()
        self._validar_fechas_filtro()
        self._actualizar_resumen_filtros()
        self._actualizar_indicador_filtros()
        self.pagina_actual = 1
        self.cerrar_filtros()
        self.actualizar_historial()

    def aplicar_filtros(self, e=None):
        if not self._validar_fechas_filtro():
            self._panel_filtros.update()
            return
        filtros = {
            "estados": set(),
            "monedas": set(),
            "fecha_desde": (self._campo_fecha_desde.value or "").strip() or None,
            "fecha_hasta": (self._campo_fecha_hasta.value or "").strip() or None,
        }
        for (grupo, valor), checkbox in self._checks_filtros.items():
            if checkbox.value:
                filtros[grupo].add(valor)
        self.filtros_seleccionados = filtros
        self.cotizaciones_seleccionadas.clear()
        self._actualizar_indicador_filtros()
        self.pagina_actual = 1
        self.cerrar_filtros()
        self.actualizar_historial()

    def cerrar_filtros(self, e=None):
        if self._panel_filtros_abierto:
            quitar_panel_flotante(self._layout_principal, self._panel_filtros)
            self._panel_filtros_abierto = False
            self.update()

    def _marcar_clic_en_boton_filtros(self, e=None):
        self._clic_en_boton_filtros = True

    def _limpiar_clic_en_boton_filtros(self, e=None):
        self._clic_en_boton_filtros = False

    def _clic_fondo_filtros(self, e=None):
        if self._clic_en_boton_filtros:
            self._clic_en_boton_filtros = False
            return
        self.cerrar_filtros()

    def _barra_herramientas(self):
        buscador = barra_busqueda(
            hint="Buscar por folio, buque o cliente...",
            on_change=self._al_buscar,
            expand=True,
        )
        self._campo_busqueda = buscador
        buscador.value = self.busqueda
        buscador.height = 42
        self._boton_filtros = boton(
            texto="Filtros",
            icono=ft.Icons.TUNE,
            tipo="secundario",
            width=160,
            height=42,
            on_click=self.abrir_filtros,
        )
        self._actualizar_indicador_filtros()
        return card(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    buscador,
                    ft.GestureDetector(
                        on_tap_down=self._marcar_clic_en_boton_filtros,
                        on_tap_up=self._limpiar_clic_en_boton_filtros,
                        on_tap_cancel=self._limpiar_clic_en_boton_filtros,
                        content=self._boton_filtros,
                    ),
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
            self._descripcion_exportacion(),
            size=11,
            color=COLOR_GRIS,
        )
        self._texto_boton_exportar = ft.Text(
            self._etiqueta_boton_exportar(),
            size=14,
            color=COLOR_AZUL,
        )
        self._boton_exportar = boton_exportacion(
            texto=self._texto_boton_exportar,
            on_click=self.alternar_menu_exportacion,
            width=(
                230
                if self.cotizaciones_seleccionadas
                else 190
                if self._hay_filtros_exportacion()
                else 150
            ),
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

        subtitulo = "Proformas PDA registradas en la base de datos"
        self._contenedor_tabla_historial = ft.Container(
            expand=True,
            border=ft.Border.all(1, "#E2EDF9"),
            border_radius=12,
            bgcolor=COLOR_BLANCO,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=self._contenido_tabla_historial(),
        )
        self._texto_total_historial = ft.Text(
            f"Mostrando {len(self.registros_actuales)} de "
            f"{self.total_registros} cotizaciones",
            size=12,
            color=COLOR_GRIS,
        )
        self._contenedor_paginacion_historial = ft.Container(
            content=paginacion(
                total_registros=max(1, self.total_registros),
                registros_por_pagina=self.registros_por_pagina,
                pagina_actual=self.pagina_actual,
                on_change=self._cambiar_pagina,
            )
        )

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
                                self._contenedor_tabla_historial,
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                    controls=[
                                        self._texto_total_historial,
                                        self._contenedor_paginacion_historial,
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
        self._actualizar_descripcion_exportacion()
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

        if self.cotizaciones_seleccionadas:
            return [
                self._normalizar_fila_tabla(item)
                for item in self.cotizaciones_seleccionadas.values()
            ]

        registros = []
        pagina = 1
        total = 0
        while pagina == 1 or len(registros) < total:
            lote, total = self.controlador.obtener_historial_cotizaciones(
                pagina=pagina,
                limite=100,
                filtros=self._filtros_repositorio(),
                texto=self.busqueda,
            )
            if not lote:
                break
            registros.extend(self._normalizar_fila_tabla(item) for item in lote)
            pagina += 1
        return registros

    def _hay_filtros_exportacion(self):
        return bool(self.busqueda.strip() or self._contar_filtros())

    def _etiqueta_boton_exportar(self):
        if self.cotizaciones_seleccionadas:
            return f"Exportar seleccionados ({len(self.cotizaciones_seleccionadas)})"
        if self._hay_filtros_exportacion():
            return "Exportar filtrados"
        return "Exportar"

    def _descripcion_exportacion(self):
        if self.cotizaciones_seleccionadas:
            return "Elige un formato para exportar las proformas seleccionadas."
        if self._hay_filtros_exportacion():
            return "Elige un formato para exportar las proformas filtradas."
        return "Elige un formato para exportar todas las proformas."

    def _nombre_archivo_exportacion(self, extension):
        sufijo = (
            "_seleccionadas"
            if self.cotizaciones_seleccionadas
            else "_filtradas"
            if self._hay_filtros_exportacion()
            else ""
        )
        return f"proformas{sufijo}.{extension}"

    def _etiqueta_registros_exportacion(self, cantidad):
        etiqueta = (
            "Proformas seleccionadas"
            if self.cotizaciones_seleccionadas
            else "Proformas filtradas"
            if self._hay_filtros_exportacion()
            else "Proformas registradas"
        )
        return f"{etiqueta}: {cantidad}"

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
                self._nombre_archivo_exportacion("xlsx"),
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
                self._nombre_archivo_exportacion("pdf"),
                titulo="Historial de proformas",
                subtitulo="Gestión de cotizaciones PDA",
                etiqueta_registros=self._etiqueta_registros_exportacion(
                    len(filas)
                ),
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

    @staticmethod
    def _clave_cotizacion(cotizacion):
        if isinstance(cotizacion, dict):
            return cotizacion.get("id") or cotizacion.get("folio")
        return getattr(cotizacion, "id", None) or getattr(
            cotizacion, "folio", id(cotizacion)
        )

    def _contenido_tabla_historial(self):
        if self.registros_actuales:
            return self._tabla_historial()
        con_filtros = bool(self.busqueda) or bool(self._contar_filtros())
        return ft.Container(
            height=190,
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
                controls=[
                    ft.Icon(
                        ft.Icons.SEARCH_OFF
                        if con_filtros
                        else ft.Icons.REQUEST_QUOTE_OUTLINED,
                        size=42,
                        color=COLOR_GRIS,
                    ),
                    ft.Text(
                        "No se encontraron cotizaciones"
                        if con_filtros
                        else "No hay cotizaciones registradas",
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=COLOR_BANNER,
                    ),
                    ft.Text(
                        "Ajusta los filtros o la búsqueda e inténtalo de nuevo."
                        if con_filtros
                        else "Las proformas guardadas aparecerán aquí.",
                        size=12,
                        color=COLOR_GRIS,
                    ),
                ],
            ),
        )

    def _tabla_historial(self):
        origen = self.registros_actuales
        filas = []
        claves_pagina = [self._clave_cotizacion(registro) for registro in origen]
        self._claves_cotizaciones_pagina = claves_pagina
        self._checkboxes_seleccion_cotizaciones = {}
        self._filas_seleccion_cotizaciones = {}
        checkbox_pagina = ft.Checkbox(
            value=bool(claves_pagina)
            and all(clave in self.cotizaciones_seleccionadas for clave in claves_pagina),
            active_color=COLOR_AZUL,
            check_color=COLOR_BLANCO,
            border_side=ft.BorderSide(1.5, "#7186A0"),
            shape=ft.RoundedRectangleBorder(radius=3),
            on_change=lambda e, registros=list(origen): self.seleccionar_pagina(
                registros, bool(e.control.value)
            ),
        )
        self._checkbox_seleccionar_pagina = checkbox_pagina
        for registro in origen:
            cotizacion = self._normalizar_fila_tabla(registro)
            clave = self._clave_cotizacion(registro)
            seleccionado = clave in self.cotizaciones_seleccionadas
            checkbox_fila = ft.Checkbox(
                value=seleccionado,
                active_color=COLOR_AZUL,
                check_color=COLOR_BLANCO,
                border_side=ft.BorderSide(1.5, "#7186A0"),
                shape=ft.RoundedRectangleBorder(radius=3),
                on_change=lambda e, r=registro: self.seleccionar_cotizacion(
                    r, bool(e.control.value)
                ),
            )
            fila = ftd.DataRow2(
                    selected=seleccionado,
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                width=44,
                                alignment=ft.Alignment(0, 0),
                                content=checkbox_fila,
                            )
                        ),
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
            filas.append(fila)
            self._checkboxes_seleccion_cotizaciones[clave] = checkbox_fila
            self._filas_seleccion_cotizaciones[clave] = fila

        return tabla(
            columnas=[
                (checkbox_pagina, 48),
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

    def seleccionar_cotizacion(self, cotizacion, seleccionado):
        clave = self._clave_cotizacion(cotizacion)
        if seleccionado:
            self.cotizaciones_seleccionadas[clave] = cotizacion
        else:
            self.cotizaciones_seleccionadas.pop(clave, None)
        self._actualizar_vista_seleccion({clave})

    def seleccionar_pagina(self, cotizaciones, seleccionado):
        claves = set()
        for cotizacion in cotizaciones:
            clave = self._clave_cotizacion(cotizacion)
            claves.add(clave)
            if seleccionado:
                self.cotizaciones_seleccionadas[clave] = cotizacion
            else:
                self.cotizaciones_seleccionadas.pop(clave, None)
        self._actualizar_vista_seleccion(claves)

    def _actualizar_vista_seleccion(self, claves_actualizadas):
        for clave in claves_actualizadas:
            checkbox = self._checkboxes_seleccion_cotizaciones.get(clave)
            fila = self._filas_seleccion_cotizaciones.get(clave)
            seleccionado = clave in self.cotizaciones_seleccionadas
            if checkbox is not None:
                checkbox.value = seleccionado
            if fila is not None:
                fila.selected = seleccionado
                fila.update()
        self._checkbox_seleccionar_pagina.value = (
            bool(self._claves_cotizaciones_pagina)
            and all(
                clave in self.cotizaciones_seleccionadas
                for clave in self._claves_cotizaciones_pagina
            )
        )
        self._checkbox_seleccionar_pagina.update()
        self._actualizar_descripcion_exportacion()
        self._boton_exportar.update()
        self._texto_resumen_exportacion.update()

    def _actualizar_descripcion_exportacion(self):
        if not hasattr(self, "_texto_resumen_exportacion"):
            return
        self._texto_resumen_exportacion.value = self._descripcion_exportacion()
        self._texto_boton_exportar.value = self._etiqueta_boton_exportar()
        self._boton_exportar.width = (
            230
            if self.cotizaciones_seleccionadas
            else 190
            if self._hay_filtros_exportacion()
            else 150
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
