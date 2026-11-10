
import flet as ft
from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import (
    banner_modulo,
    agregar_panel_flotante,
    barra_busqueda,
    boton,
    boton_exportacion,
    boton_vista,
    card,
    estado_vacio,
    fila_producto,
    menu_exportacion,
    mostrar_notificacion,
    panel_filtros,
    quitar_panel_flotante,
    seccion_opciones_filtro,
    sombra_suave,
    tarjeta_producto,
    validar_registros_exportacion,
)
from fuente.utilidades.ExportacionExcel import exportar_excel
from fuente.utilidades.ExportacionPDF import exportar_pdf
from fuente.negocio.controlador.ControladorProductos import ControladorProductos
from fuente.presentacion.PantallaRegistrarProducto import PantallaRegistrarProducto


class PantallaProductos(ft.Container):
    def __init__(self, page: ft.Page, productos=None):
        super().__init__(expand=True, bgcolor=COLOR_FONDO)

        self._page = page
        self.controlador = ControladorProductos(productos)
        self.productos = self.controlador.productos

        self.pagina_actual = 1
        self.registros_por_pagina = 10
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
    # DATOS DE PRUEBA
    # ---------------------------------------------------------
    def _demo(self):
        fotos = "https://images.unsplash.com/{}?auto=format&fit=crop&w=700&q=80"

        datos = [
            ("Tomate rojo fresco", "Frutas y verduras", "Tomate rojo de alta calidad, ideal para consumo y distribución.", "Caja", "Cajas (10 kg)", "photo-1546094096-0df4bcaaa337"),
            ("Lechuga fresca", "Frutas y verduras", "Lechuga fresca, seleccionada y de excelente calidad.", "Caja", "Cajas (10 kg)", "photo-1622206151226-18ca2c9ab4a1"),
            ("Pepino fresco", "Frutas y verduras", "Pepino fresco, ideal para ensaladas y consumo directo.", "Kilo", "Kilos", "photo-1604977042946-1eecc30f269e"),
            ("Limón", "Frutas y verduras", "Limón fresco empacado para abastecimiento de la embarcación.", "Saco", "Sacos (15 kg)", "photo-1589927986089-35812388d1f4"),
            ("Pimiento morrón verde", "Frutas y verduras", "Pimiento de buena frescura y tamaño uniforme.", "Caja", "Cajas (10 kg)", "photo-1563565375-f3fdfdbefa83"),
            ("Zanahoria", "Frutas y verduras", "Zanahoria fresca, limpia y de gran calidad.", "Saco", "Sacos (15 kg)", "photo-1445282768818-728615cc910a"),
            ("Papa grande", "Frutas y verduras", "Papa de tamaño grande, perfecta para cocina.", "Caja", "Cajas (10 kg)", "photo-1518977676601-b53f82aba655"),
            ("Cebolla roja", "Frutas y verduras", "Cebolla roja, fresca y de excelente calidad.", "Saco", "Sacos (15 kg)", "photo-1618512496248-a07fe83aa8cb"),
            ("Aguacate Hass", "Frutas y verduras", "Aguacate de buena calidad, ideal para consumo.", "Caja", "Cajas (10 kg)", "photo-1523049673857-eb18f1d7b578"),
            ("Arrachera", "Carnes", "Corte de res para preparación de alimentos a bordo.", "Kilo", "Kilos", "photo-1607623814075-e51df1bdc82f"),
            ("Pollo entero", "Carnes", "Pollo entero para abastecimiento de cocina.", "Kilo", "Kilos", "photo-1604503468506-a8da13d82791"),
            ("Camarón de mar", "Pescados y mariscos", "Camarón de mar con cáscara, tamaño grande.", "Kilo", "Kilos", "photo-1565680018434-b513d5e5fd47"),
            ("Queso fresco", "Lácteos", "Queso fresco para consumo y preparación de alimentos.", "Kilo", "Kilos", "photo-1486297678162-eb2a19b0a32d"),
            ("Pan de caja", "Abarrotes", "Pan empacado para el consumo diario de la tripulación.", "Paquete", "Paquetes", "photo-1509440159596-0249088772ff"),
            ("Arroz grano largo", "Abarrotes", "Arroz de grano largo en saco para cocina.", "Saco", "Sacos (25 kg)", "photo-1586201375761-83865001e31c"),
            ("Agua purificada", "Bebidas", "Agua purificada embotellada en paquete.", "Caja", "Cajas", "photo-1527960471264-932f39eb5846"),
        ]

        return [
            {
                "nombre": n,
                "categoria": c,
                "descripcion": d,
                "unidad_medida": u,
                "presentacion": p,
                "imagen": fotos.format(img),
            }
            for n, c, d, u, p, img in datos
        ]

    def _normalizar(self, producto):
        if isinstance(producto, dict):
            datos = producto.copy()
        else:
            concepto = getattr(producto, "concepto", producto)
            categoria = (
                getattr(producto, "categoria", None)
                or getattr(producto, "categ_producto", None)
                or getattr(producto, "categoria_producto", None)
            )

            datos = {
                "nombre": (
                    getattr(concepto, "nombre", None)
                    or getattr(concepto, "nombre_es", "Producto sin nombre")
                ),
                "descripcion": getattr(concepto, "descripcion", ""),
                "categoria": getattr(
                    categoria,
                    "nombre",
                    getattr(
                        categoria,
                        "nombre_categoria",
                        getattr(categoria, "value", "Otros productos"),
                    ),
                ),
                "unidad_medida": getattr(producto, "unidad_medida", "Unidad"),
                "imagen": getattr(producto, "imagen", ""),
                "sku": (
                    getattr(producto, "sku", None)
                    or getattr(producto, "sku_interno", None)
                    or getattr(concepto, "codigo", "")
                ),
                "activo": getattr(concepto, "activo", True),
                "es_perecedero": getattr(producto, "es_perecedero", False),
                "requiere_refrigeracion": getattr(
                    producto,
                    "requiere_refrigeracion",
                    False,
                ),
            }

        categoria = datos.get("categoria") or "Otros productos"

        if not isinstance(categoria, str):
            categoria = getattr(
                categoria,
                "nombre",
                getattr(
                    categoria,
                    "nombre_categoria",
                    getattr(categoria, "value", "Otros productos"),
                ),
            )

        unidad = datos.get("unidad_medida") or datos.get("unidad") or "Unidad"

        return {
            **datos,
            "nombre": datos.get("nombre") or "Producto sin nombre",
            "descripcion": datos.get("descripcion") or "Sin descripción disponible.",
            "categoria": categoria,
            "unidad_medida": unidad,
            "presentacion": datos.get("presentacion") or unidad,
            "imagen": datos.get("imagen") or "",
            "sku": (
                datos.get("sku")
                or datos.get("sku_interno")
                or datos.get("codigo")
                or ""
            ),
            "activo": bool(datos.get("activo", True)),
            "es_perecedero": bool(datos.get("es_perecedero", False)),
            "requiere_refrigeracion": bool(
                datos.get("requiere_refrigeracion", False)
            ),
        }

    def _opciones(self, campo):
        valores = sorted({
            p[campo]
            for p in self.productos
            if p.get(campo)
        })

        texto_todas = (
            "Todas las categorías"
            if campo == "categoria"
            else "Todas las unidades"
        )

        return [("todas", texto_todas)] + [
            (v, v) for v in valores
        ]

    # ---------------------------------------------------------
    # BUSQUEDA Y FILTROS
    # ---------------------------------------------------------
    def _crear_busqueda(self):
        buscador = barra_busqueda(
            hint="Buscar producto por nombre o SKU/código interno...",
            on_change=self.buscar,
        )
        buscador.height = 44
        return buscador

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
        self.registros_por_pagina = 20 if vista == "lista" else 10
        self.pagina_actual = 1
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
        self._boton_filtros = boton(
            texto="Filtros",
            icono=ft.Icons.TUNE,
            tipo="secundario",
            width=160,
            height=44,
            border_color="#C9DDF7",
            on_click=self._abrir_filtros,
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
        self._boton_exportar = boton_exportacion(
            texto=self._texto_boton_exportar,
            on_click=self.alternar_menu_exportacion,
            width=190 if self._hay_filtros_exportacion() else 150,
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
            on_pdf=self._exportar_productos_pdf,
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
                    boton(
                        texto="Agregar producto",
                        icono=ft.Icons.ADD,
                        tipo="principal",
                        width=210,
                        height=44,
                        on_click=self._con_cierre_de_menus(
                            self.abrir_registro_producto
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
        agregar_panel_flotante(self._layout_principal, self._panel_filtros)
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
        quitar_panel_flotante(self._layout_principal, self._panel_filtros)
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
        self._boton_exportar.width = 190 if filtrados else 150

    def _descripcion_exportacion(self):
        if self._hay_filtros_exportacion():
            return "Elige un formato para exportar los productos filtrados."
        return "Elige un formato para exportar los productos del catálogo."

    async def _exportar_productos_excel(self, e=None):
        self.cerrar_menu_exportacion()
        try:
            productos, columnas = self.controlador.obtener_datos_exportacion(
                self._filtrar_productos()
            )
            if not validar_registros_exportacion(
                self._page, productos, "productos"
            ):
                return
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

    async def _exportar_productos_pdf(self, e=None):
        self.cerrar_menu_exportacion()
        try:
            filas, _ = self.controlador.obtener_datos_exportacion(
                self._filtrar_productos()
            )
            if not validar_registros_exportacion(
                self._page, filas, "productos"
            ):
                return
            activos = sum(fila["estado"] == "Activo" for fila in filas)
            guardado = await exportar_pdf(
                self._page,
                filas,
                self.controlador.COLUMNAS_PDF,
                "productos.pdf",
                titulo="Catálogo de productos",
                subtitulo="Gestión de productos",
                etiqueta_registros=f"Productos exportados: {len(filas)}",
                metricas={
                    "Productos": len(filas),
                    "Activos": activos,
                    "Inactivos": len(filas) - activos,
                },
                orientacion="landscape",
                columnas_centradas=(
                    "Categoría",
                    "Estado",
                    "Perecedero",
                    "Requiere refrigeración",
                ),
                nombre_registro="productos",
            )
            if guardado:
                mostrar_notificacion(
                    self._page,
                    f"Se exportaron {len(filas)} productos a PDF.",
                    COLOR_VERDE,
                )
        except Exception as error:
            mostrar_notificacion(
                self._page,
                f"No se pudieron exportar los productos a PDF: {error}",
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
            return estado_vacio(
                ft.Icons.INVENTORY_2_OUTLINED,
                "No se encontraron productos",
                "Prueba cambiando la búsqueda o los filtros.",
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

        tarjetas = [
            tarjeta_producto(producto, on_info=self.ver_producto)
            for producto in productos
        ]
        filas = []
        for inicio in range(0, len(tarjetas), 5):
            controles_fila = tarjetas[inicio:inicio + 5]
            controles_fila.extend(
                ft.Container(expand=True)
                for _ in range(5 - len(controles_fila))
            )
            filas.append(ft.Row(spacing=8, controls=controles_fila))

        return ft.Column(
            expand=True,
            spacing=8,
            controls=filas,
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
