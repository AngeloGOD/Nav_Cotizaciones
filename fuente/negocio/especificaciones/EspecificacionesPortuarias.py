from __future__ import annotations

from decimal import Decimal
import unicodedata

from fuente.negocio.especificaciones.EspecificacionBase import (
    ContextoEscala,
    Especificacion,
)


def _normalizar_nombre_categoria(valor: object) -> str:
    """Normaliza un nombre de categoría a mayúsculas sin espacios ni acentos."""
    if valor is None:
        return ""
    if hasattr(valor, "categoria"):
        texto = str(getattr(valor, "categoria") or "")
    elif hasattr(valor, "value"):
        texto = str(getattr(valor, "value") or "")
    else:
        texto = str(valor)
    texto_sin_acentos = "".join(
        c
        for c in unicodedata.normalize("NFD", texto.strip())
        if unicodedata.category(c) != "Mn"
    )
    return texto_sin_acentos.upper().replace(" ", "")


class TrbMayorIgualSpec(Especificacion[ContextoEscala]):
    """Evalúa si el TRB del buque es mayor o igual al umbral especificado."""

    def __init__(self, umbral_trb: Decimal | int | float | str) -> None:
        self.umbral_trb = Decimal(str(umbral_trb))

    def es_satisfecha_por(self, candidato: ContextoEscala) -> bool:
        return Decimal(str(candidato.buque.trb)) >= self.umbral_trb


class TrbMayorEstrictoSpec(Especificacion[ContextoEscala]):
    """Evalúa si el TRB del buque es estrictamente mayor al umbral especificado."""

    def __init__(self, umbral_trb: Decimal | int | float | str) -> None:
        self.umbral_trb = Decimal(str(umbral_trb))

    def es_satisfecha_por(self, candidato: ContextoEscala) -> bool:
        return Decimal(str(candidato.buque.trb)) > self.umbral_trb


class TrbMenorEstrictoSpec(Especificacion[ContextoEscala]):
    """Evalúa si el TRB del buque es estrictamente menor al umbral especificado."""

    def __init__(self, umbral_trb: Decimal | int | float | str) -> None:
        self.umbral_trb = Decimal(str(umbral_trb))

    def es_satisfecha_por(self, candidato: ContextoEscala) -> bool:
        return Decimal(str(candidato.buque.trb)) < self.umbral_trb


class EsloraMayorIgualSpec(Especificacion[ContextoEscala]):
    """Evalúa si la eslora del buque es mayor o igual al umbral especificado."""

    def __init__(self, umbral_eslora: Decimal | int | float | str) -> None:
        self.umbral_eslora = Decimal(str(umbral_eslora))

    def es_satisfecha_por(self, candidato: ContextoEscala) -> bool:
        return Decimal(str(candidato.buque.eslora)) >= self.umbral_eslora


class CategoriaBuqueNombreSpec(Especificacion[ContextoEscala]):
    """Evalúa si la categoría del buque pertenece al conjunto de categorías permitidas."""

    def __init__(self, categorias: list[str] | tuple[str, ...]) -> None:
        if not isinstance(categorias, (list, tuple, set)):
            raise ValueError("El parámetro 'categorias' debe ser una lista o tupla de cadenas.")
        self.categorias: set[str] = {
            _normalizar_nombre_categoria(cat)
            for cat in categorias
            if cat is not None and str(cat).strip()
        }

    def es_satisfecha_por(self, candidato: ContextoEscala) -> bool:
        categoria_actual = _normalizar_nombre_categoria(
            getattr(candidato.buque, "categoria_buque", None)
        )
        if not categoria_actual:
            return False
        return (
            categoria_actual in self.categorias
            or categoria_actual.replace("_", "") in {c.replace("_", "") for c in self.categorias}
        )


class EmbarcacionMercanciaPeligrosaSpec(Especificacion[ContextoEscala]):
    """Evalúa si la embarcación transporta mercancía peligrosa o es de categoría energética/química."""

    _CATEGORIAS_PELIGROSAS = ("PETROLERO", "PETROQUIMICO", "GASERO", "TANQUERO")

    def __init__(self) -> None:
        self._spec_categoria = CategoriaBuqueNombreSpec(self._CATEGORIAS_PELIGROSAS)

    def es_satisfecha_por(self, candidato: ContextoEscala) -> bool:
        return bool(candidato.transporta_mercancia_peligrosa) or self._spec_categoria.es_satisfecha_por(
            candidato
        )


class ExentoPorAutopropulsionProaPopaSpec(Especificacion[ContextoEscala]):
    """Evalúa si la embarcación está exenta por ser turística/recreo con propulsores en proa y popa óptimos."""

    _CATEGORIAS_EXENTABLES = ("TURISTICO", "CRUCERO", "RECREO", "YATE", "RECREO_MENOR")

    def __init__(self) -> None:
        self._spec_categoria = CategoriaBuqueNombreSpec(self._CATEGORIAS_EXENTABLES)

    def es_satisfecha_por(self, candidato: ContextoEscala) -> bool:
        return (
            self._spec_categoria.es_satisfecha_por(candidato)
            and bool(candidato.buque.propulsores_proa_popa)
            and bool(candidato.propulsores_en_optimas_condiciones)
        )


REGISTRO_ESPECIFICACIONES: dict[str, type[Especificacion[ContextoEscala]]] = {
    "TRB_MAYOR_IGUAL": TrbMayorIgualSpec,
    "TRB_MAYOR_ESTRICTO": TrbMayorEstrictoSpec,
    "TRB_MENOR_ESTRICTO": TrbMenorEstrictoSpec,
    "ESLORA_MAYOR_IGUAL": EsloraMayorIgualSpec,
    "CATEGORIA_BUQUE_NOMBRE": CategoriaBuqueNombreSpec,
    "MERCANCIA_PELIGROSA": EmbarcacionMercanciaPeligrosaSpec,
    "EXENTO_AUTOPROPULSION": ExentoPorAutopropulsionProaPopaSpec,
}
