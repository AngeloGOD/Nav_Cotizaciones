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

#ELIMNAR LSO ENUM'S DE ARRIBA

class TipoPersona(str, enum.Enum):
    FISICA = "FISICA"
    MORAL = "MORAL"
    EXTRANJERO = "EXTRANJERO"

class CategoriaBuque(str, enum.Enum):
    COMERCIAL = "COMERCIAL"         # Carga general, portacontenedores, granelero
    TURISTICO = "TURISTICO"         # Cruceros (> 500 TRB en Circular 007)
    PESQUERO = "PESQUERO"           # Atuneros, camaroneros, etc.
    PETROLERO = "PETROLERO"         # Tanqueros, gaseros, petroquímicos
    RO_RO = "RO_RO"                 # Roll On - Roll Off (Anexo 1 Maniobras)
    RECREO_MENOR = "RECREO_MENOR"   # Yates, veleros y embarcaciones menores

class TipoConcepto(str, enum.Enum):
    SERVICIO = "SERVICIO"
    PRODUCTO = "PRODUCTO"

class TipoEntidadProveedora(str, enum.Enum):
    ASIPONA = "ASIPONA"
    PRESTADOR_PRIVADO = "PRESTADOR_PRIVADO"
    AUTORIDAD_GOBIERNO = "AUTORIDAD_GOBIERNO"
    AGENCIA_PROPIA = "AGENCIA_PROPIA"
    PROVEEDOR_VIVERES = "PROVEEDOR_VIVERES"

class CategoriaPDA(str, enum.Enum):
    ASIPONA_PORT = "ASIPONA (PORT)"
    SERVICES = "SERVICES"
    SEMAR = "SEMAR (HARBOR MASTER)"
    INMIGRATION = "INMIGRATION"
    AGENCY = "AGENCY"
    PROVISIONING = "PROVISIONING"

class CategoriaProducto(str, enum.Enum):
    ABARROTES = "ABARROTES"
    CARNES_PESCADOS = "CARNES_PESCADOS"
    FRUTAS_VERDURAS = "FRUTAS_VERDURAS"
    LACTEOS_EMBUTIDOS = "LACTEOS_EMBUTIDOS"
    BEBIDAS_AGUA = "BEBIDAS_AGUA"
    COMBUSTIBLE_LUBRICANTES = "COMBUSTIBLE_LUBRICANTES"
    INSUMOS_HIELO_SAL = "INSUMOS_HIELO_SAL"
    MATERIALES_SOLDADURA = "MATERIALES_SOLDADURA"

class ArquetipoCalculo(str, enum.Enum):
    CUOTA_FIJA = "CUOTA_FIJA"               
    FACTOR_SIMPLE = "FACTOR_SIMPLE"         # multiplicación de precio base por una unidad (p.e. precio_base * TBR)
    FACTOR_COMPUESTO = "FACTOR_COMPUESTO"   # multiplicación del precio base por dos factores (p.e. precio_base * eslora * tiempo)
    LINEAL_MIXTA = "LINEAL_MIXTA"           # multiplicación y suma (como la ecuación punto pendiente y = mx+b). Ej: TBR * algún_factor + cuota_fija 
    RANGO_ESCALON = "RANGO_ESCALON"         # precio por rango de precios basados en una medida del barco (p.e. 300 para los buques con TBR > 2500)
    PROGRESIVO_TRAMOS = "PROGRESIVO_TRAMOS" # tarifa que aumenta de manera progresiva (p.e. 300 los primeros 3 días, a partir del tercer día 600 hasta el décimo día, etc.) 

class VariableMedida(str, enum.Enum):
    TRB = "TRB"
    ESLORA = "ESLORA"
    TONELADAS = "TONELADAS"
    CONTENEDORES = "CONTENEDORES"
    M3 = "M3"
    PASAJEROS = "PASAJEROS"
    PESO_KG = "PESO_KG"
    HORAS = "HORAS"
    DIAS = "DIAS"
    CANTIDAD_EVENTOS = "CANTIDAD_EVENTOS"

class EstadoCargaContenedor(str, enum.Enum):
    LLENO = "LLENO"
    VACIO = "VACIO"
    TODOS = "TODOS"

class TipoModificador(str, enum.Enum):
    MULTIPLICADOR_PLANEADO = "MULTIPLICADOR_PLANEADO"
    TIEMPO_EXTRA_OPERACION = "TIEMPO_EXTRA_OPERACION"
    TIEMPO_ESPERA_DEMORA = "TIEMPO_ESPERA_DEMORA"       
    PENALIZACION_CANCELACION = "PENALIZACION_CANCELACION"
    CARGO_FIJO_ADICIONAL = "CARGO_FIJO_ADICIONAL"

class RegimenAduanero(str, enum.Enum):
    NINGUNO = "NINGUNO"
    IMPORTACION = "IMPORTACION"             # 7 días libres en tráfico marítimo
    EXPORTACION_GRAL = "EXPORTACION_GRAL"   # 15 días libres
    EXPORTACION_MINERAL = "EXPORTACION_MINERAL" # 30 días libres
    CABOTAJE_TMCD = "CABOTAJE_TMCD"         # Hasta 30 días libres (Nuevos clientes)

class Moneda(str, enum.Enum):
    USD = "USD"
    MXN = "MXN"

class EstadoCotizacion(str, enum.Enum):
    BORRADOR = "BORRADOR"
    PROFORMA = "PROFORMA"
    ANTICIPO_RECIBIDO = "ANTICIPO_RECIBIDO"
    EN_OPERACION = "EN_OPERACION"
    LIQUIDADA_FDA = "LIQUIDADA_FDA"
    CANCELADA = "CANCELADA"

class EtapaCobro(str, enum.Enum):
    PROFORMA = "PROFORMA"
    LIQUIDACION = "LIQUIDACION"