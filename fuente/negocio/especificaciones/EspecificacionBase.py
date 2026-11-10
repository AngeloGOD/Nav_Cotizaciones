from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from fuente.negocio.modelo.Buque import Buque

T = TypeVar("T")


@dataclass(frozen=True)
class ContextoEscala:
    """contexto de arrobo para evaluar la obligatoriedad de servicios en una escala"""
    buque: Buque
    transporta_mercancia_peligrosa: bool = False
    propulsores_en_optimas_condiciones: bool = True
    dias_estancia: int = 1
    horas_estancia: Decimal = Decimal("24.00")


class Especificacion(ABC, Generic[T]):
    """clase abs del Patrón Specification"""

    @abstractmethod
    def es_satisfecha_por(self, candidato: T) -> bool:
        """Evalúa si el Serviciocandidato cumple con la regla de negocio"""

    def __and__(self, otra: "Especificacion[T]") -> "Especificacion[T]":
        return AndEspecificacion(self, otra)

    def __or__(self, otra: "Especificacion[T]") -> "Especificacion[T]":
        return OrEspecificacion(self, otra)

    def __invert__(self) -> "Especificacion[T]":
        return NotEspecificacion(self)


class AndEspecificacion(Especificacion[T]):
    """Especificación compuesta para la conjunción lógica (AND)."""

    def __init__(self, izquierda: Especificacion[T], derecha: Especificacion[T]) -> None:
        self.izquierda = izquierda
        self.derecha = derecha

    def es_satisfecha_por(self, candidato: T) -> bool:
        return self.izquierda.es_satisfecha_por(candidato) and self.derecha.es_satisfecha_por(candidato)


class OrEspecificacion(Especificacion[T]):
    """Especificación compuesta para la disyunción lógica (OR)."""

    def __init__(self, izquierda: Especificacion[T], derecha: Especificacion[T]) -> None:
        self.izquierda = izquierda
        self.derecha = derecha

    def es_satisfecha_por(self, candidato: T) -> bool:
        return self.izquierda.es_satisfecha_por(candidato) or self.derecha.es_satisfecha_por(candidato)


class NotEspecificacion(Especificacion[T]):
    """Especificación compuesta para la negación lógica (NOT)."""

    def __init__(self, especificacion: Especificacion[T]) -> None:
        self.especificacion = especificacion

    def es_satisfecha_por(self, candidato: T) -> bool:
        return not self.especificacion.es_satisfecha_por(candidato)
