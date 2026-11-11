
import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import (
    campo,
    boton,
    card,
    banner_imagen_desvanecida,
    sombra_suave,
    campo_con_mensaje_error,
    crear_mensaje_validacion,
    validar_campo,
    validar_campos,
    validador_numero,
    validador_requerido,
    vincular_validacion_campo,
)
from fuente.negocio.controlador.ControladorProductos import ControladorProductos
from fuente.utilidades.ExportacionArchivos import obtener_selector_archivos


class PantallaRegistrarProducto(ft.Container):
    def __init__(self, page: ft.Page, vista_anterior=None, controlador=None):
        super().__init__(expand=True, bgcolor=COLOR_FONDO)

        self._page = page
        self.vista_anterior = vista_anterior
        self.controlador = controlador or ControladorProductos([])

        self.nombre = self.ajustar_campo(
            campo("Ej. Agua embotellada", ft.Icons.SHOPPING_BAG_OUTLINED)
        )
        self.categoria = self.dropdown(
            "Selecciona una categoría",
            [
                ("agua", "Agua embotellada"),
                ("alimentos", "Alimentos"),
                ("bebidas", "Bebidas"),
                ("agregar", "Añadir categoría"),
            ],
            editable=True,
            enable_filter=True,
        )
        self.categoria.on_select = self.seleccionar_categoria
        self.categoria_personalizada = self.ajustar_campo(
            campo("Escribe el nombre de la categoría", None)
        )
        self.campo_categoria = ft.Container(content=self.categoria)
        self.sku = self.ajustar_campo(
            campo("Ej. AGU-001", ft.Icons.BARCODE_READER)
        )
        self._archivo_imagen = None
        self._selector_archivos = obtener_selector_archivos(page)
        self.boton_imagen = ft.OutlinedButton(
            content=self.contenido_boton_imagen(),
            on_click=self.seleccionar_imagen,
            expand=18,
            height=64,
            style=ft.ButtonStyle(
                side=ft.BorderSide(1, "#B8D3F8"),
                shape=ft.RoundedRectangleBorder(radius=9),
                padding=ft.Padding(8, 4, 8, 4),
            ),
        )
        self.unidad = self.dropdown(
            "Selecciona una unidad",
            [
                ("pieza", "Pieza"),
                ("caja", "Caja"),
                ("kilogramo", "Kilogramo"),
                ("litro", "Litro"),
                ("tonelada", "Tonelada"),
            ],
        )
        self.presentacion = self.ajustar_campo(
            campo("Ej. Caja 10 KG", ft.Icons.INVENTORY_2_OUTLINED)
        )
        self.factor = self.ajustar_campo(
            campo("Ej. 10", ft.Icons.SWAP_HORIZ)
        )
        self.costo = self.ajustar_campo(
            campo("0.00", ft.Icons.ATTACH_MONEY)
        )
        self.margen = self.ajustar_campo(
            campo("15.00", ft.Icons.PERCENT)
        )
        self.precio = self.ajustar_campo(
            campo("0.00", ft.Icons.SELL_OUTLINED)
        )
        self.descripcion_es = self.ajustar_campo(
            campo(
                "Describe el producto en español...",
                None,
                multiline=True,
                min_lines=3,
                max_lines=3,
            ),
            altura=72,
        )
        self.descripcion_en = self.ajustar_campo(
            campo(
                "Product description in English...",
                None,
                multiline=True,
                min_lines=3,
                max_lines=3,
            ),
            altura=72,
        )

        self.perecedero = ft.Switch(
            value=False,
            active_color=COLOR_NARANJA,
        )
        self.refrigeracion = ft.Switch(
            value=False,
            active_color=COLOR_NARANJA,
        )
        self.activo = ft.Switch(
            value=True,
            active_color=COLOR_NARANJA,
        )

        self._errores_validacion = {
            campo: crear_mensaje_validacion(reservar_espacio=True)
            for campo in (
                "nombre",
                "categoria",
                "unidad",
                "factor",
                "costo",
                "margen",
                "precio",
                "descripcion_es",
            )
        }
        self._validaciones = {
            "nombre": (
                self.nombre,
                self._errores_validacion["nombre"],
                validador_requerido("el nombre del producto"),
            ),
            "categoria": (
                self.categoria,
                self._errores_validacion["categoria"],
                self._validar_categoria,
                (self.categoria_personalizada,),
            ),
            "unidad": (
                self.unidad,
                self._errores_validacion["unidad"],
                validador_requerido("la unidad de medida"),
            ),
            "factor": (
                self.factor,
                self._errores_validacion["factor"],
                validador_numero(
                    "El factor de conversión",
                    minimo=0,
                    minimo_exclusivo=True,
                ),
            ),
            "costo": (
                self.costo,
                self._errores_validacion["costo"],
                validador_numero("El costo", minimo=0),
            ),
            "margen": (
                self.margen,
                self._errores_validacion["margen"],
                validador_numero("El margen", minimo=0),
            ),
            "precio": (
                self.precio,
                self._errores_validacion["precio"],
                validador_numero("El precio", minimo=0),
            ),
            "descripcion_es": (
                self.descripcion_es,
                self._errores_validacion["descripcion_es"],
                validador_requerido("la descripción en español"),
            ),
        }
        for clave, (control, mensaje_error, validador, *relacionados) in (
            self._validaciones.items()
        ):
            vincular_validacion_campo(
                control,
                mensaje_error,
                validador,
                page=self._page,
                evento=(
                    "on_select"
                    if control is self.categoria or control is self.unidad
                    else "on_change"
                ),
                controles_relacionados=(
                    relacionados[0] if relacionados else ()
                ),
            )
        vincular_validacion_campo(
            self.categoria_personalizada,
            self._errores_validacion["categoria"],
            self._validar_categoria,
            page=self._page,
            controles_relacionados=(self.categoria,),
        )

        self.content = ft.Container(
            expand=True,
            padding=ft.Padding(14, 8, 14, 10),
            content=ft.Column(
                expand=True,
                spacing=10,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    self.encabezado(),
                    self.formulario(),
                ],
            ),
        )

    # ---------------------------------------------------------
    # CAMPOS
    # ---------------------------------------------------------
    def ajustar_campo(self, control, altura=44):
        control.expand = True
        control.height = altura
        control.text_size = 14
        control.content_padding = ft.Padding(12, 8, 12, 8)
        return control

    def dropdown(self, hint, opciones, editable=False, enable_filter=False):
        return ft.Dropdown(
            hint_text=hint,
            options=[
                ft.DropdownOption(key=valor, text=texto)
                for valor, texto in opciones
            ],
            editable=editable,
            enable_filter=enable_filter,
            expand=True,
            height=44,
            text_size=14,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=ft.InputBorder.OUTLINE,
            border_color=COLOR_GRIS_CLARO,
            focused_border_color=COLOR_NARANJA,
            border_radius=9,
        )

    def campo_etiquetado(
        self, titulo, icono, control, expand=True, mensaje_error=None
    ):
        if mensaje_error is None:
            mensaje_error = crear_mensaje_validacion(reservar_espacio=True)
        return ft.Container(
            expand=expand,
            content=ft.Column(
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Row(
                        spacing=8,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                icono,
                                size=18,
                                color=COLOR_BANNER,
                            ) if icono else ft.Container(width=0),
                            ft.Text(
                                titulo,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                        ],
                    ),
                    campo_con_mensaje_error(control, mensaje_error),
                ],
            ),
        )

    def seleccionar_categoria(self, e):
        if e.control.value != "agregar":
            return

        self.campo_categoria.content = ft.Row(
            spacing=4,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.categoria_personalizada,
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    icon_size=18,
                    icon_color=COLOR_AZUL,
                    tooltip="Elegir una categoría existente",
                    on_click=self.restablecer_categoria,
                    width=36,
                    height=36,
                ),
            ],
        )
        if self._page is not None:
            self._page.update()

    def restablecer_categoria(self, e=None):
        self.categoria.value = None
        self.categoria_personalizada.value = ""
        self.campo_categoria.content = self.categoria
        validar_campo(
            self.categoria,
            self._errores_validacion["categoria"],
            self._validar_categoria,
            controles_relacionados=(self.categoria_personalizada,),
        )
        if self._page is not None:
            self._page.update()

    def _validar_categoria(self, valor=None):
        if self.categoria.value == "agregar":
            return validador_requerido("el nombre de la categoría")(
                self.categoria_personalizada.value
            )
        return validador_requerido("una categoría")(self.categoria.value)

    def contenido_boton_imagen(self):
        if self._archivo_imagen is None:
            return ft.Column(
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.IMAGE_OUTLINED,
                        size=22,
                        color=COLOR_AZUL,
                    ),
                    ft.Text("Subir imagen", size=13, color=COLOR_AZUL),
                    ft.Text(
                        "JPG, PNG · Máx. 2 MB",
                        size=10,
                        color=COLOR_GRIS,
                    ),
                ],
            )

        contenido = []
        if self._archivo_imagen.path:
            contenido.append(
                ft.Image(
                    src=self._archivo_imagen.path,
                    width=42,
                    height=42,
                    fit=ft.BoxFit.COVER,
                    border_radius=6,
                )
            )
        else:
            contenido.append(
                ft.Icon(
                    ft.Icons.IMAGE_OUTLINED,
                    size=24,
                    color=COLOR_AZUL,
                )
            )
        contenido.append(
            ft.Column(
                expand=True,
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Text(
                        self._archivo_imagen.name,
                        size=11,
                        color=COLOR_AZUL,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        "Toca para cambiar",
                        size=10,
                        color=COLOR_GRIS,
                    ),
                ],
            )
        )
        return ft.Row(
            spacing=8,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=contenido,
        )

    async def seleccionar_imagen(self, e=None):
        archivos = await self._selector_archivos.pick_files(
            dialog_title="Seleccionar imagen del producto",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["jpg", "jpeg", "png"],
            allow_multiple=False,
        )
        if not archivos:
            return

        archivo = archivos[0]
        error = self.controlador.validar_imagen(archivo.name, archivo.size)
        if error:
            self.mostrar_error_imagen(error)
            return

        self._archivo_imagen = archivo
        self.boton_imagen.content = self.contenido_boton_imagen()
        self._page.update()

    def mostrar_error_imagen(self, mensaje):
        self._page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Imagen no válida"),
                content=ft.Text(mensaje),
                actions=[
                    ft.TextButton(
                        "Aceptar",
                        on_click=lambda e: self._page.pop_dialog(),
                    )
                ],
            )
        )

    # ---------------------------------------------------------
    # ENCABEZADO
    # ---------------------------------------------------------
    def encabezado(self):
        return banner_imagen_desvanecida(
            "fondo_puerto.jpg",
            altura=136,
            shadow=sombra_suave(),
            content=ft.Container(
                expand=True,
                padding=ft.Padding(22, 8, 22, 8),
                content=ft.Row(
                    spacing=18,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=68,
                            height=68,
                            border_radius=34,
                            bgcolor="#FFF0E5",
                            alignment=ft.Alignment(0, 0),
                            content=ft.Icon(
                                ft.Icons.INVENTORY_2_OUTLINED,
                                size=36,
                                color=COLOR_NARANJA,
                            ),
                        ),
                        ft.Column(
                            expand=True,
                            spacing=4,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    "REGISTRO DE PRODUCTOS",
                                    size=11,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                ),
                                ft.Text(
                                    "Registrar nuevo producto",
                                    size=29,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                ),
                                ft.Text(
                                    "Configura la información comercial y logística del producto.",
                                    size=16,
                                    color=COLOR_BANNER,
                                    max_lines=2,
                                ),
                            ],
                        ),
                    ],
                ),
            ),
        )

    # ---------------------------------------------------------
    # FORMULARIO
    # ---------------------------------------------------------
    def formulario(self):
        altura_fila_superior = 172
        altura_fila_inferior = 150

        informacion_basica = self.seccion(
            ft.Icons.ASSIGNMENT_OUTLINED,
            "Información básica del producto",
            ft.Row(
                spacing=18,
                controls=[
                    self.campo_etiquetado(
                        "Nombre del producto *",
                        ft.Icons.SHOPPING_BAG_OUTLINED,
                        self.nombre,
                        expand=21,
                        mensaje_error=self._errores_validacion["nombre"],
                    ),
                    self.campo_etiquetado(
                        "Categoría / Subtipo *",
                        ft.Icons.CATEGORY_OUTLINED,
                        self.campo_categoria,
                        expand=18,
                        mensaje_error=self._errores_validacion["categoria"],
                    ),
                    self.campo_etiquetado(
                        "SKU / Código interno",
                        ft.Icons.BARCODE_READER,
                        self.sku,
                        expand=18,
                    ),
                    self.boton_imagen,
                ],
            ),
            altura=142,
        )

        presentacion = self.seccion(
            ft.Icons.LOCAL_SHIPPING_OUTLINED,
            "Presentación y empaque logístico",
            ft.Row(
                spacing=14,
                controls=[
                    self.campo_etiquetado(
                        "Unidad de medida base *",
                        ft.Icons.SCALE_OUTLINED,
                        self.unidad,
                        mensaje_error=self._errores_validacion["unidad"],
                    ),
                    self.campo_etiquetado(
                        "Presentación estándar",
                        ft.Icons.INVENTORY_2_OUTLINED,
                        self.presentacion,
                    ),
                    self.campo_etiquetado(
                        "Factor de conversión *",
                        ft.Icons.SWAP_HORIZ,
                        self.factor,
                        mensaje_error=self._errores_validacion["factor"],
                    ),
                ],
            ),
            altura=altura_fila_superior,
        )

        costos = self.seccion(
            ft.Icons.PRICE_CHANGE_OUTLINED,
            "Costos y márgenes financieros (MXN)",
            ft.Column(
                spacing=0,
                controls=[
                    ft.Row(
                        spacing=14,
                        controls=[
                            self.campo_etiquetado(
                                "Costo de compra (MXN) *",
                                ft.Icons.ATTACH_MONEY,
                                self.costo,
                                mensaje_error=self._errores_validacion["costo"],
                            ),
                            self.campo_etiquetado(
                                "Margen de agencia (%) *",
                                ft.Icons.PERCENT,
                                self.margen,
                                mensaje_error=self._errores_validacion["margen"],
                            ),
                            self.campo_etiquetado(
                                "Precio de venta (MXN) *",
                                ft.Icons.SELL_OUTLINED,
                                self.precio,
                                mensaje_error=self._errores_validacion["precio"],
                            ),
                        ],
                    ),
                ],
            ),
            control_derecho=ft.Icon(
                ft.Icons.INFO_OUTLINE,
                size=22,
                color=COLOR_AZUL,
                tooltip=(
                    "El precio de venta se calcula automáticamente con el "
                    "costo y el margen. Puedes ajustarlo manualmente."
                ),
            ),
            altura=altura_fila_inferior,
        )
        descripciones = card(
            ft.Column(
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Container(
                        height=38,
                        content=ft.Row(
                            spacing=10,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(
                                    ft.Icons.LANGUAGE_OUTLINED,
                                    size=22,
                                    color=COLOR_NARANJA,
                                ),
                                ft.Text(
                                    "Descripciones multilenguaje",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_BANNER,
                                ),
                                ft.Container(expand=True),
                                ft.OutlinedButton(
                                    content=ft.Row(
                                        spacing=6,
                                        tight=True,
                                        controls=[
                                            ft.Icon(
                                                ft.Icons.AUTO_FIX_HIGH,
                                                size=18,
                                                color=COLOR_AZUL,
                                            ),
                                            ft.Text(
                                                "Traducir automáticamente",
                                                size=14,
                                                color=COLOR_AZUL,
                                            ),
                                        ],
                                    ),
                                    height=34,
                                    style=ft.ButtonStyle(
                                        side=ft.BorderSide(1, "#C9DDF7"),
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                        padding=ft.Padding(10, 0, 10, 0),
                                    ),
                                ),
                            ],
                        ),
                    ),
                    ft.Row(
                        spacing=14,
                        controls=[
                            self.campo_etiquetado(
                                "Descripción en español *",
                                ft.Icons.TRANSLATE_OUTLINED,
                                self.descripcion_es,
                                mensaje_error=self._errores_validacion["descripcion_es"],
                            ),
                            self.campo_etiquetado(
                                "Descripción en inglés",
                                ft.Icons.G_TRANSLATE,
                                self.descripcion_en,
                            ),
                        ],
                    ),
                ],
            ),
            padding=ft.Padding(12, 5, 12, 8),
            radius=9,
            border_color="#E2EDF9",
            shadow=sombra_suave(),
        )
        descripciones.height = altura_fila_superior
        logistica = self.seccion(
            ft.Icons.ROUTE_OUTLINED,
            "Logística, conservación y estado",
            ft.Row(
                spacing=10,
                controls=[
                    self.opcion_logistica(
                        self.perecedero,
                        "Perecedero",
                        "Requiere atención especial por su vida útil.",
                        ft.Icons.ECO_OUTLINED,
                        "#25966A",
                    ),
                    self.opcion_logistica(
                        self.refrigeracion,
                        "Refrigeración",
                        "Necesita conservar la cadena de frío.",
                        ft.Icons.AC_UNIT_OUTLINED,
                        "#1687C9",
                    ),
                    self.opcion_logistica(
                        self.activo,
                        "Disponible",
                        "Disponible en el catálogo para cotizaciones.",
                        ft.Icons.CHECK_CIRCLE_OUTLINED,
                        "#20A878",
                        icono_inactivo=ft.Icons.CANCEL_OUTLINED,
                        color_inactivo=COLOR_ROJO,
                    ),
                ],
            ),
            altura=altura_fila_inferior,
        )

        columna_izquierda = ft.Column(
            spacing=10,
            controls=[presentacion, costos],
        )

        columna_derecha = ft.Column(
            spacing=10,
            controls=[descripciones, logistica],
        )

        contenido_desplazable = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                informacion_basica,
                ft.Row(
                    spacing=10,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        ft.Container(
                            expand=1,
                            content=columna_izquierda,
                        ),
                        ft.Container(
                            expand=1,
                            content=columna_derecha,
                        ),
                    ],
                ),
                ft.Container(height=16),
            ],
        )

        return card(
            ft.Column(
                expand=True,
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    contenido_desplazable,
                    self.pie_formulario(),
                ],
            ),
            padding=ft.Padding(18, 16, 18, 14),
            radius=14,
            border_color="#E0EAF5",
            shadow=sombra_suave(),
            expand=True,
        )

    # ---------------------------------------------------------
    # SECCIONES Y OPCIONES
    # ---------------------------------------------------------
    def seccion(
        self, icono, titulo, contenido, altura=None, control_derecho=None
    ):
        encabezado = [
            ft.Icon(
                icono,
                size=22,
                color=COLOR_NARANJA,
            ),
            ft.Text(
                titulo,
                size=16,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BANNER,
            ),
        ]
        if control_derecho is not None:
            encabezado.extend(
                [
                    ft.Container(expand=True),
                    control_derecho,
                ]
            )

        seccion = card(
            ft.Column(
                spacing=6,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Row(
                        height=38,
                        spacing=10,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=encabezado,
                    ),
                    contenido,
                ],
            ),
            padding=ft.Padding(12, 5, 12, 8),
            radius=9,
            border_color="#E2EDF9",
            shadow=sombra_suave(),
        )
        seccion.height = altura
        return seccion

    def opcion_logistica(
        self,
        control,
        titulo,
        descripcion,
        icono,
        color_icono,
        icono_inactivo=None,
        color_inactivo="#98A2B3",
    ):
        icono_inactivo = icono_inactivo or icono
        indicador = ft.Icon(
            icono if control.value else icono_inactivo,
            size=22,
            color=color_icono if control.value else color_inactivo,
        )

        def actualizar_indicador(e):
            activo = bool(e.control.value)
            indicador.icon = icono if activo else icono_inactivo
            indicador.color = color_icono if activo else color_inactivo
            self._page.update()

        control.on_change = actualizar_indicador

        return ft.Container(
            expand=True,
            bgcolor="#F7FAFD",
            border_radius=9,
            padding=ft.Padding(12, 8, 12, 8),
            content=ft.Row(
                spacing=8,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Column(
                        expand=True,
                        spacing=3,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Text(
                                titulo,
                                size=12,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_BANNER,
                            ),
                            ft.Text(
                                descripcion,
                                size=10,
                                color=COLOR_GRIS,
                                max_lines=3,
                            ),
                        ],
                    ),
                    ft.Column(
                        spacing=4,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            control,
                            indicador,
                        ],
                    ),
                ],
            ),
        )

    # ---------------------------------------------------------
    # BOTONES INFERIORES
    # ---------------------------------------------------------
    def pie_formulario(self):
        return card(
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    boton(
                        texto="Cancelar",
                        icono=ft.Icons.ARROW_BACK,
                        tipo="secundario",
                        width=120,
                        height=42,
                        color=COLOR_AZUL,
                        on_click=self.cancelar,
                    ),
                    boton(
                        texto="Guardar producto",
                        icono=ft.Icons.SAVE_OUTLINED,
                        tipo="principal",
                        width=200,
                        height=44,
                        on_click=self.guardar,
                    ),
                ],
            ),
            padding=ft.Padding(12, 4, 12, 4),
            radius=10,
            border_color="#E2EDF9",
            shadow=sombra_suave(),
        )

    # ---------------------------------------------------------
    # ACCIONES
    # ---------------------------------------------------------
    def cancelar(self, e=None):
        if self.vista_anterior is not None:
            self.vista_anterior.build_ui()
            self._page.update()

    def guardar(self, e=None):
        if not validar_campos(self._validaciones):
            self._page.update()
            return

        self._page.show_dialog(
            ft.AlertDialog(
                modal=True,
                title=ft.Text("Registro de productos"),
                content=ft.Text(
                    "El registro todavía no está conectado "
                    "con la base de datos."
                ),
                actions=[
                    ft.TextButton(
                        "Aceptar",
                        on_click=lambda e: self._page.pop_dialog(),
                    )
                ],
            )
        )
