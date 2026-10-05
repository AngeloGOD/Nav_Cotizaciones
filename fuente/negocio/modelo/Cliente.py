from fuente.negocio.modelo.Base import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import Sequence, String

class Cliente:
    def __init__(self, id_cliente, nombre, rfc, direccion_fiscal, telefono, correo_elect, tipo_cliente):
        self.id_cliente = id_cliente
        self.nombre = nombre
        self.rfc = rfc
        self.direccion_fiscal = direccion_fiscal
        self.telefono = telefono
        self.correo_elect = correo_elect
        self.tipo_cliente = tipo_cliente



class Clientefinal(Base):
    __tablename__ = "cliente"
    id: Mapped[int] = mapped_column(Sequence("id_cliente_seq", start=1) ,primary_key=True)
    nombre: Mapped[str] = mapped_column(String(150), nullable=False)