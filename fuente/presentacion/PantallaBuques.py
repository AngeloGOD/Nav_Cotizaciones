
import flet as ft

from fuente.utilidades.Colores import *
from fuente.utilidades.Componentes import *
from fuente.negocio.controlador.ControladorBuque import ControladorBuque
from fuente.presentacion.PantallaRegistrarBuque import PantallaRegistrarBuque


class PantallaBuques(ft.Container):
    def __init__(self, page: ft.Page, servicio_buque):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
        )

        self._page = page
        self.servicio_buque = servicio_buque
        self.controlador = ControladorBuque(servicio_buque)
        self.pagina_actual = 1
        self.registros_por_pagina = 10
        self.total_buques = 0
        self.busqueda = ""

        self.buque_seleccionado = None
        self.dialogo_confirmacion = None

        self.build_ui()

    def build_ui(self):
        self._contenido = ft.Column(
            expand=True,
            spacing=12,
            controls=[
                self.encabezado(),
                self.barra_filtros(),
                self.directorio(),
            ],
        )

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(
                    expand=True,
                    padding=ft.Padding(
                        left=14,
                        right=14,
                        top=8,
                        bottom=18,
                    ),
                    content=self._contenido,
                )
            ],
        )

    def encabezado(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Column(
                    spacing=4,
                    expand=True,
                    controls=[
                        ft.Text(
                            "Gestión de Buques",
                            size=28,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_BANNER,
                        ),
                        ft.Text(
                            "Administra el directorio de buques, "
                            "dimensiones y datos técnicos para proformas.",
                            size=14,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                boton(
                    texto="Registrar buque",
                    icono=ft.Icons.ADD,
                    tipo="principal",
                    on_click=self.ir_a_registro,
                ),
            ],
        )

    def barra_filtros(self):
        return card(
            ft.Row(
                spacing=10,
                controls=[
                    barra_busqueda(
                        hint="Buscar por nombre, IMO, categoría, subtipo o bandera...",
                        on_change=self.buscar,
                    ),
                    boton(
                        texto="Filtros",
                        icono=ft.Icons.TUNE,
                        tipo="secundario",
                        on_click=self.abrir_filtros,
                    ),
                ],
            ),
            padding=10,
            radius=10,
        )

    def buscar(self, e):
        self.busqueda = e.control.value or ""
        self.pagina_actual = 1
        self.actualizar_directorio()

    def abrir_filtros(self, e):
        pass

    def ir_a_registro(self, e):
        self.content = PantallaRegistrarBuque(
            self._page,
            self.servicio_buque,
            vista_anterior=self,
        )
        self.update()

    def cambiar_pagina(self, pagina):
        self.pagina_actual = pagina
        self.actualizar_directorio()

    def actualizar_directorio(self):
        self._contenido.controls[2] = self.directorio()
        self.update()

    def ver_buque(self, buque):
        pass

    def editar_buque(self, buque):
        pass

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

    def crear_tabla_buques(self, buques):
        etiquetas_categoria = {
            "COMERCIAL": "Comercial",
            "TURISTICO": "Turístico",
            "PESQUERO": "Pesquero",
            "PETROLERO": "Petrolero",
            "RO_RO": "Ro-Ro",
            "RECREO_MENOR": "Recreo / Menor",
        }

        filas = []

        for buque in buques:
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
                        content=ft.Column(
                            spacing=2,
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
                spacing=2,
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
                spacing=5,
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

            valor_cat = (
                buque.categoria_buque.value
                if hasattr(buque.categoria_buque, "value")
                else str(buque.categoria_buque or "")
            )
            texto_cat = etiquetas_categoria.get(
                valor_cat.upper(),
                valor_cat or "N/A",
            )

            categoria_y_subtipo = ft.Column(
                spacing=2,
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
                spacing=3,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=5,
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
                spacing=2,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        spacing=5,
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
                        tooltip="Ver buque",
                        tipo="accion",
                        on_click=lambda e, b=buque: self.ver_buque(b),
                    ),
                    boton(
                        icono=ft.Icons.EDIT_OUTLINED,
                        tooltip="Editar buque",
                        tipo="accion",
                        on_click=lambda e, b=buque: self.editar_buque(b),
                    ),
                    boton(
                        icono=ft.Icons.DELETE_OUTLINE,
                        tooltip="Eliminar buque",
                        color=COLOR_ROJO,
                        tipo="accion",
                        on_click=lambda e, b=buque: self.eliminar_buque(b),
                    ),
                ],
            )

            filas.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(nombre),
                        ft.DataCell(identificadores),
                        ft.DataCell(bandera),
                        ft.DataCell(categoria_y_subtipo),
                        ft.DataCell(especificaciones),
                        ft.DataCell(propulsion_y_estado),
                        ft.DataCell(acciones),
                    ],
                )
            )

        columnas = [
            ("Buque", 240),
            ("IMO", 120),
            ("Bandera", 135),
            ("Categoría / Subtipo", 180),
            ("Dimensiones y Arqueo", 240),
            ("Propulsión / Estado", 180),
            ("Acciones", 125),
        ]

        return tabla(
            columnas=columnas,
            filas=filas,
            column_spacing=15,
            horizontal_margin=10,
            heading_row_height=44,
            data_row_min_height=60,
            data_row_max_height=float("inf"),
            columnas_flexibles=True,
        )

    def directorio(self):
        offset = (
            self.pagina_actual - 1
        ) * self.registros_por_pagina

        buques, self.total_buques = (
            self.controlador.obtener_buques(
                texto=self.busqueda,
                limit=self.registros_por_pagina,
                offset=offset,
            )
        )

        tabla_buques = self.crear_tabla_buques(buques)

        titulo = ft.Row(
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Icon(
                        ft.Icons.DIRECTIONS_BOAT_OUTLINED,
                        color=COLOR_BLANCO,
                        size=24,
                    ),
                    bgcolor=COLOR_NARANJA,
                    border_radius=10,
                    padding=10,
                ),
                ft.Column(
                    expand=True,
                    spacing=2,
                    controls=[
                        ft.Text(
                            "Directorio de buques",
                            size=19,
                            weight=ft.FontWeight.BOLD,
                            color=COLOR_NEGRO,
                        ),
                        ft.Text(
                            f"{self.total_buques} buques registrados",
                            size=14,
                            color=COLOR_GRIS,
                        ),
                    ],
                ),
                boton(
                    texto="Exportar",
                    icono=ft.Icons.DOWNLOAD_OUTLINED,
                    tipo="secundario",
                    on_click=self.exportar_buques,
                ),
            ],
        )

        pie = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text(
                    f"Mostrando {len(buques)} de "
                    f"{self.total_buques} buques",
                    size=14,
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

        return card(
            ft.Column(
                expand=True,
                spacing=10,
                controls=[
                    titulo,
                    ft.Divider(
                        height=1,
                        color=COLOR_GRIS_CLARO,
                    ),
                    ft.Container(
                        expand=True,
                        content=tabla_buques,
                    ),
                    ft.Divider(
                        height=1,
                        color=COLOR_GRIS_CLARO,
                    ),
                    pie,
                ],
            ),
            padding=16,
            radius=10,
            expand=True,
        )

    def exportar_buques(self, e):
        pass
