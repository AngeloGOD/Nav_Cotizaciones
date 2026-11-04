class ControladorProductos:
    COLUMNAS_EXPORTACION = {
        "Producto": "nombre",
        "Código / SKU": "sku",
        "Categoría": "categoria",
        "Descripción": "descripcion",
        "Unidad de medida": "unidad_medida",
        "Presentación": "presentacion",
        "Estado": "estado",
        "Perecedero": "es_perecedero",
        "Requiere refrigeración": "requiere_refrigeracion",
    }
    COLUMNAS_PDF = {
        "Producto": "nombre",
        "Código / SKU": "sku",
        "Categoría": "categoria",
        "Descripción": "descripcion",
        "Unidad de medida": "unidad_medida",
        "Presentación": "presentacion",
        "Estado": "estado",
        "Perecedero": lambda producto: (
            "Sí" if producto["es_perecedero"] else "No"
        ),
        "Requiere refrigeración": lambda producto: (
            "Sí" if producto["requiere_refrigeracion"] else "No"
        ),
    }

    def __init__(self, productos=None):
        origen = self._productos_demo() if productos is None else productos
        self.productos = [self.normalizar(producto) for producto in origen]

    @staticmethod
    def _productos_demo():
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
                "nombre": nombre,
                "categoria": categoria,
                "descripcion": descripcion,
                "unidad_medida": unidad,
                "presentacion": presentacion,
                "imagen": fotos.format(imagen),
            }
            for nombre, categoria, descripcion, unidad, presentacion, imagen in datos
        ]

    @staticmethod
    def normalizar(producto):
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
                    "nombre_categoria",
                    getattr(categoria, "value", "Otros productos"),
                ),
                "unidad_medida": (
                    getattr(producto, "unidad_medida", None)
                    or getattr(concepto, "unidad_medida", "Unidad")
                ),
                "imagen": getattr(producto, "imagen", ""),
                "sku": (
                    getattr(producto, "sku_interno", None)
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
                "nombre_categoria",
                getattr(categoria, "value", "Otros productos"),
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

    def obtener_opciones_filtro(self, campo):
        valores = sorted(
            {
                producto[campo]
                for producto in self.productos
                if producto.get(campo)
            }
        )
        etiqueta_todas = (
            "Todas las categorías"
            if campo == "categoria"
            else "Todas las unidades"
        )
        return [("todas", etiqueta_todas)] + [(valor, valor) for valor in valores]

    def obtener_productos_filtrados(self, busqueda="", filtros=None):
        filtros = filtros or {}
        texto = (busqueda or "").strip().casefold()
        resultado = []

        for producto in self.productos:
            buscar_en = " ".join(
                str(producto.get(campo, ""))
                for campo in ("nombre", "sku")
            ).casefold()
            if texto and texto not in buscar_en:
                continue

            categoria = filtros.get("categoria", "todas")
            if categoria != "todas" and producto["categoria"] != categoria:
                continue

            unidad_medida = filtros.get("unidad_medida", "todas")
            if (
                unidad_medida != "todas"
                and producto["unidad_medida"] != unidad_medida
            ):
                continue

            filtros_booleanos = (
                ("activo", "activo"),
                ("es_perecedero", "es_perecedero"),
                ("requiere_refrigeracion", "requiere_refrigeracion"),
            )
            if any(
                filtros.get(nombre_filtro)
                and ("si" if bool(producto[campo]) else "no")
                not in filtros[nombre_filtro]
                for nombre_filtro, campo in filtros_booleanos
            ):
                continue

            resultado.append(producto)

        return resultado

    @staticmethod
    def validar_imagen(nombre, tamano):
        extension = nombre.rsplit(".", 1)[-1].lower()
        if extension not in {"jpg", "jpeg", "png"}:
            return "Selecciona una imagen JPG o PNG."
        if tamano > 2 * 1024 * 1024:
            return "La imagen debe pesar 2 MB o menos."
        return None

    @classmethod
    def obtener_datos_exportacion(cls, productos):
        filas = [
            {
                "nombre": producto["nombre"],
                "sku": producto["sku"],
                "categoria": producto["categoria"],
                "descripcion": producto["descripcion"],
                "unidad_medida": producto["unidad_medida"],
                "presentacion": producto["presentacion"],
                "estado": (
                    "Activo" if producto.get("activo", True) else "Inactivo"
                ),
                "es_perecedero": producto["es_perecedero"],
                "requiere_refrigeracion": producto["requiere_refrigeracion"],
            }
            for producto in productos
        ]
        return filas, cls.COLUMNAS_EXPORTACION

    def registrar_producto(self, datos):
        raise NotImplementedError("El registro de productos aún no está conectado.")

    def obtener_productos(self, pagina=1, limite=10, filtros=None):
        raise NotImplementedError("La consulta del catálogo desde la base de datos aún no está conectada.")

    def obtener_producto(self, producto_id):
        raise NotImplementedError("La consulta de un producto aún no está conectada.")

    def buscar_productos(self, texto):
        raise NotImplementedError("La búsqueda de productos en la base de datos aún no está conectada.")

    def modificar_producto(self, producto_id, datos):
        raise NotImplementedError("La modificación de productos aún no está conectada.")

    def eliminar_producto(self, producto_id):
        raise NotImplementedError("La eliminación de productos aún no está conectada.")
