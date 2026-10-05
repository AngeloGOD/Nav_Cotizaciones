from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import ForeignKey, CheckConstraint
from decimal import Decimal
from fuente.negocio.modelo.ENUMs import TipoConcepto

class Concepto(Base):
    __tablename__ = 'concepto'

    id_concepto: Mapped[int] = mapped_column(primary_key=True)
    id_producto: Mapped[int | None] = mapped_column(ForeignKey('producto.id_producto', ondelete='CASCADE'))
    id_servicio: Mapped[int | None] = mapped_column(ForeignKey('servicio.id_servicio', ondelete='CASCADE'))
    tipo_concepto: Mapped[TipoConcepto] = mapped_column(nullable=True)

    __table_args__ = (
        CheckConstraint(
            "(tipo_concepto = 'PRODUCTO' AND id_producto IS NOT NULL AND id_servicio IS NULL) OR "
            "(tipo_concepto = 'SERVICIO' AND id_servicio IS NOT NULL AND id_producto IS NULL) OR "
            "(tipo_concepto = 'OTRO' AND id_producto IS NULL AND id_servicio IS NULL)",
            name='chk_concepto_origen'
        ),
    )