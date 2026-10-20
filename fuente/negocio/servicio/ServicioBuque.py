from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork as auow
from fuente.negocio.modelo.Buque import Buque

class ServicioBuque():

    def __init__(self, uow: auow):
        self.uow = uow

    def registrar_buque(self, buque: Buque):
        with self.uow:
            self.uow.buque.insertar(buque)
            self.uow.commit()

    def obtener_pagina(self, no_pagina, limite = 10):
        resultado = None
        desplazamiento = (no_pagina - 1) * limite
        with self.uow:
            resultado = self.uow.buque.consultar_pagina(desplazamiento, limite)
        return resultado
