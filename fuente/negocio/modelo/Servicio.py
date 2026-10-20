from datetime import date


from fuente.negocio.modelo.ENUMs import CategoriaBuque, EstadoCargaContenedor, TipoConcepto, TipoEntidadProveedora, TipoModificador
from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.orm import Mapped
from sqlalchemy import Boolean, Date, Integer, String, CheckConstraint, Numeric, ForeignKey
from decimal import Decimal

from fuente.negocio.modelo.Concepto import Concepto
from fuente.negocio.modelo.ENUMs import ArquetipoCalculo, VariableMedida

class Proveedor(Base):
    __tablename__ = "proveedor"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre: Mapped[str] = mapped_column(String(200))
    tipo_entidad: Mapped[TipoEntidadProveedora]
    rfc: Mapped[str | None] = mapped_column(String(20))
    porcentaje_anticipo_exigido: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("100.00"))
    dias_plazo_liquidacion: Mapped[int] = mapped_column(Integer, default=3)
    servicios: Mapped[list["Servicio"]] = relationship(back_populates="proveedor")

    
class Servicio(Concepto):
    """Subtipo B: Servicios portuarios (ASIPONA, Prestadores, Derechos y Agencia)."""
    __tablename__ = "servicio"

    concepto_id: Mapped[int] = mapped_column(ForeignKey("concepto.id", ondelete="CASCADE"), primary_key=True)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedor.id"))
    arquetipo_calculo: Mapped[ArquetipoCalculo]
    variable_primaria: Mapped[VariableMedida]
    variable_secundaria: Mapped[VariableMedida | None]  # Nullable si solo usa una variable
    minimo_unidades: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    divisor_bloque_redondeo: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("1.00"))
    duracion_base_minutos: Mapped[int | None] = mapped_column(Integer)
    oficio_referencia: Mapped[str | None] = mapped_column(String(100))
    proveedor: Mapped["Proveedor"] = relationship(back_populates="servicios")
    tarifas_base: Mapped[list["TarifaBaseServicio"]] = relationship(
        back_populates="servicio", cascade="all, delete-orphan"
    )
    reglas_modificadoras: Mapped[list["ReglaModificadorServicio"]] = relationship(
        back_populates="servicio", cascade="all, delete-orphan"
    )
    __mapper_args__ = {
        "polymorphic_identity": TipoConcepto.SERVICIO,
    }

class TarifaBaseServicio(Base):
    __tablename__ = "tarifa_base_servicio"

    id: Mapped[int] = mapped_column(primary_key=True)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicio.concepto_id", ondelete="CASCADE"))
    categoria_buque_aplicable: Mapped[CategoriaBuque | None]  # None = Aplica a todos los buques
    estado_carga: Mapped[EstadoCargaContenedor | None]
    cuota_fija_mxn: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    factor_unitario_mxn: Mapped[Decimal] = mapped_column(Numeric(12, 4), default=Decimal("0.0000"))
    vigencia_desde: Mapped[date] = mapped_column(Date)
    vigencia_hasta: Mapped[date | None] = mapped_column(Date)
    activo: Mapped[bool] = mapped_column(Boolean, default=True) 
    servicio: Mapped["Servicio"] = relationship(back_populates="tarifas_base")
    rangos_tramos: Mapped[list["TarifaRangoTramo"]] = relationship(
        back_populates="tarifa_base", cascade="all, delete-orphan", order_by="TarifaRangoTramo.numero_orden"
    )

class TarifaRangoTramo(Base):
    __tablename__ = "tarifa_rango_tramo"

    id: Mapped[int] = mapped_column(primary_key=True)
    tarifa_base_id: Mapped[int] = mapped_column(ForeignKey("tarifa_base_servicio.id", ondelete="CASCADE"))
    numero_orden: Mapped[int] = mapped_column(Integer)
    limite_inferior: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    limite_superior: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))  # None = "en adelante"
    cuota_mxn: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    tarifa_base: Mapped["TarifaBaseServicio"] = relationship(back_populates="rangos_tramos")

class ReglaModificadorServicio(Base):
    __tablename__ = "regla_modificador_servicio"

    id: Mapped[int] = mapped_column(primary_key=True)
    servicio_id: Mapped[int] = mapped_column(ForeignKey("servicio.concepto_id", ondelete="CASCADE"))
    codigo_regla: Mapped[str] = mapped_column(String(50))
    nombre_regla: Mapped[str] = mapped_column(String(200))
    fundamento_legal: Mapped[str | None] = mapped_column(String(100))
    tipo_modificador: Mapped[TipoModificador]
    factor_multiplicador: Mapped[Decimal | None] = mapped_column(Numeric(6, 4))
    monto_fijo_mxn: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    minutos_tolerancia: Mapped[int] = mapped_column(Integer, default=0)
    minutos_bloque: Mapped[int | None] = mapped_column(Integer)
    aplicacion_automatica: Mapped[bool] = mapped_column(Boolean, default=False)
    servicio: Mapped["Servicio"] = relationship(back_populates="reglas_modificadoras")