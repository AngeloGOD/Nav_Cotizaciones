from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import String, CheckConstraint, Numeric, ForeignKey
from decimal import Decimal


class Servicio(Base):
    __tablename__ = 'servicio'

    id_servicio: Mapped[int] = mapped_column(primary_key=True)
    id_cat_servicio: Mapped[int | None] = mapped_column(ForeignKey('categ_servicios.id_cat_servicio', ondelete='SET NULL'))
    codigo_servicio: Mapped[str | None] = mapped_column(String(50), unique=True)
    descripcion_servicio: Mapped[str] = mapped_column(String(150))
    concepto_ingles: Mapped[str | None] = mapped_column(String(150))
    categoria_tarifa: Mapped[str | None] = mapped_column(String(100))
    tarifa_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'))
    tipo_origen: Mapped[str | None] = mapped_column(String(50))
    comision_variable: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), default=Decimal('0.00'))

    __table_args__ = (
        CheckConstraint('tarifa_base >= 0', name='chk_servicios_tarifa_base'),
        CheckConstraint('comision_variable >= 0', name='chk_servicios_comision_variable'),
    )