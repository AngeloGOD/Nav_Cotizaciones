import json
import os
from pathlib import Path
from uuid import uuid4


_CAMPOS_INFORME = (
    "nombre",
    "periodo",
    "generado",
    "formato",
    "color",
    "archivo",
    "extension",
    "archivo_datos",
)


def _directorio_historial():
    personalizado = os.environ.get("NAV_COTIZACIONES_REPORTS_DIR")
    if personalizado:
        return Path(personalizado)

    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "Nav_Cotizaciones" / "reportes"
    if os.name == "nt":
        return Path.home() / "AppData" / "Local" / "Nav_Cotizaciones" / "reportes"
    return Path.home() / ".local" / "share" / "nav_cotizaciones" / "reportes"


def cargar_historial_informes():
    directorio = _directorio_historial()
    manifiesto = directorio / "historial.json"
    if not manifiesto.exists():
        return []

    with manifiesto.open("r", encoding="utf-8") as archivo:
        registros = json.load(archivo)
    if not isinstance(registros, list):
        raise ValueError("El historial de reportes tiene un formato no válido.")

    informes = []
    for registro in registros:
        if not isinstance(registro, dict) or not all(
            campo in registro for campo in _CAMPOS_INFORME
        ):
            raise ValueError("Un registro del historial de reportes no es válido.")
        nombre_archivo_datos = registro["archivo_datos"]
        if (
            not isinstance(nombre_archivo_datos, str)
            or Path(nombre_archivo_datos).name != nombre_archivo_datos
        ):
            raise ValueError("La ruta de un archivo del historial no es válida.")
        if (directorio / nombre_archivo_datos).is_file():
            informes.append(dict(registro))
    return informes


def guardar_informe_generado(informe, contenido):
    directorio = _directorio_historial()
    directorio.mkdir(parents=True, exist_ok=True)
    archivo_datos = f"reporte_{uuid4().hex}.{informe['extension']}"
    (directorio / archivo_datos).write_bytes(contenido)

    informe_persistente = {
        campo: informe[campo]
        for campo in _CAMPOS_INFORME
        if campo in informe
    }
    informe_persistente["archivo_datos"] = archivo_datos
    historial = cargar_historial_informes()
    historial.insert(0, informe_persistente)

    manifiesto = directorio / "historial.json"
    temporal = directorio / f"historial_{uuid4().hex}.tmp"
    try:
        with temporal.open("w", encoding="utf-8") as archivo:
            json.dump(historial, archivo, ensure_ascii=False, indent=2)
        os.replace(temporal, manifiesto)
    finally:
        if temporal.exists():
            temporal.unlink()
    return informe_persistente


def leer_contenido_informe(informe):
    if "contenido" in informe:
        return informe["contenido"]

    nombre_archivo_datos = informe.get("archivo_datos")
    if (
        not isinstance(nombre_archivo_datos, str)
        or Path(nombre_archivo_datos).name != nombre_archivo_datos
    ):
        raise ValueError("La ruta del archivo del informe no es válida.")

    ruta = _directorio_historial() / nombre_archivo_datos
    try:
        return ruta.read_bytes()
    except OSError as error:
        raise OSError(
            f"No se encontró el archivo guardado del reporte '{informe['archivo']}'."
        ) from error
