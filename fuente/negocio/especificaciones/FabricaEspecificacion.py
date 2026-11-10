from __future__ import annotations

from fuente.negocio.especificaciones.EspecificacionBase import (
    ContextoEscala,
    Especificacion,
)
from fuente.negocio.especificaciones.EspecificacionesPortuarias import (
    REGISTRO_ESPECIFICACIONES,
)


class FabricaEspecificacion:
    """fbrica que construye un árbol de especificaciones a partir de un AST en diccionario json"""

    @classmethod
    def construir(cls, nodo: dict) -> Especificacion[ContextoEscala]:
        if not isinstance(nodo, dict) or not nodo:
            raise ValueError("El nodo del AST debe ser un diccionario no vacío.")

        match nodo.get("tipo"):
            case "AND":
                hijos = nodo.get("hijos")
                if not isinstance(hijos, list) or len(hijos) < 2:
                    raise ValueError(
                        "El nodo 'AND' requiere una lista 'hijos' con al menos 2 elementos."
                    )
                especificacion = cls.construir(hijos[0])
                for hijo in hijos[1:]:
                    especificacion = especificacion & cls.construir(hijo)
                return especificacion

            case "OR":
                hijos = nodo.get("hijos")
                if not isinstance(hijos, list) or len(hijos) < 2:
                    raise ValueError(
                        "El nodo 'OR' requiere una lista 'hijos' con al menos 2 elementos."
                    )
                especificacion = cls.construir(hijos[0])
                for hijo in hijos[1:]:
                    especificacion = especificacion | cls.construir(hijo)
                return especificacion

            case "NOT":
                hijos = nodo.get("hijos")
                if not isinstance(hijos, list) or len(hijos) != 1:
                    raise ValueError(
                        "El nodo 'NOT' requiere una lista 'hijos' con exactamente 1 elemento."
                    )
                return ~cls.construir(hijos[0])

            case "REGLA":
                nombre = nodo.get("nombre")
                if not isinstance(nombre, str) or nombre not in REGISTRO_ESPECIFICACIONES:
                    raise ValueError(
                        f"La regla de especificación '{nombre}' no está registrada o no es válida."
                    )
                parametros = nodo.get("parametros", {})
                if parametros is None:
                    parametros = {}
                if not isinstance(parametros, dict):
                    raise ValueError(
                        f"Los parámetros de la regla '{nombre}' deben ser un diccionario."
                    )
                clase_especificacion = REGISTRO_ESPECIFICACIONES[nombre]
                return clase_especificacion(**parametros)

            case tipo_invalido:
                raise ValueError(
                    f"Tipo de nodo AST desconocido o inválido: '{tipo_invalido}'."
                )
