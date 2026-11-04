from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fuente.negocio.modelo.Base import Base

if TYPE_CHECKING:
    from fuente.negocio.modelo.Buque import Buque
    from fuente.negocio.modelo.Servicio import Servicio


class CategoriaBuque(Base):
    __tablename__ = "categoria_buque"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)

    buques: Mapped[list["Buque"]] = relationship(back_populates="categoria_buque")
    servicios: Mapped[list["Servicio"]] = relationship(back_populates="categoria_buque")
