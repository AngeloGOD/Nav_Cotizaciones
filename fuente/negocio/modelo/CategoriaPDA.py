from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fuente.negocio.modelo.Base import Base

if TYPE_CHECKING:
    from fuente.negocio.modelo.Concepto import Concepto


class CategoriaPDA(Base):
    __tablename__ = "categoria_pda"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    conceptos: Mapped[list["Concepto"]] = relationship(back_populates="categoria_pda")
