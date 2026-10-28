from sqlalchemy.exc import SQLAlchemyError

from fuente.negocio.modelo.Cliente import Cliente
from fuente.negocio.modelo.ENUMs import TipoPersona


class ErrorRegistroCliente(Exception):
    pass


class ControladorRegistrarCliente:
    CAMPOS_OBLIGATORIOS = {
        "razon_social": "Nombre o razón social",
        "tipo_persona": "Tipo de persona",
        "direccion": "Dirección fiscal",
        "rfc": "RFC",
        "telefono": "Número telefónico",
        "correo_elect": "Correo electrónico",
    }

    def __init__(self, servicio_cliente):
        self.servicio_cliente = servicio_cliente

    def registrar_cliente(
        self,
        razon_social,
        tipo_persona,
        direccion=None,
        rfc=None,
        telefono=None,
        correo_elect=None,
        es_nuevo_cliente=False,
        activo=True,
    ):
        datos = self.normalizar_datos_cliente(
            razon_social,
            tipo_persona,
            direccion,
            rfc,
            telefono,
            correo_elect,
            es_nuevo_cliente,
            activo,
        )
        self._validar_campos_obligatorios(datos)

        cliente = Cliente(**datos)
        try:
            self.servicio_cliente.registrar_cliente(cliente)
        except SQLAlchemyError as error:
            raise ErrorRegistroCliente(
                "Ocurrió un error al guardar el cliente en la base de datos."
            ) from error
        return cliente

    @staticmethod
    def normalizar_datos_cliente(
        razon_social,
        tipo_persona,
        direccion,
        rfc,
        telefono,
        correo_elect,
        es_nuevo_cliente,
        activo,
    ):
        if isinstance(tipo_persona, str):
            tipo_persona = tipo_persona.strip().upper()
            tipo_persona = TipoPersona(tipo_persona) if tipo_persona else None

        return {
            "razon_social": razon_social.strip() if razon_social else "",
            "tipo_persona": tipo_persona,
            "direccion": direccion.strip() if direccion and direccion.strip() else None,
            "rfc": rfc.strip().upper() if rfc and rfc.strip() else None,
            "telefono": telefono.strip() if telefono and telefono.strip() else None,
            "correo_elect": (
                correo_elect.strip()
                if correo_elect and correo_elect.strip()
                else None
            ),
            "es_nuevo_cliente": bool(es_nuevo_cliente),
            "activo": bool(activo),
        }

    @classmethod
    def _validar_campos_obligatorios(cls, datos):
        faltantes = [
            etiqueta
            for campo, etiqueta in cls.CAMPOS_OBLIGATORIOS.items()
            if not datos[campo]
        ]
        if faltantes:
            raise ValueError(
                "Completa los campos obligatorios: " + ", ".join(faltantes) + "."
            )
