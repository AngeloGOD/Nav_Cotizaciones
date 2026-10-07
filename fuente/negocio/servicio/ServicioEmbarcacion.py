from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork as auow
from fuente.negocio.modelo.Embarcacion import Embarcacion

class ServicioEmbarcacion():

    def __init__(self, uow: auow):
        self.uow = uow

    def registrar_embarcacion(self, embarcacion: Embarcacion):
        with self.uow:
            self.uow.embarcacion.insertar(embarcacion)
            self.uow.commit()

    def obtener_pagina(self, no_pagina, limite = 10):
        resultado = None
        desplazamiento = (no_pagina - 1) * limite
        with self.uow:
            resultado = self.uow.embarcacion.consultar_pagina(desplazamiento, limite)
        return resultado

