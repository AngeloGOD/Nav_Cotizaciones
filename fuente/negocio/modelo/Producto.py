from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import String, CheckConstraint, Numeric, ForeignKey
from decimal import Decimal

class Producto(Base):
    __tablename__ = 'producto'

    id_producto: Mapped[int] = mapped_column(primary_key=True)
    id_cat_producto: Mapped[int | None] = mapped_column(ForeignKey('categ_productos.id_cat_producto', ondelete='SET NULL'))
    codigo_producto: Mapped[str | None] = mapped_column(String(50), unique=True)
    nombre_producto: Mapped[str] = mapped_column(String(150))
    nombre_ingles: Mapped[str | None] = mapped_column(String(150))
    unidad_medida: Mapped[str] = mapped_column(String(30))
    precio_base: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal('0.00'))

    __table_args__ = (
        CheckConstraint('precio_base >= 0', name='chk_productos_precio_base'),
    )