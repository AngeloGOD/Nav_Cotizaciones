from __future__ import annotations
from typing import TYPE_CHECKING
from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import String, Text, Boolean, DateTime, func
from fuente.negocio.modelo.ENUMs import *
from datetime import datetime

if TYPE_CHECKING:
    from fuente.negocio.modelo.Buque import Buque


class Cliente(Base):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(200))
    direccion: Mapped[str | None] = mapped_column(Text)
    rfc: Mapped[str | None] = mapped_column(String(50))
    correo_elect: Mapped[str | None] = mapped_column(String(150))
    telefono: Mapped[str | None] = mapped_column(String(50))
    tipo_persona: Mapped[TipoPersona]
    es_nuevo_cliente: Mapped[bool] = mapped_column(Boolean, default=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    buques: Mapped[list["Buque"]] = relationship(back_populates="cliente")
    #falta añadirle la lista de cotizaciones a su nombre
