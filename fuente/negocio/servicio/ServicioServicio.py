from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from fuente.negocio.especificaciones.EspecificacionBase import ContextoEscala
from fuente.negocio.especificaciones.FabricaEspecificacion import FabricaEspecificacion
from fuente.negocio.modelo.ENUMs import CaracterServicio
from fuente.negocio.modelo.Servicio import Servicio
from fuente.persistencia.uow.AbstractUnitOfWork import AbstractUnitOfWork


@dataclass
class PartidaSugeridaProforma:
    """Representa una partida de servicio sugerida automáticamente para una Proforma (PDA)."""
    servicio: Servicio
    etiqueta_maniobra: str = ""
    cantidad_maniobras: Decimal = Decimal("1.00")
    cuota_basica_estimada_mxn: Decimal | None = None


class ServicioServicio:
    """Servicio de dominio para la gestión del catálogo de servicios portuarios y evaluación de obligatoriedad."""

    def __init__(self, uow: AbstractUnitOfWork):
        self.uow = uow

    def registrar_servicio(
        self, servicio: Servicio, proveedor_ids: list[int] | None = None
    ):
        with self.uow as uow:
            uow.servicio.insertar(servicio, proveedor_ids=proveedor_ids)
            uow.commit()

    def modificar_servicio(
        self, servicio: Servicio, proveedor_ids: list[int] | None = None
    ):
        with self.uow as uow:
            uow.servicio.modificar(servicio, proveedor_ids=proveedor_ids)
            uow.commit()

    def eliminar_servicio(self, servicio: Servicio):
        with self.uow as uow:
            uow.servicio.eliminar(servicio)
            uow.commit()

    def buscar_por_id(self, id: int) -> Servicio | None:
        with self.uow as uow:
            return uow.servicio.buscar_por_id(id)

    def buscar_por_nombre(self, nombre: str) -> list[Servicio]:
        with self.uow as uow:
            return uow.servicio.buscar_por_nombre(nombre)

    def obtener_pagina(
        self, no_pagina: int, limite: int = 10, filtros: dict | None = None
    ) -> list[Servicio]:
        desplazamiento = (no_pagina - 1) * limite
        with self.uow as uow:
            return uow.servicio.consultar_pagina(
                desplazamiento, limite, filtros or {}
            )

    def obtener_cantidad_registros(self, filtros: dict | None = None) -> int:
        with self.uow as uow:
            return uow.servicio.contar_registros(filtros or {})

    def obtener_catalogos_registro(self):
        with self.uow as uow:
            return uow.catalogos_servicio.obtener_catalogos_registro()

    def obtener_categorias_pda(self):
        with self.uow as uow:
            return uow.catalogos_servicio.obtener_categorias_pda()

    def cumple_condicion_obligatoriedad(
        self, servicio: Servicio, contexto: ContextoEscala
    ) -> bool:
        if servicio.caracter == CaracterServicio.OBLIGATORIO:
            return True
        if servicio.caracter == CaracterServicio.OPCIONAL:
            return False
        if servicio.caracter == CaracterServicio.CONDICIONAL:
            if not servicio.regla_obligatoriedad:
                return False
            especificacion = FabricaEspecificacion.construir(
                servicio.regla_obligatoriedad
            )
            return especificacion.es_satisfecha_por(contexto)
        return False

    def obtener_servicios_obligatorios_para_escala(
        self,
        contexto: ContextoEscala,
        datos_calculo: dict[str, Decimal] | None = None,
    ) -> list[PartidaSugeridaProforma]:
        categoria_buque_id = contexto.buque.categoria_buque_id
        if (
            categoria_buque_id is None
            and getattr(contexto.buque, "categoria_buque", None) is not None
        ):
            categoria_buque_id = getattr(contexto.buque.categoria_buque, "id", None)

        with self.uow as uow:
            candidatos = uow.servicio.obtener_candidatos_obligatorios_y_condicionales(
                categoria_buque_id
            )

        partidas_sugeridas: list[PartidaSugeridaProforma] = []
        for servicio in candidatos:
            if not self.cumple_condicion_obligatoriedad(servicio, contexto):
                continue

            cuota_estimada: Decimal | None = None
            if datos_calculo is not None:
                cuota_estimada = servicio.calcular_cuota_basica(datos_calculo)

            if servicio.requiere_entrada_salida:
                partidas_sugeridas.append(
                    PartidaSugeridaProforma(
                        servicio=servicio,
                        etiqueta_maniobra="ON ARRIVAL",
                        cantidad_maniobras=Decimal("1.00"),
                        cuota_basica_estimada_mxn=cuota_estimada,
                    )
                )
                partidas_sugeridas.append(
                    PartidaSugeridaProforma(
                        servicio=servicio,
                        etiqueta_maniobra="ON DEPARTURE",
                        cantidad_maniobras=Decimal("1.00"),
                        cuota_basica_estimada_mxn=cuota_estimada,
                    )
                )
            else:
                partidas_sugeridas.append(
                    PartidaSugeridaProforma(
                        servicio=servicio,
                        etiqueta_maniobra="",
                        cantidad_maniobras=Decimal("1.00"),
                        cuota_basica_estimada_mxn=cuota_estimada,
                    )
                )

        return partidas_sugeridas
