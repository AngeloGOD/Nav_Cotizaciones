
import flet as ft
from fuente.utilidades.Colores import *

from fuente.utilidades.Componentes import (
    banner_modulo,
    boton_vista,
    card,
    fila_producto,
    menu_exportacion,
    mostrar_notificacion,
    panel_filtros,
    seccion_opciones_filtro,
    sombra_suave,
    tarjeta_producto,
)
from fuente.utilidades.ExportacionExcel import exportar_excel
from fuente.negocio.controlador.ControladorProductos import ControladorProductos
from fuente.presentacion.PantallaRegistrarProducto import PantallaRegistrarProducto


class PantallaProductos(ft.Container):
    def __init__(self, page: ft.Page, productos=None):
        super().__init__(expand=True, bgcolor=COLOR_FONDO)

        self._page = page
        self.controlador = ControladorProductos(productos)
        self.productos = self.controlador.productos

        self.pagina_actual = 1
        self.registros_por_pagina = 8
        self.busqueda = ""
        self.categoria = "todas"
        self.unidad = "todas"
        self.filtros_seleccionados = {
            "categoria": "todas",
            "unidad_medida": "todas",
            "activo": set(),
            "es_perecedero": set(),
            "requiere_refrigeracion": set(),
        }
        self.vista = "catalogo"
        self._panel_filtros_abierto = False
        self._menu_exportacion_abierto = False
        self._clic_en_boton_menu = False
        self._controles_filtros = {}
        self._checks_filtros = {}

        self._zona_productos = ft.Container(expand=True)
        self._texto_total = ft.Text(size=13, color=COLOR_GRIS)
        self._control_paginacion = ft.Container()
        self._campo_busqueda = self._crear_busqueda()
        self._zona_catalogo = ft.Container(expand=True)

        # Construir la pantalla una sola vez.
        self.build_ui()

    # ---------------------------------------------------------
    # BUSQUEDA Y FILTROS
    # ---------------------------------------------------------
    def _crear_busqueda(self):
        return ft.TextField(
            hint_text="Buscar producto por nombre o SKU/código interno...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            height=44,
            text_size=14,
            content_padding=ft.Padding(12, 8, 12, 8),
            border={
                ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                    border_radius=8,
                    side=ft.BorderSide(1, COLOR_GRIS_CLARO),
                ),
                ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                    border_radius=8,
                    side=ft.BorderSide(1, COLOR_AZUL),
                ),
            },
            on_change=self.buscar,
        )

    def _seccion_filtro(self, clave, titulo, icono, opciones, valor):
        dropdown = ft.Dropdown(
            value=valor,
            options=[
                ft.DropdownOption(key=clave_opcion, text=texto)
                for clave_opcion, texto in opciones
            ],
            on_select=self._cambio_filtro,
            expand=True,
            height=44,
            text_size=14,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
        )
        self._controles_filtros[clave] = dropdown
        return ft.Container(
            padding=ft.Padding(14, 8, 14, 6),
            content=ft.Column(
                spacing=5,
                controls=[
                    ft.Row(
                        spacing=7,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(icono, size=16, color=COLOR_BANNER),
                            ft.Text(
                                titulo,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                        ],
                    ),
                    dropdown,
                ],
            ),
        )

    def _cantidad_filtros(self, filtros=None):
        filtros = filtros or self.filtros_seleccionados
        cantidad = 0
        for clave, valor in filtros.items():
            if isinstance(valor, set):
                cantidad += len(valor)
            elif valor not in {"todas", "todos"}:
                cantidad += 1
        return cantidad

    def _seccion_checkbox_filtro(
        self, clave, titulo, icono, opciones, expand=False
    ):
        seccion, checkboxes = seccion_opciones_filtro(
            titulo,
            opciones,
            self.filtros_seleccionados[clave],
            self._cambio_filtro,
            icono=icono,
        )
        seccion.expand = expand
        self._checks_filtros.update(
            {(clave, valor): checkbox for valor, checkbox in checkboxes.items()}
        )
        return seccion

    def _actualizar_indicador_filtros(self):
        cantidad = self._cantidad_filtros()
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
        if self.page is not None:
            self._boton_filtros.update()

    def _actualizar_resumen_filtros(self):
        cantidad = sum(
            (control.value or "todas") != "todas"
            for control in self._controles_filtros.values()
        ) + sum(
            bool(checkbox.value) for checkbox in self._checks_filtros.values()
        )
        self._texto_resumen_filtros.value = (
            "1 filtro seleccionado"
            if cantidad == 1
            else f"{cantidad} filtros seleccionados"
        )
        if self.page is not None:
            self._texto_resumen_filtros.update()

    def _cambio_filtro(self, e):
        self._actualizar_resumen_filtros()

    def buscar(self, e):
        self.busqueda = e.control.value or ""
        self.pagina_actual = 1
        self._actualizar_resultados()

    def cambiar_vista(self, vista):
        self.cerrar_menus()
        self.vista = vista
        self._botones_vista = self._crear_botones_vista()
        self._campo_busqueda.on_focus = self.cerrar_menus
        self._actualizar_resultados()

    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        self._actualizar_resultados()

    def _filtrar_productos(self):
        return self.controlador.obtener_productos_filtrados(
            self.busqueda,
            self.filtros_seleccionados,
        )

    # ---------------------------------------------------------
    # ENCABEZADO Y HERRAMIENTAS
    # ---------------------------------------------------------
    def cabecera_productos(self):
        return banner_modulo(
            src="fondo_puerto.jpg",
            categoria="Catálogo de productos",
            titulo="Productos",
            descripcion="Consulta y administra los productos por categoría.",
            icono=ft.Icons.INVENTORY_2_OUTLINED,
        )

    def barra_herramientas(self):
        self._botones_vista = self._crear_botones_vista()
        self._boton_filtros = ft.OutlinedButton(
            content=ft.Row(
                tight=True,
                spacing=7,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.TUNE, size=18, color=COLOR_AZUL),
                    ft.Text("Filtros", size=14, color=COLOR_AZUL),
                ],
            ),
            width=145,
            height=44,
            on_click=self._abrir_filtros,
            style=ft.ButtonStyle(
                color=COLOR_AZUL,
                side=ft.BorderSide(1, "#C7DAFF"),
                shape=ft.RoundedRectangleBorder(radius=9),
            ),
        )
        boton_filtros = ft.GestureDetector(
            on_tap_down=self._marcar_clic_en_boton_menu,
            on_tap_up=self._limpiar_clic_en_boton_menu,
            on_tap_cancel=self._limpiar_clic_en_boton_menu,
            content=self._boton_filtros,
        )
        self._texto_boton_exportar = ft.Text(
            "Exportar",
            size=14,
            color=COLOR_AZUL,
        )
        self._boton_exportar = ft.OutlinedButton(
            content=ft.Row(
                tight=True,
                spacing=7,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.DOWNLOAD_OUTLINED,
                        size=18,
                        color=COLOR_AZUL,
                    ),
                    self._texto_boton_exportar,
                ],
            ),
            width=145,
            height=44,
            on_click=self.alternar_menu_exportacion,
            style=ft.ButtonStyle(
                color=COLOR_AZUL,
                side=ft.BorderSide(1, "#C7DAFF"),
                shape=ft.RoundedRectangleBorder(radius=9),
            ),
        )
        boton_exportar = ft.GestureDetector(
            on_tap_down=self._marcar_clic_en_boton_menu,
            on_tap_up=self._limpiar_clic_en_boton_menu,
            on_tap_cancel=self._limpiar_clic_en_boton_menu,
            content=self._boton_exportar,
        )
        self._texto_resumen_exportacion = ft.Text(
            self._descripcion_exportacion(),
            size=11,
            color=COLOR_GRIS,
        )
        self._menu_exportacion = menu_exportacion(
            descripcion=self._texto_resumen_exportacion,
            on_pdf=lambda e: self._informar_exportacion("PDF"),
            on_excel=self._exportar_productos_excel,
            descripcion_pdf="Genera un archivo PDF del catálogo de productos.",
            descripcion_excel="Descarga una hoja de cálculo de los productos.",
            top=210,
            right=14,
            width=280,
        )
        self._menu_exportacion.visible = False

        return card(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    self._campo_busqueda,
                    boton_filtros,
                    ft.Button(
                        ft.Text(
                            "Agregar producto",
                            size=14,
                            weight=ft.FontWeight.W_500,
                            color=COLOR_BLANCO,
                        ),
                        icon=ft.Icons.ADD,
                        height=44,
                        on_click=self._con_cierre_de_menus(
                            self.abrir_registro_producto
                        ),
                        style=ft.ButtonStyle(
                            bgcolor=COLOR_NARANJA,
                            color=COLOR_BLANCO,
                            shape=ft.RoundedRectangleBorder(radius=9),
                        ),
                    ),
                    boton_exportar,
                ],
            ),
            padding=10,
            radius=10,
            shadow=sombra_suave(),
        )

    def _abrir_filtros(self, e=None):
        self._clic_en_boton_menu = False
        self.cerrar_menu_exportacion()
        if self._panel_filtros_abierto:
            self.cerrar_filtros()
            return

        self._controles_filtros = {}
        self._checks_filtros = {}
        self._panel_filtros, self._texto_resumen_filtros = panel_filtros(
            titulo="Filtrar productos",
            secciones=[
                self._seccion_filtro(
                    "categoria",
                    "Categoría / Subtipo",
                    ft.Icons.CATEGORY_OUTLINED,
                    self.controlador.obtener_opciones_filtro("categoria"),
                    self.filtros_seleccionados["categoria"],
                ),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_filtro(
                    "unidad_medida",
                    "Unidad de medida base",
                    ft.Icons.SCALE_OUTLINED,
                    self.controlador.obtener_opciones_filtro("unidad_medida"),
                    self.filtros_seleccionados["unidad_medida"],
                ),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_checkbox_filtro(
                    "activo",
                    "Disponibilidad",
                    ft.Icons.CHECK_CIRCLE_OUTLINED,
                    [("si", "Disponible"), ("no", "No disponible")],
                ),
                ft.Row(
                    spacing=0,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        self._seccion_checkbox_filtro(
                            "es_perecedero",
                            "Perecedero",
                            ft.Icons.ECO_OUTLINED,
                            [("si", "Sí"), ("no", "No")],
                            expand=True,
                        ),
                        ft.VerticalDivider(width=1, color="#E2EDF9"),
                        self._seccion_checkbox_filtro(
                            "requiere_refrigeracion",
                            "Refrigeración",
                            ft.Icons.AC_UNIT_OUTLINED,
                            [("si", "Sí"), ("no", "No")],
                            expand=True,
                        ),
                    ],
                ),
            ],
            resumen=self._resumen_filtros(),
            on_limpiar=self.limpiar_filtros,
            on_aplicar=self.aplicar_filtros,
            on_cerrar=self.cerrar_filtros,
            top=218,
            right=324,
            width=340,
            height=405,
        )
        self._layout_principal.controls.append(self._panel_filtros)
        self._panel_filtros_abierto = True
        if self.page is not None:
            self.update()

    def _resumen_filtros(self):
        filtros = {
            clave: control.value
            for clave, control in self._controles_filtros.items()
        }
        filtros.update(
            {
                clave: {
                    valor
                    for (grupo, valor), checkbox in self._checks_filtros.items()
                    if grupo == clave and checkbox.value
                }
                for clave in (
                    "activo",
                    "es_perecedero",
                    "requiere_refrigeracion",
                )
            }
        )
        cantidad = self._cantidad_filtros(filtros)
        return (
            "1 filtro seleccionado"
            if cantidad == 1
            else f"{cantidad} filtros seleccionados"
        )

    def limpiar_filtros(self, e=None):
        valores_iniciales = {
            "categoria": "todas",
            "unidad_medida": "todas",
            "activo": set(),
            "es_perecedero": set(),
            "requiere_refrigeracion": set(),
        }
        for clave, control in self._controles_filtros.items():
            control.value = valores_iniciales[clave]
        for (clave, _), checkbox in self._checks_filtros.items():
            checkbox.value = False
        self.filtros_seleccionados = valores_iniciales
        self.categoria = "todas"
        self.unidad = "todas"
        self.pagina_actual = 1
        self._actualizar_indicador_filtros()
        self._actualizar_resultados()
        self._actualizar_resumen_filtros()

    def aplicar_filtros(self, e=None):
        self.filtros_seleccionados = {
            clave: control.value or "todas"
            for clave, control in self._controles_filtros.items()
        }
        for clave in (
            "activo",
            "es_perecedero",
            "requiere_refrigeracion",
        ):
            self.filtros_seleccionados[clave] = {
                valor
                for (grupo, valor), checkbox in self._checks_filtros.items()
                if grupo == clave and checkbox.value
            }
        self.categoria = self.filtros_seleccionados["categoria"]
        self.unidad = self.filtros_seleccionados["unidad_medida"]
        self.pagina_actual = 1
        self._actualizar_indicador_filtros()
        self._actualizar_resultados()
        self.cerrar_filtros()

    def cerrar_filtros(self, e=None):
        if not self._panel_filtros_abierto:
            return
        if self._panel_filtros in self._layout_principal.controls:
            self._layout_principal.controls.remove(self._panel_filtros)
        self._panel_filtros_abierto = False
        if self.page is not None:
            self.update()

    def alternar_menu_exportacion(self, e=None):
        self._clic_en_boton_menu = False
        self.cerrar_filtros()
        self._menu_exportacion_abierto = not self._menu_exportacion_abierto
        self._actualizar_menu_exportacion()

    def cerrar_menus(self, e=None):
        self.cerrar_menu_exportacion()
        self.cerrar_filtros()

    def cerrar_menu_exportacion(self, e=None):
        if not self._menu_exportacion_abierto:
            return
        self._menu_exportacion_abierto = False
        self._actualizar_menu_exportacion()

    def _actualizar_menu_exportacion(self):
        if self._menu_exportacion_abierto:
            self._texto_resumen_exportacion.value = self._descripcion_exportacion()
        self._menu_exportacion.visible = self._menu_exportacion_abierto
        if self.page is not None:
            self._menu_exportacion.update()

    def _clic_fuera_de_menus(self, e=None):
        if not self._clic_en_boton_menu:
            self.cerrar_menus()

    def _marcar_clic_en_boton_menu(self, e=None):
        self._clic_en_boton_menu = True

    def _limpiar_clic_en_boton_menu(self, e=None):
        self._clic_en_boton_menu = False

    def _hay_filtros_exportacion(self):
        return bool(self.busqueda.strip() or self._cantidad_filtros())

    def _actualizar_boton_exportar(self):
        filtrados = self._hay_filtros_exportacion()
        self._texto_boton_exportar.value = (
            "Exportar filtrados" if filtrados else "Exportar"
        )
        self._boton_exportar.width = 190 if filtrados else 145

    def _descripcion_exportacion(self):
        if self._hay_filtros_exportacion():
            return "Elige un formato para exportar los productos filtrados."
        return "Elige un formato para exportar los productos del catálogo."

    def _informar_exportacion(self, formato):
        self.cerrar_menu_exportacion()
        self._page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Exportación no disponible"),
                content=ft.Text(
                    f"La exportación de productos a {formato} todavía "
                    "no está conectada."
                ),
                actions=[
                    ft.TextButton(
                        "Aceptar",
                        on_click=lambda e: self._page.pop_dialog(),
                    )
                ],
            )
        )

    async def _exportar_productos_excel(self, e=None):
        self.cerrar_menu_exportacion()
        try:
            productos, columnas = self.controlador.obtener_datos_exportacion(
                self._filtrar_productos()
            )
            guardado = await exportar_excel(
                self._page,
                productos,
                columnas,
                "productos.xlsx",
                nombre_hoja="Productos",
            )
            if guardado:
                mostrar_notificacion(
                    self._page,
                    f"Se exportaron {len(productos)} productos a Excel.",
                    COLOR_VERDE,
                )
        except Exception as error:
            mostrar_notificacion(
                self._page,
                f"No se pudieron exportar los productos: {error}",
                COLOR_ROJO,
            )

    def _con_cierre_de_menus(self, accion):
        def ejecutar(*args, **kwargs):
            try:
                return accion(*args, **kwargs)
            finally:
                self.cerrar_menus()

        return ejecutar

    def _crear_botones_vista(self):
        return ft.Row(
            spacing=6,
            controls=[
                boton_vista(
                    ft.Icons.GRID_VIEW,
                    "Vista de catálogo",
                    self.vista == "catalogo",
                    self._con_cierre_de_menus(
                        lambda e: self.cambiar_vista("catalogo")
                    ),
                ),
                boton_vista(
                    ft.Icons.VIEW_LIST_OUTLINED,
                    "Vista de lista",
                    self.vista == "lista",
                    self._con_cierre_de_menus(
                        lambda e: self.cambiar_vista("lista")
                    ),
                ),
            ],
        )

    # ---------------------------------------------------------
    # VISTAS DE PRODUCTOS
    # ---------------------------------------------------------
    def _crear_vista(self, productos):
        if not productos:
            return ft.Container(
                expand=True,
                alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(
                            ft.Icons.INVENTORY_2_OUTLINED,
                            size=42,
                            color=COLOR_GRIS,
                        ),
                        ft.Text(
                            "No se encontraron productos",
                            size=16,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            "Prueba cambiando la búsqueda o los filtros.",
                            size=13,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
            )

        if self.vista == "lista":
            return ft.ListView(
                expand=True,
                spacing=8,
                padding=ft.Padding(2, 2, 2, 2),
                controls=[
                    fila_producto(p, on_info=self.ver_producto)
                    for p in productos
                ],
            )

        return ft.GridView(
            expand=True,
            max_extent=330,
            child_aspect_ratio=1.02,
            spacing=12,
            run_spacing=12,
            padding=ft.Padding(2, 2, 2, 2),
            controls=[
                tarjeta_producto(p, on_info=self.ver_producto)
                for p in productos
            ],
        )

    def _crear_paginacion(self, total):
        total_paginas = max(
            1,
            (total + self.registros_por_pagina - 1)
            // self.registros_por_pagina,
        )

        controles = [
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                tooltip="Página anterior",
                icon_color=COLOR_GRIS,
                disabled=self.pagina_actual <= 1,
                on_click=lambda e: self.cambiar_pagina(
                    self.pagina_actual - 1
                ),
            )
        ]

        for pagina in range(1, total_paginas + 1):
            controles.append(
                ft.Container(
                    width=34,
                    height=34,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=(
                        COLOR_AZUL
                        if pagina == self.pagina_actual
                        else "transparent"
                    ),
                    border_radius=8,
                    ink=True,
                    on_click=lambda e, p=pagina: self.cambiar_pagina(p),
                    content=ft.Text(
                        str(pagina),
                        size=13,
                        color=(
                            COLOR_BLANCO
                            if pagina == self.pagina_actual
                            else COLOR_GRIS
                        ),
                        weight=(
                            ft.FontWeight.BOLD
                            if pagina == self.pagina_actual
                            else ft.FontWeight.NORMAL
                        ),
                    ),
                )
            )

        controles.append(
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                tooltip="Página siguiente",
                icon_color=COLOR_GRIS,
                disabled=self.pagina_actual >= total_paginas,
                on_click=lambda e: self.cambiar_pagina(
                    self.pagina_actual + 1
                ),
            )
        )

        return ft.Row(
            controls=controles,
            spacing=2,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    # ---------------------------------------------------------
    # ACTUALIZAR CATALOGO
    # ---------------------------------------------------------
    def _actualizar_resultados(self, actualizar=True):
        self._actualizar_boton_exportar()
        self._productos_filtrados = self._filtrar_productos()
        total = len(self._productos_filtrados)

        paginas = max(
            1,
            (total + self.registros_por_pagina - 1)
            // self.registros_por_pagina,
        )

        self.pagina_actual = min(self.pagina_actual, paginas)

        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        actuales = self._productos_filtrados[
            inicio:inicio + self.registros_por_pagina
        ]

        self._zona_productos.content = self._crear_vista(actuales)

        self._zona_catalogo.content = card(
            ft.Column(
                expand=True,
                spacing=12,
                controls=[
                    ft.Row(
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
                                    ft.Icons.INVENTORY_2_OUTLINED,
                                    size=25,
                                    color=COLOR_BLANCO,
                                ),
                            ),
                            ft.Column(
                                expand=True,
                                spacing=3,
                                controls=[
                                    ft.Text(
                                        "Listado de productos",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_NEGRO,
                                    ),
                                    ft.Text(
                                        f"{total} productos en el catálogo",
                                        size=12,
                                        color=COLOR_GRIS,
                                    ),
                                ],
                            ),
                            self._botones_vista,
                        ],
                    ),
                    ft.Divider(height=1, color=COLOR_GRIS_CLARO),
                    self._zona_productos,
                ],
            ),
            padding=ft.Padding(12, 11, 12, 11),
            radius=12,
            shadow=sombra_suave(),
        )

        self._texto_total.value = f"{total} productos en el catálogo"
        self._control_paginacion.content = self._crear_paginacion(total)

        if actualizar and self.page is not None:
            self.update()

    # ---------------------------------------------------------
    # INFORMACION DEL PRODUCTO
    # ---------------------------------------------------------
    def ver_producto(self, producto):
        self._page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(
                    producto["nombre"],
                    color=COLOR_BANNER,
                    weight=ft.FontWeight.BOLD,
                ),
                content=ft.Column(
                    tight=True,
                    spacing=8,
                    controls=[
                        ft.Text(producto["descripcion"], color=COLOR_GRIS),
                        ft.Text(
                            f"Categoría: {producto['categoria']}",
                            color=COLOR_NEGRO,
                        ),
                        ft.Text(
                            f"Unidad de medida: {producto['unidad_medida']}",
                            color=COLOR_NEGRO,
                        ),
                        ft.Text(
                            "El precio se definirá en cada cotización.",
                            color=COLOR_GRIS,
                            italic=True,
                        ),
                    ],
                ),
                actions=[
                    ft.TextButton(
                        "Cerrar",
                        on_click=lambda e: self._page.pop_dialog(),
                    )
                ],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )

    # ---------------------------------------------------------
    # NAVEGACION ENTRE CATALOGO Y REGISTRO
    # ---------------------------------------------------------
    def abrir_registro_producto(self, e=None):
        # Reemplaza solamente el contenido de esta pantalla.
        # No modifica page.controls ni elimina el contenedor principal.
        self.cerrar_menus()
        self.content = PantallaRegistrarProducto(
            page=self._page,
            vista_anterior=self,
            controlador=self.controlador,
        )

        self.update()

    def build_ui(self):
        # Reconstruye el catálogo dentro del mismo contenedor.
        self._panel_filtros_abierto = False
        self._menu_exportacion_abierto = False
        self._columna_contenido = ft.Column(
            expand=True,
            spacing=12,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                ft.Column(
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        self.cabecera_productos(),
                        self.barra_herramientas(),
                    ],
                ),
                self._zona_catalogo,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self._texto_total,
                        self._control_paginacion,
                    ],
                ),
            ],
        )
        self._contenido = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[
                ft.GestureDetector(
                    expand=True,
                    on_tap_down=self._clic_fuera_de_menus,
                    content=self._columna_contenido,
                ),
                self._menu_exportacion,
            ],
        )

        self._layout_principal = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[
                ft.Column(
                    expand=True,
                    scroll=ft.ScrollMode.AUTO,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=[
                        ft.Container(
                            expand=True,
                            padding=ft.Padding(14, 8, 14, 16),
                            content=self._contenido,
                        )
                    ],
                )
            ],
        )
        self.content = self._layout_principal

        self._actualizar_resultados(actualizar=False)
