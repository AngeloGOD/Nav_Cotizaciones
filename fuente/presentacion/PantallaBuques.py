
import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorBuque import ControladorBuque
from fuente.negocio.servicio.ServicioCategoriaBuque import ServicioCategoriaBuque
from fuente.presentacion.PantallaRegistrarBuque import PantallaRegistrarBuque
from fuente.presentacion.SelectorCliente import SelectorCliente
from fuente.presentacion.SelectorCategoriaBuque import SelectorCategoriaBuque
from fuente.infraestructura.servicios_externos.ServicioPaises import ServicioPaises


class PantallaBuques(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_buque,
        servicio_cliente,
        servicio_categoria_buque=None,
    ):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page
        self.servicio_buque = servicio_buque
        self.servicio_cliente = servicio_cliente
        self.servicio_categoria_buque = (
            servicio_categoria_buque
            if servicio_categoria_buque is not None
            else ServicioCategoriaBuque(servicio_buque.uow)
        )
        self.controlador = ControladorBuque(
            servicio_buque,
            servicio_categoria_buque=self.servicio_categoria_buque,
        )
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.total_buques = 0
        self.busqueda = ""
        self.buques_seleccionados = {}
        self.filtros_seleccionados = {
            "categorias": set(),
            "banderas": set(),
            "autopropulsion": set(),
            "propulsores": set(),
            "estados": set(),
            "trb_min": "", "trb_max": "",
            "eslora_min": "", "eslora_max": "",
            "calado_min": "", "calado_max": "",
        }
        self._checks_filtros = {}
        self._panel_filtros_abierto = False

        self.buque_seleccionado = None
        self.dialogo_confirmacion = None

        self.build_ui()

    def build_ui(self):
        self._columna_contenido = ft.Column(
            expand=True,
            spacing=12,
            controls=[
                self.cabecera_buques(),
                self.directorio(),
            ],
        )

        self._contenido = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[
                self._columna_contenido,
            ],
        )

        contenido_desplazable = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding(14, 8, 14, 16),
                    content=self._contenido,
                )
            ],
        )

        self._layout_principal = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[
                contenido_desplazable,
            ],
        )

        self.content = self._layout_principal

    def cabecera_buques(self):
        buscador = barra_busqueda(
            hint="Buscar por nombre, IMO, categoría, subtipo o bandera...",
            on_change=self.buscar,
        )
        buscador.height = 44

        self._boton_filtros = boton(
            texto="Filtros",
            icono=ft.Icons.TUNE,
            tipo="secundario",
            width=160,
            height=44,
            border_color="#C9DDF7",
            on_click=self.abrir_filtros,
        )

        boton_filtros = self._boton_filtros

        boton_registrar_buque = boton(
            texto="Registrar buque",
            icono=ft.Icons.ADD,
            tipo="principal",
            width=210,
            height=44,
            on_click=self.ir_a_registro,
        )

        barra_herramientas = card(
            ft.Row(
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    buscador,
                    boton_filtros,
                    boton_registrar_buque,
                ],
            ),
            padding=10,
            radius=10,
            border_color="#E0ECF9",
            shadow=sombra_suave(),
        )

        banner = banner_modulo(
            src="fondo_PantallaClientes.jpg",
            categoria="Gestión de buques",
            titulo="Buques",
            descripcion=(
                "Administra el directorio de buques, sus dimensiones, "
                "categorías y características técnicas."
            ),
            icono=ft.Icons.DIRECTIONS_BOAT_OUTLINED,
        )

        return ft.Column(
            spacing=10,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                banner,
                barra_herramientas,
            ],
        )

    def buscar(self, e):
        self.busqueda = e.control.value or ""
        self.pagina_actual = 1
        self.buques_seleccionados.clear()
        self.actualizar_directorio()

    # ---------------------------------------------------------
    # PANEL DE FILTROS (CONECTADO A LA CONSULTA)
    # ---------------------------------------------------------

    def _crear_boton_filtros(self):
        self._boton_filtros = boton(
            texto="Filtros",
            icono=ft.Icons.TUNE,
            tipo="secundario",
            width=160,
            height=48,
            border_color="#C9DDF7",
            on_click=self.abrir_filtros,
        )
        self._actualizar_indicador_filtros()
        return self._boton_filtros

    def abrir_filtros(self, e=None):
        if self._panel_filtros_abierto:
            self.cerrar_filtros()
            return

        self._checks_filtros = {}
        self._campos_rango_filtros = {}
        self._panel_filtros = self._crear_panel_filtros()
        # Se agrega como capa del Stack, no como elemento de la columna.
        self._layout_principal.controls.append(self._panel_filtros)
        self._panel_filtros_abierto = True
        self.update()

    def _actualizar_indicador_filtros(self):
        if not hasattr(self, "_boton_filtros"):
            return
        cantidad = self._contar_filtros()
        controles = [
            ft.Icon(ft.Icons.TUNE, size=18, color=COLOR_AZUL),
            ft.Text("Filtros", size=14, color=COLOR_AZUL),
        ]
        if cantidad:
            controles.append(ft.Container(
                width=20, height=20, alignment=ft.Alignment(0, 0),
                bgcolor="#E8F2FF", border_radius=10,
                content=ft.Text(str(cantidad), size=11, color=COLOR_AZUL,
                               weight=ft.FontWeight.BOLD),
            ))
        self._boton_filtros.content = ft.Row(
            tight=True, spacing=7, alignment=ft.MainAxisAlignment.CENTER,
            controls=controles,
        )

    def _contar_filtros(self):
        f = self.filtros_seleccionados
        return (
            sum(len(f[k]) for k in ("categorias", "banderas", "autopropulsion", "propulsores", "estados"))
            + sum(bool(f[k]) for k in ("trb_min", "trb_max", "eslora_min", "eslora_max", "calado_min", "calado_max"))
        )

    def _seccion_checks_filtro(self, titulo, clave, opciones, columnas=2):
        seleccionados = self.filtros_seleccionados[clave]
        checks = {}
        controles = []
        for valor, etiqueta in opciones:
            cb = ft.Checkbox(
                label=etiqueta, value=valor in seleccionados,
                active_color=COLOR_AZUL, label_style=ft.TextStyle(size=12, color=COLOR_NEGRO),
                on_change=self._cambio_filtro_visual,
            )
            checks[valor] = cb
            self._checks_filtros[(clave, valor)] = cb
            controles.append(ft.Container(expand=True, content=cb))
        filas = []
        for i in range(0, len(controles), columnas):
            filas.append(ft.Row(spacing=4, controls=controles[i:i + columnas]))
        return ft.Container(
            padding=ft.Padding(14, 8, 14, 8),
            content=ft.Column(spacing=5, controls=[
                ft.Text(titulo, size=12, weight=ft.FontWeight.BOLD, color=COLOR_BANNER),
                *filas,
            ]),
        )

    def _campo_rango_filtro(self, etiqueta, clave, hint):
        campo = ft.TextField(
            value=self.filtros_seleccionados.get(clave, ""),
            hint_text=hint, height=38, text_size=12,
            keyboard_type=ft.KeyboardType.NUMBER,
            content_padding=ft.Padding(9, 5, 9, 5),
            border=ft.InputBorder.OUTLINE, border_color="#C9DDF7",
            focused_border_color=COLOR_AZUL, border_radius=8,
            on_change=self._cambio_filtro_visual,
        )
        self._campos_rango_filtros[clave] = campo
        return ft.Column(expand=True, spacing=3, controls=[
            ft.Text(etiqueta, size=11, color=COLOR_GRIS), campo
        ])

    def _seccion_rango_filtro(self, titulo, prefijo, unidad):
        return ft.Container(
            padding=ft.Padding(14, 8, 14, 8),
            content=ft.Column(spacing=6, controls=[
                ft.Text(titulo, size=12, weight=ft.FontWeight.BOLD, color=COLOR_BANNER),
                ft.Row(spacing=8, controls=[
                    self._campo_rango_filtro("Mínimo", f"{prefijo}_min", f"0 {unidad}"),
                    self._campo_rango_filtro("Máximo", f"{prefijo}_max", f"Sin límite ({unidad})"),
                ]),
            ]),
        )

    def _seccion_filtro_banderas(self):
        try:
            paises = ServicioPaises.obtener_paises()
        except RuntimeError:
            paises = []

        seleccionados = self.filtros_seleccionados.get("banderas", set())
        self._busqueda_banderas_filtro = ft.TextField(
            hint_text="Buscar país...",
            prefix_icon=ft.Icons.SEARCH,
            height=38,
            text_size=12,
            content_padding=ft.Padding(9, 5, 9, 5),
            border=ft.InputBorder.OUTLINE,
            border_color="#C9DDF7",
            focused_border_color=COLOR_AZUL,
            border_radius=8,
            on_change=self._filtrar_opciones_banderas,
        )
        self._checks_banderas_filtro = {}
        self._opciones_banderas_filtro = []
        for pais in paises:
            nombre = pais["nombre"]
            cb = ft.Checkbox(
                label=f'{pais["emoji"]}  {nombre}',
                value=nombre in seleccionados,
                active_color=COLOR_AZUL,
                label_style=ft.TextStyle(size=12, color=COLOR_NEGRO),
                on_change=self._cambio_filtro_visual,
            )
            self._checks_banderas_filtro[nombre] = cb
            self._opciones_banderas_filtro.append(
                ft.Container(content=cb, visible=True)
            )

        # Mantiene visibles valores guardados previamente que no estén en la API.
        for nombre in seleccionados:
            if nombre not in self._checks_banderas_filtro:
                cb = ft.Checkbox(
                    label=f"🌐  {nombre} (valor anterior)",
                    value=True,
                    active_color=COLOR_AZUL,
                    label_style=ft.TextStyle(size=12, color=COLOR_NEGRO),
                    on_change=self._cambio_filtro_visual,
                )
                self._checks_banderas_filtro[nombre] = cb
                self._opciones_banderas_filtro.append(ft.Container(content=cb, visible=True))

        self._lista_banderas_filtro = ft.Column(
            spacing=2,
            scroll=ft.ScrollMode.AUTO,
            height=150,
            controls=self._opciones_banderas_filtro,
        )
        return ft.Container(
            padding=ft.Padding(14, 8, 14, 8),
            content=ft.Column(spacing=6, controls=[
                ft.Text("Bandera / país", size=12, weight=ft.FontWeight.BOLD, color=COLOR_BANNER),
                self._busqueda_banderas_filtro,
                self._lista_banderas_filtro,
            ]),
        )

    def _filtrar_opciones_banderas(self, e=None):
        termino = (self._busqueda_banderas_filtro.value or "").strip().casefold()
        for nombre, contenedor in zip(
            self._checks_banderas_filtro.keys(), self._opciones_banderas_filtro
        ):
            contenedor.visible = termino in nombre.casefold()
        self._lista_banderas_filtro.update()

    def _obtener_opciones_categorias_filtro(self):
        try:
            categorias = self.controlador.obtener_categorias_buque(1, limite=50)
            if categorias:
                return [(int(c.id), c.categoria) for c in categorias]
        except Exception:
            pass
        return [
            ("COMERCIAL", "Comercial"), ("TURISTICO", "Turístico"),
            ("PESQUERO", "Pesquero"), ("PETROLERO", "Petrolero"),
            ("RO_RO", "Ro-Ro"), ("RECREO_MENOR", "Recreo / Menor"),
        ]

    def _crear_panel_filtros(self):
        cantidad = self._contar_filtros()
        resumen = (
            "1 filtro seleccionado"
            if cantidad == 1
            else f"{cantidad} filtros seleccionados"
        )

        self._panel_filtros, self._texto_resumen_filtros_control = panel_filtros(
            titulo="Filtrar buques",
            secciones=[
                self._seccion_checks_filtro(
                    "Categoría del buque",
                    "categorias",
                    self._obtener_opciones_categorias_filtro(),
                ),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_rango_filtro("Arqueo bruto (TRB)", "trb", "TRB"),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_rango_filtro("Eslora (metros)", "eslora", "m"),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_rango_filtro("Calado (metros)", "calado", "m"),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_checks_filtro("Autopropulsión", "autopropulsion", [
                    ("SI", "Autopropulsado"), ("NO", "Sin autopropulsión"),
                ]),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_checks_filtro("Propulsores", "propulsores", [
                    ("SI", "Con proa/popa"), ("NO", "Sin proa/popa"),
                ]),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_checks_filtro("Estado del buque", "estados", [
                    ("ACTIVO", "Activo"), ("INACTIVO", "Inactivo"),
                ]),
                ft.Divider(height=1, color="#E2EDF9"),
                self._seccion_filtro_banderas(),
            ],
            resumen=resumen,
            on_limpiar=self.limpiar_filtros,
            on_aplicar=self.aplicar_filtros,
            on_cerrar=self.cerrar_filtros,
        )
        return self._panel_filtros

    def _texto_resumen_filtros(self):
        n = self._contar_filtros()
        return "Sin filtros seleccionados" if n == 0 else ("1 filtro seleccionado" if n == 1 else f"{n} filtros seleccionados")

    def _cambio_filtro_visual(self, e=None):
        if hasattr(self, "_texto_resumen_filtros_control"):
            self._texto_resumen_filtros_control.value = self._texto_resumen_filtros()
            self._texto_resumen_filtros_control.update()

    def limpiar_filtros(self, e=None):
        for checkbox in self._checks_filtros.values():
            checkbox.value = False
        for checkbox in getattr(self, "_checks_banderas_filtro", {}).values():
            checkbox.value = False
        for campo in self._campos_rango_filtros.values():
            campo.value = ""
        self.filtros_seleccionados = {
            "categorias": set(), "banderas": set(),
            "autopropulsion": set(), "propulsores": set(), "estados": set(),
            "trb_min": "", "trb_max": "", "eslora_min": "", "eslora_max": "",
            "calado_min": "", "calado_max": "",
        }
        self._actualizar_indicador_filtros()
        self._cambio_filtro_visual()
        self.pagina_actual = 1
        self.buques_seleccionados.clear()
        self.actualizar_directorio()

    def aplicar_filtros(self, e=None):
        # Guarda los filtros elegidos; el repositorio los aplica en PostgreSQL.
        for clave in ("categorias", "autopropulsion", "propulsores", "estados"):
            self.filtros_seleccionados[clave] = {
                valor for (grupo, valor), cb in self._checks_filtros.items()
                if grupo == clave and cb.value
            }
        self.filtros_seleccionados["banderas"] = {
            nombre for nombre, cb in getattr(self, "_checks_banderas_filtro", {}).items()
            if cb.value
        }
        for clave, campo in self._campos_rango_filtros.items():
            self.filtros_seleccionados[clave] = (campo.value or "").strip()
        self.pagina_actual = 1
        self.buques_seleccionados.clear()
        self._actualizar_indicador_filtros()
        self.cerrar_filtros()
        self.actualizar_directorio()

    def cerrar_filtros(self, e=None):
        if self._panel_filtros_abierto:
            self._layout_principal.controls = self._layout_principal.controls[:1]
            self._panel_filtros_abierto = False
            self.update()

    def ir_a_registro(self, e):
        self.content = PantallaRegistrarBuque(
            self._page,
            self.servicio_buque,
            self.servicio_cliente,
            vista_anterior=self,
            servicio_categoria_buque=self.servicio_categoria_buque,
        )
        self.update()

    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        self.buques_seleccionados.clear()
        self.actualizar_directorio()

    def actualizar_directorio(self):
        self._columna_contenido.controls[1] = self.directorio()
        self.update()


    def ver_buque(self, buque):
        """Abre la ficha del buque; la edición se realiza dentro del mismo diálogo."""
        self.buque_en_detalle = buque
        self.modo_edicion_buque = False
        self.dialogo_buque = self._crear_dialogo_buque()
        self._page.show_dialog(self.dialogo_buque)

    def _crear_dialogo_buque(self):
        return ft.AlertDialog(
            modal=True,
            bgcolor="#F4F8FC",
            shape=ft.RoundedRectangleBorder(radius=18),
            title=self._encabezado_ficha_buque(),
            title_padding=ft.Padding(18, 12, 18, 6),
            content=ft.Container(
                width=640,
                content=self._contenido_ficha_buque(),
            ),
            content_padding=ft.Padding(14, 0, 14, 0),
            actions=self._acciones_ficha_buque(),
            actions_alignment=ft.MainAxisAlignment.END,
            actions_padding=ft.Padding(14, 8, 14, 12),
            scrollable=True,
        )

    def _encabezado_ficha_buque(self):
        buque = self.buque_en_detalle
        editando = self.modo_edicion_buque
        activo = bool(getattr(buque, "activo", False))

        return ft.Row(
            spacing=13,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=54,
                    height=54,
                    border_radius=27,
                    bgcolor="#FFF0E5",
                    alignment=ft.Alignment(0, 0),
                    content=ft.Icon(
                        ft.Icons.EDIT_OUTLINED if editando else ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                        size=28,
                        color=COLOR_NARANJA,
                    ),
                ),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text(
                            "Editar buque" if editando else "Ficha del buque",
                            size=22,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            "Actualiza los datos generales y técnicos"
                            if editando
                            else (getattr(buque, "nombre", None) or "Información general y técnica"),
                            size=13,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                ft.Container(
                    padding=ft.Padding(10, 5, 10, 5),
                    border_radius=20,
                    bgcolor="#EAF7EF" if activo else "#FDECEC",
                    content=ft.Text(
                        "Activo" if activo else "Inactivo",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_VERDE if activo else COLOR_ROJO,
                    ),
                ),
                ft.IconButton(
                    icon=ft.Icons.CLOSE,
                    tooltip="Cerrar",
                    icon_color=COLOR_BANNER,
                    on_click=self.cerrar_ficha_buque,
                ),
            ],
        )



    def _contenido_ficha_buque(self):
        buque = self.buque_en_detalle
        self.campos_ficha_buque = {}

        categoria_obj = getattr(buque, "categoria_buque", None)
        categoria = (
            getattr(categoria_obj, "categoria", None)
            or (
                categoria_obj.value
                if hasattr(categoria_obj, "value")
                else str(categoria_obj or "")
            )
        )

        identificacion = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        self._campo_ficha_buque(
                            "Nombre del buque",
                            "nombre",
                            buque.nombre,
                            expand=True,
                        ),
                        self._campo_ficha_buque(
                            "Número IMO",
                            "numero_imo",
                            buque.numero_imo,
                            expand=True,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=12,
                    controls=[
                        self._campo_ficha_buque(
                            "Cliente asignado",
                            "cliente_id",
                            buque.cliente_id,
                            expand=True,
                        ),
                        self._campo_ficha_buque(
                            "Bandera / país",
                            "bandera_pais",
                            buque.bandera_pais,
                            expand=True,
                        ),
                    ],
                ),
            ],
        )

        clasificacion = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    spacing=10,
                    controls=[
                        self._campo_ficha_buque(
                            "Categoría del buque",
                            "categoria_buque",
                            categoria,
                            tipo_categoria=True,
                            expand=True,
                        ),
                        self._campo_ficha_buque(
                            "Subtipo / descripción",
                            "subtipo_descripcion",
                            buque.subtipo_descripcion,
                            expand=True,
                        ),
                    ],
                ),
            ],
        )

        caracteristicas = ft.Column(
            spacing=8,
            controls=[
                ft.Row(
                    spacing=12,
                    controls=[
                        self._campo_ficha_buque(
                            "Arqueo bruto / TRB",
                            "trb_arqueo_bruto",
                            buque.trb_arqueo_bruto,
                            expand=True,
                        ),
                        self._campo_ficha_buque(
                            "Eslora (m)",
                            "eslora_metros",
                            buque.eslora_metros,
                            expand=True,
                        ),
                    ],
                ),
                self._campo_ficha_buque(
                    "Calado (m)",
                    "calado_metros",
                    buque.calado_metros,
                    expand=True,
                ),
            ],
        )

        propulsion = ft.Column(
            spacing=6,
            controls=[
                ft.Row(
                    spacing=8,
                    controls=[
                        self._campo_ficha_buque(
                            "Autopropulsado",
                            "es_autopropulsado",
                            buque.es_autopropulsado,
                            switch=True,
                            expand=True,
                        ),
                        self._campo_ficha_buque(
                            "Propulsores proa/popa",
                            "propulsores_proa_popa",
                            buque.propulsores_proa_popa,
                            switch=True,
                            expand=True,
                        ),
                    ],
                ),
                self._campo_ficha_buque(
                    "Buque activo",
                    "activo",
                    buque.activo,
                    switch=True,
                    expand=True,
                ),
            ],
        )

        tarjetas = [
            tarjeta_detalle(
                "Identificación y cliente",
                ft.Icons.FOLDER_OUTLINED,
                identificacion,
            ),
            tarjeta_detalle(
                "Clasificación",
                ft.Icons.CATEGORY_OUTLINED,
                clasificacion,
            ),
            tarjeta_detalle(
                "Características técnicas",
                ft.Icons.STRAIGHTEN,
                caracteristicas,
            ),
            tarjeta_detalle(
                "Propulsión y estado",
                ft.Icons.SETTINGS_OUTLINED,
                propulsion,
            ),
        ]

        contenido = ft.Column(
            tight=True,
            spacing=7,
            controls=tarjetas,
        )

        if self.modo_edicion_buque:
            selector_cliente = self.campos_ficha_buque.get("cliente_id")
            selector_categoria = self.campos_ficha_buque.get("categoria_buque")

            capas = [contenido]
            if selector_cliente:
                capas.append(
                    ft.Container(
                        top=205,
                        left=14,
                        width=330,
                        content=selector_cliente.contenido_resultados,
                    )
                )
            if selector_categoria and hasattr(selector_categoria, "contenido_resultados"):
                capas.append(
                    ft.Container(
                        top=332,
                        left=14,
                        width=330,
                        content=selector_categoria.contenido_resultados,
                    )
                )
            if len(capas) > 1:
                return ft.Stack(
                    clip_behavior=ft.ClipBehavior.NONE,
                    controls=capas,
                )

        return contenido

    def _campo_ficha_buque(
        self,
        etiqueta,
        nombre,
        valor,
        expand=False,
        tipo_categoria=False,
        switch=False,
    ):
        if self.modo_edicion_buque:
            if nombre == "cliente_id":
                control = SelectorCliente(self.servicio_cliente)
                cliente_obj = getattr(self.buque_en_detalle, "cliente", None)
                control.establecer_cliente(cliente_obj)
                self.campos_ficha_buque[nombre] = control
                return campo_detalle(etiqueta, control, expand=expand)
            elif tipo_categoria:
                control = SelectorCategoriaBuque(self.servicio_categoria_buque, height=44)
                categoria_obj = getattr(self.buque_en_detalle, "categoria_buque", None)
                control.establecer_categoria(categoria_obj)
                self.campos_ficha_buque[nombre] = control
                return campo_detalle(etiqueta, control, expand=expand)
            elif nombre == "bandera_pais":
                try:
                    paises = ServicioPaises.obtener_paises()
                except RuntimeError:
                    paises = []
                opciones = [
                    ft.DropdownOption(key=p["nombre"], text=f'{p["emoji"]}  {p["nombre"]}')
                    for p in paises
                ]
                valor_actual = "" if valor is None else str(valor)
                if valor_actual and valor_actual not in {p["nombre"] for p in paises}:
                    opciones.append(ft.DropdownOption(
                        key=valor_actual, text=f"🌐  {valor_actual} (valor anterior)"
                    ))
                control = ft.Dropdown(
                    value=valor_actual or None,
                    options=opciones,
                    hint_text="Selecciona país",
                    leading_icon=ft.Icons.FLAG_OUTLINED,
                    height=44,
                    text_size=14,
                    content_padding=ft.Padding(12, 8, 12, 8),
                    border=ft.InputBorder.OUTLINE,
                    border_color=COLOR_GRIS_CLARO,
                    focused_border_color=COLOR_NARANJA,
                    border_radius=9,
                )
                self.campos_ficha_buque[nombre] = control
            elif switch:
                control = ft.Switch(
                    value=bool(valor),
                    active_color=COLOR_NARANJA,
                )
                self.campos_ficha_buque[nombre] = control
            else:
                control = ft.TextField(
                    value="" if valor is None else str(valor),
                    text_size=14,
                    content_padding=ft.Padding(12, 9, 12, 9),
                    border=ft.InputBorder.OUTLINE,
                    border_color=COLOR_GRIS_CLARO,
                    focused_border_color=COLOR_NARANJA,
                    border_radius=9,
                )
                self.campos_ficha_buque[nombre] = control

        elif switch:
            activo = bool(valor)
            color = COLOR_VERDE if activo else COLOR_ROJO
            control = ft.Container(
                bgcolor="#EAF7EF" if activo else "#FDECEC",
                border_radius=16,
                padding=ft.Padding(10, 5, 10, 5),
                content=ft.Row(
                    tight=True,
                    spacing=6,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE_OUTLINE if activo else ft.Icons.CANCEL_OUTLINED,
                            size=16,
                            color=color,
                        ),
                        ft.Text(
                            "Sí" if activo else "No",
                            color=color,
                            size=13,
                            weight=ft.FontWeight.BOLD,
                        ),
                    ],
                ),
            )
        else:
            if nombre == "cliente_id":
                cliente_obj = getattr(self.buque_en_detalle, "cliente", None)
                texto = (
                    getattr(cliente_obj, "razon_social", None)
                    or (f"ID {valor}" if valor is not None else "Sin cliente asignado")
                )
            elif nombre == "categoria_buque":
                etiquetas = {
                    "COMERCIAL": "Comercial",
                    "TURISTICO": "Turístico",
                    "PESQUERO": "Pesquero",
                    "PETROLERO": "Petrolero",
                    "RO_RO": "Ro-Ro",
                    "RECREO_MENOR": "Recreo / Menor",
                }
                categoria_obj = getattr(self.buque_en_detalle, "categoria_buque", None)
                nombre_cat = getattr(categoria_obj, "categoria", None) or valor
                texto = etiquetas.get(str(nombre_cat or "").upper(), nombre_cat or "—")
            else:
                texto = valor if valor not in (None, "") else "—"
            control = ft.Text(
                str(texto),
                color=COLOR_NEGRO,
                size=14,
                max_lines=2,
                overflow=ft.TextOverflow.ELLIPSIS,
                selectable=True,
            )

        if switch:
            return ft.Container(
                expand=expand,
                padding=ft.Padding(9, 3, 9, 3),
                bgcolor="#F0F7FC" if self.modo_edicion_buque else "#FFFFFF",
                border=ft.Border.all(1, "#E1EAF3"),
                border_radius=9,
                content=ft.Row(
                    tight=True,
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text(etiqueta, size=12, color=COLOR_NEGRO, expand=True),
                        control,
                    ],
                ),
            )
        return campo_detalle(etiqueta, control, expand=expand)

    def _acciones_ficha_buque(self):
        if self.modo_edicion_buque:
            return [
                ft.Row(
                    expand=True,
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.OutlinedButton(
                            content=ft.Row(
                                tight=True,
                                spacing=6,
                                controls=[
                                    ft.Icon(ft.Icons.DELETE_OUTLINE, color=COLOR_ROJO, size=18),
                                    ft.Text("Eliminar", color=COLOR_ROJO),
                                ],
                            ),
                            on_click=self.pedir_confirmacion_eliminacion_ficha_buque,
                            style=ft.ButtonStyle(
                                side=ft.BorderSide(1, COLOR_ROJO),
                                shape=ft.RoundedRectangleBorder(radius=8),
                            ),
                        ),
                        ft.Row(
                            spacing=9,
                            controls=[
                                ft.OutlinedButton(
                                    content=ft.Row(
                                        tight=True,
                                        spacing=6,
                                        controls=[
                                            ft.Icon(ft.Icons.CLOSE, color=COLOR_BANNER, size=18),
                                            ft.Text("Cancelar", color=COLOR_BANNER),
                                        ],
                                    ),
                                    on_click=self.cancelar_edicion_buque,
                                    style=ft.ButtonStyle(
                                        side=ft.BorderSide(1, COLOR_GRIS_CLARO),
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                ),
                                ft.FilledButton(
                                    content=ft.Row(
                                        tight=True,
                                        spacing=6,
                                        controls=[
                                            ft.Icon(ft.Icons.SAVE_OUTLINED, color=COLOR_BLANCO, size=18),
                                            ft.Text("Guardar cambios", color=COLOR_BLANCO),
                                        ],
                                    ),
                                    on_click=self.guardar_cambios_buque,
                                    style=ft.ButtonStyle(
                                        bgcolor=COLOR_VERDE,
                                        shape=ft.RoundedRectangleBorder(radius=8),
                                    ),
                                ),
                            ],
                        ),
                    ],
                )
            ]

        return [
            ft.Row(
                expand=True,
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.OutlinedButton(
                        content=ft.Row(
                            tight=True,
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.DELETE_OUTLINE, color=COLOR_ROJO, size=18),
                                ft.Text("Eliminar", color=COLOR_ROJO),
                            ],
                        ),
                        on_click=self.pedir_confirmacion_eliminacion_ficha_buque,
                        style=ft.ButtonStyle(
                            side=ft.BorderSide(1, COLOR_ROJO),
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                    ft.FilledButton(
                        content=ft.Row(
                            tight=True,
                            spacing=6,
                            controls=[
                                ft.Icon(ft.Icons.EDIT_OUTLINED, color=COLOR_BLANCO, size=18),
                                ft.Text("Editar", color=COLOR_BLANCO),
                            ],
                        ),
                        on_click=self.activar_edicion_buque,
                        style=ft.ButtonStyle(
                            bgcolor=COLOR_NARANJA,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                    ),
                ],
            )
        ]

    def _actualizar_ficha_buque(self):
        self.dialogo_buque.title = self._encabezado_ficha_buque()
        self.dialogo_buque.content = ft.Container(
            width=700,
            content=self._contenido_ficha_buque(),
        )
        self.dialogo_buque.actions = self._acciones_ficha_buque()
        self._page.update()

    def activar_edicion_buque(self, e):
        self.modo_edicion_buque = True
        self._actualizar_ficha_buque()

    def cancelar_edicion_buque(self, e):
        self.modo_edicion_buque = False
        self._actualizar_ficha_buque()

    def guardar_cambios_buque(self, e):
        campos = self.campos_ficha_buque
        nombre = (campos["nombre"].value or "").strip()
        categoria_buque_id = getattr(
            campos["categoria_buque"],
            "categoria_buque_id_seleccionada",
            None,
        )
        trb = (campos["trb_arqueo_bruto"].value or "").strip()
        eslora = (campos["eslora_metros"].value or "").strip()

        if not nombre or not categoria_buque_id or not trb or not eslora:
            self._mostrar_notificacion(
                "El nombre, la categoría, el arqueo bruto y la eslora son obligatorios.",
                COLOR_ROJO,
            )
            return

        cliente_id = campos["cliente_id"].cliente_id_seleccionado

        try:
            self.controlador.modificar_buque(
                buque=self.buque_en_detalle,
                nombre=nombre,
                categoria_buque_id=categoria_buque_id,
                trb_arqueo_bruto=trb,
                eslora_metros=eslora,
                cliente_id=cliente_id,
                numero_imo=(campos["numero_imo"].value or "").strip(),
                subtipo_descripcion=(campos["subtipo_descripcion"].value or "").strip(),
                calado_metros=(campos["calado_metros"].value or "").strip() or None,
                propulsores_proa_popa=bool(campos["propulsores_proa_popa"].value),
                es_autopropulsado=bool(campos["es_autopropulsado"].value),
                bandera_pais=(campos["bandera_pais"].value or "").strip(),
                activo=bool(campos["activo"].value),
            )
        except Exception as error:
            self._mostrar_notificacion(f"No se pudieron guardar los cambios: {error}", COLOR_ROJO)
            return

        self.modo_edicion_buque = False
        self.actualizar_directorio()
        self._actualizar_ficha_buque()
        self._mostrar_notificacion("Cambios guardados correctamente.", COLOR_VERDE)

    def pedir_confirmacion_eliminacion_ficha_buque(self, e):
        buque = self.buque_en_detalle
        self._page.show_dialog(
            dialogo_confirmacion(
                page=self._page,
                titulo="Confirmar eliminación",
                mensaje=f"¿Deseas eliminar el buque '{buque.nombre}'? Esta acción no se puede deshacer.",
                on_confirmar=lambda: self._confirmar_eliminacion_ficha_buque(buque),
                texto_confirmar="Eliminar",
                texto_cancelar="Cancelar",
                color_confirmar=COLOR_ROJO,
            )
        )

    def _confirmar_eliminacion_ficha_buque(self, buque):
        try:
            self.controlador.servicio_buque.eliminar_buque(buque)
        except Exception as error:
            self._mostrar_notificacion(f"No se pudo eliminar el buque: {error}", COLOR_ROJO)
            return

        self._page.pop_dialog()  # cierra la ficha que queda debajo de la confirmación
        self.buques_seleccionados.pop(self._clave_buque(buque), None)
        if self.pagina_actual > 1:
            registros, _ = self.controlador.obtener_buques(
                texto=self.busqueda,
                limit=self.registros_por_pagina,
                offset=(self.pagina_actual - 1) * self.registros_por_pagina,
                filtros=self.filtros_seleccionados,
            )
            if not registros:
                self.pagina_actual -= 1
        self.actualizar_directorio()
        self._mostrar_notificacion(f"Buque '{buque.nombre}' eliminado correctamente.", COLOR_VERDE)

    def cerrar_ficha_buque(self, e):
        self._page.pop_dialog()

    # ---------------------------------------------------------
    # ELIMINAR BUQUE CON CONFIRMACIÓN
    # ---------------------------------------------------------

    def eliminar_buque(self, buque):
        self.buque_seleccionado = buque

        self.dialogo_confirmacion = ft.AlertDialog(
            modal=True,
            title=ft.Text(
                "Confirmar eliminación",
                weight=ft.FontWeight.BOLD,
                color=COLOR_BANNER,
            ),
            content=ft.Text(
                f"¿Estás seguro de que deseas eliminar el buque "
                f"'{buque.nombre}'? Esta acción no se puede deshacer.",
                color=COLOR_NEGRO,
            ),
            actions=[
                ft.TextButton(
                    "Cancelar",
                    on_click=self.cancelar_eliminacion,
                ),
                ft.TextButton(
                    "Eliminar",
                    on_click=self.confirmar_eliminacion,
                    style=ft.ButtonStyle(
                        color=COLOR_ROJO,
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        self._page.show_dialog(self.dialogo_confirmacion)

    def cancelar_eliminacion(self, e):
        self._page.pop_dialog()
        self.buque_seleccionado = None
        self.dialogo_confirmacion = None

    def confirmar_eliminacion(self, e):
        buque = self.buque_seleccionado

        self._page.pop_dialog()
        self.dialogo_confirmacion = None
        self.buque_seleccionado = None

        if buque is None:
            return

        try:
            self.controlador.servicio_buque.eliminar_buque(buque)
            self.buques_seleccionados.pop(self._clave_buque(buque), None)

            self._mostrar_notificacion(
                f"Buque '{buque.nombre}' eliminado correctamente.",
                COLOR_VERDE,
            )

            # Si eliminamos el último registro de una página,
            # regresamos a la página anterior cuando corresponda.
            if (
                self.pagina_actual > 1
                and len(
                    self.controlador.obtener_buques(
                        texto=self.busqueda,
                        limit=self.registros_por_pagina,
                        offset=(self.pagina_actual - 1)
                        * self.registros_por_pagina,
                        filtros=self.filtros_seleccionados,
                    )[0]
                ) == 0
            ):
                self.pagina_actual -= 1

            self.actualizar_directorio()

        except Exception as error:
            self._mostrar_notificacion(
                f"No se pudo eliminar el buque: {error}",
                COLOR_ROJO,
            )

    def _mostrar_notificacion(self, mensaje, color):
        snack = ft.SnackBar(
            content=ft.Text(
                mensaje,
                color=COLOR_BLANCO,
            ),
            bgcolor=color,
        )

        self._page.show_dialog(snack)
        self._page.update()

    # ---------------------------------------------------------

    def _clave_buque(self, buque):
        return getattr(buque, "id_buque", getattr(buque, "id", id(buque)))

    def seleccionar_buque(self, buque, seleccionado):
        clave = self._clave_buque(buque)
        if seleccionado:
            self.buques_seleccionados[clave] = buque
        else:
            self.buques_seleccionados.pop(clave, None)
        self.actualizar_directorio()

    def seleccionar_pagina_buques(self, buques, seleccionado):
        for buque in buques:
            clave = self._clave_buque(buque)
            if seleccionado:
                self.buques_seleccionados[clave] = buque
            else:
                self.buques_seleccionados.pop(clave, None)
        self.actualizar_directorio()

    def cancelar_seleccion_buques(self, e=None):
        self.buques_seleccionados.clear()
        self.actualizar_directorio()

    def confirmar_eliminar_buques_seleccionados(self, e=None):
        cantidad = len(self.buques_seleccionados)
        if not cantidad:
            return

        self._page.show_dialog(
            dialogo_confirmacion(
                page=self._page,
                titulo="Eliminar buques seleccionados",
                mensaje=(
                    f"¿Deseas eliminar {cantidad} buque(s) seleccionado(s)? "
                    "Esta acción no se puede deshacer."
                ),
                on_confirmar=self._eliminar_buques_seleccionados,
                texto_confirmar="Eliminar",
                texto_cancelar="Cancelar",
                color_confirmar=COLOR_ROJO,
            )
        )

    def _eliminar_buques_seleccionados(self):
        seleccionados = list(self.buques_seleccionados.values())
        eliminados = 0

        try:
            for buque in seleccionados:
                self.controlador.servicio_buque.eliminar_buque(buque)
                eliminados += 1
        except Exception as error:
            for buque in seleccionados[:eliminados]:
                self.buques_seleccionados.pop(self._clave_buque(buque), None)
            self.actualizar_directorio()
            self._mostrar_notificacion(
                f"Se eliminaron {eliminados}; ocurrió un error: {error}",
                COLOR_ROJO,
            )
            return

        self.buques_seleccionados.clear()
        paginas = max(
            1,
            (max(0, self.total_buques - eliminados) + self.registros_por_pagina - 1)
            // self.registros_por_pagina,
        )
        self.pagina_actual = min(self.pagina_actual, paginas)
        self.actualizar_directorio()
        self._mostrar_notificacion(
            f"Se eliminaron {eliminados} buque(s).",
            COLOR_VERDE,
        )


    def crear_tabla_buques(self, buques):
        etiquetas_categoria = {
            "COMERCIAL": "Comercial",
            "TURISTICO": "Turístico",
            "PESQUERO": "Pesquero",
            "PETROLERO": "Petrolero",
            "RO_RO": "Ro-Ro",
            "RECREO_MENOR": "Recreo / Menor",
        }

        claves_pagina = [self._clave_buque(b) for b in buques]
        pagina_completa_seleccionada = bool(buques) and all(
            clave in self.buques_seleccionados for clave in claves_pagina
        )

        encabezado_seleccion = ft.Container(
            width=52,
            alignment=ft.Alignment(0, 0),
            content=ft.Checkbox(
                value=pagina_completa_seleccionada,
                active_color=COLOR_AZUL,
                check_color=COLOR_BLANCO,
                border_side=ft.BorderSide(1.5, "#7186A0"),
                shape=ft.RoundedRectangleBorder(radius=3),
                on_change=lambda e, bs=list(buques): self.seleccionar_pagina_buques(
                    bs, bool(e.control.value)
                ),
            ),
        )

        filas = []

        for buque in buques:
            clave = self._clave_buque(buque)
            seleccionado = clave in self.buques_seleccionados

            inicial = ft.Container(
                content=ft.Text(
                    buque.nombre[:1].upper() if buque.nombre else "?",
                    size=14,
                    color=COLOR_BLANCO,
                    weight=ft.FontWeight.BOLD,
                ),
                bgcolor=COLOR_BANNER,
                border_radius=9,
                width=35,
                height=35,
                alignment=ft.Alignment(0, 0),
            )

            cliente_obj = getattr(buque, "cliente", None)

            if cliente_obj and getattr(cliente_obj, "razon_social", None):
                texto_cliente = f"Cliente: {cliente_obj.razon_social}"
            elif buque.cliente_id is not None:
                texto_cliente = f"Cliente ID: {buque.cliente_id}"
            else:
                texto_cliente = "Sin cliente asignado"

            nombre = ft.Row(
                spacing=9,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    inicial,
                    ft.Container(
                        expand=True,
                        padding=ft.Padding(8, 0, 0, 0),
                        content=ft.Column(
                            spacing=3,
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Text(
                                    buque.nombre or "Sin nombre",
                                    size=14,
                                    color=COLOR_NEGRO,
                                    weight=ft.FontWeight.BOLD,
                                    max_lines=2,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                                ft.Text(
                                    texto_cliente,
                                    size=12,
                                    color=COLOR_GRIS,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ],
                        ),
                    ),
                ],
            )

            identificadores = ft.Column(
                spacing=3,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        f"IMO: {buque.numero_imo or 'N/A'}",
                        size=13,
                        color=COLOR_NEGRO,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
            )

            bandera = ft.Row(
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Icon(
                        ft.Icons.FLAG_OUTLINED,
                        size=16,
                        color=COLOR_GRIS,
                    ),
                    ft.Container(
                        expand=True,
                        content=ft.Text(
                            buque.bandera_pais or "N/A",
                            size=14,
                            color=COLOR_NEGRO,
                            max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ),
                ],
            )

            categoria_obj = getattr(buque, "categoria_buque", None)
            valor_cat = (
                getattr(categoria_obj, "categoria", None)
                or (
                    categoria_obj.value
                    if hasattr(categoria_obj, "value")
                    else str(categoria_obj or "")
                )
            )

            texto_cat = etiquetas_categoria.get(
                str(valor_cat).upper(),
                valor_cat or "N/A",
            )

            categoria_y_subtipo = ft.Column(
                spacing=3,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        texto_cat,
                        size=14,
                        color=COLOR_NEGRO,
                        weight=ft.FontWeight.W_500,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        buque.subtipo_descripcion or "Sin subtipo",
                        size=12,
                        color=COLOR_GRIS,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            )

            calado_texto = (
                f"{buque.calado_metros} m"
                if buque.calado_metros is not None
                else "N/A"
            )

            especificaciones = ft.Column(
                spacing=5,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=5,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.STRAIGHTEN_OUTLINED,
                                size=15,
                                color=COLOR_GRIS,
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    f"Eslora: {buque.eslora_metros} m | "
                                    f"Calado: {calado_texto}",
                                    size=13,
                                    color=COLOR_NEGRO,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ),
                        ],
                    ),
                    ft.Row(
                        spacing=5,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.SCALE_OUTLINED,
                                size=15,
                                color=COLOR_GRIS,
                            ),
                            ft.Container(
                                expand=True,
                                content=ft.Text(
                                    f"TRB: {buque.trb_arqueo_bruto}",
                                    size=13,
                                    color=COLOR_NEGRO,
                                    max_lines=1,
                                    overflow=ft.TextOverflow.ELLIPSIS,
                                ),
                            ),
                        ],
                    ),
                ],
            )

            propulsion_y_estado = ft.Column(
                spacing=3,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=5,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.CIRCLE,
                                size=10,
                                color=COLOR_VERDE if buque.activo else COLOR_ROJO,
                            ),
                            ft.Text(
                                "Activo" if buque.activo else "Inactivo",
                                size=13,
                                color=COLOR_NEGRO,
                                weight=ft.FontWeight.W_500,
                            ),
                        ],
                    ),
                    ft.Text(
                        f"Autoprop.: {'Sí' if buque.es_autopropulsado else 'No'} | "
                        f"Prop. P/P: {'Sí' if buque.propulsores_proa_popa else 'No'}",
                        size=12,
                        color=COLOR_GRIS,
                        max_lines=1,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
            )

            acciones = ft.Row(
                spacing=0,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    boton(
                        icono=ft.Icons.VISIBILITY_OUTLINED,
                        tooltip="Ver detalles del buque",
                        tipo="accion",
                        on_click=lambda e, b=buque: self.ver_buque(b),
                    ),
                ],
            )

            checkbox_seleccion = ft.Checkbox(
                value=seleccionado,
                active_color=COLOR_AZUL,
                check_color=COLOR_BLANCO,
                border_side=ft.BorderSide(1.5, "#7186A0"),
                shape=ft.RoundedRectangleBorder(radius=3),
                on_change=lambda e, b=buque: self.seleccionar_buque(
                    b, bool(e.control.value)
                ),
            )

            filas.append(
                ft.DataRow(
                    selected=seleccionado,
                    cells=[
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                alignment=ft.Alignment(0, 0),
                                content=checkbox_seleccion,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                padding=ft.Padding(8, 0, 0, 0),
                                content=nombre,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                content=identificadores,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                content=bandera,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                content=categoria_y_subtipo,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                content=especificaciones,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                content=propulsion_y_estado,
                            )
                        ),
                        ft.DataCell(
                            ft.Container(
                                expand=True,
                                alignment=ft.Alignment(0, 0),
                                content=acciones,
                            )
                        ),
                    ],
                )
            )

        columnas = [
            (encabezado_seleccion, 52),
            (self._encabezado_columna("Buque", ft.Icons.DIRECTIONS_BOAT_OUTLINED), 240),
            (self._encabezado_columna("IMO", ft.Icons.BADGE_OUTLINED), 120),
            (self._encabezado_columna("Bandera", ft.Icons.FLAG_OUTLINED), 135),
            (self._encabezado_columna("Categoría / Subtipo", ft.Icons.CATEGORY_OUTLINED), 180),
            (self._encabezado_columna("Dimensiones y arqueo", ft.Icons.STRAIGHTEN_OUTLINED), 240),
            (self._encabezado_columna("Propulsión / Estado", ft.Icons.SETTINGS_OUTLINED), 180),
            ("Acciones", 80),
        ]

        return tabla(
            columnas=columnas,
            filas=filas,
            column_spacing=6,
            horizontal_margin=6,
            heading_row_height=46,
            data_row_min_height=68,
            data_row_max_height=float("inf"),
            columnas_flexibles=True,
            heading_row_color="#EEF5FD",
            heading_text_size=14,
            heading_text_color=COLOR_NEGRO,
            vertical_lines=True,
            horizontal_lines=True,
            border_color="#E3EAF2",
            columnas_compactas=True,
        )


    def directorio(self):
        offset = (self.pagina_actual - 1) * self.registros_por_pagina

        buques, self.total_buques = self.controlador.obtener_buques(
            texto=self.busqueda,
            limit=self.registros_por_pagina,
            offset=offset,
            filtros=self.filtros_seleccionados,
        )

        tabla_buques = self.crear_tabla_buques(buques)

        controles_seleccion = []

        if self.buques_seleccionados:
            cantidad = len(self.buques_seleccionados)

            controles_seleccion = [
                ft.Row(
                    spacing=7,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE_OUTLINED,
                            size=18,
                            color=COLOR_AZUL,
                        ),
                        ft.Text(
                            (
                                f"{cantidad} buque seleccionado"
                                if cantidad == 1
                                else f"{cantidad} buques seleccionados"
                            ),
                            size=12,
                            color=COLOR_NEGRO,
                            weight=ft.FontWeight.BOLD,
                            max_lines=1,
                        ),
                        boton(
                            texto="Eliminar",
                            icono=ft.Icons.DELETE_OUTLINE,
                            tipo="secundario",
                            color=COLOR_ROJO,
                            border_color="#FFC8CF",
                            height=36,
                            on_click=self.confirmar_eliminar_buques_seleccionados,
                        ),
                        ft.TextButton(
                            "Cancelar",
                            on_click=self.cancelar_seleccion_buques,
                            style=ft.ButtonStyle(color=COLOR_BANNER),
                        ),
                    ],
                )
            ]

        cabecera_directorio = ft.Row(
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
                        ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                        color=COLOR_BLANCO,
                        size=25,
                    ),
                ),
                ft.Container(
                    expand=True,
                    content=ft.Column(
                        expand=True,
                        spacing=3,
                        controls=[
                            ft.Text(
                                "Directorio de buques",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_NEGRO,
                            ),
                            ft.Text(
                                f"{self.total_buques} buques registrados",
                                size=12,
                                color=COLOR_GRIS,
                            ),
                        ],
                    ),
                ),
                *controles_seleccion,
                boton(
                    texto=(
                        f"Exportar seleccionados ({len(self.buques_seleccionados)})"
                        if self.buques_seleccionados
                        else "Exportar"
                    ),
                    icono=ft.Icons.DOWNLOAD_OUTLINED,
                    tipo="secundario",
                    width=230 if self.buques_seleccionados else 150,
                    height=44,
                    border_color="#C9DDF7",
                    on_click=self.exportar_buques,
                ),
            ],
        )

        contenedor_tabla = ft.Container(
            expand=True,
            border=ft.Border.all(1, "#E2EDF9"),
            border_radius=12,
            bgcolor=COLOR_BLANCO,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            content=tabla_buques,
        )

        pie_directorio = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Mostrando {len(buques)} de {self.total_buques} buques",
                    size=12,
                    color=COLOR_GRIS,
                ),
                paginacion(
                    total_registros=self.total_buques,
                    registros_por_pagina=self.registros_por_pagina,
                    pagina_actual=self.pagina_actual,
                    on_change=self.cambiar_pagina,
                ),
            ],
        )

        controles = [
            cabecera_directorio,
            ft.Divider(height=1, color="#E2EDF9"),
            contenedor_tabla,
            pie_directorio,
        ]

        contenido_directorio = ft.Stack(
            expand=True,
            clip_behavior=ft.ClipBehavior.NONE,
            controls=[
                ft.Column(
                    expand=True,
                    spacing=12,
                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                    controls=controles,
                ),
            ],
        )

        return card(
            contenido_directorio,
            padding=ft.Padding(12, 11, 12, 11),
            radius=12,
            border_color="#E0ECF9",
            shadow=sombra_suave(),
            expand=True,
        )

    def _encabezado_columna(self, texto, icono):
        return ft.Row(
            tight=True,
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(icono, size=15, color="#6684A8"),
                ft.Text(
                    texto,
                    size=14,
                    weight=ft.FontWeight.BOLD,
                    color=COLOR_NEGRO,
                    max_lines=1,
                    overflow=ft.TextOverflow.ELLIPSIS,
                ),
            ],
        )

    def exportar_buques(self, e):
        pass
