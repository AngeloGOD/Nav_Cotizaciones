import enum


class EstadoUsuario(enum.Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    BLOQUEADO = "bloqueado"


class RolUsuario(enum.Enum):
    ADMINISTRADOR = "administrador"
    GERENTE = "gerente"
    OPERADOR = "operador"


class TipoCotizacion(enum.Enum):
    PROFORMA_PUERTO = "proforma_puerto"
    VIVERES_PROVEEDURIA = "viveres_proveeduria"
    GENERAL = "general"


class EstadoPago(enum.Enum):
    PENDIENTE = "pendiente"
    PAGADO = "pagado"
    CANCELADO = "cancelado"


class EstadoEnvio(enum.Enum):
    ENVIADO = "enviado"
    FALLIDO = "fallido"
    PENDIENTE = "pendiente"


# =========================================================================
# ENUMS DE BASE DE DATOS POSTGRESQL
# =========================================================================

class TipoPersona(str, enum.Enum):
    FISICA = "FISICA"
    MORAL = "MORAL"
    EXTRANJERO = "EXTRANJERO"


class CaracterServicio(str, enum.Enum):
    OBLIGATORIO = "OBLIGATORIO"
    CONDICIONAL = "CONDICIONAL"
    OPCIONAL = "OPCIONAL"


class TipoProveedor(str, enum.Enum):
    SERVICIOS = "SERVICIOS"
    PRODUCTOS = "PRODUCTOS"
    MIXTO = "MIXTO"


class TipoConcepto(str, enum.Enum):
    PRODUCTO = "PRODUCTO"
    SERVICIO_CUOTA_FIJA = "SERVICIO_CUOTA_FIJA"
    SERVICIO_FACTOR_UNITARIO = "SERVICIO_FACTOR_UNITARIO"
    SERVICIO_LINEAL_MIXTO = "SERVICIO_LINEAL_MIXTO"
    SERVICIO_FACTOR_COMPUESTO = "SERVICIO_FACTOR_COMPUESTO"
    SERVICIO_RANGO = "SERVICIO_RANGO"
    SERVICIO_INCREMENTAL = "SERVICIO_INCREMENTAL"


class VariableMedida(str, enum.Enum):
    TRB = "TRB"
    ESLORA = "ESLORA"
    TONELADAS = "TONELADAS"
    CONTENEDORES = "CONTENEDORES"
    M3 = "M3"
    PASAJEROS = "PASAJEROS"
    PESO_KG = "PESO_KG"
    HORAS_ESTANCIA = "HORAS_ESTANCIA"
    DIAS_ESTANCIA = "DIAS_ESTANCIA"
    DIAS_ALMACENAJE = "DIAS_ALMACENAJE"
    CANTIDAD_EVENTOS = "CANTIDAD_EVENTOS"


class RegimenAduanero(str, enum.Enum):
    NINGUNO = "NINGUNO"
    IMPORTACION = "IMPORTACION"
    EXPORTACION_GRAL = "EXPORTACION_GRAL"
    EXPORTACION_MINERAL = "EXPORTACION_MINERAL"
    CABOTAJE_TMCD = "CABOTAJE_TMCD"


class Moneda(str, enum.Enum):
    MXN = "MXN"
    USD = "USD"


class EstadoCotizacion(str, enum.Enum):
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"


class EtapaCobro(str, enum.Enum):
    PROFORMA = "PROFORMA"
    LIQUIDACION = "LIQUIDACION"
