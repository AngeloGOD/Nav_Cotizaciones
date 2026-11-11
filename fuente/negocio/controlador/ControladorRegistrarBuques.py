from decimal import Decimal, InvalidOperation

from sqlalchemy.exc import SQLAlchemyError

from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.servicio.ServicioCategoriaBuque import ServicioCategoriaBuque


class ErrorRegistroBuque(Exception):
    pass


class ControladorRegistrarBuques:
    CAMPOS_OBLIGATORIOS = {
        "nombre": "Nombre del buque",
        "categoria_buque_id": "Categoría del buque",
        "trb": "Arqueo bruto (TRB)",
        "eslora": "Eslora (m)",
    }

    def __init__(self, servicio_buque, servicio_categoria_buque=None):
        self.servicio_buque = servicio_buque
        self.servicio_categoria_buque = (
            servicio_categoria_buque
            if servicio_categoria_buque is not None
            else ServicioCategoriaBuque(servicio_buque.uow)
        )

    def registrar_buque(
        self,
        nombre,
        categoria_buque_id,
        trb_arqueo_bruto,
        eslora_metros,
        cliente_id=None,
        numero_imo=None,
        subtipo_descripcion=None,
        calado_metros=None,
        propulsores_proa_popa=False,
        es_autopropulsado=True,
        bandera_pais=None,
        activo=True,
    ):
        datos = self.normalizar_datos_buque(
            nombre=nombre,
            categoria_buque_id=categoria_buque_id,
            trb_arqueo_bruto=trb_arqueo_bruto,
            eslora_metros=eslora_metros,
            cliente_id=cliente_id,
            numero_imo=numero_imo,
            subtipo_descripcion=subtipo_descripcion,
            calado_metros=calado_metros,
            propulsores_proa_popa=propulsores_proa_popa,
            es_autopropulsado=es_autopropulsado,
            bandera_pais=bandera_pais,
            activo=activo,
        )
        self._validar_campos_obligatorios(datos)
        self._validar_numero_imo_disponible(datos["numero_imo"])

        buque = Buque(**datos)
        try:
            self.servicio_buque.registrar_buque(buque)
        except SQLAlchemyError as error:
            raise ErrorRegistroBuque(
                self._mensaje_error_bd(error)
            ) from error
        return buque

    def modificar_buque(
        self,
        buque,
        nombre,
        categoria_buque_id,
        trb_arqueo_bruto,
        eslora_metros,
        cliente_id=None,
        numero_imo=None,
        subtipo_descripcion=None,
        calado_metros=None,
        propulsores_proa_popa=False,
        es_autopropulsado=True,
        bandera_pais=None,
        activo=True,
    ):
        datos = self.normalizar_datos_buque(
            nombre=nombre,
            categoria_buque_id=categoria_buque_id,
            trb_arqueo_bruto=trb_arqueo_bruto,
            eslora_metros=eslora_metros,
            cliente_id=cliente_id,
            numero_imo=numero_imo,
            subtipo_descripcion=subtipo_descripcion,
            calado_metros=calado_metros,
            propulsores_proa_popa=propulsores_proa_popa,
            es_autopropulsado=es_autopropulsado,
            bandera_pais=bandera_pais,
            activo=activo,
        )
        self._validar_campos_obligatorios(datos)
        self._validar_numero_imo_disponible(
            datos["numero_imo"], excluir_id=getattr(buque, "id", None)
        )

        for atributo, valor in datos.items():
            setattr(buque, atributo, valor)
        if self.servicio_categoria_buque is not None:
            buque.categoria_buque = self.servicio_categoria_buque.buscar_por_id(
                datos["categoria_buque_id"]
            )

        try:
            self.servicio_buque.modificar_buque(buque)
        except SQLAlchemyError as error:
            raise ErrorRegistroBuque(
                self._mensaje_error_bd(error)
            ) from error
        return buque

    @staticmethod
    def _texto_o_none(valor):
        texto = str(valor).strip() if valor is not None else ""
        return texto or None

    @classmethod
    def _entero_o_none(cls, valor, etiqueta):
        texto = cls._texto_o_none(valor)
        if texto is None:
            return None
        try:
            return int(texto)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{etiqueta} no es válido.") from error

    @staticmethod
    def _decimal_o_none(valor, etiqueta):
        if valor is None or str(valor).strip() == "":
            return None
        try:
            numero = Decimal(str(valor).strip())
        except (InvalidOperation, ValueError, TypeError) as error:
            raise ValueError(f"{etiqueta} debe ser un número válido.") from error
        if not numero.is_finite():
            raise ValueError(f"{etiqueta} debe ser un número válido.")
        return numero

    @classmethod
    def normalizar_datos_buque(
        cls,
        nombre,
        categoria_buque_id,
        trb_arqueo_bruto,
        eslora_metros,
        cliente_id=None,
        numero_imo=None,
        subtipo_descripcion=None,
        calado_metros=None,
        propulsores_proa_popa=False,
        es_autopropulsado=True,
        bandera_pais=None,
        activo=True,
    ):
        return {
            "cliente_id": cls._entero_o_none(cliente_id, "El cliente"),
            "nombre": str(nombre).strip() if nombre is not None else "",
            "numero_imo": cls._texto_o_none(numero_imo),
            "categoria_buque_id": cls._entero_o_none(
                categoria_buque_id, "La categoría del buque"
            ),
            "subtipo_descripcion": cls._texto_o_none(subtipo_descripcion),
            "trb": cls._decimal_o_none(
                trb_arqueo_bruto, "El arqueo bruto (TRB)"
            ),
            "eslora": cls._decimal_o_none(eslora_metros, "La eslora"),
            "calado": cls._decimal_o_none(calado_metros, "El calado"),
            "propulsores_proa_popa": bool(propulsores_proa_popa),
            "es_autopropulsado": bool(es_autopropulsado),
            "bandera_pais": cls._texto_o_none(bandera_pais),
            "activo": bool(activo),
        }

    @classmethod
    def _validar_campos_obligatorios(cls, datos):
        faltantes = [
            etiqueta
            for campo, etiqueta in cls.CAMPOS_OBLIGATORIOS.items()
            if datos.get(campo) in (None, "")
        ]
        if faltantes:
            raise ValueError(
                "Completa los campos obligatorios: "
                + ", ".join(faltantes)
                + "."
            )
        if datos["trb"] <= 0:
            raise ValueError("El arqueo bruto (TRB) debe ser mayor que 0.")
        if datos["eslora"] <= 0:
            raise ValueError("La eslora debe ser mayor que 0.")
        if datos["calado"] is not None and datos["calado"] <= 0:
            raise ValueError("El calado debe ser mayor que 0.")

    def _validar_numero_imo_disponible(
        self, numero_imo: str | None, excluir_id: int | None = None
    ):
        if numero_imo and self.servicio_buque.existe_numero_imo(
            numero_imo, excluir_id
        ):
            raise ValueError(self._mensaje_imo_duplicado(numero_imo))

    @staticmethod
    def _mensaje_imo_duplicado(numero_imo: str) -> str:
        return f"El número IMO '{numero_imo}' ya está registrado en otro buque."

    @staticmethod
    def _mensaje_error_bd(error):
        origen = getattr(error, "orig", error)
        diagnostico = getattr(origen, "diag", None)
        constraint = getattr(diagnostico, "constraint_name", None)
        detalle = str(origen).lower()
        if (
            constraint == "buque_numero_imo_key"
            or "unique constraint failed: buque.numero_imo" in detalle
        ):
            return "Ya existe un buque registrado con ese número IMO."
        return "Ocurrió un error al guardar el buque en la base de datos."

    def obtener_datos(self, pantalla):
        categoria_buque_id = getattr(
            pantalla.categoria_buque,
            "categoria_buque_id_seleccionada",
            None,
        )
        if categoria_buque_id is None:
            categoria_buque_id = getattr(pantalla.categoria_buque, "value", None)
        if isinstance(categoria_buque_id, str):
            categoria_buque_id = categoria_buque_id.strip() or None

        return {
            "nombre": (pantalla.nombre.value or "").strip(),
            "numero_imo": (pantalla.numero_imo.value or "").strip(),
            "cliente_id": pantalla.cliente_busqueda.cliente_id_seleccionado,
            "categoria_buque_id": categoria_buque_id,
            "subtipo_descripcion": (pantalla.subtipo_descripcion.value or "").strip(),
            "bandera_pais": (pantalla.bandera_pais.value or "").strip(),
            "trb_arqueo_bruto": (pantalla.trb_arqueo_bruto.value or "").strip(),
            "eslora_metros": (pantalla.eslora_metros.value or "").strip(),
            "calado_metros": (pantalla.calado_metros.value or "").strip(),
            "es_autopropulsado": bool(pantalla.es_autopropulsado.value),
            "propulsores_proa_popa": bool(pantalla.propulsores_proa_popa.value),
            "activo": bool(pantalla.activo.value),
        }

    def validar_datos(self, datos):
        try:
            normalizados = self.normalizar_datos_buque(**datos)
            self._validar_campos_obligatorios(normalizados)
        except ValueError as error:
            return False, str(error)
        return True, ""

    def guardar_buque(self, datos, buque_a_editar=None):
        valido, mensaje = self.validar_datos(datos)
        if not valido:
            return False, mensaje
        try:
            if buque_a_editar is not None:
                self.modificar_buque(
                    buque=buque_a_editar,
                    **datos,
                )
                return True, "Buque modificado correctamente."
            self.registrar_buque(**datos)
            return True, "Buque registrado correctamente."
        except (ValueError, ErrorRegistroBuque) as error:
            return False, str(error)
        except Exception as error:
            print(f"Error al guardar el buque: {error}")
            return False, "No se pudieron guardar los cambios del buque."
