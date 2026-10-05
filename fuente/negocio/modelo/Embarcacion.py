from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Sequence, String, Numeric, ForeignKey, CheckConstraint
from decimal import Decimal
from fuente.negocio.modelo.ENUMs import RolUsuario

class Embarcacion(Base):
    __tablename__ = 'embarcacion'

    id_embarcacion: Mapped[int] = mapped_column(primary_key=True)
    id_cliente: Mapped[int | None] = mapped_column(ForeignKey('cliente.id_cliente', ondelete='SET NULL'))
    nombre: Mapped[str] = mapped_column(String(100))
    matricula: Mapped[str | None] = mapped_column(String(50))
    imo: Mapped[str | None] = mapped_column(String(30), unique=True)
    bandera: Mapped[str | None] = mapped_column(String(50))
    tipo_embarcacion: Mapped[str | None] = mapped_column(String(100))
    
    loa: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    gtr: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    trb: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    tonelaje: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    manga: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    puntual: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    calado_draft: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))
    volumen_cubico: Mapped[Decimal | None] = mapped_column(Numeric(10, 2))

    __table_args__ = (
        CheckConstraint('loa >= 0', name='chk_embarcacion_loa'),
        CheckConstraint('gtr >= 0', name='chk_embarcacion_gtr'),
        CheckConstraint('trb >= 0', name='chk_embarcacion_trb'),
        CheckConstraint('tonelaje >= 0', name='chk_embarcacion_tonelaje'),
        CheckConstraint('manga >= 0', name='chk_embarcacion_manga'),
        CheckConstraint('puntual >= 0', name='chk_embarcacion_puntual'),
        CheckConstraint('calado_draft >= 0', name='chk_embarcacion_calado_draft'),
        CheckConstraint('volumen_cubico >= 0', name='chk_embarcacion_volumen_cubico'),
    )