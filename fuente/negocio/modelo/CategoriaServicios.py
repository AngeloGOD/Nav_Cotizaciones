from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Sequence, String, Text

class CategServicios(Base):
    __tablename__ = 'categ_servicios'

    id_cat_servicio: Mapped[int] = mapped_column(primary_key=True)
    nombre_categoria: Mapped[str] = mapped_column(String(100), unique=True)
    descripcion: Mapped[str | None] = mapped_column(Text)