from __future__ import annotations
from typing import TYPE_CHECKING
from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import ForeignKey, String, Numeric, Boolean
from fuente.negocio.modelo.ENUMs import CategoriaBuque
from decimal import Decimal

if TYPE_CHECKING:
    from fuente.negocio.modelo.Cliente import Cliente

class Buque(Base):
    __tablename__ = "buque"

    id: Mapped[int] = mapped_column(primary_key=True)
    cliente_id: Mapped[int | None] = mapped_column(ForeignKey("cliente.id", ondelete="SET NULL"))
    nombre: Mapped[str] = mapped_column(String(150))
    numero_imo: Mapped[str | None] = mapped_column(String(20), unique=True)
    categoria_buque: Mapped[CategoriaBuque]
    subtipo_descripcion: Mapped[str | None] = mapped_column(String(100))
    trb_arqueo_bruto: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    eslora_metros: Mapped[Decimal] = mapped_column(Numeric(8, 2))
    calado_metros: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    propulsores_proa_popa: Mapped[bool] = mapped_column(Boolean, default=False)
    es_autopropulsado: Mapped[bool] = mapped_column(Boolean, default=True)
    bandera_pais: Mapped[str | None] = mapped_column(String(80))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    cliente: Mapped["Cliente | None"] = relationship(back_populates="buques")
    #Falta la lista de cotizaciones para el buqe
