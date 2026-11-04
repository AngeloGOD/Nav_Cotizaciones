from __future__ import annotations
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, Enum as SqlEnum, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.ENUMs import TipoProveedor

if TYPE_CHECKING:
    from fuente.negocio.modelo.Concepto import Concepto


class Proveedor(Base):
    __tablename__ = "proveedor"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200), nullable=False)
    rfc: Mapped[str | None] = mapped_column(String(20))
    telefono: Mapped[str | None] = mapped_column(String(50))
    correo: Mapped[str | None] = mapped_column(String(150))
    tipo_proveedor: Mapped[TipoProveedor] = mapped_column(
        SqlEnum(TipoProveedor, name="tipo_proveedor_enum", native_enum=True),
        nullable=False,
    )
    activo: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    conceptos: Mapped[list["Concepto"]] = relationship(
        secondary="concepto_proveedor",
        back_populates="proveedores",
    )
