from decimal import Decimal

from sqlalchemy.exc import SQLAlchemyError

from fuente.negocio.controlador.ControladorRegistrarBuques import (
    ControladorRegistrarBuques,
    ErrorRegistroBuque,
)
from fuente.negocio.modelo.Buque import Buque
from fuente.negocio.servicio.ServicioCategoriaBuque import ServicioCategoriaBuque


class ControladorBuque:
    GRUPOS_FILTROS = (
        "categorias",
        "banderas",
        "autopropulsion",
        "propulsores",
        "estados",
    )
    CAMPOS_RANGO_FILTRO = (
        "trb_min",
        "trb_max",
        "eslora_min",
        "eslora_max",
        "calado_min",
        "calado_max",
    )
    ETIQUETAS_CATEGORIA = {
        "COMERCIAL": "Comercial",
        "TURISTICO": "Turístico",
        "PESQUERO": "Pesquero",
        "PETROLERO": "Petrolero",
        "RO_RO": "Ro-Ro",
        "RECREO_MENOR": "Recreo / Menor",
    }
    COLUMNAS_EXPORTACION = {
        "Buque": "nombre",
        "IMO": "numero_imo",
        "Cliente": "cliente",
        "Bandera / País": "bandera_pais",
        "Categoría": "categoria",
        "Subtipo": "subtipo_descripcion",
        "TRB": "trb",
        "Eslora (m)": "eslora",
        "Calado (m)": "calado",
        "Autopropulsado": "autopropulsado",
        "Propulsores P/P": "propulsores",
        "Estado": "estado",
    }
    COLUMNAS_PDF = {
        "Buque": "nombre",
        "IMO": "numero_imo",
        "Cliente": "cliente",
        "Bandera / País": "bandera_pais",
        "Categoría": "categoria",
        "Subtipo": "subtipo_descripcion",
        "TRB": "trb",
        "Eslora (m)": "eslora",
        "Calado (m)": "calado",
        "Autopropulsado": "autopropulsado",
        "Propulsores P/P": "propulsores",
        "Estado": "estado",
    }

    def __init__(self, servicio_buque, servicio_categoria_buque=None):
        self.servicio_buque = servicio_buque
        self.servicio_categoria_buque = (
            servicio_categoria_buque
            if servicio_categoria_buque is not None
            else ServicioCategoriaBuque(servicio_buque.uow)
        )
        self.controlador_registro = ControladorRegistrarBuques(
            servicio_buque,
            servicio_categoria_buque=self.servicio_categoria_buque,
        )

    @classmethod
    def contar_filtros(cls, filtros):
        if not filtros:
            return 0
        return (
            sum(len(filtros.get(grupo) or ()) for grupo in cls.GRUPOS_FILTROS)
            + sum(
                bool(str(filtros.get(campo) or "").strip())
                for campo in cls.CAMPOS_RANGO_FILTRO
            )
        )

    @classmethod
    def etiqueta_categoria(cls, categoria_buque):
        valor = getattr(categoria_buque, "categoria", None)
        if valor is None:
            valor = getattr(categoria_buque, "value", categoria_buque)
        texto = str(valor or "").strip()
        if not texto:
            return ""
        return cls.ETIQUETAS_CATEGORIA.get(texto.upper(), texto)

    @staticmethod
    def _texto_o_none(valor):
        texto = str(valor).strip() if valor is not None else ""
        return texto or None

    @staticmethod
    def _decimal_o_none(valor):
        if valor is None or str(valor).strip() == "":
            return None
        return Decimal(str(valor).strip())

    def obtener_categorias_buque(self, no_pagina=1, limite=10, filtros=None):
        return self.servicio_categoria_buque.obtener_pagina(
            no_pagina, limite=limite, filtros=filtros or {}
        )

    def obtener_todas_categorias_buque(self):
        if hasattr(self.servicio_categoria_buque, "obtener_todas"):
            return self.servicio_categoria_buque.obtener_todas()
        return self.servicio_categoria_buque.obtener_pagina(
            1, limite=100, filtros={}
        )

    def obtener_banderas_registradas(self):
        return self.servicio_buque.obtener_banderas_registradas()

    def buscar_categorias_buque(self, termino="", limite=10):
        termino = (termino or "").strip()
        filtros = {"nombre": termino} if termino else {}
        return self.servicio_categoria_buque.obtener_pagina(
            1, limite=limite, filtros=filtros
        )

    def registrar_buque(
        self,
        nombre,
        categoria_buque_id,
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
        return self.controlador_registro.registrar_buque(
            nombre=nombre,
            categoria_buque_id=categoria_buque_id,
            trb_arqueo_bruto=trb_arqueo_bruto,
            eslora_metros=eslora_metros,
            cliente_id=cliente_id,
            numero_imo=numero_imo,
            subtipo_descripcion=subtipo_descripcion,
            calado_metros=calado_metros,
            propulsores_proa_popa=propulsores_proa_popa,
            es_autopropulsado=es_autopropulsado,
            bandera_pais=bandera_pais,
            activo=activo,
        )

    def obtener_buques(self, texto="", limit=10, offset=0, filtros=None):
        pagina = (offset // limit) + 1 if limit else 1
        return self.servicio_buque.consultar_pagina(
            no_pagina=pagina, limite=limit, filtros=filtros or {}, texto=texto or ""
        )

    def obtener_datos_exportacion(
        self,
        buques_seleccionados=None,
        texto="",
        filtros=None,
    ):
        if buques_seleccionados is not None:
            buques = list(buques_seleccionados)
        else:
            buques = []
            desplazamiento = 0
            total = 0
            while desplazamiento == 0 or desplazamiento < total:
                pagina, total = self.obtener_buques(
                    texto=texto,
                    limit=500,
                    offset=desplazamiento,
                    filtros=filtros,
                )
                if not pagina:
                    break
                buques.extend(pagina)
                desplazamiento += len(pagina)

        filas = []
        for buque in buques:
            cliente_obj = getattr(buque, "cliente", None)
            razon_social = (
                getattr(cliente_obj, "razon_social", None)
                if cliente_obj is not None
                else None
            )
            categoria_obj = getattr(buque, "categoria_buque", None)
            filas.append(
                {
                    "nombre": buque.nombre,
                    "numero_imo": buque.numero_imo,
                    "cliente": (
                        razon_social
                        if razon_social
                        else "Sin cliente asignado"
                    ),
                    "bandera_pais": buque.bandera_pais,
                    "categoria": self.etiqueta_categoria(categoria_obj),
                    "subtipo_descripcion": buque.subtipo_descripcion,
                    "trb": getattr(
                        buque, "trb", getattr(buque, "trb_arqueo_bruto", None)
                    ),
                    "eslora": getattr(
                        buque, "eslora", getattr(buque, "eslora_metros", None)
                    ),
                    "calado": getattr(
                        buque, "calado", getattr(buque, "calado_metros", None)
                    ),
                    "autopropulsado": (
                        "Sí"
                        if getattr(buque, "es_autopropulsado", False)
                        else "No"
                    ),
                    "propulsores": (
                        "Sí"
                        if getattr(buque, "propulsores_proa_popa", False)
                        else "No"
                    ),
                    "estado": (
                        "Activo"
                        if getattr(buque, "activo", False)
                        else "Inactivo"
                    ),
                }
            )
        return filas, self.COLUMNAS_EXPORTACION

    def obtener_pagina(self, pagina, limite=10, filtros=None, texto=""):
        return self.servicio_buque.consultar_pagina(
            no_pagina=pagina, limite=limite, filtros=filtros or {}, texto=texto or ""
        )

    def modificar_buque(
        self,
        buque,
        nombre,
        categoria_buque_id,
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
        datos = ControladorRegistrarBuques.normalizar_datos_buque(
            nombre=nombre,
            categoria_buque_id=categoria_buque_id,
            trb_arqueo_bruto=trb_arqueo_bruto,
            eslora_metros=eslora_metros,
            cliente_id=cliente_id,
            numero_imo=numero_imo,
            subtipo_descripcion=subtipo_descripcion,
            calado_metros=calado_metros,
            propulsores_proa_popa=propulsores_proa_popa,
            es_autopropulsado=es_autopropulsado,
            bandera_pais=bandera_pais,
            activo=activo,
        )
        ControladorRegistrarBuques._validar_campos_obligatorios(datos)
        if datos["numero_imo"] and self.servicio_buque.existe_numero_imo(
            datos["numero_imo"], excluir_id=getattr(buque, "id", None)
        ):
            raise ValueError(
                ControladorRegistrarBuques._mensaje_imo_duplicado(
                    datos["numero_imo"]
                )
            )

        for atributo, valor in datos.items():
            setattr(buque, atributo, valor)
        if self.servicio_categoria_buque is not None:
            buque.categoria_buque = self.servicio_categoria_buque.buscar_por_id(
                datos["categoria_buque_id"]
            )

        try:
            self.servicio_buque.modificar_buque(buque)
        except SQLAlchemyError as error:
            raise ErrorRegistroBuque(
                ControladorRegistrarBuques._mensaje_error_bd(error)
            ) from error
        return buque
