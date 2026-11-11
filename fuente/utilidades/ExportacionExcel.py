from collections.abc import Callable, Iterable, Mapping
from datetime import date, datetime
from enum import Enum
from io import BytesIO
from typing import Any

import flet as ft
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, Reference

from fuente.utilidades.Colores import COLOR_BLANCO, COLOR_SIDEBAR
from fuente.utilidades.ExportacionArchivos import obtener_selector_archivos


ValorColumna = str | Callable[[Any], object]


def crear_excel(
    registros: Iterable[Any],
    columnas: Mapping[str, ValorColumna],
    nombre_hoja: str = "Datos",
) -> bytes:
    if not columnas:
        raise ValueError("Debe especificarse al menos una columna.")

    nombre_hoja = nombre_hoja or "Datos"
    for caracter in '\\/*?:[]':
        nombre_hoja = nombre_hoja.replace(caracter, "-")
    nombre_hoja = nombre_hoja[:31]

    libro = Workbook()
    hoja = libro.active
    hoja.title = nombre_hoja
    hoja.freeze_panes = "A2"

    encabezado = Font(bold=True, color=COLOR_BLANCO.lstrip("#"))
    fondo_encabezado = PatternFill(
        "solid",
        fgColor=COLOR_SIDEBAR.lstrip("#"),
    )
    for indice, titulo in enumerate(columnas, start=1):
        celda = hoja.cell(row=1, column=indice, value=titulo)
        celda.font = encabezado
        celda.fill = fondo_encabezado
        celda.alignment = Alignment(vertical="center")

    anchos = [len(str(titulo)) for titulo in columnas]
    for fila_indice, registro in enumerate(registros, start=2):
        for columna_indice, valor_columna in enumerate(columnas.values(), start=1):
            if callable(valor_columna):
                valor = valor_columna(registro)
            elif isinstance(registro, Mapping):
                valor = registro.get(valor_columna)
            else:
                valor = getattr(registro, valor_columna, None)

            if isinstance(valor, Enum):
                valor = valor.value
            if valor is None:
                valor = ""
            if isinstance(valor, datetime) and valor.utcoffset() is not None:
                valor = valor.replace(tzinfo=None)

            celda = hoja.cell(row=fila_indice, column=columna_indice)
            celda.value = valor
            if isinstance(valor, str):
                celda.data_type = "s"
            elif isinstance(valor, datetime):
                celda.number_format = "dd/mm/yyyy hh:mm"
            elif isinstance(valor, date):
                celda.number_format = "dd/mm/yyyy"
            celda.alignment = Alignment(vertical="top", wrap_text=True)
            anchos[columna_indice - 1] = max(
                anchos[columna_indice - 1],
                max((len(linea) for linea in str(valor).splitlines()), default=0),
            )

    for indice, ancho in enumerate(anchos, start=1):
        hoja.column_dimensions[get_column_letter(indice)].width = min(
            max(ancho + 2, 12),
            60,
        )

    hoja.auto_filter.ref = hoja.dimensions
    hoja.row_dimensions[1].height = 24

    archivo = BytesIO()
    libro.save(archivo)
    return archivo.getvalue()


def crear_excel_con_grafica(
    registros: Iterable[Any],
    columnas: Mapping[str, ValorColumna],
    nombre_hoja: str,
    grafica: Iterable[tuple[str, int | float]],
) -> bytes:
    contenido = crear_excel(registros, columnas, nombre_hoja)
    libro = load_workbook(BytesIO(contenido))
    hoja = libro.create_sheet("Gráfica")
    hoja.append(["Categoría", "Valor"])
    for categoria, valor in grafica:
        hoja.append([categoria, valor])

    if hoja.max_row > 1:
        chart = BarChart()
        chart.type = "bar"
        chart.style = 10
        chart.title = nombre_hoja
        chart.y_axis.title = "Categoría"
        chart.x_axis.title = "Valor"
        chart.height = 9
        chart.width = 18
        chart.add_data(
            Reference(hoja, min_col=2, min_row=1, max_row=hoja.max_row),
            titles_from_data=True,
        )
        chart.set_categories(
            Reference(hoja, min_col=1, min_row=2, max_row=hoja.max_row)
        )
        hoja.add_chart(chart, "D2")

    archivo = BytesIO()
    libro.save(archivo)
    return archivo.getvalue()


async def exportar_excel(
    page: ft.Page,
    registros: Iterable[Any],
    columnas: Mapping[str, ValorColumna],
    nombre_archivo: str,
    nombre_hoja: str = "Datos",
) -> bool:
    contenido = crear_excel(registros, columnas, nombre_hoja)
    if not nombre_archivo.lower().endswith(".xlsx"):
        nombre_archivo = f"{nombre_archivo}.xlsx"

    selector = obtener_selector_archivos(page)
    ruta = await selector.save_file(
        dialog_title="Exportar a Excel",
        file_name=nombre_archivo,
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["xlsx"],
        src_bytes=contenido,
    )

    return ruta is not None
