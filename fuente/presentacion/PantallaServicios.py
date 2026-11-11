import asyncio
import logging

import flet as ft
from sqlalchemy.exc import SQLAlchemyError

from fuente.negocio.controlador.ControladorServicios import ControladorServicios
from fuente.negocio.modelo.ENUMs import CaracterServicio, TipoConcepto
from fuente.negocio.servicio.ServicioServicio import ServicioServicio
from fuente.presentacion.PantallaNuevoServicio import PantallaNuevoServicio
from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_BANNER,
    COLOR_FONDO,
    COLOR_NARANJA,
    COLOR_BLANCO,
    COLOR_GRIS,
    COLOR_NEGRO,
)
from fuente.utilidades.Componentes import (
    banner_modulo,
    barra_busqueda,
    boton,
    boton_vista,
    card,
    estado_vacio,
    fila_catalogo,
    panel_filtros,
    paginacion,
    seccion_opciones_filtro,
    agregar_panel_flotante,
    quitar_panel_flotante,
    mostrar_notificacion,
    sombra_suave,
    tarjeta_detalle,
    tarjeta_catalogo,
)
from fuente.utilidades.feedback import avisar_eliminacion_no_implementada

COLOR_AZUL_OSCURO = "#0d1b2a" 

class PantallaServicios(ft.Container):
    
    def __init__(
        self,
        main_page,
        servicio_servicio: ServicioServicio | None = None,
    ):
        super().__init__(expand=True, bgcolor=COLOR_FONDO, padding=0)
        self.main_page = main_page 
        self.servicio_servicio = servicio_servicio
        self.controlador_servicios = (
            ControladorServicios(servicio_servicio)
            if servicio_servicio is not None
            else None
        )
        
        self._menu_exportacion_abierto = False
        self._vista_servicios = "catalogo"
        self.registros_por_pagina = 8
        self.pagina_actual = 1
        self.busqueda = ""
        self.servicios_catalogo = []
        self.total_servicios = 0
        self.filtros_seleccionados = {
            "tipos": set(),
            "caracteres": set(),
            "estados": set(),
            "categorias_pda": set(),
        }
        self._opciones_categoria_pda = []
        self._categorias_pda_cargadas = False
        self._checks_filtros = {}
        self._panel_filtros_abierto = False
        self._clic_en_boton_filtros = False
        self._tarea_busqueda = None
        self._texto_busqueda_pendiente = ""
        self._error_catalogo = None
        if self.controlador_servicios is not None:
            try:
                self._cargar_servicios_catalogo()
            except SQLAlchemyError as error:
                logging.exception("No se pudo cargar el catálogo de servicios.")
                self._error_catalogo = error
        
        banner = banner_modulo(
            src="fondo_puerto.jpg",
            categoria="Catálogo de servicios",
            titulo="Servicios",
            descripcion="Administra las tarifas y tipos de cobro de la agencia.",
            icono=ft.Icons.WORK_OUTLINE,
        )

        buscador_servicios = barra_busqueda(
            hint="Buscar servicio por nombre o categoría...",
            on_change=self.buscar_servicios,
        )
        buscador_servicios.height = 44
        buscador_servicios.value = self.busqueda
        self._campo_busqueda = buscador_servicios
        self._boton_filtros = boton(
            texto="Filtros",
            icono=ft.Icons.TUNE,
            tipo="secundario",
            width=160,
            height=44,
            border_color="#C9DDF7",
            on_click=self.abrir_filtros,
        )
        self._actualizar_indicador_filtros()

        barra_herramientas = card(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    buscador_servicios,
                    ft.GestureDetector(
                        on_tap_down=self._marcar_clic_en_boton_filtros,
                        on_tap_up=self._limpiar_clic_en_boton_filtros,
                        on_tap_cancel=self._limpiar_clic_en_boton_filtros,
                        content=self._boton_filtros,
                    ),
                    boton(
                        texto="Agregar servicio",
                        icono=ft.Icons.ADD,
                        tipo="principal",
                        width=210,
                        height=44,
                        on_click=self.abrir_nuevo_servicio,
                    ),
                ],
            ),
            padding=10,
            radius=10,
            shadow=sombra_suave(),
        )

        # --- TARJETAS RESUMEN ---
        conteos = self._obtener_conteos_resumen()
        self._texto_resumen_total = self._crear_texto_resumen(conteos["total"])
        self._texto_resumen_fija = self._crear_texto_resumen(conteos["fija"])
        self._texto_resumen_factor = self._crear_texto_resumen(conteos["factor"])
        self._texto_resumen_variable = self._crear_texto_resumen(conteos["variable"])
        tarjetas_resumen = ft.Row([
            self.crear_tarjeta_resumen(
                "Total Servicios",
                self._texto_resumen_total,
                ft.Icons.FORMAT_LIST_BULLETED,
                COLOR_AZUL,
                "#EAF2FF",
                "#D7E6FF",
            ),
            self.crear_tarjeta_resumen(
                "Cuota Fija",
                self._texto_resumen_fija,
                ft.Icons.ATTACH_MONEY,
                "#16A765",
                "#EAF8F0",
                "#D5F0E2",
            ),
            self.crear_tarjeta_resumen(
                "Factor Unitario",
                self._texto_resumen_factor,
                ft.Icons.CALCULATE_OUTLINED,
                "#168BDE",
                "#EAF4FF",
                "#D4E8FA",
            ),
            self.crear_tarjeta_resumen(
                "Por Rangos/Días",
                self._texto_resumen_variable,
                ft.Icons.LAYERS_OUTLINED,
                "#8B35D3",
                "#F4ECFF",
                "#E5D4F5",
            ),
        ], spacing=10)

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
            f"{self.total_servicios} servicios en el catálogo",
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
                    self._texto_pie_catalogo(),
                    size=12,
                    color=COLOR_GRIS,
                ),
                ft.Row(
                    controls=[],
                ),
            ],
        )
        self._texto_pie = pie_catalogo.controls[0]
        self._pie_catalogo = pie_catalogo
        self._actualizar_pie_catalogo()

        contenido_principal = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding(14, 8, 14, 16),
                    content=ft.Column(
                        expand=True,
                        spacing=12,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            ft.Column(
                                spacing=10,
                                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                                controls=[banner, barra_herramientas],
                            ),
                            tarjetas_resumen,
                            catalogo_servicios,
                            pie_catalogo,
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

    def _cargar_servicios_catalogo(self):
        if self.controlador_servicios is None:
            return
        if not self._categorias_pda_cargadas:
            self._opciones_categoria_pda = [
                (categoria.id, categoria.nombre)
                for categoria in self.controlador_servicios.obtener_categorias_pda()
            ]
            self._categorias_pda_cargadas = True
        filtros = self._filtros_repositorio()
        self.total_servicios = self.controlador_servicios.obtener_cantidad_registros(
            filtros
        )
        registros = self.controlador_servicios.obtener_servicios(
            pagina=1,
            limite=max(self.total_servicios, 1),
            filtros=filtros,
        )
        self.servicios_catalogo = [
            self._adaptar_servicio(servicio) for servicio in registros
        ]

    def _filtros_repositorio(self):
        estados = self.filtros_seleccionados["estados"]
        activos = [
            valor == "ACTIVO"
            for valor in ("ACTIVO", "INACTIVO")
            if valor in estados
        ]
        return {
            "tipo_concepto": self.filtros_seleccionados["tipos"],
            "caracter": self.filtros_seleccionados["caracteres"],
            "activo": activos,
            "categoria_pda_id": self.filtros_seleccionados["categorias_pda"],
            "nombre": self.busqueda,
        }

    def buscar_servicios(self, e):
        texto = (e.control.value or "").strip()
        self._texto_busqueda_pendiente = texto
        if self._tarea_busqueda is not None:
            self._tarea_busqueda.cancel()
            self._tarea_busqueda = None

        if len(texto) < 3:
            if self.busqueda:
                self._aplicar_busqueda("")
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
        self.recargar_catalogo()

    def _seccion_filtro(self, titulo, opciones, clave, icono):
        seleccionados = self.filtros_seleccionados[clave]
        seccion, checkboxes = seccion_opciones_filtro(
            titulo,
            opciones,
            seleccionados,
            self._cambio_checkbox_filtro,
            icono=icono,
        )
        self._checks_filtros.update(
            {(clave, valor): checkbox for valor, checkbox in checkboxes.items()}
        )
        return seccion

    def abrir_filtros(self, e=None):
        if self._panel_filtros_abierto:
            self.cerrar_filtros()
            return

        self._checks_filtros = {}
        tipos = (
            (TipoConcepto.SERVICIO_CUOTA_FIJA, "Cuota fija"),
            (TipoConcepto.SERVICIO_FACTOR_UNITARIO, "Factor unitario"),
            (TipoConcepto.SERVICIO_LINEAL_MIXTO, "Lineal mixto"),
            (TipoConcepto.SERVICIO_FACTOR_COMPUESTO, "Factor compuesto"),
            (TipoConcepto.SERVICIO_RANGO, "Por rangos"),
            (TipoConcepto.SERVICIO_INCREMENTAL, "Por tramos"),
        )
        caracteres = (
            (CaracterServicio.OBLIGATORIO, "Obligatorio"),
            (CaracterServicio.CONDICIONAL, "Condicional"),
            (CaracterServicio.OPCIONAL, "Opcional"),
        )
        estados = (("ACTIVO", "Activo"), ("INACTIVO", "Inactivo"))
        categorias = [
            (str(categoria_id), nombre)
            for categoria_id, nombre in self._opciones_categoria_pda
        ]
        categoria_ids_seleccionados = {
            str(valor) for valor in self.filtros_seleccionados["categorias_pda"]
        }
        secciones = [
            self._seccion_filtro(
                "Tipo de cobro",
                [(tipo.value, etiqueta) for tipo, etiqueta in tipos],
                "tipos",
                ft.Icons.ATTACH_MONEY,
            ),
            ft.Divider(height=1, color="#E2EDF9"),
            self._seccion_filtro(
                "Carácter del servicio",
                [(caracter.value, etiqueta) for caracter, etiqueta in caracteres],
                "caracteres",
                ft.Icons.RULE_OUTLINED,
            ),
            ft.Divider(height=1, color="#E2EDF9"),
            self._seccion_filtro(
                "Estado",
                estados,
                "estados",
                ft.Icons.CHECK_CIRCLE_OUTLINED,
            ),
        ]
        if categorias:
            self.filtros_seleccionados["categorias_pda"] = categoria_ids_seleccionados
            secciones.extend(
                [
                    ft.Divider(height=1, color="#E2EDF9"),
                    self._seccion_filtro(
                        "Categoría PDA",
                        categorias,
                        "categorias_pda",
                        ft.Icons.CATEGORY_OUTLINED,
                    ),
                ]
            )

        self._panel_filtros, self._texto_resumen_filtros = panel_filtros(
            titulo="Filtrar servicios",
            secciones=secciones,
            resumen=self._resumen_filtros_actual(),
            on_limpiar=self.limpiar_filtros,
            on_aplicar=self.aplicar_filtros,
            on_cerrar=self.cerrar_filtros,
            top=220,
            right=155,
            width=360,
            height=500,
        )
        agregar_panel_flotante(self._layout_principal, self._panel_filtros)
        self._panel_filtros_abierto = True
        self.update()

    def _resumen_filtros_actual(self):
        cantidad = sum(
            len(valores) for valores in self.filtros_seleccionados.values()
        )
        return (
            "Sin filtros seleccionados"
            if cantidad == 0
            else "1 filtro seleccionado"
            if cantidad == 1
            else f"{cantidad} filtros seleccionados"
        )

    def _actualizar_indicador_filtros(self):
        cantidad = sum(
            len(valores) for valores in self.filtros_seleccionados.values()
        )
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

    def _cambio_checkbox_filtro(self, e=None):
        cantidad = sum(
            bool(checkbox.value) for checkbox in self._checks_filtros.values()
        )
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
        self.filtros_seleccionados = {
            "tipos": set(),
            "caracteres": set(),
            "estados": set(),
            "categorias_pda": set(),
        }
        self._actualizar_indicador_filtros()
        self._texto_resumen_filtros.value = "Sin filtros seleccionados"
        self._texto_resumen_filtros.update()
        self.pagina_actual = 1
        self.recargar_catalogo()

    def aplicar_filtros(self, e=None):
        filtros = {clave: set() for clave in self.filtros_seleccionados}
        for (grupo, valor), checkbox in self._checks_filtros.items():
            if checkbox.value:
                filtros[grupo].add(valor)
        filtros["categorias_pda"] = {
            int(valor) for valor in filtros["categorias_pda"]
        }
        self.filtros_seleccionados = filtros
        self._actualizar_indicador_filtros()
        self.pagina_actual = 1
        self.cerrar_filtros()
        self.recargar_catalogo()

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

    @staticmethod
    def _adaptar_servicio(servicio):
        tipo = servicio.tipo_concepto.value
        variable = getattr(servicio, "variable_primaria", None)
        variable = variable.value if variable is not None else None
        if tipo == TipoConcepto.SERVICIO_CUOTA_FIJA.value:
            detalle = f"${servicio.cuota:,.2f} MXN"
        elif tipo == TipoConcepto.SERVICIO_FACTOR_UNITARIO.value:
            detalle = f"${servicio.factor_mxn:,.4f} MXN / {variable}"
        elif tipo == TipoConcepto.SERVICIO_LINEAL_MIXTO.value:
            detalle = (
                f"${servicio.cuota_base:,.2f} + "
                f"${servicio.factor_mxn:,.4f} MXN / {variable}"
            )
        elif tipo == TipoConcepto.SERVICIO_FACTOR_COMPUESTO.value:
            detalle = (
                f"${servicio.factor_mxn:,.4f} MXN / {variable} × "
                f"{servicio.variable_secundaria.value}"
            )
        elif tipo == TipoConcepto.SERVICIO_RANGO.value:
            detalle = f"{len(servicio.rangos)} rangos · {servicio.variable_rangos.value}"
        else:
            detalle = f"{len(servicio.tramos)} tramos · {servicio.variable_dias.value}"

        return {
            "id": servicio.id,
            "nombre": servicio.nombre_es,
            "categoria": (
                servicio.categoria_pda.nombre
                if servicio.categoria_pda is not None
                else "Sin categoría"
            ),
            "categoria_pda_id": servicio.categoria_pda_id,
            "descripcion": servicio.nombre_en or f"Unidad: {servicio.unidad_medida}",
            "detalle": detalle,
            "tipo": tipo,
            "caracter": getattr(servicio.caracter, "value", servicio.caracter),
            "activo": bool(servicio.activo),
            "sku": servicio.sku,
            "proveedores": [proveedor.nombre for proveedor in servicio.proveedores],
            "imagen": servicio.imagen_path,
        }

    def _obtener_conteos_resumen(self):
        tipos_factor = {
            TipoConcepto.SERVICIO_FACTOR_UNITARIO.value,
            TipoConcepto.SERVICIO_LINEAL_MIXTO.value,
            TipoConcepto.SERVICIO_FACTOR_COMPUESTO.value,
        }
        tipos_variables = {
            TipoConcepto.SERVICIO_RANGO.value,
            TipoConcepto.SERVICIO_INCREMENTAL.value,
        }
        return {
            "total": self.total_servicios,
            "fija": sum(
                servicio["tipo"] == TipoConcepto.SERVICIO_CUOTA_FIJA.value
                for servicio in self.servicios_catalogo
            ),
            "factor": sum(
                servicio["tipo"] in tipos_factor
                for servicio in self.servicios_catalogo
            ),
            "variable": sum(
                servicio["tipo"] in tipos_variables
                for servicio in self.servicios_catalogo
            ),
        }

    def _texto_pie_catalogo(self):
        if not self.total_servicios:
            return "Mostrando 0 de 0 servicios"
        primero = (self.pagina_actual - 1) * self.registros_por_pagina + 1
        ultimo = min(
            self.pagina_actual * self.registros_por_pagina,
            self.total_servicios,
        )
        return f"Mostrando {primero}–{ultimo} de {self.total_servicios} servicios"

    def _crear_control_paginacion(self):
        return paginacion(
            total_registros=self.total_servicios,
            registros_por_pagina=self.registros_por_pagina,
            pagina_actual=self.pagina_actual,
            on_change=self.cambiar_pagina,
        )

    def _actualizar_pie_catalogo(self):
        self._texto_pie.value = self._texto_pie_catalogo()
        self._pie_catalogo.controls[1] = self._crear_control_paginacion()

    def cambiar_pagina(self, pagina):
        total_paginas = max(
            1,
            (self.total_servicios + self.registros_por_pagina - 1)
            // self.registros_por_pagina,
        )
        if pagina < 1 or pagina > total_paginas or pagina == self.pagina_actual:
            return
        self.pagina_actual = pagina
        self._actualizar_pie_catalogo()
        self._contenido_servicios.content = self._crear_vista_servicios()
        if self.main_page is not None:
            self.main_page.update()

    def recargar_catalogo(self):
        try:
            self._cargar_servicios_catalogo()
        except SQLAlchemyError as error:
            self._error_catalogo = error
            self._contenido_servicios.content = self._crear_vista_servicios()
            raise
        self._error_catalogo = None
        total_paginas = max(
            1,
            (self.total_servicios + self.registros_por_pagina - 1)
            // self.registros_por_pagina,
        )
        self.pagina_actual = min(self.pagina_actual, total_paginas)
        self._texto_total_servicios.value = (
            f"{self.total_servicios} servicios en el catálogo"
        )
        conteos = self._obtener_conteos_resumen()
        self._texto_resumen_total.value = str(conteos["total"])
        self._texto_resumen_fija.value = str(conteos["fija"])
        self._texto_resumen_factor.value = str(conteos["factor"])
        self._texto_resumen_variable.value = str(conteos["variable"])
        self._actualizar_pie_catalogo()
        self._contenido_servicios.content = self._crear_vista_servicios()
        if self.main_page is not None:
            self.main_page.update()

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
        fondo, color = estilos.get(categoria, ("#EAF2FF", "#176FC1"))
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
        if self._error_catalogo is not None:
            return self._contenedor_estado_catalogo(
                ft.Icons.ERROR_OUTLINE,
                "No se pudo cargar el catálogo",
                "Revisa la conexión con la base de datos e inténtalo de nuevo.",
            )

        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        servicios = self.servicios_catalogo[
            inicio:inicio + self.registros_por_pagina
        ]
        if not servicios:
            con_filtros = bool(self.busqueda) or any(
                self.filtros_seleccionados.values()
            )
            return self._contenedor_estado_catalogo(
                ft.Icons.SEARCH_OFF if con_filtros else ft.Icons.WORK_OUTLINE,
                (
                    "No se encontraron servicios"
                    if con_filtros
                    else "Aún no hay servicios registrados"
                ),
                (
                    "Ajusta los filtros o la búsqueda e inténtalo de nuevo."
                    if con_filtros
                    else "Registra un servicio para que esté disponible al crear cotizaciones."
                ),
            )

        if self._vista_servicios == "lista":
            tarjetas = [
                fila_catalogo(
                    titulo=servicio["nombre"],
                    descripcion=servicio["descripcion"],
                    etiqueta=self._crear_etiqueta_servicio(
                        servicio["categoria"]
                    ),
                    detalle=servicio["detalle"],
                    ruta_imagen=servicio["imagen"] or None,
                    icono_secundario=ft.Icons.ATTACH_MONEY,
                    on_info=lambda e, s=servicio: self.ver_servicio(s),
                )
                for servicio in servicios
            ]
            filas = []
            for inicio in range(0, len(tarjetas), 2):
                controles_fila = tarjetas[inicio:inicio + 2]
                if len(controles_fila) == 1:
                    controles_fila.append(ft.Container(expand=True))
                filas.append(
                    ft.Row(
                        height=120,
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=controles_fila,
                    )
                )
            return ft.Container(
                expand=True,
                padding=ft.Padding(2, 2, 2, 2),
                content=ft.Column(
                    expand=True,
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                    controls=filas,
                ),
            )

        tarjetas = [
            tarjeta_catalogo(
                titulo=servicio["nombre"],
                descripcion=servicio["descripcion"],
                etiqueta=self._crear_etiqueta_servicio(
                    servicio["categoria"]
                ),
                detalle=servicio["detalle"],
                ruta_imagen=servicio["imagen"] or None,
                icono_secundario=ft.Icons.ATTACH_MONEY,
                on_click=lambda e, s=servicio: self.ver_servicio(s),
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

    def _contenedor_estado_catalogo(self, icono, titulo, descripcion):
        return ft.Container(
            height=220 if self._vista_servicios == "catalogo" else 120,
            alignment=ft.Alignment(0, 0),
            content=estado_vacio(icono, titulo, descripcion),
        )

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
        self.registros_por_pagina = 16 if vista == "lista" else 8
        self.pagina_actual = 1
        self._actualizar_pie_catalogo()
        self._contenido_servicios.content = self._crear_vista_servicios()
        self._botones_vista.controls = self._crear_botones_vista()
        if self.main_page is not None:
            self.main_page.update()

    def ver_servicio(self, servicio):
        datos_generales = ft.Column(
            spacing=8,
            controls=[
                ft.Text(servicio["nombre"], color=COLOR_NEGRO, size=15),
                ft.Text(servicio["descripcion"], color=COLOR_GRIS),
                ft.Text(f"Categoría PDA: {servicio['categoria']}", color=COLOR_NEGRO),
                ft.Text(f"Método y tarifa: {servicio['detalle']}", color=COLOR_NEGRO),
            ],
        )
        tarjetas = [
            tarjeta_detalle(
                "Datos generales",
                ft.Icons.WORK_OUTLINE,
                datos_generales,
            )
        ]
        if servicio["sku"]:
            tarjetas.append(
                tarjeta_detalle(
                    "Identificación",
                    ft.Icons.QR_CODE_2_OUTLINED,
                    ft.Text(f"SKU: {servicio['sku']}", color=COLOR_NEGRO),
                )
            )
        if servicio["proveedores"]:
            tarjetas.append(
                tarjeta_detalle(
                    "Proveedores autorizados",
                    ft.Icons.BUSINESS_OUTLINED,
                    ft.Text(
                        ", ".join(servicio["proveedores"]),
                        color=COLOR_NEGRO,
                    ),
                )
            )
        controles = []
        if servicio["imagen"]:
            controles.append(
                ft.Container(
                    height=180,
                    border_radius=10,
                    bgcolor="#EAF1F7",
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                    content=ft.Image(
                        src=servicio["imagen"],
                        width=float("inf"),
                        height=180,
                        fit=ft.BoxFit.COVER,
                    ),
                )
            )
        else:
            controles.append(
                ft.Container(
                    height=120,
                    border_radius=10,
                    bgcolor="#EAF1F7",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.IMAGE_OUTLINED,
                        size=36,
                        color=COLOR_GRIS,
                    ),
                )
            )
        controles.extend(tarjetas)
        self.main_page.show_dialog(
            ft.AlertDialog(
                modal=True,
                bgcolor="#F4F8FC",
                shape=ft.RoundedRectangleBorder(radius=18),
                title=ft.Row(
                    controls=[
                        ft.Column(
                            spacing=2,
                            expand=True,
                            controls=[
                                ft.Text(
                                    "Ficha del servicio",
                                    color=COLOR_BANNER,
                                    weight=ft.FontWeight.BOLD,
                                ),
                                ft.Text(
                                    servicio["nombre"],
                                    size=13,
                                    color=COLOR_GRIS,
                                ),
                            ],
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            tooltip="Cerrar",
                            icon_color=COLOR_BANNER,
                            on_click=lambda e: self.main_page.pop_dialog(),
                        ),
                    ],
                ),
                title_padding=ft.Padding(22, 18, 22, 10),
                content=ft.Column(
                    width=650,
                    tight=True,
                    spacing=8,
                    controls=controles,
                ),
                actions=[
                    ft.Row(
                        expand=True,
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        controls=[
                            ft.OutlinedButton(
                                content=ft.Row(
                                    tight=True,
                                    spacing=6,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.DELETE_OUTLINE,
                                            color=ft.Colors.RED_600,
                                            size=18,
                                        ),
                                        ft.Text(
                                            "Eliminar",
                                            color=ft.Colors.RED_600,
                                        ),
                                    ],
                                ),
                                on_click=lambda e, item=servicio: (
                                    self.pedir_confirmacion_eliminacion(item)
                                ),
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, ft.Colors.RED_600),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                            ft.Button(
                                content=ft.Row(
                                    tight=True,
                                    spacing=6,
                                    controls=[
                                        ft.Icon(
                                            ft.Icons.EDIT_OUTLINED,
                                            color=COLOR_BLANCO,
                                            size=18,
                                        ),
                                        ft.Text("Editar", color=COLOR_BLANCO),
                                    ],
                                ),
                                bgcolor=COLOR_NARANJA,
                                on_click=lambda e, item=servicio: (
                                    self.editar_servicio(item)
                                ),
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                ),
                            ),
                        ],
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                actions_padding=ft.Padding(18, 12, 18, 18),
                content_padding=ft.Padding(18, 0, 18, 0),
                scrollable=True,
            )
        )

    def pedir_confirmacion_eliminacion(self, servicio):
        avisar_eliminacion_no_implementada(self.main_page)

    def _eliminar_servicio(self, servicio):
        avisar_eliminacion_no_implementada(self.main_page)

    def editar_servicio(self, servicio):
        self.main_page.pop_dialog()
        try:
            registro = self.controlador_servicios.buscar_por_id(servicio["id"])
        except SQLAlchemyError:
            logging.exception("No se pudo recuperar el servicio para editarlo.")
            mostrar_notificacion(
                self.main_page,
                "No se pudo cargar el servicio para editarlo.",
                ft.Colors.RED_600,
            )
            return
        if registro is None:
            mostrar_notificacion(
                self.main_page,
                "El servicio que intentas editar ya no existe.",
                ft.Colors.RED_600,
            )
            return

        self.vista_catalogo = self.content
        self.padding = 0
        self.content = PantallaNuevoServicio(
            self.main_page,
            vista_anterior=self,
            controlador=self.controlador_servicios,
            servicio_edicion=registro,
        )
        self.update()

    # =========================================================
    # 2. CAMBIO: Función para hacer el cambio de pantalla
    # =========================================================
    def abrir_nuevo_servicio(self, e):
        # Guardar la vista de la tabla actual en memoria
        self.vista_catalogo = self.content
        self.padding = 0
        self.content = PantallaNuevoServicio(
            self.main_page,
            vista_anterior=self,
            controlador=self.controlador_servicios,
        )
        self.update()
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

    def crear_tarjeta_resumen(
        self,
        titulo,
        cantidad,
        icono,
        color_icono,
        bg_icono,
        color_borde,
    ):
        texto_cantidad = (
            cantidad
            if isinstance(cantidad, ft.Text)
            else self._crear_texto_resumen(cantidad)
        )
        return card(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=48,
                        height=48,
                        alignment=ft.Alignment(0, 0),
                        bgcolor=bg_icono,
                        border_radius=24,
                        content=ft.Icon(icono, size=25, color=color_icono),
                    ),
                    ft.Column(
                        expand=True,
                        spacing=2,
                        controls=[
                            ft.Text(
                                titulo,
                                size=13,
                                color=COLOR_NEGRO,
                                weight=ft.FontWeight.W_600,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            texto_cantidad,
                        ],
                    ),
                    ft.Icon(
                        ft.Icons.CHEVRON_RIGHT,
                        size=18,
                        color="#9AAABD",
                    ),
                ],
            ),
            padding=12,
            border_color=color_borde,
            radius=12,
            shadow=sombra_suave(),
            expand=True,
        )

    @staticmethod
    def _crear_texto_resumen(cantidad):
        return ft.Text(
            str(cantidad),
            size=22,
            color=COLOR_BANNER,
            weight=ft.FontWeight.BOLD,
            max_lines=1,
            overflow=ft.TextOverflow.ELLIPSIS,
        )
