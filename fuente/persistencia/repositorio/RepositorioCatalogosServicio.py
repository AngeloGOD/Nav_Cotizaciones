from sqlalchemy import select
from sqlalchemy.orm.session import Session

from fuente.negocio.modelo.CategoriaBuque import CategoriaBuque
from fuente.negocio.modelo.CategoriaPDA import CategoriaPDA
from fuente.negocio.modelo.ENUMs import TipoProveedor
from fuente.negocio.modelo.Proveedor import Proveedor


class RepositorioCatalogosServicio:
    def __init__(self, sesion: Session):
        self.sesion = sesion

    def obtener_categorias_pda(self):
        return list(
            self.sesion.scalars(
                select(CategoriaPDA).order_by(CategoriaPDA.nombre)
            ).all()
        )

    def obtener_catalogos_registro(self):
        categorias_pda = self.obtener_categorias_pda()
        categorias_buque = self.sesion.scalars(
            select(CategoriaBuque).order_by(CategoriaBuque.categoria)
        ).all()
        proveedores = self.sesion.scalars(
            select(Proveedor)
            .where(
                Proveedor.activo.is_(True),
                Proveedor.tipo_proveedor.in_(
                    [TipoProveedor.SERVICIOS, TipoProveedor.MIXTO]
                ),
            )
            .order_by(Proveedor.nombre)
        ).all()
        return {
            "categorias_pda": list(categorias_pda),
            "categorias_buque": list(categorias_buque),
            "proveedores": list(proveedores),
        }
