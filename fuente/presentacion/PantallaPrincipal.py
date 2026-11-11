import flet as ft

from fuente.negocio.servicio.ServicioCotizacion import ServicioCotizacion
from fuente.negocio.servicio.ServicioReportes import ServicioReportes
from fuente.negocio.servicio.ServicioServicio import ServicioServicio
from fuente.presentacion.MenuLateral import MenuLateral
from fuente.presentacion.BarraSuperior import BarraSuperior
from fuente.presentacion.dashboard import dashboard
from fuente.presentacion.PantallaClientes import PantallaClientes
from fuente.presentacion.PantallaBuques import PantallaBuques
from fuente.presentacion.PantallaCotizaciones import PantallaCotizaciones
from fuente.presentacion.PantallaProductos import PantallaProductos
from fuente.presentacion.PantallaServicios import PantallaServicios
from fuente.presentacion.PantallaReportes import PantallaReportes
from fuente.utilidades.Colores import COLOR_FONDO


class PantallaPrincipal(ft.Container):
    def __init__(
        self,
        page: ft.Page,
        servicio_cliente,
        servicio_buque,
        servicio_categoria_buque=None,
        servicio_cotizacion=None,
        servicio_servicio=None,
    ):
        super().__init__(
            expand=True,
            bgcolor=COLOR_FONDO,
            padding=0,
        )

        self.main_page = page
        self.servicio_cliente = servicio_cliente
        self.servicio_buque = servicio_buque
        self.servicio_categoria_buque = servicio_categoria_buque
        uow = getattr(servicio_buque, "uow", None) or getattr(
            servicio_cliente, "uow", None
        ) or getattr(servicio_cotizacion, "uow", None)
        self.servicio_cotizacion = (
            servicio_cotizacion
            if servicio_cotizacion is not None
            else (ServicioCotizacion(uow) if uow is not None else None)
        )
        self.servicio_servicio = (
            servicio_servicio
            if servicio_servicio is not None
            else (ServicioServicio(uow) if uow is not None else None)
        )
        self.servicio_reportes = (
            ServicioReportes(uow) if uow is not None else None
        )
        self.informes_generados = []

        self.content_area = ft.Container(
            expand=True,
            content=dashboard(
                servicio_cliente=self.servicio_cliente,
                servicio_cotizacion=self.servicio_cotizacion,
                on_navigate=self.cambiar_pantalla,
            ),
        )

        self.menu_lateral = MenuLateral(
            on_cambiar_pantalla=self.cambiar_pantalla
        )

        self.content = ft.Row(
            expand=True,
            spacing=0,
            controls=[
                self.menu_lateral,
                ft.Column(
                    expand=True,
                    spacing=0,
                    controls=[
                        BarraSuperior(),
                        self.content_area,
                    ],
                ),
            ],
        )

    def cambiar_pantalla(self, ruta):
        if ruta == "ruta_dashboard":
            self.content_area.content = dashboard(
                servicio_cliente=self.servicio_cliente,
                servicio_cotizacion=self.servicio_cotizacion,
                on_navigate=self.cambiar_pantalla,
            )

        elif ruta == "ruta_clientes":
            self.content_area.content = PantallaClientes(
                self.main_page,
                self.servicio_cliente,
            )

        elif ruta == "ruta_buques":
            self.content_area.content = PantallaBuques(
                self.main_page,
                self.servicio_buque,
                self.servicio_cliente,
                servicio_categoria_buque=self.servicio_categoria_buque,
            )
        elif ruta == "ruta_cotizaciones":
            self.content_area.content = PantallaCotizaciones(
                self.main_page,
                servicio_cotizacion=self.servicio_cotizacion,
                servicio_buque=self.servicio_buque,
                servicio_cliente=self.servicio_cliente,
                servicio_servicio=self.servicio_servicio,
            )
        elif ruta == "ruta_productos":
            self.content_area.content = PantallaProductos(
                self.main_page
            )
        elif ruta == "ruta_servicios":
            self.content_area.content = PantallaServicios(
                self.main_page,
                servicio_servicio=self.servicio_servicio,
            )
        elif ruta == "ruta_reportes":
            if self.servicio_reportes is None:
                raise RuntimeError(
                    "No se puede abrir Reportes sin una unidad de trabajo configurada."
                )
            self.content_area.content = PantallaReportes(
                self.main_page,
                self.servicio_reportes,
                self.informes_generados,
            )

        if self.page is not None:
            self.content_area.update()
