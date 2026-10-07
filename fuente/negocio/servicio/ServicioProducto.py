from fuente.persistencia.uow.UnitOFWork import AlchemyUnitOfWork as auow
from fuente.negocio.modelo.Producto import Producto

class ServicioProducto():

    def __init__(self, uow: auow):
        self.uow = uow

    def registrar_producto(self, producto: Producto):
        with self.uow:
            self.uow.producto.insertar(producto)
            self.uow.commit()

    def obtener_pagina(self, no_pagina, limite = 10):
        resultado = None
        desplazamiento = (no_pagina - 1) * limite
        with self.uow:
            resultado = self.uow.producto.consultar_pagina(desplazamiento, limite)
        return resultado
