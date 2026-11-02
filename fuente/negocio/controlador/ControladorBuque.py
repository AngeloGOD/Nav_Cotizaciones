from decimal import Decimal

from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.ENUMs import CategoriaBuque


class ControladorBuque:
    def __init__(self, servicio_buque):
        self.servicio_buque = servicio_buque

    @staticmethod
    def _texto_o_none(valor):
        texto = str(valor).strip() if valor is not None else ""
        return texto or None

    @staticmethod
    def _decimal_o_none(valor):
        if valor is None or str(valor).strip() == "":
            return None
        return Decimal(str(valor).strip())

    def registrar_buque(self, nombre, categoria_buque, trb_arqueo_bruto,
                        eslora_metros, cliente_id=None, numero_imo=None,
                        subtipo_descripcion=None, calado_metros=None,
                        propulsores_proa_popa=False, es_autopropulsado=True,
                        bandera_pais=None, activo=True):
        if isinstance(categoria_buque, str):
            categoria_buque = CategoriaBuque(categoria_buque.strip().upper())

        cliente_id_val = int(str(cliente_id).strip()) if self._texto_o_none(cliente_id) else None
        buque = Buque(
            cliente_id=cliente_id_val,
            nombre=str(nombre).strip(),
            numero_imo=self._texto_o_none(numero_imo),
            categoria_buque=categoria_buque,
            subtipo_descripcion=self._texto_o_none(subtipo_descripcion),
            trb_arqueo_bruto=Decimal(str(trb_arqueo_bruto).strip()),
            eslora_metros=Decimal(str(eslora_metros).strip()),
            calado_metros=self._decimal_o_none(calado_metros),
            propulsores_proa_popa=bool(propulsores_proa_popa),
            es_autopropulsado=bool(es_autopropulsado),
            bandera_pais=self._texto_o_none(bandera_pais),
            activo=bool(activo),
        )
        self.servicio_buque.registrar_buque(buque)
        return buque

    def obtener_buques(self, texto="", limit=10, offset=0, filtros=None):
        pagina = (offset // limit) + 1 if limit else 1
        return self.servicio_buque.consultar_pagina(
            no_pagina=pagina, limite=limit, filtros=filtros or {}, texto=texto or ""
        )

    def obtener_pagina(self, pagina, limite=10, filtros=None, texto=""):
        return self.servicio_buque.consultar_pagina(
            no_pagina=pagina, limite=limite, filtros=filtros or {}, texto=texto or ""
        )

    def modificar_buque(self, buque, nombre, categoria_buque, trb_arqueo_bruto,
                        eslora_metros, cliente_id=None, numero_imo=None,
                        subtipo_descripcion=None, calado_metros=None,
                        propulsores_proa_popa=False, es_autopropulsado=True,
                        bandera_pais=None, activo=True):
        if isinstance(categoria_buque, str):
            categoria_buque = CategoriaBuque(categoria_buque.strip().upper())
        buque.cliente_id = int(str(cliente_id).strip()) if self._texto_o_none(cliente_id) else None
        buque.nombre = str(nombre).strip()
        buque.numero_imo = self._texto_o_none(numero_imo)
        buque.categoria_buque = categoria_buque
        buque.subtipo_descripcion = self._texto_o_none(subtipo_descripcion)
        buque.trb_arqueo_bruto = Decimal(str(trb_arqueo_bruto).strip())
        buque.eslora_metros = Decimal(str(eslora_metros).strip())
        buque.calado_metros = self._decimal_o_none(calado_metros)
        buque.propulsores_proa_popa = bool(propulsores_proa_popa)
        buque.es_autopropulsado = bool(es_autopropulsado)
        buque.bandera_pais = self._texto_o_none(bandera_pais)
        buque.activo = bool(activo)
        self.servicio_buque.modificar_buque(buque)
        return buque
