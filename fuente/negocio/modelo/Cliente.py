from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, Enum as SqlEnum, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship, synonym
from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.ENUMs import TipoPersona

if TYPE_CHECKING:
    from fuente.negocio.modelo.Buque import Buque


class Cliente(Base):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(primary_key=True)
    razon_social: Mapped[str] = mapped_column(
        "nombre_razon_social", String(200), nullable=False
    )
    tipo_persona: Mapped[TipoPersona] = mapped_column(
        SqlEnum(TipoPersona, name="tipo_persona_enum", native_enum=True),
        nullable=False,
    )
    rfc: Mapped[str | None] = mapped_column("rfc_tax_id", String(50))
    direccion: Mapped[str | None] = mapped_column(Text)
    correo_elect: Mapped[str | None] = mapped_column("correo_contacto", String(150))
    telefono: Mapped[str | None] = mapped_column(String(50))
    es_nuevo_cliente: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    activo: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    nombre_razon_social = synonym("razon_social")
    rfc_tax_id = synonym("rfc")
    correo_contacto = synonym("correo_elect")

    buques: Mapped[list["Buque"]] = relationship(back_populates="cliente")
