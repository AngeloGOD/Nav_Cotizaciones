from decimal import Decimal
from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.modelo.ENUMs import CategoriaBuque


class ControladorBuque:
    def __init__(self, servicio_buque):
        self.servicio_buque = servicio_buque

    def registrar_buque(
        self,
        nombre,
        categoria_buque,
        trb_arqueo_bruto,
        eslora_metros,
        cliente_id=None,
        numero_imo=None,
        subtipo_descripcion=None,
        calado_metros=None,
        propulsores_proa_popa=False,
        es_autopropulsado=True,
        bandera_pais=None,
        activo=True,
    ):
        if isinstance(categoria_buque, str):
            categoria_buque = CategoriaBuque(categoria_buque.strip().upper())

        cliente_id_val = None
        if cliente_id is not None and str(cliente_id).strip() != "":
            cliente_id_val = int(str(cliente_id).strip())

        calado_val = None
        if calado_metros is not None and str(calado_metros).strip() != "":
            calado_val = Decimal(str(calado_metros).strip())

        buque = Buque(
            cliente_id=cliente_id_val,
            nombre=nombre.strip(),
            numero_imo=numero_imo.strip() if numero_imo and numero_imo.strip() else None,
            categoria_buque=categoria_buque,
            subtipo_descripcion=subtipo_descripcion.strip() if subtipo_descripcion and subtipo_descripcion.strip() else None,
            trb_arqueo_bruto=Decimal(str(trb_arqueo_bruto).strip()),
            eslora_metros=Decimal(str(eslora_metros).strip()),
            calado_metros=calado_val,
            propulsores_proa_popa=bool(propulsores_proa_popa),
            es_autopropulsado=bool(es_autopropulsado),
            bandera_pais=bandera_pais.strip() if bandera_pais and bandera_pais.strip() else None,
            activo=bool(activo),
        )
        self.servicio_buque.registrar_buque(buque)
        return buque

    def obtener_buques(self, texto="", limit=10, offset=0):
        pagina = (offset // limit) + 1 if limit else 1
        buques = self.servicio_buque.obtener_pagina(pagina, limit) or []

        texto = (texto or "").strip().lower()
        if texto:
            buques = [
                buque
                for buque in buques
                if texto in (buque.nombre or "").lower()
                or texto in (buque.numero_imo or "").lower()
                or texto in (buque.bandera_pais or "").lower()
                or texto in (buque.subtipo_descripcion or "").lower()
                or texto in (
                    buque.categoria_buque.value
                    if hasattr(buque.categoria_buque, "value")
                    else str(buque.categoria_buque or "")
                ).lower()
            ]

        return buques, len(buques)

    def obtener_pagina(self, pagina, limite=10):
        return self.servicio_buque.obtener_pagina(pagina, limite)

    def modificar_buque(
        self, buque, nombre, categoria_buque, trb_arqueo_bruto,
        eslora_metros, cliente_id=None, numero_imo=None,
        subtipo_descripcion=None, calado_metros=None,
        propulsores_proa_popa=False, es_autopropulsado=True,
        bandera_pais=None, activo=True
    ):
        if isinstance(categoria_buque, str):
            categoria_buque = CategoriaBuque(categoria_buque.strip().upper())

        cliente_id_val = None
        if cliente_id is not None and str(cliente_id).strip() != "":
            cliente_id_val = int(str(cliente_id).strip())

        calado_val = None
        if calado_metros is not None and str(calado_metros).strip() != "":
            calado_val = Decimal(str(calado_metros).strip())

        buque.cliente_id = cliente_id_val
        buque.nombre = nombre.strip()
        buque.numero_imo = numero_imo.strip() if numero_imo and numero_imo.strip() else None
        buque.categoria_buque = categoria_buque
        buque.subtipo_descripcion = (
            subtipo_descripcion.strip()
            if subtipo_descripcion and subtipo_descripcion.strip()
            else None
        )
        buque.trb_arqueo_bruto = Decimal(str(trb_arqueo_bruto).strip())
        buque.eslora_metros = Decimal(str(eslora_metros).strip())
        buque.calado_metros = calado_val
        buque.propulsores_proa_popa = bool(propulsores_proa_popa)
        buque.es_autopropulsado = bool(es_autopropulsado)
        buque.bandera_pais = (
            bandera_pais.strip()
            if bandera_pais and bandera_pais.strip()
            else None
        )
        buque.activo = bool(activo)

        self.servicio_buque.modificar_buque(buque)
        return buque
