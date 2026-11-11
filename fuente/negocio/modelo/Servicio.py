from __future__ import annotations
from decimal import Decimal
import math
from typing import TYPE_CHECKING
from sqlalchemy import (
    CheckConstraint,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from fuente.negocio.modelo.Base import Base
from fuente.negocio.modelo.CategoriaBuque import CategoriaBuque
from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.ENUMs import TipoConcepto, VariableMedida
from fuente.negocio.modelo.ENUMs import CaracterServicio


class Servicio(Concepto):
    """Herencia 1 rama B, subtipo de concepto y padre de todos los servicios"""
    __tablename__ = "servicio"

    id: Mapped[int] = mapped_column(
        ForeignKey("concepto.id", ondelete="CASCADE"),
        primary_key=True,
    )

    sku: Mapped[str | None] = mapped_column(String(50), nullable=True)
    imagen_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    caracter: Mapped[CaracterServicio] = mapped_column(
        SqlEnum(CaracterServicio, name="caracter_servicio_enum", native_enum=True),
        nullable=False,
    )

    requiere_entrada_salida: Mapped[bool] = mapped_column(nullable=False)

    regla_obligatoriedad: Mapped[dict | None] = mapped_column(
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
    )

    categoria_buque_id: Mapped[int | None] = mapped_column(
        ForeignKey("categoria_buque.id", ondelete="RESTRICT"),
        nullable=True,
    )

    categoria_buque: Mapped["CategoriaBuque | None"] = relationship(
        back_populates="servicios"
    )

    __table_args__ = (
        Index("uq_servicio_sku", "sku", unique=True),
        CheckConstraint(
            "(caracter != 'CONDICIONAL') OR (regla_obligatoriedad IS NOT NULL)",
            name="chk_reglas_si_condicional",
        ),
    )

    __mapper_args__ = {
        "polymorphic_abstract": True,
    }


class ServicioCuotaFija(Servicio):
    """herencia 2 rama A Servicio de Cuota Fija."""
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

    def calcular_cuota_basica(self, datos: dict[str, Decimal]) -> Decimal:
        return Decimal(str(self.cuota))


class ServicioFactorUnitario(Servicio):
    """herencia 2 rama B servicio de factor unitario (padre de lineal mixto y faactor compuesto)"""
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

    def calcular_cuota_basica(self, datos: dict[str, Decimal]) -> Decimal:
        valor_bruto = Decimal(str(datos[self.variable_primaria.value]))
        minimo = Decimal(str(self.unidades_minimas if self.unidades_minimas is not None else "0.00"))
        u1 = max(valor_bruto, minimo)
        return u1 * Decimal(str(self.factor_mxn))


class ServicioLinealMixto(ServicioFactorUnitario):
    """herencia 3 rama B1 servicio lineal mixto"""
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

    def calcular_cuota_basica(self, datos: dict[str, Decimal]) -> Decimal:
        return Decimal(str(self.cuota_base)) + super().calcular_cuota_basica(datos)


class ServicioFactorCompuesto(ServicioFactorUnitario):
    """herencia 3 rama B2 Servicio Factor Compuesto"""
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

    def calcular_cuota_basica(self, datos: dict[str, Decimal]) -> Decimal:
        u2 = Decimal(str(datos[self.variable_secundaria.value]))
        return super().calcular_cuota_basica(datos) * u2


class ServicioRango(Servicio):
    """herencia 2 rama C servicio por rango de wscalón unico"""
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

    def calcular_cuota_basica(self, datos: dict[str, Decimal]) -> Decimal:
        valor = Decimal(str(datos[self.variable_rangos.value]))
        rangos_ordenados = sorted(
            self.rangos,
            key=lambda r: (
                r.disc if r.disc is not None else 0,
                Decimal(str(r.limite_inferior)),
            ),
        )
        for rango in rangos_ordenados:
            lim_inf = Decimal(str(rango.limite_inferior))
            lim_sup = (
                Decimal(str(rango.limite_superior))
                if rango.limite_superior is not None
                else None
            )
            if valor >= lim_inf and (lim_sup is None or valor <= lim_sup):
                return Decimal(str(rango.cuota_mxn))
        raise ValueError(
            f"El valor {valor} para la variable '{self.variable_rangos.value}' "
            f"no coincide con ningún rango del servicio '{self.nombre_es}'."
        )


class Rango(Base):
    """entidad debil de servicio_rango 'rangos'"""
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
    """herencia 2 rama D servicio incremental (progresivamente por tramos de días)"""
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

    def calcular_cuota_basica(self, datos: dict[str, Decimal]) -> Decimal:
        cantidad = Decimal(str(datos[self.variable_cantidad.value]))
        dias_cobrables = Decimal(str(datos[self.variable_dias.value]))

        if dias_cobrables <= Decimal("0") or cantidad <= Decimal("0"):
            return Decimal("0.00")

        bloque = Decimal(str(self.bloque_redondeo if self.bloque_redondeo is not None else "1.00"))
        bloques = Decimal(math.ceil(cantidad / bloque))

        tramos_ordenados = sorted(
            self.tramos,
            key=lambda t: (t.disc if t.disc is not None else 0, t.dia_inicio),
        )

        acumulado_por_bloque = Decimal("0.00")
        for tramo in tramos_ordenados:
            inicio = Decimal(tramo.dia_inicio)
            if dias_cobrables < inicio:
                continue
            fin_efectivo = (
                min(dias_cobrables, Decimal(tramo.dia_fin))
                if tramo.dia_fin is not None
                else dias_cobrables
            )
            dias_en_tramo = fin_efectivo - inicio + Decimal("1")
            if dias_en_tramo > Decimal("0"):
                acumulado_por_bloque += dias_en_tramo * Decimal(str(tramo.cuota_diaria_mxn))

        return bloques * acumulado_por_bloque


class Tramo(Base):
    """entidad debil de servicio_incremental: 'tramo'"""
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
