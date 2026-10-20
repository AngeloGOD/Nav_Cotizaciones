from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey, CheckConstraint, String, Numeric, Boolean
from decimal import Decimal
from fuente.negocio.modelo.ENUMs import TipoConcepto, CategoriaPDA


class Concepto(Base):
    """tabla general para servicios portuarios y productos de avituallamiento."""
    __tablename__ = "concepto"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(40), unique=True)
    nombre_es: Mapped[str] = mapped_column(String(200))
    nombre_en: Mapped[str | None] = mapped_column(String(200))
    tipo_concepto: Mapped[TipoConcepto]
    categoria_pda: Mapped[CategoriaPDA]
    unidad_medida: Mapped[str] = mapped_column(String(40))
    tasa_iva: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.1600"))
    tasa_isr_retencion: Mapped[Decimal] = mapped_column(Numeric(5, 4), default=Decimal("0.0000"))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    __mapper_args__ = {
        "polymorphic_on": "tipo_concepto",
        "polymorphic_identity": "CONCEPTO_BASE",
    }