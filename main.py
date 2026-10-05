import flet as ft
from fuente.presentacion.PantallaPrincipal import PantallaPrincipal
from fuente.utilidades.Colores import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork
from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.Cliente import Clientefinal
from fuente.negocio.modelo.Usuario import Usuario
from fuente.negocio.modelo.Embarcacion import Embarcacion
from fuente.negocio.modelo.CategoriaProductos import CategoriaProductos
from fuente.negocio.modelo.CategoriaServicios import CategServicios
from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.Producto import Producto
from fuente.negocio.modelo.Servicio import Servicio

def main(page: ft.Page):
    page.bgcolor = COLOR_FONDO
    page.padding = 0
    page.spacing = 0
    page.theme_mode = ft.ThemeMode.LIGHT

    page.add(
        ft.Row(
            controls=[
                ft.Container(
                    expand=True,
                    bgcolor=COLOR_FONDO,
                    content=PantallaPrincipal(page),
                )
            ],
            expand=True,
            spacing=0,
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

    sessionFactory = sessionmaker(bind=engine)
    uow = AlchemyUnitOfWork(sessionFactory)
    #A partir de aquí se puede inyectar el uow al servicio

    ft.run(main)


if __name__ == "__main__":
    run()