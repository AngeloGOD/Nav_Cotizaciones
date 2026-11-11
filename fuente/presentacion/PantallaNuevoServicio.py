from __future__ import annotations

import logging

import flet as ft
from sqlalchemy.exc import SQLAlchemyError

from fuente.negocio.modelo.ENUMs import TipoConcepto, VariableMedida
from fuente.utilidades.ExportacionArchivos import obtener_selector_archivos
from fuente.utilidades.Colores import COLOR_NARANJA, COLOR_BLANCO, COLOR_GRIS
from fuente.utilidades.inputs import (
    campo_con_mensaje_error,
    crear_mensaje_validacion,
    validar_campos,
    validador_requerido,
    vincular_validacion_campo,
)
from fuente.utilidades.feedback import reproducir_sonido


COLOR_NARANJA = "#ff6600"     
COLOR_AZUL_OSCURO = "#0d1b2a"   
COLOR_BLANCO = "#ffffff"        
COLOR_GRIS = "#8A94A6"          
COLOR_FONDO = "#f4f7fb"         


COLOR_BORDE_SUAVE = "#E2E8F0"
COLOR_SUPERFICIE_SUAVE = "#F8FAFC"
COLOR_NARANJA_SUAVE = "#FFF3EB"
COLOR_AZUL_SUAVE = "#EEF4FF"
COLOR_VERDE_EXITO = "#16A34A"
COLOR_ROJO_ALERTA = "#DC2626"



# CATÁLOGOS DEMO Y ETIQUETAS DE NEGOCIO

ETIQUETAS_VARIABLES_MEDIDA: list[tuple[str, str]] = [
    (VariableMedida.TRB.value, "TRB — Tonelaje de Registro Bruto"),
    (VariableMedida.ESLORA.value, "Eslora — Metros de Eslora Total"),
    (VariableMedida.TONELADAS.value, "Toneladas — Toneladas Métricas de Carga"),
    (VariableMedida.CONTENEDORES.value, "Contenedores — Unidades TEU / FEU"),
    (VariableMedida.M3.value, "m³ — Volumen en Metros Cúbicos"),
    (VariableMedida.PASAJEROS.value, "Pasajeros — Número de Pasajeros / Tripulantes"),
    (VariableMedida.PESO_KG.value, "Peso — Kilogramos (kg)"),
    (VariableMedida.HORAS_ESTANCIA.value, "Horas de Estancia / Operación"),
    (VariableMedida.DIAS_ESTANCIA.value, "Días de Estancia en Puerto"),
    (VariableMedida.DIAS_ALMACENAJE.value, "Días de Almacenaje en Recinto"),
    (VariableMedida.CANTIDAD_EVENTOS.value, "Cantidad de Maniobras / Eventos"),
]

UNIDADES_MEDIDA_DEMO: list[tuple[str, str]] = [
    ("SERVICIO", "Servicio / Operación"),
    ("MANIOBRA", "Maniobra Portuaria"),
    ("DIA", "Día Natural / Fracción"),
    ("HORA", "Hora Efectiva"),
    ("TRB", "Por Unidad de TRB"),
    ("TONELADA", "Por Tonelada Métrica"),
    ("CONTENEDOR", "Por Contenedor"),
]

TASAS_IVA_DEMO: list[tuple[str, str]] = [
    ("0.1600", "16% — Tasa General"),
    ("0.0800", "8% — Estímulo Región Fronteriza"),
    ("0.0000", "0% — Tasa Cero / Exportación"),
]


class PantallaNuevoServicio(ft.Container):
    """
    Pantalla 'Nuevo Servicio' (Tarea NAV-23) - ERP OPL Pacífico Sur.
    Implementa un formulario dinámico de Revelación Progresiva (Progressive Disclosure)
    basado estrictamente en la jerarquía de especialización del diagrama Entidad-Relación:
      - Nivel 0: `concepto` (con relaciones a `categoria_pda` y `proveedor`)
      - Nivel 1: `servicio` (con relación opcional a `categoria_buque`)
      - Nivel 2 (Discriminador): `servicio_cuota_fija`, `servicio_factor_unitario`,
        `servicio_rango` (+ entidad débil `rangos`), `servicio_incremental` (+ entidad débil `tramo`)
      - Nivel 3 (Sub-especialización disjunta de Factor Unitario):
        `servicio_lineal_mixto` y `servicio_factor_compuesto`.
    """

    def __init__(
        self,
        main_page: ft.Page | None = None,
        vista_anterior=None,
        controlador=None,
        servicio_edicion=None,
    ):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
            padding=ft.Padding(24, 18, 24, 20),
        )
        self.main_page = main_page
        self.vista_anterior = vista_anterior
        self.controlador = controlador
        self.servicio_edicion = servicio_edicion
        self.es_edicion = servicio_edicion is not None
        self._imagen_path = (
            getattr(servicio_edicion, "imagen_path", None)
            if self.es_edicion
            else None
        )
        self._archivo_imagen = None
        self._selector_archivos = (
            obtener_selector_archivos(main_page)
            if main_page is not None
            else None
        )
        self._error_catalogos = None
        self._catalogos = {
            "categorias_pda": [],
            "categorias_buque": [],
            "proveedores": [],
        }
        if self.controlador is not None:
            try:
                self._catalogos = self.controlador.obtener_catalogos_registro()
            except SQLAlchemyError as error:
                logging.exception("No se pudieron cargar catálogos de servicios.")
                self._error_catalogos = error

        self._proveedores_por_id = {
            str(proveedor.id): proveedor
            for proveedor in self._catalogos["proveedores"]
        }
        self._proveedores_seleccionados = []
        self._filas_rangos: list[dict] = []
        self._filas_tramos: list[dict] = []

       
        self._inicializar_controles_fase1()
        self._inicializar_controles_fase2()
        self._inicializar_controles_fase3()
        self._inicializar_validaciones()
        if self.es_edicion:
            self.dd_tipo_cobro.disabled = True

        self.content = self._construir_layout()
        if self.es_edicion:
            self._cargar_servicio_edicion()
        if self._error_catalogos is not None:
            self._mostrar_aviso(
                "No se pudieron cargar categorías y proveedores desde la base de datos."
            )

    
    
    
    def _borde_input(self, activo: bool = False) -> dict[ft.ControlState, ft.InputBorder]:
        color_defecto = COLOR_AZUL_OSCURO if activo else COLOR_BORDE_SUAVE
        grosor_defecto = 1.5 if activo else 1.0
        return {
            ft.ControlState.DEFAULT: ft.OutlineInputBorder(
                side=ft.BorderSide(grosor_defecto, color_defecto),
                border_radius=8,
            ),
            ft.ControlState.FOCUSED: ft.OutlineInputBorder(
                side=ft.BorderSide(1.8, COLOR_AZUL_OSCURO),
                border_radius=8,
            ),
        }

    def _crear_textfield(
        self,
        placeholder: str,
        valor_inicial: str = "",
        icono: ft.IconData | None = None,
        prefijo: str | None = None,
        sufijo: str | None = None,
        on_change=None,
        expand: bool | int = True,
    ) -> ft.TextField:
        return ft.TextField(
            value=valor_inicial,
            hint_text=placeholder,
            hint_style=ft.TextStyle(color=COLOR_GRIS, size=13),
            text_style=ft.TextStyle(
                color=COLOR_AZUL_OSCURO,
                size=13,
                weight=ft.FontWeight.W_500,
            ),
            prefix_icon=icono,
            prefix=ft.Text(prefijo, color=COLOR_GRIS, size=13) if prefijo else None,
            suffix=ft.Text(sufijo, color=COLOR_GRIS, size=13) if sufijo else None,
            height=42,
            expand=expand,
            filled=True,
            fill_color=COLOR_BLANCO,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=self._borde_input(),
            on_change=on_change,
        )

    def _crear_dropdown(
        self,
        placeholder: str,
        opciones: list[tuple[str, str]],
        valor_inicial: str | None = None,
        icono: ft.IconData | None = None,
        on_select=None,
        destacado: bool = False,
        expand: bool | int = True,
    ) -> ft.Dropdown:
        
        return ft.Dropdown(
            value=valor_inicial,
            hint_text=placeholder,
            hint_style=ft.TextStyle(color=COLOR_GRIS, size=13),
            text_style=ft.TextStyle(
                color=COLOR_AZUL_OSCURO,
                size=13,
                weight=ft.FontWeight.W_600 if destacado else ft.FontWeight.W_500,
            ),
            leading_icon=icono,
            options=[
                ft.DropdownOption(key=clave, text=texto)
                for clave, texto in opciones
            ],
            expand=expand,
            filled=True,
            fill_color=COLOR_BLANCO,
            content_padding=ft.Padding(12, 8, 12, 8),
            border=self._borde_input(activo=destacado),
            on_select=on_select,
        )

    def _campo_con_etiqueta(
        self,
        etiqueta: str,
        control: ft.Control,
        obligatorio: bool = False,
        expand: bool | int = 1,
    ) -> ft.Container:
        encabezado = [
            ft.Text(
                etiqueta,
                size=12,
                weight=ft.FontWeight.W_600,
                color=COLOR_AZUL_OSCURO,
            )
        ]
        if obligatorio:
            encabezado.append(
                ft.Text("*", size=13, weight=ft.FontWeight.BOLD, color=COLOR_NARANJA)
            )

        return ft.Container(
            expand=expand,
            content=ft.Column(
                spacing=5,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Row(
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=encabezado,
                    ),
                    control,
                ],
            ),
        )

    def _inicializar_validaciones(self):
        self._validaciones_formulario = {}
        self._mensajes_validacion = {}
        controles = {
            "nombre_es": (
                self.txt_nombre_es,
                validador_requerido("el nombre en español"),
                "on_change",
            ),
            "unidad_medida": (
                self.dd_unidad_medida,
                validador_requerido("la unidad de medida"),
                "on_select",
            ),
            "tasa_iva": (
                self.dd_tasa_iva,
                validador_requerido("la tasa de IVA"),
                "on_select",
            ),
            "categoria_pda": (
                self.dd_categoria_pda,
                validador_requerido("una categoría PDA"),
                "on_select",
            ),
            "tipo_cobro": (
                self.dd_tipo_cobro,
                validador_requerido("un método de cobro"),
                "on_select",
            ),
        }
        for clave, (control, validador, evento) in controles.items():
            mensaje = crear_mensaje_validacion(reservar_espacio=True)
            self._mensajes_validacion[clave] = mensaje
            self._validaciones_formulario[clave] = (
                control,
                mensaje,
                validador,
            )
            vincular_validacion_campo(
                control,
                mensaje,
                validador,
                page=self.main_page,
                evento=evento,
            )

    def _cargar_servicio_edicion(self):
        servicio = self.servicio_edicion
        self.txt_nombre_es.value = servicio.nombre_es
        self.txt_nombre_en.value = servicio.nombre_en or ""
        self.txt_sku.value = servicio.sku or ""
        self.dd_unidad_medida.value = servicio.unidad_medida
        self.dd_tasa_iva.value = str(servicio.tasa_iva)
        self.dd_categoria_pda.value = str(servicio.categoria_pda_id)
        self.dd_categoria_buque.value = (
            str(servicio.categoria_buque_id)
            if servicio.categoria_buque_id is not None
            else "TODAS"
        )
        self._proveedores_seleccionados = [
            self._proveedores_por_id[str(proveedor.id)]
            for proveedor in servicio.proveedores
            if str(proveedor.id) in self._proveedores_por_id
        ]
        self._renderizar_chips_proveedores()
        self.boton_imagen.content = self._contenido_boton_imagen()

        tipo = servicio.tipo_concepto
        tipo = tipo.value if hasattr(tipo, "value") else str(tipo)
        tipos_cobro = {
            TipoConcepto.SERVICIO_CUOTA_FIJA.value: "CUOTA_FIJA",
            TipoConcepto.SERVICIO_FACTOR_UNITARIO.value: "FACTOR_UNITARIO",
            TipoConcepto.SERVICIO_LINEAL_MIXTO.value: "FACTOR_UNITARIO",
            TipoConcepto.SERVICIO_FACTOR_COMPUESTO.value: "FACTOR_UNITARIO",
            TipoConcepto.SERVICIO_RANGO.value: "POR_RANGOS",
            TipoConcepto.SERVICIO_INCREMENTAL.value: "INCREMENTAL",
        }
        self.dd_tipo_cobro.value = tipos_cobro[tipo]

        if tipo == TipoConcepto.SERVICIO_CUOTA_FIJA.value:
            self.txt_cuota_fija.value = str(servicio.cuota)
        elif tipo in {
            TipoConcepto.SERVICIO_FACTOR_UNITARIO.value,
            TipoConcepto.SERVICIO_LINEAL_MIXTO.value,
            TipoConcepto.SERVICIO_FACTOR_COMPUESTO.value,
        }:
            self.dd_variable_primaria.value = servicio.variable_primaria.value
            self.txt_factor_mxn.value = str(servicio.factor_mxn)
            self.txt_unidades_minimas.value = str(servicio.unidades_minimas)
            self.sw_lineal_mixto.value = (
                tipo == TipoConcepto.SERVICIO_LINEAL_MIXTO.value
            )
            self.sw_factor_compuesto.value = (
                tipo == TipoConcepto.SERVICIO_FACTOR_COMPUESTO.value
            )
            if self.sw_lineal_mixto.value:
                self.txt_cuota_base.value = str(servicio.cuota_base)
            if self.sw_factor_compuesto.value:
                self.dd_variable_secundaria.value = (
                    servicio.variable_secundaria.value
                )
        elif tipo == TipoConcepto.SERVICIO_RANGO.value:
            self.dd_variable_rangos.value = servicio.variable_rangos.value
            self._filas_rangos.clear()
            self.columna_filas_rangos.controls.clear()
            for rango in servicio.rangos:
                self._agregar_fila_rango(
                    str(rango.limite_inferior),
                    (
                        str(rango.limite_superior)
                        if rango.limite_superior is not None
                        else ""
                    ),
                    str(rango.cuota_mxn),
                    actualizar=False,
                )
        elif tipo == TipoConcepto.SERVICIO_INCREMENTAL.value:
            self.dd_variable_cantidad.value = servicio.variable_cantidad.value
            self.dd_variable_dias.value = servicio.variable_dias.value
            self.txt_bloque_redondeo.value = str(servicio.bloque_redondeo)
            self._filas_tramos.clear()
            self.columna_filas_tramos.controls.clear()
            for tramo in servicio.tramos:
                self._agregar_fila_tramo(
                    str(tramo.dia_inicio),
                    str(tramo.dia_fin) if tramo.dia_fin is not None else "",
                    str(tramo.cuota_diaria_mxn),
                    actualizar=False,
                )

        self.on_change_tipo_cobro()
        self._actualizar_vista()

    def _campo_validado(self, clave: str, control: ft.Control) -> ft.Control:
        return campo_con_mensaje_error(
            control,
            self._mensajes_validacion[clave],
        )

    def _contenido_boton_imagen(self):
        if self._imagen_path:
            return ft.Row(
                spacing=6,
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Image(
                        src=self._imagen_path,
                        width=30,
                        height=30,
                        fit=ft.BoxFit.COVER,
                        border_radius=6,
                    ),
                    ft.Column(
                        expand=True,
                        spacing=0,
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Text(
                                self._nombre_imagen(),
                                size=10,
                                color=COLOR_AZUL_OSCURO,
                                max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.Text("Cambiar imagen", size=9, color=COLOR_GRIS),
                        ],
                    ),
                ],
            )
        return ft.Row(
            spacing=6,
            alignment=ft.MainAxisAlignment.CENTER,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Icon(ft.Icons.IMAGE_OUTLINED, size=18, color=COLOR_AZUL_OSCURO),
                ft.Text("Subir imagen", size=11, color=COLOR_AZUL_OSCURO),
            ],
        )

    def _nombre_imagen(self):
        if self._archivo_imagen is not None:
            return self._archivo_imagen.name
        if self._imagen_path:
            return self._imagen_path.replace("\\", "/").rsplit("/", 1)[-1]
        return ""

    async def seleccionar_imagen(self, e=None):
        if self._selector_archivos is None:
            self._mostrar_aviso("El selector de archivos no está disponible.")
            return
        archivos = await self._selector_archivos.pick_files(
            dialog_title="Seleccionar imagen del servicio",
            file_type=ft.FilePickerFileType.CUSTOM,
            allowed_extensions=["jpg", "jpeg", "png"],
            allow_multiple=False,
        )
        if not archivos:
            return

        archivo = archivos[0]
        ruta = archivo.path
        error = self.controlador.validar_imagen(
            archivo.name,
            archivo.size,
            ruta,
        )
        if error:
            self._mostrar_aviso(error)
            return

        self._archivo_imagen = archivo
        self._imagen_path = ruta
        self.boton_imagen.content = self._contenido_boton_imagen()
        self._actualizar_vista()

    def _tarjeta_seccion(
        self,
        numero_paso: str,
        titulo: str,
        icono: ft.IconData,
        contenido: ft.Control,
        borde_destacado: bool = False,
    ) -> ft.Container:
        controles_encabezado = [
            ft.Container(
                width=36,
                height=36,
                border_radius=9,
                bgcolor=(
                    COLOR_NARANJA
                    if borde_destacado
                    else COLOR_NARANJA_SUAVE
                ),
                alignment=ft.Alignment(0, 0),
                content=ft.Icon(
                    icono,
                    size=19,
                    color=COLOR_BLANCO if borde_destacado else COLOR_NARANJA,
                ),
            ),
            ft.Row(
                spacing=8,
                expand=True,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(
                        f"PASO {numero_paso}",
                        size=10,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_NARANJA,
                    ),
                    ft.Text("•", size=10, color=COLOR_GRIS),
                    ft.Text(
                        titulo,
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_AZUL_OSCURO,
                    ),
                ],
            ),
        ]
        if titulo == "Datos Generales":
            controles_encabezado.append(self.boton_imagen)

        return ft.Container(
            bgcolor=COLOR_BLANCO,
            border_radius=12,
            padding=ft.Padding(22, 18, 22, 20),
            border=ft.Border.all(
                1.5 if borde_destacado else 1.0,
                COLOR_AZUL_OSCURO if borde_destacado else COLOR_BORDE_SUAVE,
            ),
            shadow=ft.BoxShadow(
                blur_radius=18,
                color="#0D1B2A0C",
                offset=ft.Offset(0, 6),
            ),
            content=ft.Column(
                spacing=16,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                controls=[
                    ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=controles_encabezado,
                    ),
                    ft.Divider(height=1, color=COLOR_BORDE_SUAVE),
                    contenido,
                ],
            ),
        )

   
    # CONTROLES DE DATOS GENERALES
    
    def _inicializar_controles_fase1(self):
        self.txt_nombre_es = self._crear_textfield(
            placeholder="Ej. Servicio de Practicaje de Entrada / Salida",
            icono=ft.Icons.DIRECTIONS_BOAT_OUTLINED,
        )
        self.txt_nombre_en = self._crear_textfield(
            placeholder="Ej. Inbound / Outbound Pilotage Service",
            icono=ft.Icons.TRANSLATE_OUTLINED,
        )
        self.txt_sku = self._crear_textfield(
            placeholder="Ej. SRV-PDA-001",
            icono=ft.Icons.QR_CODE_2_OUTLINED,
        )
        self.boton_imagen = ft.OutlinedButton(
            content=self._contenido_boton_imagen(),
            on_click=self.seleccionar_imagen,
            width=190,
            height=42,
            style=ft.ButtonStyle(
                side=ft.BorderSide(1, "#B8D3F8"),
                shape=ft.RoundedRectangleBorder(radius=9),
                padding=ft.Padding(6, 3, 6, 3),
            ),
        )
        self.dd_unidad_medida = self._crear_dropdown(
            placeholder="Selecciona unidad",
            opciones=UNIDADES_MEDIDA_DEMO,
            valor_inicial="SERVICIO",
            icono=ft.Icons.STRAIGHTEN_OUTLINED,
        )
        self.dd_tasa_iva = self._crear_dropdown(
            placeholder="Selecciona IVA",
            opciones=TASAS_IVA_DEMO,
            valor_inicial="0.1600",
            icono=ft.Icons.PERCENT_OUTLINED,
        )

        self.dd_categoria_pda = self._crear_dropdown(
            placeholder="Selecciona categoría PDA...",
            opciones=[
                (str(categoria.id), categoria.nombre)
                for categoria in self._catalogos["categorias_pda"]
            ],
            icono=ft.Icons.FOLDER_OUTLINED,
        )
        self.dd_categoria_buque = self._crear_dropdown(
            placeholder="Aplica a categoría de buque...",
            opciones=[
                ("TODAS", "General — Aplica a todas las categorías"),
                *[
                    (str(categoria.id), categoria.categoria)
                    for categoria in self._catalogos["categorias_buque"]
                ],
            ],
            valor_inicial="TODAS",
            icono=ft.Icons.SAILING_OUTLINED,
        )
        self.dd_proveedor = self._crear_dropdown(
            placeholder="Vincular proveedor autorizado...",
            opciones=[
                (
                    str(proveedor.id),
                    f"{proveedor.nombre} ({proveedor.tipo_proveedor.value})",
                )
                for proveedor in self._catalogos["proveedores"]
            ],
            icono=ft.Icons.BUSINESS_OUTLINED,
            on_select=self.on_change_agregar_proveedor,
        )
        self.contenedor_chips_proveedores = ft.Row(
            spacing=8,
            run_spacing=8,
            wrap=True,
        )
        self._renderizar_chips_proveedores()

    def _renderizar_chips_proveedores(self):
        if not self._proveedores_seleccionados:
            self.contenedor_chips_proveedores.controls = [
                ft.Text(
                    "Sin proveedores vinculados. Selecciona al menos un proveedor autorizado.",
                    size=11,
                    color=COLOR_ROJO_ALERTA,
                )
            ]
            return

        chips = []
        for proveedor in self._proveedores_seleccionados:
            chips.append(
                ft.Container(
                    padding=ft.Padding(10, 5, 6, 5),
                    border_radius=20,
                    bgcolor=COLOR_SUPERFICIE_SUAVE,
                    border=ft.Border.all(1, COLOR_BORDE_SUAVE),
                    content=ft.Row(
                        tight=True,
                        spacing=6,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.VERIFIED_OUTLINED,
                                size=14,
                                color=COLOR_NARANJA,
                            ),
                            ft.Text(
                                proveedor.nombre,
                                size=11,
                                weight=ft.FontWeight.W_600,
                                color=COLOR_AZUL_OSCURO,
                            ),
                            ft.Container(
                                padding=ft.Padding(5, 1, 5, 1),
                                border_radius=4,
                                bgcolor=COLOR_NARANJA_SUAVE,
                                content=ft.Text(
                                proveedor.tipo_proveedor.value,
                                    size=9,
                                    weight=ft.FontWeight.BOLD,
                                    color=COLOR_NARANJA,
                                ),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.CLOSE,
                                icon_size=13,
                                icon_color=COLOR_GRIS,
                                width=22,
                                height=22,
                                padding=0,
                                tooltip="Quitar proveedor",
                                on_click=lambda e, p_id=str(proveedor.id): self._quitar_proveedor(p_id),
                            ),
                        ],
                    ),
                )
            )
        self.contenedor_chips_proveedores.controls = chips

    def on_change_agregar_proveedor(self, e: ft.ControlEvent):
        pid = self.dd_proveedor.value
        if not pid:
            return
        encontrado = self._proveedores_por_id.get(str(pid))
        if encontrado and encontrado not in self._proveedores_seleccionados:
            self._proveedores_seleccionados.append(encontrado)
            self._renderizar_chips_proveedores()
        self.dd_proveedor.value = None
        self._actualizar_vista()

    def _quitar_proveedor(self, proveedor_id: str):
        self._proveedores_seleccionados = [
            proveedor
            for proveedor in self._proveedores_seleccionados
            if str(proveedor.id) != proveedor_id
        ]
        self._renderizar_chips_proveedores()
        self._actualizar_vista()


    # MÉTODO DE COBRO (REGLA TARIFARIA)
    
    def _inicializar_controles_fase2(self):
        self.dd_tipo_cobro = self._crear_dropdown(
            placeholder="Selecciona el método de cobro...",
            opciones=[
                ("CUOTA_FIJA", "Cuota Fija"),
                ("FACTOR_UNITARIO", "Factor Unitario"),
                ("POR_RANGOS", "Por Rangos (Escalón Único)"),
                ("INCREMENTAL", "Incremental (Por Tramos de Días)"),
            ],
            icono=ft.Icons.ACCOUNT_TREE_OUTLINED,
            on_select=self.on_change_tipo_cobro,
            destacado=True,
        )

        self.txt_badge_polimorfico = ft.Text(
            "PENDIENTE DE SELECCIÓN",
            size=11,
            weight=ft.FontWeight.BOLD,
            color=COLOR_NARANJA,
        )
        self.txt_resumen_formula = ft.Text(
            "Selecciona un método de cobro para configurar los parámetros de la tarifa.",
            size=12,
            color=COLOR_GRIS,
        )

        
        self.circulo_paso3 = ft.Container(
            width=26,
            height=26,
            border_radius=13,
            bgcolor=COLOR_SUPERFICIE_SUAVE,
            border=ft.Border.all(1.5, COLOR_BORDE_SUAVE),
            alignment=ft.Alignment(0, 0),
            content=ft.Text(
                "3",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=COLOR_GRIS,
            ),
        )
        self.texto_paso3 = ft.Text(
            "3. Configuración Adicional",
            size=12,
            weight=ft.FontWeight.W_600,
            color=COLOR_GRIS,
        )
        self.conector_paso3 = ft.Container(
            width=28,
            height=2,
            bgcolor=COLOR_BORDE_SUAVE,
            border_radius=1,
        )

    
    # FORMULARIOS DINÁMICOS DE CONFIGURACIÓN ADICIONAL
    
    def _inicializar_controles_fase3(self):
       
        self.txt_cuota_fija = self._crear_textfield(
            placeholder="0.00",
            prefijo="$ ",
            sufijo=" MXN",
            icono=ft.Icons.PAYMENTS_OUTLINED,
        )
        self.panel_cuota_fija = self._construir_subformulario_cuota_fija()

       
        self.dd_variable_primaria = self._crear_dropdown(
            placeholder="Selecciona variable primaria...",
            opciones=ETIQUETAS_VARIABLES_MEDIDA,
            valor_inicial=VariableMedida.TRB.value,
            icono=ft.Icons.SPEED_OUTLINED,
        )
        self.txt_factor_mxn = self._crear_textfield(
            placeholder="0.0000",
            prefijo="$ ",
            sufijo=" MXN",
            icono=ft.Icons.CALCULATE_OUTLINED,
        )
        self.txt_unidades_minimas = self._crear_textfield(
            placeholder="0.00",
            valor_inicial="0.00",
            icono=ft.Icons.VERTICAL_ALIGN_BOTTOM_OUTLINED,
        )

        # Modalidades opcionales de Factor Unitario
        self.sw_lineal_mixto = ft.Switch(
            value=False,
            active_color=COLOR_NARANJA,
            on_change=self.on_change_lineal_mixto,
        )
        self.txt_cuota_base = self._crear_textfield(
            placeholder="0.00",
            prefijo="$ ",
            sufijo=" MXN",
            icono=ft.Icons.ADD_CARD_OUTLINED,
        )
        self.contenedor_hijo_lineal_mixto = ft.Container(
            visible=False,
            padding=ft.Padding(14, 12, 14, 12),
            border_radius=8,
            bgcolor=COLOR_NARANJA_SUAVE,
            border=ft.Border.all(1, COLOR_NARANJA),
            content=self._campo_con_etiqueta(
                etiqueta="Cuota Base Fija",
                control=self.txt_cuota_base,
                obligatorio=True,
            ),
        )

        self.sw_factor_compuesto = ft.Switch(
            value=False,
            active_color=COLOR_NARANJA,
            on_change=self.on_change_factor_compuesto,
        )
        self.dd_variable_secundaria = self._crear_dropdown(
            placeholder="Selecciona variable secundaria...",
            opciones=ETIQUETAS_VARIABLES_MEDIDA,
            valor_inicial=VariableMedida.HORAS_ESTANCIA.value,
            icono=ft.Icons.LAYERS_OUTLINED,
        )
        self.contenedor_hijo_factor_compuesto = ft.Container(
            visible=False,
            padding=ft.Padding(14, 12, 14, 12),
            border_radius=8,
            bgcolor=COLOR_NARANJA_SUAVE,
            border=ft.Border.all(1, COLOR_NARANJA),
            content=self._campo_con_etiqueta(
                etiqueta="Variable Secundaria",
                control=self.dd_variable_secundaria,
                obligatorio=True,
            ),
        )
        self.panel_factor_unitario = self._construir_subformulario_factor_unitario()

        
        self.dd_variable_rangos = self._crear_dropdown(
            placeholder="Variable que determina el escalón...",
            opciones=ETIQUETAS_VARIABLES_MEDIDA,
            valor_inicial=VariableMedida.TRB.value,
            icono=ft.Icons.STACKED_BAR_CHART_OUTLINED,
        )
        self.columna_filas_rangos = ft.Column(spacing=8)
        self._agregar_fila_rango(actualizar=False)
        self._agregar_fila_rango(actualizar=False)
        self.panel_por_rangos = self._construir_subformulario_por_rangos()

       
        self.dd_variable_cantidad = self._crear_dropdown(
            placeholder="Variable de volumen / masa...",
            opciones=ETIQUETAS_VARIABLES_MEDIDA,
            valor_inicial=VariableMedida.TRB.value,
            icono=ft.Icons.SCALE_OUTLINED,
        )
        self.dd_variable_dias = self._crear_dropdown(
            placeholder="Variable de tiempo / días...",
            opciones=ETIQUETAS_VARIABLES_MEDIDA,
            valor_inicial=VariableMedida.DIAS_ESTANCIA.value,
            icono=ft.Icons.CALENDAR_MONTH_OUTLINED,
        )
        self.txt_bloque_redondeo = self._crear_textfield(
            placeholder="1.00",
            valor_inicial="1.00",
            icono=ft.Icons.GRID_VIEW_OUTLINED,
        )
        self.columna_filas_tramos = ft.Column(spacing=8)
        self._agregar_fila_tramo(actualizar=False)
        self._agregar_fila_tramo(actualizar=False)
        self.panel_incremental = self._construir_subformulario_incremental()

        # Estado vacío inicial antes de elegir el método de cobro
        self.panel_vacio_fase3 = self._construir_estado_vacio_fase3()

        # Contenedor dinámico maestro para el Paso 3
        self.contenedor_dinamico_fase3 = ft.Container(
            content=self.panel_vacio_fase3,
        )

    
    # FORMULARIOS DE PASO 3
    
    def _construir_estado_vacio_fase3(self) -> ft.Container:
        return ft.Container(
            bgcolor=COLOR_BLANCO,
            border_radius=12,
            padding=ft.Padding(28, 32, 28, 32),
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            alignment=ft.Alignment(0, 0),
            content=ft.Column(
                spacing=8,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=52,
                        height=52,
                        border_radius=26,
                        bgcolor=COLOR_NARANJA_SUAVE,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Icon(
                            ft.Icons.TUNE_OUTLINED,
                            size=26,
                            color=COLOR_NARANJA,
                        ),
                    ),
                    ft.Text(
                        "Configuración Adicional",
                        size=15,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_AZUL_OSCURO,
                    ),
                    ft.Text(
                        "Selecciona un Método de Cobro en el paso anterior para habilitar los campos de configuración.",
                        size=12,
                        color=COLOR_GRIS,
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
            ),
        )

    def _construir_subformulario_cuota_fija(self) -> ft.Container:
        contenido = ft.Row(
            spacing=20,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                self._campo_con_etiqueta(
                    etiqueta="Cuota Fija del Servicio",
                    control=self.txt_cuota_fija,
                    obligatorio=True,
                    expand=1,
                ),
                ft.Container(
                    expand=1,
                    padding=ft.Padding(16, 12, 16, 12),
                    border_radius=8,
                    bgcolor=COLOR_SUPERFICIE_SUAVE,
                    border=ft.Border.all(1, COLOR_BORDE_SUAVE),
                    content=ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.INFO_OUTLINE,
                                color=COLOR_NARANJA,
                                size=20,
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        "Regla de Negocio — Cuota Fija",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_AZUL_OSCURO,
                                    ),
                                    ft.Text(
                                        "El importe se aplica como un monto único en MXN por evento o escala, "
                                        "sin depender de dimensiones del buque ni días de estancia.",
                                        size=11,
                                        color=COLOR_GRIS,
                                    ),
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        )
        return self._tarjeta_seccion(
            numero_paso="3",
            titulo="Configuración Adicional — Cuota Fija",
            icono=ft.Icons.REQUEST_QUOTE_OUTLINED,
            contenido=contenido,
        )

    def _construir_subformulario_factor_unitario(self) -> ft.Container:
        fila_base = ft.Row(
            spacing=16,
            controls=[
                self._campo_con_etiqueta(
                    etiqueta="Variable Primaria",
                    control=self.dd_variable_primaria,
                    obligatorio=True,
                    expand=2,
                ),
                self._campo_con_etiqueta(
                    etiqueta="Factor Unitario MXN",
                    control=self.txt_factor_mxn,
                    obligatorio=True,
                    expand=1,
                ),
                self._campo_con_etiqueta(
                    etiqueta="Unidades Mínimas",
                    control=self.txt_unidades_minimas,
                    obligatorio=True,
                    expand=1,
                ),
            ],
        )

        tarjeta_toggle_lineal = ft.Container(
            expand=1,
            padding=ft.Padding(14, 12, 14, 12),
            border_radius=10,
            bgcolor=COLOR_SUPERFICIE_SUAVE,
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.LINEAR_SCALE_OUTLINED,
                                size=18,
                                color=COLOR_AZUL_OSCURO,
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        "Modalidad: Lineal Mixto",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_AZUL_OSCURO,
                                    ),
                                    ft.Text(
                                        "Suma una cuota base fija al cobro variable: Cuota Base + (Variable × Factor).",
                                        size=11,
                                        color=COLOR_GRIS,
                                    ),
                                ],
                            ),
                            self.sw_lineal_mixto,
                        ],
                    ),
                    self.contenedor_hijo_lineal_mixto,
                ],
            ),
        )

        tarjeta_toggle_compuesto = ft.Container(
            expand=1,
            padding=ft.Padding(14, 12, 14, 12),
            border_radius=10,
            bgcolor=COLOR_SUPERFICIE_SUAVE,
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            content=ft.Column(
                spacing=10,
                controls=[
                    ft.Row(
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.HUB_OUTLINED,
                                size=18,
                                color=COLOR_AZUL_OSCURO,
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        "Modalidad: Factor Compuesto",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_AZUL_OSCURO,
                                    ),
                                    ft.Text(
                                        "Multiplica por una segunda variable: Variable Primaria × Variable Secundaria × Factor.",
                                        size=11,
                                        color=COLOR_GRIS,
                                    ),
                                ],
                            ),
                            self.sw_factor_compuesto,
                        ],
                    ),
                    self.contenedor_hijo_factor_compuesto,
                ],
            ),
        )

        contenido = ft.Column(
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                fila_base,
                ft.Divider(height=1, color=COLOR_BORDE_SUAVE),
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(
                            ft.Icons.CALL_SPLIT_OUTLINED,
                            size=16,
                            color=COLOR_NARANJA,
                        ),
                        ft.Text(
                            "Modalidades Adicionales (Opcional)",
                            size=12,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_AZUL_OSCURO,
                        ),
                    ],
                ),
                ft.Row(
                    spacing=16,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                    controls=[
                        tarjeta_toggle_lineal,
                        tarjeta_toggle_compuesto,
                    ],
                ),
            ],
        )

        return self._tarjeta_seccion(
            numero_paso="3",
            titulo="Configuración Adicional — Factor Unitario",
            icono=ft.Icons.CALCULATE_OUTLINED,
            contenido=contenido,
        )

    def _construir_subformulario_por_rangos(self) -> ft.Container:
        cabecera_rangos = ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.END,
            controls=[
                self._campo_con_etiqueta(
                    etiqueta="Variable de Evaluación de Rangos",
                    control=self.dd_variable_rangos,
                    obligatorio=True,
                    expand=2,
                ),
                ft.Container(expand=1),
                ft.Button(
                    content="Agregar Rango",
                    icon=ft.Icons.ADD,
                    bgcolor=COLOR_NARANJA,
                    color=COLOR_BLANCO,
                    height=42,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding(16, 0, 16, 0),
                    ),
                    on_click=lambda e: self._agregar_fila_rango(),
                ),
            ],
        )

        encabezado_tabla = ft.Container(
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=6,
            bgcolor=COLOR_SUPERFICIE_SUAVE,
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Container(
                        width=70,
                        content=ft.Text(
                            "#",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                    ft.Container(
                        expand=1,
                        content=ft.Text(
                            "LÍMITE INFERIOR *",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                    ft.Container(
                        expand=1,
                        content=ft.Text(
                            "LÍMITE SUPERIOR",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                    ft.Container(
                        expand=1,
                        content=ft.Text(
                            "CUOTA DEL ESCALÓN *",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                    ft.Container(
                        width=44,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "ACCIÓN",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                ],
            ),
        )

        contenido = ft.Column(
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                cabecera_rangos,
                ft.Divider(height=1, color=COLOR_BORDE_SUAVE),
                encabezado_tabla,
                self.columna_filas_rangos,
            ],
        )

        return self._tarjeta_seccion(
            numero_paso="3",
            titulo="Configuración Adicional — Tabulador por Rangos",
            icono=ft.Icons.VIEW_TIMELINE_OUTLINED,
            contenido=contenido,
        )

    def _construir_subformulario_incremental(self) -> ft.Container:
        fila_parametros = ft.Row(
            spacing=16,
            vertical_alignment=ft.CrossAxisAlignment.END,
            controls=[
                self._campo_con_etiqueta(
                    etiqueta="Variable de Cantidad",
                    control=self.dd_variable_cantidad,
                    obligatorio=True,
                    expand=2,
                ),
                self._campo_con_etiqueta(
                    etiqueta="Variable de Días",
                    control=self.dd_variable_dias,
                    obligatorio=True,
                    expand=2,
                ),
                self._campo_con_etiqueta(
                    etiqueta="Bloque de Redondeo",
                    control=self.txt_bloque_redondeo,
                    obligatorio=True,
                    expand=1,
                ),
                ft.Button(
                    content="Agregar Tramo",
                    icon=ft.Icons.ADD,
                    bgcolor=COLOR_NARANJA,
                    color=COLOR_BLANCO,
                    height=42,
                    style=ft.ButtonStyle(
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding(16, 0, 16, 0),
                    ),
                    on_click=lambda e: self._agregar_fila_tramo(),
                ),
            ],
        )

        encabezado_tabla = ft.Container(
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=6,
            bgcolor=COLOR_SUPERFICIE_SUAVE,
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            content=ft.Row(
                spacing=12,
                controls=[
                    ft.Container(
                        width=70,
                        content=ft.Text(
                            "#",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                    ft.Container(
                        expand=1,
                        content=ft.Text(
                            "DÍA INICIO *",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                    ft.Container(
                        expand=1,
                        content=ft.Text(
                            "DÍA FIN",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                    ft.Container(
                        expand=1,
                        content=ft.Text(
                            "CUOTA DIARIA *",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                    ft.Container(
                        width=44,
                        alignment=ft.Alignment(0, 0),
                        content=ft.Text(
                            "ACCIÓN",
                            size=11,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_GRIS,
                        ),
                    ),
                ],
            ),
        )

        contenido = ft.Column(
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                fila_parametros,
                ft.Divider(height=1, color=COLOR_BORDE_SUAVE),
                encabezado_tabla,
                self.columna_filas_tramos,
            ],
        )

        return self._tarjeta_seccion(
            numero_paso="3",
            titulo="Configuración Adicional — Cobro Incremental por Tramos",
            icono=ft.Icons.TRENDING_UP_OUTLINED,
            contenido=contenido,
        )

    
    #  ENTIDADES DÉBILES (`rangos` Y `tramo`)
   
    def _agregar_fila_rango(
        self,
        limite_inf: str = "",
        limite_sup: str = "",
        cuota: str = "",
        actualizar: bool = True,
    ):
        disc_num = len(self._filas_rangos) + 1
        etiqueta_disc = ft.Text(
            f"#{disc_num}",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=COLOR_AZUL_OSCURO,
        )
        txt_inf = self._crear_textfield(
            placeholder="Ej. 0.00",
            valor_inicial=limite_inf,
        )
        txt_sup = self._crear_textfield(
            placeholder="Sin límite (∞)",
            valor_inicial=limite_sup,
        )
        txt_cuota = self._crear_textfield(
            placeholder="0.00",
            valor_inicial=cuota,
            prefijo="$ ",
            sufijo=" MXN",
        )

        registro = {
            "disc_label": etiqueta_disc,
            "limite_inferior": txt_inf,
            "limite_superior": txt_sup,
            "cuota_mxn": txt_cuota,
        }

        contenedor_fila = ft.Container(
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=8,
            bgcolor=COLOR_BLANCO,
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=70,
                        padding=ft.Padding(8, 6, 8, 6),
                        border_radius=6,
                        bgcolor=COLOR_NARANJA_SUAVE,
                        alignment=ft.Alignment(0, 0),
                        content=etiqueta_disc,
                    ),
                    txt_inf,
                    txt_sup,
                    txt_cuota,
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=COLOR_ROJO_ALERTA,
                        icon_size=19,
                        tooltip="Eliminar escalón de rango",
                        on_click=lambda e, reg=registro: self._eliminar_fila_rango(reg),
                    ),
                ],
            ),
        )
        registro["container"] = contenedor_fila
        self._filas_rangos.append(registro)
        self.columna_filas_rangos.controls.append(contenedor_fila)

        if actualizar:
            self._actualizar_vista()

    def _eliminar_fila_rango(self, registro: dict):
        if len(self._filas_rangos) <= 1:
            self._mostrar_aviso(
                "Debe existir al menos un rango configurado."
            )
            return

        self._filas_rangos.remove(registro)
        self.columna_filas_rangos.controls.remove(registro["container"])
        for idx, item in enumerate(self._filas_rangos, start=1):
            item["disc_label"].value = f"#{idx}"
        self._actualizar_vista()

    def _agregar_fila_tramo(
        self,
        dia_ini: str = "",
        dia_fin: str = "",
        cuota_diaria: str = "",
        actualizar: bool = True,
    ):
        disc_num = len(self._filas_tramos) + 1
        etiqueta_disc = ft.Text(
            f"#{disc_num}",
            size=12,
            weight=ft.FontWeight.BOLD,
            color=COLOR_AZUL_OSCURO,
        )
        txt_ini = self._crear_textfield(
            placeholder="Ej. 1",
            valor_inicial=dia_ini,
            sufijo=" día",
        )
        txt_fin = self._crear_textfield(
            placeholder="En adelante",
            valor_inicial=dia_fin,
            sufijo=" día",
        )
        txt_cuota = self._crear_textfield(
            placeholder="0.00",
            valor_inicial=cuota_diaria,
            prefijo="$ ",
            sufijo=" /día",
        )

        registro = {
            "disc_label": etiqueta_disc,
            "dia_inicio": txt_ini,
            "dia_fin": txt_fin,
            "cuota_diaria_mxn": txt_cuota,
        }

        contenedor_fila = ft.Container(
            padding=ft.Padding(12, 8, 12, 8),
            border_radius=8,
            bgcolor=COLOR_BLANCO,
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Container(
                        width=70,
                        padding=ft.Padding(8, 6, 8, 6),
                        border_radius=6,
                        bgcolor=COLOR_NARANJA_SUAVE,
                        alignment=ft.Alignment(0, 0),
                        content=etiqueta_disc,
                    ),
                    txt_ini,
                    txt_fin,
                    txt_cuota,
                    ft.IconButton(
                        icon=ft.Icons.DELETE_OUTLINE,
                        icon_color=COLOR_ROJO_ALERTA,
                        icon_size=19,
                        tooltip="Eliminar tramo",
                        on_click=lambda e, reg=registro: self._eliminar_fila_tramo(reg),
                    ),
                ],
            ),
        )
        registro["container"] = contenedor_fila
        self._filas_tramos.append(registro)
        self.columna_filas_tramos.controls.append(contenedor_fila)

        if actualizar:
            self._actualizar_vista()

    def _eliminar_fila_tramo(self, registro: dict):
        if len(self._filas_tramos) <= 1:
            self._mostrar_aviso(
                "Debe existir al menos un tramo configurado."
            )
            return

        self._filas_tramos.remove(registro)
        self.columna_filas_tramos.controls.remove(registro["container"])
        for idx, item in enumerate(self._filas_tramos, start=1):
            item["disc_label"].value = f"#{idx}"
        self._actualizar_vista()

    
    # MANEJO DE ESTADO Y EVENTOS DINÁMICOS (`on_change` / `on_select`)

    def _actualizar_estado_stepper(self, paso3_activo: bool):
        if paso3_activo:
            self.circulo_paso3.bgcolor = COLOR_NARANJA
            self.circulo_paso3.border = None
            self.circulo_paso3.content = ft.Text(
                "3",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=COLOR_BLANCO,
            )
            self.texto_paso3.color = COLOR_AZUL_OSCURO
            self.conector_paso3.bgcolor = COLOR_NARANJA
        else:
            self.circulo_paso3.bgcolor = COLOR_SUPERFICIE_SUAVE
            self.circulo_paso3.border = ft.Border.all(1.5, COLOR_BORDE_SUAVE)
            self.circulo_paso3.content = ft.Text(
                "3",
                size=11,
                weight=ft.FontWeight.BOLD,
                color=COLOR_GRIS,
            )
            self.texto_paso3.color = COLOR_GRIS
            self.conector_paso3.bgcolor = COLOR_BORDE_SUAVE

    def on_change_tipo_cobro(self, e: ft.ControlEvent | None = None):
        """
        Transforma dinámicamente el Paso 3 según el Método de Cobro elegido
        en el Paso 2.
        """
        seleccion = self.dd_tipo_cobro.value

        if seleccion == "CUOTA_FIJA":
            self.contenedor_dinamico_fase3.content = self.panel_cuota_fija
            self.txt_badge_polimorfico.value = TipoConcepto.SERVICIO_CUOTA_FIJA.value
            self.txt_resumen_formula.value = (
                "Fórmula activa: Importe MXN = Cuota Fija única por servicio."
            )
            self._actualizar_estado_stepper(True)

        elif seleccion == "FACTOR_UNITARIO":
            self.contenedor_dinamico_fase3.content = self.panel_factor_unitario
            self._actualizar_subtipo_factor_unitario()
            self._actualizar_estado_stepper(True)

        elif seleccion == "POR_RANGOS":
            self.contenedor_dinamico_fase3.content = self.panel_por_rangos
            self.txt_badge_polimorfico.value = TipoConcepto.SERVICIO_RANGO.value
            self.txt_resumen_formula.value = (
                "Fórmula activa: Se evalúa la variable dentro del rango correspondiente "
                "y se asigna la cuota del escalón."
            )
            self._actualizar_estado_stepper(True)

        elif seleccion == "INCREMENTAL":
            self.contenedor_dinamico_fase3.content = self.panel_incremental
            self.txt_badge_polimorfico.value = TipoConcepto.SERVICIO_INCREMENTAL.value
            self.txt_resumen_formula.value = (
                "Fórmula activa: (Cantidad / Bloque de Redondeo) × Σ(Días en tramo × Cuota Diaria)."
            )
            self._actualizar_estado_stepper(True)

        else:
            self.contenedor_dinamico_fase3.content = self.panel_vacio_fase3
            self.txt_badge_polimorfico.value = "PENDIENTE DE SELECCIÓN"
            self.txt_resumen_formula.value = (
                "Selecciona un método de cobro para configurar los parámetros de la tarifa."
            )
            self._actualizar_estado_stepper(False)

        self._actualizar_vista()

    def on_change_lineal_mixto(self, e: ft.ControlEvent):
        activo = bool(self.sw_lineal_mixto.value)
        if activo and self.sw_factor_compuesto.value:
            self.sw_factor_compuesto.value = False
            self.contenedor_hijo_factor_compuesto.visible = False

        self.contenedor_hijo_lineal_mixto.visible = activo
        self._actualizar_subtipo_factor_unitario()
        self._actualizar_vista()

    def on_change_factor_compuesto(self, e: ft.ControlEvent):
        activo = bool(self.sw_factor_compuesto.value)
        if activo and self.sw_lineal_mixto.value:
            self.sw_lineal_mixto.value = False
            self.contenedor_hijo_lineal_mixto.visible = False

        self.contenedor_hijo_factor_compuesto.visible = activo
        self._actualizar_subtipo_factor_unitario()
        self._actualizar_vista()

    def _actualizar_subtipo_factor_unitario(self):
        if self.sw_lineal_mixto.value:
            self.txt_badge_polimorfico.value = TipoConcepto.SERVICIO_LINEAL_MIXTO.value
            self.txt_resumen_formula.value = (
                "Fórmula activa (Lineal Mixto): Importe MXN = Cuota Base + (máx(Variable Primaria, Unidades Mínimas) × Factor Unitario)."
            )
        elif self.sw_factor_compuesto.value:
            self.txt_badge_polimorfico.value = (
                TipoConcepto.SERVICIO_FACTOR_COMPUESTO.value
            )
            self.txt_resumen_formula.value = (
                "Fórmula activa (Factor Compuesto): Importe MXN = máx(Variable Primaria, Unidades Mínimas) × Variable Secundaria × Factor Unitario."
            )
        else:
            self.txt_badge_polimorfico.value = (
                TipoConcepto.SERVICIO_FACTOR_UNITARIO.value
            )
            self.txt_resumen_formula.value = (
                "Fórmula activa (Factor Unitario Simple): Importe MXN = máx(Variable Primaria, Unidades Mínimas) × Factor Unitario."
            )

    
    # LAYOUT GENERAL (ENCABEZADO CON STEPPER, PASOS 1-3 Y PIE)
    
    def _construir_stepper(self) -> ft.Container:
        paso1 = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=26,
                    height=26,
                    border_radius=13,
                    bgcolor=COLOR_NARANJA,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "1",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BLANCO,
                    ),
                ),
                ft.Text(
                    "1. Datos Generales",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=COLOR_AZUL_OSCURO,
                ),
            ],
        )

        conector1 = ft.Container(
            width=28,
            height=2,
            bgcolor=COLOR_NARANJA,
            border_radius=1,
        )

        paso2 = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    width=26,
                    height=26,
                    border_radius=13,
                    bgcolor=COLOR_NARANJA,
                    alignment=ft.Alignment(0, 0),
                    content=ft.Text(
                        "2",
                        size=11,
                        weight=ft.FontWeight.BOLD,
                        color=COLOR_BLANCO,
                    ),
                ),
                ft.Text(
                    "2. Regla Tarifaria",
                    size=12,
                    weight=ft.FontWeight.W_600,
                    color=COLOR_AZUL_OSCURO,
                ),
            ],
        )

        paso3 = ft.Row(
            spacing=8,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.circulo_paso3,
                self.texto_paso3,
            ],
        )

        return ft.Container(
            padding=ft.Padding(16, 10, 16, 10),
            border_radius=10,
            bgcolor=COLOR_SUPERFICIE_SUAVE,
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            content=ft.Row(
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    paso1,
                    conector1,
                    paso2,
                    self.conector_paso3,
                    paso3,
                ],
            ),
        )

    def _construir_encabezado(self) -> ft.Container:
        return ft.Container(
            bgcolor=COLOR_BLANCO,
            border_radius=12,
            padding=ft.Padding(22, 16, 22, 16),
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            content=ft.Row(
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK_OUTLINED,
                        icon_color=COLOR_AZUL_OSCURO,
                        icon_size=20,
                        tooltip="Volver al Catálogo de Servicios",
                        style=ft.ButtonStyle(
                            bgcolor=COLOR_SUPERFICIE_SUAVE,
                            shape=ft.RoundedRectangleBorder(radius=8),
                        ),
                        on_click=self.cancelar,
                    ),
                    ft.Column(
                        spacing=3,
                        expand=True,
                        controls=[
                            ft.Row(
                                spacing=6,
                                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                                controls=[
                                    ft.Text(
                                        "Catálogo de Servicios",
                                        size=11,
                                        color=COLOR_GRIS,
                                    ),
                                    ft.Icon(
                                        ft.Icons.CHEVRON_RIGHT,
                                        size=14,
                                        color=COLOR_GRIS,
                                    ),
                                    ft.Text(
                                        (
                                            "Editar Servicio"
                                            if self.es_edicion
                                            else "Nuevo Servicio"
                                        ),
                                        size=11,
                                        weight=ft.FontWeight.W_600,
                                        color=COLOR_NARANJA,
                                    ),
                                ],
                            ),
                            ft.Text(
                                (
                                    "Actualiza los datos y la tarifa del servicio"
                                    if self.es_edicion
                                    else "Registro y Configuración Tarifaria de Servicio"
                                ),
                                size=22,
                                weight=ft.FontWeight.BOLD,
                                color=COLOR_AZUL_OSCURO,
                            ),
                        ],
                    ),
                    self._construir_stepper(),
                ],
            ),
        )

    def _construir_seccion_fase1(self) -> ft.Container:
        fila_concepto = ft.Row(
            spacing=14,
            controls=[
                self._campo_con_etiqueta(
                    etiqueta="Nombre en Español",
                    control=self._campo_validado("nombre_es", self.txt_nombre_es),
                    obligatorio=True,
                    expand=5,
                ),
                self._campo_con_etiqueta(
                    etiqueta="Nombre en Inglés",
                    control=self.txt_nombre_en,
                    expand=5,
                ),
                self._campo_con_etiqueta(
                    etiqueta="SKU / Código",
                    control=self.txt_sku,
                    expand=3,
                ),
                self._campo_con_etiqueta(
                    etiqueta="Unidad de Medida",
                    control=self._campo_validado(
                        "unidad_medida",
                        self.dd_unidad_medida,
                    ),
                    obligatorio=True,
                    expand=3,
                ),
                self._campo_con_etiqueta(
                    etiqueta="Tasa de IVA",
                    control=self._campo_validado("tasa_iva", self.dd_tasa_iva),
                    obligatorio=True,
                    expand=3,
                ),
            ],
        )

        fila_relaciones = ft.Row(
            spacing=14,
            vertical_alignment=ft.CrossAxisAlignment.START,
            controls=[
                self._campo_con_etiqueta(
                    etiqueta="Categoría PDA",
                    control=self._campo_validado(
                        "categoria_pda",
                        self.dd_categoria_pda,
                    ),
                    obligatorio=True,
                    expand=2,
                ),
                self._campo_con_etiqueta(
                    etiqueta="Categoría de Buque",
                    control=self.dd_categoria_buque,
                    expand=2,
                ),
                ft.Container(
                    expand=3,
                    content=ft.Column(
                        spacing=6,
                        horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
                        controls=[
                            self._campo_con_etiqueta(
                                etiqueta="Proveedores Autorizados",
                                control=self.dd_proveedor,
                                obligatorio=True,
                            ),
                            self.contenedor_chips_proveedores,
                        ],
                    ),
                ),
            ],
        )

        contenido = ft.Column(
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                fila_concepto,
                fila_relaciones,
            ],
        )

        return self._tarjeta_seccion(
            numero_paso="1",
            titulo="Datos Generales",
            icono=ft.Icons.DESCRIPTION_OUTLINED,
            contenido=contenido,
        )

    def _construir_seccion_fase2(self) -> ft.Container:
        contenido = ft.Row(
            spacing=18,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self._campo_con_etiqueta(
                    etiqueta="Método de Cobro",
                    control=self._campo_validado(
                        "tipo_cobro",
                        self.dd_tipo_cobro,
                    ),
                    obligatorio=True,
                    expand=2,
                ),
                ft.Container(
                    expand=3,
                    padding=ft.Padding(16, 12, 16, 12),
                    border_radius=8,
                    bgcolor=COLOR_SUPERFICIE_SUAVE,
                    border=ft.Border.all(1, COLOR_BORDE_SUAVE),
                    content=ft.Row(
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(
                                ft.Icons.FUNCTIONS_OUTLINED,
                                color=COLOR_NARANJA,
                                size=22,
                            ),
                            ft.Column(
                                spacing=2,
                                expand=True,
                                controls=[
                                    ft.Text(
                                        "Regla Tarifaria Seleccionada",
                                        size=11,
                                        weight=ft.FontWeight.BOLD,
                                        color=COLOR_AZUL_OSCURO,
                                    ),
                                    self.txt_resumen_formula,
                                ],
                            ),
                        ],
                    ),
                ),
            ],
        )

        return self._tarjeta_seccion(
            numero_paso="2",
            titulo="Método de Cobro",
            icono=ft.Icons.ALT_ROUTE_OUTLINED,
            contenido=contenido,
            borde_destacado=True,
        )

    def _construir_pie_acciones(self) -> ft.Container:
        return ft.Container(
            bgcolor=COLOR_BLANCO,
            border_radius=12,
            padding=ft.Padding(20, 12, 20, 12),
            border=ft.Border.all(1, COLOR_BORDE_SUAVE),
            content=ft.Row(
                alignment=ft.MainAxisAlignment.END,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=12,
                        controls=[
                            ft.Button(
                                content="Limpiar Formulario",
                                icon=ft.Icons.RESTART_ALT_OUTLINED,
                                visible=not self.es_edicion,
                                bgcolor=COLOR_BLANCO,
                                color=COLOR_GRIS,
                                elevation=0,
                                height=42,
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, COLOR_BORDE_SUAVE),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding(16, 0, 16, 0),
                                ),
                                on_click=self.limpiar_formulario,
                            ),
                            ft.Button(
                                content="Cancelar",
                                icon=ft.Icons.CLOSE_OUTLINED,
                                bgcolor=COLOR_BLANCO,
                                color=COLOR_AZUL_OSCURO,
                                elevation=0,
                                height=42,
                                style=ft.ButtonStyle(
                                    side=ft.BorderSide(1, COLOR_AZUL_OSCURO),
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding(18, 0, 18, 0),
                                ),
                                on_click=self.cancelar,
                            ),
                            ft.Button(
                                content=(
                                    "Guardar cambios"
                                    if self.es_edicion
                                    else "Guardar Servicio"
                                ),
                                icon=ft.Icons.SAVE_OUTLINED,
                                bgcolor=COLOR_NARANJA,
                                color=COLOR_BLANCO,
                                elevation=1,
                                height=42,
                                style=ft.ButtonStyle(
                                    shape=ft.RoundedRectangleBorder(radius=8),
                                    padding=ft.Padding(22, 0, 22, 0),
                                ),
                                on_click=self.guardar_servicio,
                            ),
                        ],
                    ),
                ],
            ),
        )

    def _construir_layout(self) -> ft.Column:
        cuerpo_scrollable = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                self._construir_seccion_fase1(),
                self._construir_seccion_fase2(),
                self.contenedor_dinamico_fase3,
            ],
        )

        return ft.Column(
            expand=True,
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            controls=[
                self._construir_encabezado(),
                cuerpo_scrollable,
                self._construir_pie_acciones(),
            ],
        )

    
    # SIMULACIÓN DE GUARDADO
    def limpiar_formulario(self, e: ft.ControlEvent | None = None):
        self.txt_nombre_es.value = ""
        self.txt_nombre_en.value = ""
        self.txt_sku.value = ""
        self._imagen_path = None
        self._archivo_imagen = None
        self.boton_imagen.content = self._contenido_boton_imagen()
        self.dd_unidad_medida.value = "SERVICIO"
        self.dd_tasa_iva.value = "0.1600"
        self.dd_categoria_pda.value = None
        self.dd_categoria_buque.value = "TODAS"
        self._proveedores_seleccionados.clear()
        self._renderizar_chips_proveedores()

        self.dd_tipo_cobro.value = None
        self.txt_cuota_fija.value = ""
        self.txt_factor_mxn.value = ""
        self.txt_unidades_minimas.value = "0.00"
        self.sw_lineal_mixto.value = False
        self.sw_factor_compuesto.value = False
        self.txt_cuota_base.value = ""
        self.contenedor_hijo_lineal_mixto.visible = False
        self.contenedor_hijo_factor_compuesto.visible = False

        self.on_change_tipo_cobro()

    def guardar_servicio(self, e: ft.ControlEvent | None = None):
        if self.controlador is None:
            self._mostrar_aviso(
                "El controlador de servicios no está conectado a la base de datos."
            )
            return
        if not validar_campos(self._validaciones_formulario):
            reproducir_sonido(self._obtener_pagina(), "error")
            self._actualizar_vista()
            return
        if self._archivo_imagen is not None:
            error_imagen = self.controlador.validar_imagen(
                self._archivo_imagen.name,
                self._archivo_imagen.size,
                self._imagen_path,
            )
            if error_imagen:
                self._mostrar_aviso(error_imagen)
                return

        datos = {
            "nombre_es": self.txt_nombre_es.value,
            "nombre_en": self.txt_nombre_en.value,
            "sku": self.txt_sku.value,
            "imagen_path": self._imagen_path,
            "unidad_medida": self.dd_unidad_medida.value,
            "tasa_iva": self.dd_tasa_iva.value,
            "categoria_pda_id": self.dd_categoria_pda.value,
            "categoria_buque_id": self.dd_categoria_buque.value,
            "proveedor_ids": [
                proveedor.id for proveedor in self._proveedores_seleccionados
            ],
            "tipo_cobro": self.dd_tipo_cobro.value,
            "cuota_fija": self.txt_cuota_fija.value,
            "variable_primaria": self.dd_variable_primaria.value,
            "factor_mxn": self.txt_factor_mxn.value,
            "unidades_minimas": self.txt_unidades_minimas.value,
            "lineal_mixto": self.sw_lineal_mixto.value,
            "cuota_base": self.txt_cuota_base.value,
            "factor_compuesto": self.sw_factor_compuesto.value,
            "variable_secundaria": self.dd_variable_secundaria.value,
            "variable_rangos": self.dd_variable_rangos.value,
            "rangos": [
                {
                    "limite_inferior": fila["limite_inferior"].value,
                    "limite_superior": fila["limite_superior"].value,
                    "cuota_mxn": fila["cuota_mxn"].value,
                }
                for fila in self._filas_rangos
            ],
            "variable_cantidad": self.dd_variable_cantidad.value,
            "variable_dias": self.dd_variable_dias.value,
            "bloque_redondeo": self.txt_bloque_redondeo.value,
            "tramos": [
                {
                    "dia_inicio": fila["dia_inicio"].value,
                    "dia_fin": fila["dia_fin"].value,
                    "cuota_diaria_mxn": fila["cuota_diaria_mxn"].value,
                }
                for fila in self._filas_tramos
            ],
        }
        try:
            if self.es_edicion:
                servicio = self.controlador.modificar_servicio(
                    self.servicio_edicion.id,
                    datos,
                )
            else:
                servicio = self.controlador.registrar_servicio(datos)
        except ValueError as error:
            self._mostrar_aviso(str(error))
            return
        except SQLAlchemyError:
            logging.exception("No se pudo guardar el servicio en la base de datos.")
            self._mostrar_aviso(
                "No se pudo guardar el servicio. Revisa la conexión y los datos de la base."
            )
            return

        if self.vista_anterior is not None and hasattr(
            self.vista_anterior, "recargar_catalogo"
        ):
            try:
                self.vista_anterior.recargar_catalogo()
            except SQLAlchemyError:
                logging.exception(
                    "El servicio se guardó, pero no se pudo actualizar el catálogo."
                )
                self._mostrar_aviso(
                    "El servicio se guardó, pero no se pudo actualizar el catálogo."
                )
                return

        if self.es_edicion:
            self.cancelar()
        self._mostrar_aviso(
            (
                f"Servicio '{servicio.nombre_es}' actualizado correctamente."
                if self.es_edicion
                else f"Servicio '{servicio.nombre_es}' guardado correctamente."
            ),
            exito=True,
        )

    def cancelar(self, e: ft.ControlEvent | None = None):
        if self.vista_anterior is not None:
            # Caso 1: PantallaServicios guardó su vista previa en `vista_catalogo`
            if hasattr(self.vista_anterior, "vista_catalogo"):
                self.vista_anterior.padding = ft.Padding(20, 20, 20, 20)
                self.vista_anterior.content = self.vista_anterior.vista_catalogo
                self.vista_anterior.update()
                return
            # Caso 2: El contenedor padre intercambió su `.content`
            if self.parent is not None and hasattr(self.parent, "content"):
                self.parent.content = self.vista_anterior
                self.parent.update()
                return
            # Caso 3: La vista anterior expone `build_ui()`
            if hasattr(self.vista_anterior, "build_ui"):
                self.vista_anterior.build_ui()
                self._actualizar_vista()

    def _mostrar_aviso(self, mensaje: str, exito: bool = False):
        pagina = self._obtener_pagina()
        if pagina is None:
            return
        pagina.show_dialog(
            ft.SnackBar(
                content=ft.Text(
                    mensaje,
                    color=COLOR_BLANCO,
                    weight=ft.FontWeight.W_600,
                ),
                bgcolor=COLOR_VERDE_EXITO if exito else COLOR_AZUL_OSCURO,
            )
        )
        pagina.update()
        reproducir_sonido(pagina, "exito" if exito else "error")

    def _obtener_pagina(self):
        if self.main_page is not None:
            return self.main_page
        try:
            return self.page
        except RuntimeError:
            return None

    def _actualizar_vista(self):
        pagina = self._obtener_pagina()
        if pagina is not None:
            pagina.update()
