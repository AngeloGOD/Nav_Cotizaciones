from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Enum as SqlEnum,
    ForeignKey,
    Numeric,
    String,
    Table,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.CategoriaPDA import CategoriaPDA
from fuente.negocio.modelo.ENUMs import TipoConcepto

if TYPE_CHECKING:
    from fuente.negocio.modelo.Proveedor import Proveedor


concepto_proveedor = Table(
    "concepto_proveedor",
    Base.metadata,
    Column(
        "concepto_id",
        ForeignKey("concepto.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    Column(
        "proveedor_id",
        ForeignKey("proveedor.id", ondelete="RESTRICT"),
        primary_key=True,
        nullable=False,
    ),
)


class Concepto(Base):
    """Entidad padre (Nivel 0) para servicios portuarios y productos de avituallamiento."""
    __tablename__ = "concepto"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_pda_id: Mapped[int] = mapped_column(
        ForeignKey("categoria_pda.id", ondelete="RESTRICT"),
        nullable=False,
    )
    nombre_es: Mapped[str] = mapped_column(String(200), nullable=False)
    nombre_en: Mapped[str | None] = mapped_column(String(200))
    unidad_medida: Mapped[str] = mapped_column(String(40), nullable=False)
    tasa_iva: Mapped[Decimal] = mapped_column(
        Numeric(5, 4),
        nullable=False,
        default=Decimal("0.1600"),
        server_default=text("0.1600"),
    )
    tipo_concepto: Mapped[TipoConcepto] = mapped_column(
        SqlEnum(TipoConcepto, name="tipo_concepto_enum", native_enum=True),
        nullable=False,
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    categoria_pda: Mapped["CategoriaPDA"] = relationship(back_populates="conceptos")
    proveedores: Mapped[list["Proveedor"]] = relationship(
        secondary=concepto_proveedor,
        back_populates="conceptos",
    )

    __table_args__ = (
        CheckConstraint("tasa_iva >= 0", name="chk_concepto_tasa_iva"),
    )

    __mapper_args__ = {
        "polymorphic_on": "tipo_concepto",
    }
