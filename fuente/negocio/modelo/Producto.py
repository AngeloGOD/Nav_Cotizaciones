from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.Concepto import Concepto
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Boolean, String, CheckConstraint, Numeric, ForeignKey
from decimal import Decimal
from fuente.negocio.modelo.ENUMs import CategoriaProducto, TipoConcepto

class Producto(Concepto):
    """Subtipo A: Abarrotes, carnes, víveres, diésel, sal, etc."""
    __tablename__ = "producto"

    concepto_id: Mapped[int] = mapped_column(ForeignKey("concepto.id", ondelete="CASCADE"), primary_key=True)
    categoria_producto: Mapped[CategoriaProducto]
    sku_interno: Mapped[str | None] = mapped_column(String(50))
    costo_compra_mxn: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    porcentaje_margen_agencia: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    precio_venta_mxn: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    es_perecedero: Mapped[bool] = mapped_column(Boolean, default=False)
    requiere_refrigeracion: Mapped[bool] = mapped_column(Boolean, default=False)

    __mapper_args__ = {
        "polymorphic_identity": TipoConcepto.PRODUCTO,
    }