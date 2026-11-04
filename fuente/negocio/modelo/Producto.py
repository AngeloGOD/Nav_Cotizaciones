from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fuente.negocio.modelo.CategoriaProducto import CategoriaProducto
from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.ENUMs import TipoConcepto


class Producto(Concepto):
    """Nivel 1 (Rama A): Subtipo 'producto'."""
    __tablename__ = "producto"

    id: Mapped[int] = mapped_column(
        ForeignKey("concepto.id", ondelete="CASCADE"),
        primary_key=True,
    )
    categoria_producto_id: Mapped[int] = mapped_column(
        ForeignKey("categoria_producto.id", ondelete="RESTRICT"),
        nullable=False,
    )
    sku: Mapped[str | None] = mapped_column(String(50), unique=True)
    costo_compra: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default=text("0.00"),
    )
    margen_agencia: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default=text("0.00"),
    )
    precio_venta: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    es_perecedero: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )
    requiere_refrigeracion: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=text("false"),
    )

    categoria_producto: Mapped["CategoriaProducto"] = relationship(
        back_populates="productos"
    )

    __table_args__ = (
        CheckConstraint("costo_compra >= 0", name="chk_producto_costo_compra"),
        CheckConstraint("margen_agencia >= 0", name="chk_producto_margen_agencia"),
        CheckConstraint("precio_venta >= 0", name="chk_producto_precio_venta"),
    )

    __mapper_args__ = {
        "polymorphic_identity": TipoConcepto.PRODUCTO,
    }
