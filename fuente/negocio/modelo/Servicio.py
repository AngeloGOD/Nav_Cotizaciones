from __future__ import annotations
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    Enum as SqlEnum,
    ForeignKey,
    Integer,
    Numeric,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.CategoriaBuque import CategoriaBuque
from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.ENUMs import TipoConcepto, VariableMedida
from fuente.negocio.modelo.ENUMs import CaracterServicio

class Servicio(Concepto):
    """Nivel 1 (Rama B): Subtipo intermedio 'servicio'."""
    __tablename__ = "servicio"

    id: Mapped[int] = mapped_column(
        ForeignKey("concepto.id", ondelete="CASCADE"),
        primary_key=True,
    )

    caracter: Mapped[CaracterServicio] = mapped_column(
         SqlEnum(CaracterServicio, name="caracter_servicio_enum", native_enum=True),
        nullable=False,
    )

    requiere_entrada_salida: Mapped[bool] = mapped_column(nullable=False,)

    categoria_buque_id: Mapped[int | None] = mapped_column(
        ForeignKey("categoria_buque.id", ondelete="RESTRICT"),
        nullable=True,
    )

    categoria_buque: Mapped["CategoriaBuque | None"] = relationship(
        back_populates="servicios"
    )


class ServicioCuotaFija(Servicio):
    """Nivel 2.A: Servicio de Cuota Fija."""
    __tablename__ = "servicio_cuota_fija"

    id: Mapped[int] = mapped_column(
        ForeignKey("servicio.id", ondelete="CASCADE"),
        primary_key=True,
    )
    cuota: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("cuota >= 0", name="chk_servicio_cuota_fija_cuota"),
    )

    __mapper_args__ = {
        "polymorphic_identity": TipoConcepto.SERVICIO_CUOTA_FIJA,
    }


class ServicioFactorUnitario(Servicio):
    """Nivel 2.B: Servicio de Factor Unitario (Padre de Lineal Mixto y Factor Compuesto)."""
    __tablename__ = "servicio_factor_unitario"

    id: Mapped[int] = mapped_column(
        ForeignKey("servicio.id", ondelete="CASCADE"),
        primary_key=True,
    )
    variable_primaria: Mapped[VariableMedida] = mapped_column(
        SqlEnum(VariableMedida, name="variable_medida_enum", native_enum=True),
        nullable=False,
    )
    factor_mxn: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False)
    unidades_minimas: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default=text("0.00"),
    )

    __table_args__ = (
        CheckConstraint("factor_mxn >= 0", name="chk_servicio_factor_unitario_factor"),
        CheckConstraint("unidades_minimas >= 0", name="chk_servicio_factor_unitario_minimas"),
    )

    __mapper_args__ = {
        "polymorphic_identity": TipoConcepto.SERVICIO_FACTOR_UNITARIO,
    }


class ServicioLinealMixto(ServicioFactorUnitario):
    """Nivel 3.B1: Servicio Lineal Mixto."""
    __tablename__ = "servicio_lineal_mixto"

    id: Mapped[int] = mapped_column(
        ForeignKey("servicio_factor_unitario.id", ondelete="CASCADE"),
        primary_key=True,
    )
    cuota_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    __table_args__ = (
        CheckConstraint("cuota_base >= 0", name="chk_servicio_lineal_mixto_cuota_base"),
    )

    __mapper_args__ = {
        "polymorphic_identity": TipoConcepto.SERVICIO_LINEAL_MIXTO,
    }


class ServicioFactorCompuesto(ServicioFactorUnitario):
    """Nivel 3.B2: Servicio Factor Compuesto."""
    __tablename__ = "servicio_factor_compuesto"

    id: Mapped[int] = mapped_column(
        ForeignKey("servicio_factor_unitario.id", ondelete="CASCADE"),
        primary_key=True,
    )
    variable_secundaria: Mapped[VariableMedida] = mapped_column(
        SqlEnum(VariableMedida, name="variable_medida_enum", native_enum=True),
        nullable=False,
    )

    __mapper_args__ = {
        "polymorphic_identity": TipoConcepto.SERVICIO_FACTOR_COMPUESTO,
    }


class ServicioRango(Servicio):
    """Nivel 2.C: Servicio por Rango de Escalón Único."""
    __tablename__ = "servicio_rango"

    id: Mapped[int] = mapped_column(
        ForeignKey("servicio.id", ondelete="CASCADE"),
        primary_key=True,
    )
    variable_rangos: Mapped[VariableMedida] = mapped_column(
        SqlEnum(VariableMedida, name="variable_medida_enum", native_enum=True),
        nullable=False,
    )

    rangos: Mapped[list["Rango"]] = relationship(
        back_populates="servicio",
        cascade="all, delete-orphan",
        order_by="Rango.disc",
    )

    __mapper_args__ = {
        "polymorphic_identity": TipoConcepto.SERVICIO_RANGO,
    }


class Rango(Base):
    """Entidad débil de servicio_rango: 'rangos'."""
    __tablename__ = "rangos"

    servicio_id: Mapped[int] = mapped_column(
        ForeignKey("servicio_rango.id", ondelete="CASCADE"),
        primary_key=True,
    )
    disc: Mapped[int] = mapped_column(Integer, primary_key=True)
    limite_inferior: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    limite_superior: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    cuota_mxn: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    servicio: Mapped["ServicioRango"] = relationship(back_populates="rangos")

    __table_args__ = (
        CheckConstraint("disc > 0", name="chk_rangos_disc"),
        CheckConstraint("limite_inferior >= 0", name="chk_rangos_limite_inferior"),
        CheckConstraint("cuota_mxn >= 0", name="chk_rangos_cuota_mxn"),
        CheckConstraint(
            "limite_superior IS NULL OR limite_superior >= limite_inferior",
            name="chk_rangos_limites",
        ),
    )


class ServicioIncremental(Servicio):
    """Nivel 2.D: Servicio Incremental (Progresivo por Tramos de Días)."""
    __tablename__ = "servicio_incremental"

    id: Mapped[int] = mapped_column(
        ForeignKey("servicio.id", ondelete="CASCADE"),
        primary_key=True,
    )
    variable_cantidad: Mapped[VariableMedida] = mapped_column(
        SqlEnum(VariableMedida, name="variable_medida_enum", native_enum=True),
        nullable=False,
    )
    bloque_redondeo: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("1.00"),
        server_default=text("1.00"),
    )
    variable_dias: Mapped[VariableMedida] = mapped_column(
        SqlEnum(VariableMedida, name="variable_medida_enum", native_enum=True),
        nullable=False,
    )

    tramos: Mapped[list["Tramo"]] = relationship(
        back_populates="servicio",
        cascade="all, delete-orphan",
        order_by="Tramo.disc",
    )

    __table_args__ = (
        CheckConstraint("bloque_redondeo > 0", name="chk_servicio_incremental_bloque"),
    )

    __mapper_args__ = {
        "polymorphic_identity": TipoConcepto.SERVICIO_INCREMENTAL,
    }


class Tramo(Base):
    """Entidad débil de servicio_incremental: 'tramo'."""
    __tablename__ = "tramo"

    servicio_id: Mapped[int] = mapped_column(
        ForeignKey("servicio_incremental.id", ondelete="CASCADE"),
        primary_key=True,
    )
    disc: Mapped[int] = mapped_column(Integer, primary_key=True)
    dia_inicio: Mapped[int] = mapped_column(Integer, nullable=False)
    dia_fin: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cuota_diaria_mxn: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    servicio: Mapped["ServicioIncremental"] = relationship(back_populates="tramos")

    __table_args__ = (
        CheckConstraint("disc > 0", name="chk_tramo_disc"),
        CheckConstraint("dia_inicio > 0", name="chk_tramo_dia_inicio"),
        CheckConstraint("cuota_diaria_mxn >= 0", name="chk_tramo_cuota_diaria_mxn"),
        CheckConstraint(
            "dia_fin IS NULL OR dia_fin >= dia_inicio",
            name="chk_tramo_dias",
        ),
    )
