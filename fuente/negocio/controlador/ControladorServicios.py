from decimal import Decimal, InvalidOperation
from pathlib import Path

from fuente.negocio.modelo.ENUMs import (
    CaracterServicio,
    VariableMedida,
)
from fuente.negocio.modelo.Servicio import (
    Rango,
    Servicio,
    ServicioCuotaFija,
    ServicioFactorCompuesto,
    ServicioFactorUnitario,
    ServicioIncremental,
    ServicioLinealMixto,
    ServicioRango,
    Tramo,
)
from fuente.negocio.servicio.ServicioServicio import ServicioServicio


class ControladorServicios:
    def __init__(self, servicio: ServicioServicio):
        self.servicio = servicio

    def obtener_catalogos_registro(self):
        return self.servicio.obtener_catalogos_registro()

    @staticmethod
    def _decimal(valor, etiqueta, permitir_vacio=False):
        texto = str("" if valor is None else valor).strip()
        texto = texto.replace("$", "").replace(",", "")
        if not texto:
            if permitir_vacio:
                return None
            raise ValueError(f"{etiqueta} es obligatorio.")
        try:
            numero = Decimal(texto)
        except (InvalidOperation, ValueError) as error:
            raise ValueError(f"{etiqueta} debe ser un número válido.") from error
        if not numero.is_finite() or numero < 0:
            raise ValueError(f"{etiqueta} debe ser un número mayor o igual a cero.")
        return numero

    @staticmethod
    def _id(valor, etiqueta, opcional=False):
        if opcional and (valor is None or str(valor).strip() in ("", "TODAS")):
            return None
        try:
            resultado = int(valor)
        except (TypeError, ValueError) as error:
            raise ValueError(f"Selecciona {etiqueta}.") from error
        if resultado <= 0:
            raise ValueError(f"Selecciona {etiqueta}.")
        return resultado

    @staticmethod
    def _variable(valor, etiqueta):
        try:
            return VariableMedida(str(valor))
        except ValueError as error:
            raise ValueError(f"Selecciona {etiqueta}.") from error

    @classmethod
    def _crear_rangos(cls, filas):
        if not filas:
            raise ValueError("Agrega al menos un rango tarifario.")
        rangos = []
        limite_anterior = None
        for disc, fila in enumerate(filas, start=1):
            inferior = cls._decimal(
                fila["limite_inferior"], f"El límite inferior del rango {disc}"
            )
            superior = cls._decimal(
                fila["limite_superior"],
                f"El límite superior del rango {disc}",
                permitir_vacio=True,
            )
            cuota = cls._decimal(fila["cuota_mxn"], f"La cuota del rango {disc}")
            if superior is not None and superior < inferior:
                raise ValueError(
                    f"El límite superior del rango {disc} no puede ser menor "
                    "que el límite inferior."
                )
            if limite_anterior is not None and inferior <= limite_anterior:
                raise ValueError("Los rangos no deben traslaparse.")
            if limite_anterior is not None and inferior > limite_anterior + Decimal("0.01"):
                raise ValueError("Los rangos deben ser continuos.")
            rangos.append(
                Rango(
                    disc=disc,
                    limite_inferior=inferior,
                    limite_superior=superior,
                    cuota_mxn=cuota,
                )
            )
            limite_anterior = superior
            if superior is None and disc != len(filas):
                raise ValueError("El rango sin límite superior debe ser el último.")
        return rangos

    @classmethod
    def _crear_tramos(cls, filas):
        if not filas:
            raise ValueError("Agrega al menos un tramo tarifario.")
        tramos = []
        dia_anterior = 0
        for disc, fila in enumerate(filas, start=1):
            try:
                dia_inicio = int(str(fila["dia_inicio"]).strip())
            except (TypeError, ValueError) as error:
                raise ValueError(f"El día inicial del tramo {disc} debe ser entero.") from error
            dia_fin_texto = str(fila["dia_fin"] or "").strip()
            try:
                dia_fin = int(dia_fin_texto) if dia_fin_texto else None
            except ValueError as error:
                raise ValueError(f"El día final del tramo {disc} debe ser entero.") from error
            es_consecutivo = (
                disc == 1 or dia_inicio == dia_anterior + 1
            )
            if (
                not es_consecutivo
                or dia_inicio <= dia_anterior
                or (dia_fin is not None and dia_fin < dia_inicio)
            ):
                raise ValueError("Los tramos deben tener días válidos, consecutivos y sin traslapes.")
            cuota = cls._decimal(
                fila["cuota_diaria_mxn"], f"La cuota diaria del tramo {disc}"
            )
            tramos.append(
                Tramo(
                    disc=disc,
                    dia_inicio=dia_inicio,
                    dia_fin=dia_fin,
                    cuota_diaria_mxn=cuota,
                )
            )
            dia_anterior = dia_fin if dia_fin is not None else dia_inicio
            if dia_fin is None and disc != len(filas):
                raise ValueError("El tramo abierto debe ser el último.")
        return tramos

    def construir_servicio(self, datos: dict) -> tuple[Servicio, list[int]]:
        nombre_es = str(datos.get("nombre_es") or "").strip()
        if not nombre_es:
            raise ValueError("El nombre en español es obligatorio.")
        tipo_cobro = str(datos.get("tipo_cobro") or "").strip()
        categoria_pda_id = self._id(
            datos.get("categoria_pda_id"), "una categoría PDA"
        )
        categoria_buque_id = self._id(
            datos.get("categoria_buque_id"),
            "una categoría de buque válida",
            opcional=True,
        )
        proveedor_ids = [
            self._id(value, "un proveedor autorizado")
            for value in datos.get("proveedor_ids", [])
        ]
        if not proveedor_ids:
            raise ValueError("Selecciona al menos un proveedor autorizado.")

        unidad_medida = str(datos.get("unidad_medida") or "").strip()
        if not unidad_medida:
            raise ValueError("La unidad de medida es obligatoria.")
        sku = str(datos.get("sku") or "").strip() or None
        if sku is not None and len(sku) > 50:
            raise ValueError("El SKU no puede tener más de 50 caracteres.")
        imagen_path = str(datos.get("imagen_path") or "").strip() or None
        if imagen_path is not None and len(imagen_path) > 1000:
            raise ValueError("La ruta de la imagen no puede superar 1000 caracteres.")
        tasa_iva = self._decimal(datos.get("tasa_iva"), "La tasa de IVA")
        if tasa_iva > Decimal("1"):
            raise ValueError("La tasa de IVA debe expresarse entre 0 y 1.")

        comunes = {
            "categoria_pda_id": categoria_pda_id,
            "nombre_es": nombre_es,
            "nombre_en": str(datos.get("nombre_en") or "").strip() or None,
            "sku": sku,
            "imagen_path": imagen_path,
            "unidad_medida": unidad_medida,
            "tasa_iva": tasa_iva,
            "activo": True,
            "caracter": CaracterServicio.OPCIONAL,
            "requiere_entrada_salida": False,
            "categoria_buque_id": categoria_buque_id,
            "regla_obligatoriedad": None,
        }

        if tipo_cobro == "CUOTA_FIJA":
            servicio = ServicioCuotaFija(
                **comunes,
                cuota=self._decimal(datos.get("cuota_fija"), "La cuota fija"),
            )
        elif tipo_cobro == "FACTOR_UNITARIO":
            comunes_factor = {
                **comunes,
                "variable_primaria": self._variable(
                    datos.get("variable_primaria"), "la variable primaria"
                ),
                "factor_mxn": self._decimal(
                    datos.get("factor_mxn"), "El factor en MXN"
                ),
                "unidades_minimas": self._decimal(
                    datos.get("unidades_minimas") or "0",
                    "Las unidades mínimas",
                ),
            }
            if datos.get("lineal_mixto"):
                servicio = ServicioLinealMixto(
                    **comunes_factor,
                    cuota_base=self._decimal(
                        datos.get("cuota_base"), "La cuota base"
                    ),
                )
            elif datos.get("factor_compuesto"):
                servicio = ServicioFactorCompuesto(
                    **comunes_factor,
                    variable_secundaria=self._variable(
                        datos.get("variable_secundaria"),
                        "la variable secundaria",
                    ),
                )
            else:
                servicio = ServicioFactorUnitario(**comunes_factor)
        elif tipo_cobro == "POR_RANGOS":
            servicio = ServicioRango(
                **comunes,
                variable_rangos=self._variable(
                    datos.get("variable_rangos"), "la variable de rangos"
                ),
                rangos=self._crear_rangos(datos.get("rangos") or []),
            )
        elif tipo_cobro == "INCREMENTAL":
            servicio = ServicioIncremental(
                **comunes,
                variable_cantidad=self._variable(
                    datos.get("variable_cantidad"), "la variable de cantidad"
                ),
                bloque_redondeo=self._decimal(
                    datos.get("bloque_redondeo") or "1",
                    "El bloque de redondeo",
                ),
                variable_dias=self._variable(
                    datos.get("variable_dias"), "la variable de días"
                ),
                tramos=self._crear_tramos(datos.get("tramos") or []),
            )
        else:
            tipos_validos = ", ".join(
                (
                    "CUOTA_FIJA",
                    "FACTOR_UNITARIO",
                    "POR_RANGOS",
                    "INCREMENTAL",
                )
            )
            raise ValueError(f"Selecciona un método de cobro válido: {tipos_validos}.")

        return servicio, proveedor_ids

    def registrar_servicio(self, datos: dict) -> Servicio:
        servicio, proveedor_ids = self.construir_servicio(datos)
        self.servicio.registrar_servicio(servicio, proveedor_ids=proveedor_ids)
        return servicio

    def modificar_servicio(self, servicio_id: int, datos: dict) -> Servicio:
        actual = self.servicio.buscar_por_id(servicio_id)
        if actual is None:
            raise ValueError("El servicio que intentas editar ya no existe.")
        tipo_cobro = str(datos.get("tipo_cobro") or "").strip()
        if tipo_cobro == "CUOTA_FIJA":
            clase_esperada = ServicioCuotaFija
        elif tipo_cobro == "FACTOR_UNITARIO":
            clase_esperada = (
                ServicioLinealMixto
                if datos.get("lineal_mixto")
                else (
                    ServicioFactorCompuesto
                    if datos.get("factor_compuesto")
                    else ServicioFactorUnitario
                )
            )
        elif tipo_cobro == "POR_RANGOS":
            clase_esperada = ServicioRango
        elif tipo_cobro == "INCREMENTAL":
            clase_esperada = ServicioIncremental
        else:
            raise ValueError("Selecciona un método de cobro válido.")
        if type(actual) is not clase_esperada:
            raise ValueError(
                "No se puede cambiar el método de cobro durante la edición."
            )
        servicio, proveedor_ids = self.construir_servicio(datos)
        servicio.id = actual.id
        self.servicio.modificar_servicio(servicio, proveedor_ids=proveedor_ids)
        return servicio

    @staticmethod
    def validar_imagen(nombre: str, tamano: int, ruta: str | None) -> str | None:
        extension = Path(nombre).suffix.lower()
        if extension not in {".jpg", ".jpeg", ".png"}:
            return "Selecciona una imagen JPG o PNG."
        if tamano > 2 * 1024 * 1024:
            return "La imagen debe pesar 2 MB o menos."
        if not ruta:
            return "No se pudo obtener la ruta local de la imagen seleccionada."
        if len(ruta) > 1000:
            return "La ruta de la imagen no puede superar 1000 caracteres."
        if not Path(ruta).is_file():
            return "El archivo de imagen ya no está disponible en esa ruta."
        return None

    def obtener_servicios(self, pagina=1, limite=10, filtros=None):
        return self.servicio.obtener_pagina(pagina, limite, filtros)

    def obtener_cantidad_registros(self):
        return self.servicio.obtener_cantidad_registros()

    def buscar_por_id(self, servicio_id: int) -> Servicio | None:
        return self.servicio.buscar_por_id(servicio_id)

    def eliminar_servicio(self, servicio_id: int):
        servicio = self.servicio.buscar_por_id(servicio_id)
        if servicio is None:
            raise ValueError("El servicio que intentas eliminar ya no existe.")
        self.servicio.eliminar_servicio(servicio)

    def actualizar_imagen(
        self,
        servicio_id: int,
        nombre: str,
        tamano: int,
        ruta: str | None,
    ) -> Servicio:
        error = self.validar_imagen(nombre, tamano, ruta)
        if error:
            raise ValueError(error)
        servicio = self.servicio.buscar_por_id(servicio_id)
        if servicio is None:
            raise ValueError("El servicio que intentas editar ya no existe.")
        servicio.imagen_path = ruta
        self.servicio.modificar_servicio(
            servicio,
            proveedor_ids=[proveedor.id for proveedor in servicio.proveedores],
        )
        return servicio
