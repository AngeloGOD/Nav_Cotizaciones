from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.CategoriaBuque import CategoriaBuque

if TYPE_CHECKING:
    from fuente.negocio.modelo.Cliente import Cliente


class Buque(Base):
    __tablename__ = "buque"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int | None] = mapped_column(
        ForeignKey("cliente.id", ondelete="SET NULL")
    )
    categoria_buque_id: Mapped[int] = mapped_column(
        ForeignKey("categoria_buque.id", ondelete="RESTRICT"),
        nullable=False,
    )
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    numero_imo: Mapped[str | None] = mapped_column(String(20), unique=True)
    subtipo_descripcion: Mapped[str | None] = mapped_column(String(100))
    trb: Mapped[Decimal] = mapped_column("trb", Numeric(12, 2), nullable=False)
    eslora: Mapped[Decimal] = mapped_column("eslora", Numeric(8, 2), nullable=False)
    calado: Mapped[Decimal | None] = mapped_column("calado", Numeric(6, 2))
    propulsores_proa_popa: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    es_autopropulsado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    bandera_pais: Mapped[str | None] = mapped_column(String(80))
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )

    trb_arqueo_bruto = synonym("trb")
    eslora_metros = synonym("eslora")
    calado_metros = synonym("calado")

    cliente: Mapped["Cliente | None"] = relationship(back_populates="buques")
    categoria_buque: Mapped["CategoriaBuque"] = relationship(back_populates="buques")

    __table_args__ = (
        CheckConstraint("trb > 0", name="chk_buque_trb"),
        CheckConstraint("eslora > 0", name="chk_buque_eslora"),
        CheckConstraint("calado > 0", name="chk_buque_calado"),
    )
