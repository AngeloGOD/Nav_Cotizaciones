import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import (
    banner_imagen_desvanecida,
    boton_vista,
    card,
    fila_producto,
    sombra_suave,
    tarjeta_producto,
)


class PantallaProductos(ft.Container):
    def __init__(self, page: ft.Page, productos=None):
        super().__init__(expand=True, bgcolor=COLOR_FONDO)
        self._page = page
        self.productos = [self._normalizar(p) for p in (productos if productos is not None else self._demo())]
        self.pagina_actual = 1
        self.registros_por_pagina = 8
        self.busqueda = ""
        self.categoria = "todas"
        self.unidad = "todas"
        self.vista = "catalogo"

        self._zona_productos = ft.Container(expand=True)
        self._texto_total = ft.Text(size=13, color=COLOR_GRIS)
        self._control_paginacion = ft.Container()
        self._campo_busqueda = self._crear_busqueda()
        self._selector_categoria = self._crear_selector(
            ft.Icons.INVENTORY_2_OUTLINED, self._opciones("categoria"), self.cambiar_categoria, 235
        )
        self._selector_unidad = self._crear_selector(
            ft.Icons.STRAIGHTEN, self._opciones("unidad_medida"), self.cambiar_unidad, 205
        )

        self._contenido = ft.Column(
            expand=True,
            spacing=12,
            controls=[
                self.cabecera_productos(),
                self.barra_herramientas(),
                self._zona_productos,
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[self._texto_total, self._control_paginacion],
                ),
            ],
        )
        self.content = ft.Container(
            expand=True,
            padding=ft.Padding(14, 8, 14, 16),
            content=self._contenido,
        )
        self._actualizar_resultados(actualizar=False)

    def _demo(self):
        # Productos de muestra para revisar la interfaz; no se muestran precios.
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
            {"nombre": n, "categoria": c, "descripcion": d, "unidad_medida": u,
             "presentacion": p, "imagen": fotos.format(img)}
            for n, c, d, u, p, img in datos
        ]

    def _normalizar(self, producto):
        if isinstance(producto, dict):
            datos = producto.copy()
        else:
            concepto = getattr(producto, "concepto", producto)
            categoria = getattr(producto, "categoria", None) or getattr(producto, "categ_producto", None)
            datos = {
                "nombre": getattr(concepto, "nombre", "Producto sin nombre"),
                "descripcion": getattr(concepto, "descripcion", ""),
                "categoria": getattr(categoria, "nombre_categoria", "Otros productos"),
                "unidad_medida": getattr(producto, "unidad_medida", "Unidad"),
                "imagen": getattr(producto, "imagen", ""),
            }
        categoria = datos.get("categoria") or "Otros productos"
        if not isinstance(categoria, str):
            categoria = getattr(categoria, "nombre_categoria", "Otros productos")
        unidad = datos.get("unidad_medida") or datos.get("unidad") or "Unidad"
        return {
            **datos,
            "nombre": datos.get("nombre") or "Producto sin nombre",
            "descripcion": datos.get("descripcion") or "Sin descripción disponible.",
            "categoria": categoria,
            "unidad_medida": unidad,
            "presentacion": datos.get("presentacion") or unidad,
            "imagen": datos.get("imagen") or "",
        }

    def _opciones(self, campo):
        valores = sorted({p[campo] for p in self.productos if p.get(campo)})
        texto_todas = "Todas las categorías" if campo == "categoria" else "Todas las unidades"
        return [("todas", texto_todas)] + [(v, v) for v in valores]

    def _crear_busqueda(self):
        return ft.TextField(
            hint_text="Buscar producto por nombre, descripción o unidad de medida...",
            prefix_icon=ft.Icons.SEARCH,
            expand=True,
            height=44,
            text_size=13,
            content_padding=ft.Padding(12, 8, 12, 8),
            border={
                ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                    border_radius=8, side=ft.BorderSide(1, COLOR_GRIS_CLARO)
                ),
                ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                    border_radius=8, side=ft.BorderSide(1, COLOR_AZUL)
                ),
            },
            on_change=self.buscar,
        )

    def _crear_selector(self, icono, opciones, on_select, ancho):
        return ft.Container(
            width=ancho,
            height=44,
            bgcolor=COLOR_BLANCO,
            border=ft.Border.all(1, COLOR_GRIS_CLARO),
            border_radius=8,
            padding=ft.Padding(9, 0, 6, 0),
            content=ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(icono, size=19, color=COLOR_BANNER),
                    ft.Dropdown(
                        value="todas",
                        options=[ft.DropdownOption(key=k, text=t) for k, t in opciones],
                        on_select=on_select,
                        expand=True,
                        height=42,
                        text_size=13,
                        content_padding=ft.Padding(4, 6, 2, 6),
                        border=ft.NoInputBorder(),
                    ),
                ],
            ),
        )

    def cabecera_productos(self):
        texto = ft.Container(
            expand=True,
            padding=ft.Padding(22, 16, 22, 16),
            content=ft.Row(
                spacing=14,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=58, height=58, alignment=ft.Alignment(0, 0),
                        bgcolor=COLOR_BLANCO,
                        border=ft.Border.all(1, COLOR_GRIS_CLARO),
                        border_radius=30,
                        content=ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=32, color=COLOR_NARANJA),
                    ),
                    ft.Column(
                        expand=True, spacing=3,
                        controls=[
                            ft.Text("CATÁLOGO DE PRODUCTOS", size=11, weight=ft.FontWeight.BOLD, color=COLOR_GRIS),
                            ft.Text("Productos", size=28, weight=ft.FontWeight.BOLD, color=COLOR_BANNER),
                            ft.Text("Consulta y administra los productos por categoría.", size=14, color=COLOR_GRIS),
                        ],
                    ),
                ],
            ),
        )
        return banner_imagen_desvanecida("barco_banner_opl.png", altura=145, content=texto)

    def barra_herramientas(self):
        self._botones_vista = self._crear_botones_vista()
        return card(
            ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[self._campo_busqueda, self._selector_categoria, self._selector_unidad, self._botones_vista],
            ),
            padding=10, radius=10, shadow=sombra_suave(),
        )

    def _crear_botones_vista(self):
        return ft.Row(
            spacing=6,
            controls=[
                boton_vista(ft.Icons.GRID_VIEW, "Vista de catálogo", self.vista == "catalogo",
                            lambda e: self.cambiar_vista("catalogo")),
                boton_vista(ft.Icons.VIEW_LIST_OUTLINED, "Vista de lista", self.vista == "lista",
                            lambda e: self.cambiar_vista("lista")),
            ],
        )

    def buscar(self, e):
        self.busqueda = e.control.value or ""
        self.pagina_actual = 1
        self._actualizar_resultados()

    def cambiar_categoria(self, e):
        self.categoria = e.control.value or "todas"
        self.pagina_actual = 1
        self._actualizar_resultados()

    def cambiar_unidad(self, e):
        self.unidad = e.control.value or "todas"
        self.pagina_actual = 1
        self._actualizar_resultados()

    def cambiar_vista(self, vista):
        self.vista = vista
        self._botones_vista = self._crear_botones_vista()
        self._contenido.controls[1].content.controls[-1] = self._botones_vista
        self._actualizar_resultados()

    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        self._actualizar_resultados()

    def _filtrar_productos(self):
        texto = self.busqueda.strip().casefold()
        resultado = []
        for p in self.productos:
            buscar_en = " ".join(str(p.get(c, "")) for c in
                ("nombre", "descripcion", "categoria", "unidad_medida", "presentacion")).casefold()
            if texto and texto not in buscar_en:
                continue
            if self.categoria != "todas" and p["categoria"] != self.categoria:
                continue
            if self.unidad != "todas" and p["unidad_medida"] != self.unidad:
                continue
            resultado.append(p)
        return resultado

    def _crear_vista(self, productos):
        if not productos:
            return ft.Container(
                expand=True, alignment=ft.Alignment(0, 0),
                content=ft.Column(
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=8,
                    controls=[
                        ft.Icon(ft.Icons.INVENTORY_2_OUTLINED, size=42, color=COLOR_GRIS),
                        ft.Text("No se encontraron productos", size=16, weight=ft.FontWeight.BOLD, color=COLOR_BANNER),
                        ft.Text("Prueba cambiando la búsqueda o los filtros.", size=13, color=COLOR_GRIS),
                    ],
                ),
            )
        if self.vista == "lista":
            return ft.ListView(
                expand=True, spacing=8, padding=ft.Padding(2, 2, 2, 2),
                controls=[fila_producto(p, on_info=self.ver_producto) for p in productos],
            )
        return ft.GridView(
            expand=True, max_extent=330, child_aspect_ratio=1.02,
            spacing=12, run_spacing=12, padding=ft.Padding(2, 2, 2, 2),
            controls=[tarjeta_producto(p, on_info=self.ver_producto) for p in productos],
        )

    def _crear_paginacion(self, total):
        total_paginas = max(1, (total + self.registros_por_pagina - 1) // self.registros_por_pagina)
        controles = [
            ft.IconButton(
                icon=ft.Icons.CHEVRON_LEFT,
                tooltip="Página anterior",
                icon_color=COLOR_GRIS,
                disabled=self.pagina_actual <= 1,
                on_click=lambda e: self.cambiar_pagina(self.pagina_actual - 1),
            )
        ]
        for pagina in range(1, total_paginas + 1):
            controles.append(
                ft.Container(
                    width=34, height=34, alignment=ft.Alignment(0, 0),
                    bgcolor=COLOR_AZUL if pagina == self.pagina_actual else "transparent",
                    border_radius=8,
                    ink=True,
                    on_click=lambda e, p=pagina: self.cambiar_pagina(p),
                    content=ft.Text(
                        str(pagina), size=13,
                        color=COLOR_BLANCO if pagina == self.pagina_actual else COLOR_GRIS,
                        weight=ft.FontWeight.BOLD if pagina == self.pagina_actual else ft.FontWeight.NORMAL,
                    ),
                )
            )
        controles.append(
            ft.IconButton(
                icon=ft.Icons.CHEVRON_RIGHT,
                tooltip="Página siguiente",
                icon_color=COLOR_GRIS,
                disabled=self.pagina_actual >= total_paginas,
                on_click=lambda e: self.cambiar_pagina(self.pagina_actual + 1),
            )
        )
        return ft.Row(controls=controles, spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    def _actualizar_resultados(self, actualizar=True):
        self._productos_filtrados = self._filtrar_productos()
        total = len(self._productos_filtrados)
        paginas = max(1, (total + self.registros_por_pagina - 1) // self.registros_por_pagina)
        self.pagina_actual = min(self.pagina_actual, paginas)
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        actuales = self._productos_filtrados[inicio:inicio + self.registros_por_pagina]

        self._zona_productos.content = self._crear_vista(actuales)
        self._texto_total.value = f"{total} productos en el catálogo"
        self._control_paginacion.content = self._crear_paginacion(total)
        if actualizar and self.page is not None:
            self.update()

    def ver_producto(self, producto):
        self._page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text(producto["nombre"], color=COLOR_BANNER, weight=ft.FontWeight.BOLD),
                content=ft.Column(
                    tight=True, spacing=8,
                    controls=[
                        ft.Text(producto["descripcion"], color=COLOR_GRIS),
                        ft.Text(f"Categoría: {producto['categoria']}", color=COLOR_NEGRO),
                        ft.Text(f"Unidad de medida: {producto['unidad_medida']}", color=COLOR_NEGRO),
                        ft.Text("El precio se definirá en cada cotización.", color=COLOR_GRIS, italic=True),
                    ],
                ),
                actions=[ft.TextButton("Cerrar", on_click=lambda e: self._page.pop_dialog())],
                actions_alignment=ft.MainAxisAlignment.END,
            )
        )
