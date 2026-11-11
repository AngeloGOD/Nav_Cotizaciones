from __future__ import annotations

from datetime import datetime
from decimal import Decimal
import math

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.Cliente import Cliente
from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.ENUMs import EstadoCotizacion, Moneda
from fuente.negocio.modelo.Producto import Producto  # noqa: F401
from fuente.negocio.modelo.Servicio import Servicio  # noqa: F401


class Cotizacion(Base):
    """reepresenta una PDA (Port Disbursement Account)."""
    __tablename__ = "cotizacion"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    folio: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    cliente_id: Mapped[int] = mapped_column(
        ForeignKey("cliente.id", ondelete="RESTRICT"),
        nullable=False,
    )
    buque_id: Mapped[int] = mapped_column(
        ForeignKey("buque.id", ondelete="RESTRICT"),
        nullable=False,
    )
    fecha_arribo: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    fecha_zarpe: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    horas_estancia: Mapped[Decimal] = mapped_column(
        Numeric(8, 2),
        nullable=False,
        default=Decimal("24.00"),
    )
    moneda: Mapped[Moneda] = mapped_column(
        SqlEnum(Moneda, name="moneda_enum", native_enum=True),
        nullable=False,
        default=Moneda.MXN,
    )
    tipo_cambio: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        nullable=False,
        default=Decimal("1.0000"),
    )
    estado: Mapped[EstadoCotizacion] = mapped_column(
        SqlEnum(EstadoCotizacion, name="estado_cotizacion_enum", native_enum=True),
        nullable=False,
        default=EstadoCotizacion.PENDIENTE,
    )
    total: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
        default=Decimal("0.00"),
    )
    creado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    cliente: Mapped["Cliente"] = relationship()
    buque: Mapped["Buque"] = relationship()
    detalles: Mapped[list["DetalleCotizacion"]] = relationship(
        back_populates="cotizacion",
        cascade="all, delete-orphan",
        order_by="DetalleCotizacion.disc",
    )

    __table_args__ = (
        CheckConstraint("horas_estancia > 0", name="chk_cotizacion_horas_positivas"),
        CheckConstraint("tipo_cambio > 0", name="chk_cotizacion_tc_positivo"),
        CheckConstraint("total >= 0", name="chk_cotizacion_total_no_negativo"),
        CheckConstraint(
            "fecha_zarpe IS NULL OR fecha_zarpe >= fecha_arribo",
            name="chk_cotizacion_fechas_validas",
        ),
    )

    @property
    def dias_estancia(self) -> int:
        if self.horas_estancia is None:
            return 1
        return max(1, math.ceil(Decimal(str(self.horas_estancia)) / Decimal("24")))

    @property
    def subtotal(self) -> Decimal:
        if not self.detalles:
            return Decimal("0.00")
        return sum(
            (
                Decimal(str(d.subtotal))
                for d in self.detalles
                if d.subtotal is not None
            ),
            Decimal("0.00"),
        )

    @property
    def iva(self) -> Decimal:
        if not self.detalles:
            return Decimal("0.00")
        return sum(
            (
                Decimal(str(d.iva))
                for d in self.detalles
                if d.iva is not None
            ),
            Decimal("0.00"),
        )


class DetalleCotizacion(Base):
    """representa cada partida cotizada/fila de la proforma"""
    __tablename__ = "detalle_cotizacion"

    cotizacion_id: Mapped[int] = mapped_column(
        ForeignKey("cotizacion.id", ondelete="CASCADE"),
        primary_key=True,
    )
    disc: Mapped[int] = mapped_column(Integer, primary_key=True)
    concepto_id: Mapped[int] = mapped_column(
        ForeignKey("concepto.id", ondelete="RESTRICT"),
        nullable=False,
    )
    cantidad: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("1.00"),
    )
    precio_unitario: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    subtotal: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    iva: Mapped[Decimal] = mapped_column(
        Numeric(14, 2),
        nullable=False,
    )
    factura: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    observaciones: Mapped[str | None] = mapped_column(
        String(250),
        nullable=True,
    )

    cotizacion: Mapped["Cotizacion"] = relationship(back_populates="detalles")
    concepto: Mapped["Concepto"] = relationship()

    __table_args__ = (
        CheckConstraint("disc > 0", name="chk_detalle_disc_positivo"),
        CheckConstraint("cantidad > 0", name="chk_detalle_cantidad_positiva"),
        CheckConstraint("precio_unitario >= 0", name="chk_detalle_precio_no_negativo"),
        CheckConstraint("subtotal >= 0", name="chk_detalle_subtotal_no_negativo"),
        CheckConstraint("iva >= 0", name="chk_detalle_iva_no_negativo"),
    )

    @property
    def total(self) -> Decimal:
        sub = Decimal(str(self.subtotal)) if self.subtotal is not None else Decimal("0.00")
        imp = Decimal(str(self.iva)) if self.iva is not None else Decimal("0.00")
        return sub + imp
