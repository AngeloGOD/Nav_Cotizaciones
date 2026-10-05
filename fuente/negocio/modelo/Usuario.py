from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Sequence, String
from fuente.negocio.modelo.ENUMs import RolUsuario, EstadoUsuario

class Usuario(Base):
    __tablename__ = "usuario"
    id_usuario: Mapped[int] = mapped_column(Sequence("id_usuario_seq", start=1), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)
    correo_elect: Mapped[str] = mapped_column(String(150), nullable=False, unique= True)
    contraseña_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[RolUsuario] = mapped_column(insert_default= RolUsuario.GERENTE, nullable=False)
    estado: Mapped[EstadoUsuario] = mapped_column(insert_default= EstadoUsuario.ACTIVO, nullable=False)