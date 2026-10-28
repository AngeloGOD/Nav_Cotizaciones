import flet as ft
from decimal import Decimal
from fuente.presentacion.PantallaPrincipal import PantallaPrincipal
from fuente.utilidades.Colores import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork
from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.Cliente import Cliente
from fuente.negocio.modelo.Usuario import Usuario
from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.CategoriaProductos import CategoriaProductos
from fuente.negocio.modelo.CategoriaServicios import CategServicios
from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.Producto import Producto
from fuente.negocio.modelo.Servicio import Servicio
from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.servicio.ServicioCliente import ServicioCliente
from fuente.negocio.servicio.ServicioBuque import ServicioBuque
from fuente.negocio.servicio.ServicioProducto import ServicioProducto


IMAGENES_ESTATICAS = (
    "fondo_puerto.jpg",
    "fondo_PantallaClientes.jpg",
    "fondo_PantallaRegistrarClientes.jpg",
    "fondo_menulateral.jpg",
    "oplcompleto.png",
)


def main(page: ft.Page, servicio_cliente, servicio_buque):
    page.bgcolor = COLOR_FONDO
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    page.add(
        ft.Stack(
            expand=True,
            controls=[
                ft.Row(
                    height=1,
                    spacing=0,
                    opacity=0,
                    controls=[
                        ft.Image(
                            src=imagen,
                            width=1,
                            height=1,
                            fit=ft.BoxFit.CONTAIN,
                        )
                        for imagen in IMAGENES_ESTATICAS
                    ],
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            expand=True,
                            bgcolor=COLOR_FONDO,
                            content=PantallaPrincipal(
                                page,
                                servicio_cliente,
                                servicio_buque,
                            ),
                        )
                    ],
                    expand=True,
                    spacing=0,
                ),
            ],
        )
    )

def run():
    engine = create_engine(
    "postgresql+psycopg://",
    pool_size=2,
    max_overflow=4,
    pool_pre_ping=True,
    pool_recycle=3600,
    hide_parameters=True,
    isolation_level="READ COMMITTED",
    echo=True
)

    base = Base()
    base.metadata.create_all(engine)
    """datos_buque = {
    'cliente_id': 1,
    'nombre': "Santa María",
    'numero_imo': "9876543",
    'categoria_buque': "COMERCIAL",
    'subtipo_descripcion': "Buque de Carga General",
    'trb_arqueo_bruto': Decimal('2100.00'),
    'eslora_metros': Decimal('120.50'),
    'calado_metros': Decimal('7.80'),
    'propulsores_proa_popa': False,
    'es_autopropulsado': True,
    'bandera_pais': "México",
    'activo': True,
}"""

    args = {
        "razon_social": "ETDA",
        "direccion": "Carretera a Puerto Madero KM 51",
        "rfc": "ETD010101AAA",
        "telefono": "9618084041",
        "correo_elect": "etda@unach.mx",
        "tipo_persona": "MORAL",
        "es_nuevo_cliente": False,
        "activo": True,
    }
    sessionFactory = sessionmaker(bind=engine)
    uow = AlchemyUnitOfWork(sessionFactory)
    serv_cliente = ServicioCliente(uow=uow)
    serv_buque = ServicioBuque(uow=uow)
    servicio_producto = ServicioProducto(uow= uow)
    #serv_buque.registrar_buque(Buque(**datos_buque))
    """
    res = serv_cliente.obtener_pagina(3);
    for cliente in res:
        print((cliente.rfc or "") + " " + cliente.razon_social)
        """
   #serv_cliente.registrar_cliente(cliente= Cliente(**args))
    #A partir de aquí se puede inyectar el uow al servicio

    ft.run(lambda page: main(page, serv_cliente, serv_buque))

if __name__ == "__main__":
    run()
