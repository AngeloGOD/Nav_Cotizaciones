from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Sequence, String, Text

class Cliente(Base):
    __tablename__ = "cliente"
    id_cliente: Mapped[int] = mapped_column(Sequence("id_cliente_seq", start=1) ,primary_key=True)
    razon_social: Mapped[str] = mapped_column(String(150), nullable=False)
    direccion: Mapped[str] = mapped_column(Text)
    rfc: Mapped[str] = mapped_column(String(20), unique=True)
    telefono: Mapped[str] = mapped_column(String(30), unique=True)
    correo_elect: Mapped[str] = mapped_column(String(150), nullable=False, unique= True)
    tipo_cliente: Mapped[str] = mapped_column(String(50), insert_default="armador")
