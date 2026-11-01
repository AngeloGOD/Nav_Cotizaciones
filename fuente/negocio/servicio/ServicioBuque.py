from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork as auow
from fuente.negocio.modelo.Buque import Buque


class ServicioBuque:
    def __init__(self, uow: auow):
        self.uow = uow

    def registrar_buque(self, buque: Buque):
        with self.uow:
            self.uow.buque.insertar(buque)
            self.uow.commit()

    def consultar_pagina(self, no_pagina, limite=10, filtros=None, texto=""):
        desplazamiento = (no_pagina - 1) * limite
        filtros = filtros or {}
        with self.uow:
            registros = self.uow.buque.consultar_pagina(
                desplazamiento,
                limite,
                filtros=filtros,
                texto=texto or "",
            )
            total = self.uow.buque.contar(
                filtros=filtros,
                texto=texto or "",
            )
        return registros, total

    def obtener_pagina(self, no_pagina, limite=10):
        # Compatibilidad con pantallas o procesos anteriores que esperan solo una lista.
        registros, _ = self.consultar_pagina(no_pagina, limite)
        return registros

    def obtener_cantidad_registros(self):
        with self.uow:
            return self.uow.buque.contar_registros()

    def modificar_buque(self, buque: Buque):
        with self.uow:
            self.uow.buque.modificar(buque)
            self.uow.commit()

    def eliminar_buque(self, buque: Buque):
        with self.uow:
            self.uow.buque.eliminar(buque)
            self.uow.commit()

    def buscar_por_id(self, id: int):
        with self.uow:
            return self.uow.buque.buscar_por_id(id)

    def buscar_por_nombre(self, nombre: str):
        with self.uow:
            return self.uow.buque.buscar_por_nombre(nombre)
