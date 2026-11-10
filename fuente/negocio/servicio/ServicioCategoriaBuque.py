from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork as auow


class ServicioCategoriaBuque:

    def __init__(self, uow: auow):
        self.uow = uow

    def _limpiar_filtros(self, filtros: dict) -> dict:
        filtros_limpios = {}
        if filtros and "nombre" in filtros:
            nombre = filtros.get("nombre")
            filtros_limpios["nombre"] = (
                nombre.strip() if isinstance(nombre, str) else ""
            )
        return filtros_limpios

    def obtener_pagina(self, no_pagina, limite=10, filtros: dict = {}):
        resultado = None
        desplazamiento = (no_pagina - 1) * limite
        with self.uow:
            if not filtros:
                resultado = self.uow.categoria_buque.consultar_pagina(
                    desplazamiento, limite, {}
                )
            else:
                filtros_limpios = self._limpiar_filtros(filtros)
                resultado = self.uow.categoria_buque.consultar_pagina(
                    desplazamiento, limite, filtros_limpios
                )
        return resultado

    def obtener_todas(self):
        with self.uow:
            return self.uow.categoria_buque.obtener_todas()

    def buscar_por_id(self, id: int):
        with self.uow:
            return self.uow.categoria_buque.buscar_por_id(id)
