import enum

class EstadoUsuario(enum.Enum):
    ACTIVO = 'activo'
    INACTIVO = 'inactivo'
    BLOQUEADO = 'bloqueado'

class RolUsuario(enum.Enum):
    ADMINISTRADOR = 'administrador'
    GERENTE = 'gerente'
    OPERADOR = 'operador'

class EstadoCotizacion(enum.Enum):
    BORRADOR = 'borrador'
    ENVIADA = 'enviada'
    ACEPTADA = 'aceptada'
    RECHAZADA = 'rechazada'
    FACTURADA = 'facturada'

class TipoCotizacion(enum.Enum):
    PROFORMA_PUERTO = 'proforma_puerto'
    VIVERES_PROVEEDURIA = 'viveres_proveeduria'
    GENERAL = 'general'

class EstadoPago(enum.Enum):
    PENDIENTE = 'pendiente'
    PAGADO = 'pagado'
    CANCELADO = 'cancelado'

class EstadoEnvio(enum.Enum):
    ENVIADO = 'enviado'
    FALLIDO = 'fallido'
    PENDIENTE = 'pendiente'

class TipoConcepto(enum.Enum):
    PRODUCTO = 'producto'
    SERVICIO = 'servicio'
    OTRO = 'otro'