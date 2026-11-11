from collections.abc import Callable, Iterable, Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from html import escape, unescape
from io import BytesIO
from pathlib import Path
from typing import Any

import flet as ft
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4, landscape, legal
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    LongTable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from fuente.utilidades.Colores import (
    COLOR_AZUL,
    COLOR_AZUL_INTENSO,
    COLOR_BLANCO,
    COLOR_GRIS,
    COLOR_NARANJA,
    COLOR_ROJO,
    COLOR_SIDEBAR,
    COLOR_VERDE,
)
from fuente.utilidades.ExportacionArchivos import obtener_selector_archivos


ValorColumna = str | Callable[[Any], object]
COLOR_AZUL_MARINO = colors.HexColor(COLOR_SIDEBAR)
TAMANO_PAGINA_REGISTROS = 10
LOGO_OPL = (
    Path(__file__).resolve().parents[2]
    / "assets"
    / "logoOPL_parareportes.png"
)


def _aclarar_color(color_hex, proporcion_blanco=0.82):
    color = colors.HexColor(color_hex)
    return colors.Color(
        color.red * (1 - proporcion_blanco) + proporcion_blanco,
        color.green * (1 - proporcion_blanco) + proporcion_blanco,
        color.blue * (1 - proporcion_blanco) + proporcion_blanco,
    )


class _CanvasNumerado(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._estados_pagina = []

    def showPage(self):
        self._estados_pagina.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_paginas = len(self._estados_pagina)
        for estado in self._estados_pagina:
            self.__dict__.update(estado)
            self.setFont("Helvetica-Bold", 8.5)
            self.setFillColor(COLOR_BLANCO)
            self.drawRightString(
                self._pagesize[0] - 20 * mm,
                6 * mm,
                f"Página {self._pageNumber} de {total_paginas}",
            )
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


def _texto(valor: object) -> str:
    if valor is None:
        return "—"
    if isinstance(valor, Enum):
        valor = valor.value
    if isinstance(valor, datetime):
        if valor.utcoffset() is not None:
            valor = valor.replace(tzinfo=None)
        texto = valor.strftime("%d/%m/%Y %H:%M")
    elif isinstance(valor, date):
        texto = valor.strftime("%d/%m/%Y")
    else:
        texto = str(valor)
    return escape(texto).replace("\n", "<br/>")


def _obtener_valor(registro: Any, valor_columna: ValorColumna) -> object:
    if callable(valor_columna):
        return valor_columna(registro)
    if isinstance(registro, Mapping):
        return registro.get(valor_columna)
    return getattr(registro, valor_columna, None)


class _TarjetaMetrica(Flowable):
    def __init__(self, ancho, valor, etiqueta, color, color_acento, icono):
        super().__init__()
        self.width = ancho
        self.height = 43
        self.valor = str(valor)
        self.etiqueta = etiqueta
        self.color = color
        self.color_acento = color_acento
        self.icono = icono

    def draw(self):
        lienzo = self.canv
        lienzo.setFillColor(self.color)
        lienzo.setStrokeColor(_aclarar_color(self.color_acento, 0.62))
        lienzo.setLineWidth(1.5)
        lienzo.roundRect(0, 0, self.width, self.height, 6, fill=1, stroke=1)

        ancho_texto = max(
            stringWidth(self.etiqueta, "Helvetica", 8),
            stringWidth(self.valor, "Helvetica-Bold", 13),
        )
        ancho_contenido = 28 + 10 + ancho_texto
        icono_x = max(10, (self.width - ancho_contenido) / 2)
        icono_y = (self.height - 28) / 2
        lienzo.setFillColor(self.color_acento)
        lienzo.roundRect(icono_x, icono_y, 28, 28, 5, fill=1, stroke=0)
        centro_x = icono_x + 14
        centro_y = icono_y + 14
        lienzo.setStrokeColor(self.color_acento)
        lienzo.setFillColor(COLOR_BLANCO)
        lienzo.setLineWidth(1.8)
        if self.icono == ft.Icons.GROUPS:
            lienzo.circle(centro_x, centro_y + 5, 2.6, fill=1, stroke=0)
            lienzo.circle(centro_x - 6.5, centro_y + 3.5, 2.1, fill=1, stroke=0)
            lienzo.circle(centro_x + 6.5, centro_y + 3.5, 2.1, fill=1, stroke=0)
            cuerpo_central = lienzo.beginPath()
            cuerpo_central.moveTo(centro_x - 6, centro_y - 6)
            cuerpo_central.lineTo(centro_x - 6, centro_y - 3)
            cuerpo_central.curveTo(
                centro_x - 6, centro_y + 1, centro_x + 6, centro_y + 1,
                centro_x + 6, centro_y - 3,
            )
            cuerpo_central.lineTo(centro_x + 6, centro_y - 6)
            cuerpo_central.close()
            lienzo.drawPath(cuerpo_central, fill=1, stroke=0)
            for lado in (-1, 1):
                cuerpo_lateral = lienzo.beginPath()
                cuerpo_lateral.moveTo(centro_x + lado * 5, centro_y - 5)
                cuerpo_lateral.curveTo(
                    centro_x + lado * 7, centro_y - 1,
                    centro_x + lado * 11, centro_y - 1,
                    centro_x + lado * 12, centro_y - 5,
                )
                cuerpo_lateral.lineTo(centro_x + lado * 11, centro_y - 6)
                cuerpo_lateral.close()
                lienzo.drawPath(cuerpo_lateral, fill=1, stroke=0)
        elif self.icono == "activo":
            lienzo.circle(centro_x, centro_y, 9, fill=1, stroke=0)
            lienzo.setStrokeColor(self.color_acento)
            lienzo.setFillColor(self.color_acento)
            lienzo.setLineWidth(2.2)
            ruta = lienzo.beginPath()
            ruta.moveTo(centro_x - 4.5, centro_y)
            ruta.lineTo(centro_x - 1, centro_y - 3.5)
            ruta.lineTo(centro_x + 5, centro_y + 4)
            lienzo.drawPath(ruta, stroke=1, fill=0)
        else:
            lienzo.circle(centro_x, centro_y, 9, fill=1, stroke=0)
            lienzo.setStrokeColor(self.color_acento)
            lienzo.setFillColor(self.color_acento)
            lienzo.setLineWidth(2.2)
            lienzo.line(centro_x - 4, centro_y - 4, centro_x + 4, centro_y + 4)
            lienzo.line(centro_x - 4, centro_y + 4, centro_x + 4, centro_y - 4)

        x_texto = icono_x + 38
        centro_y_texto = self.height / 2
        lienzo.setFillColor(COLOR_GRIS)
        lienzo.setFont("Helvetica", 8)
        lienzo.drawString(x_texto, centro_y_texto + 3, self.etiqueta)
        lienzo.setFillColor(COLOR_SIDEBAR)
        lienzo.setFont("Helvetica-Bold", 13)
        lienzo.drawString(x_texto, centro_y_texto - 11, self.valor)


def _texto_celda(
    valor: object,
    ancho: float,
    font_size: float,
    envolver: bool = False,
) -> str:
    texto_celda = _texto(valor)
    if envolver:
        return texto_celda

    texto = unescape(texto_celda.replace("<br/>", " "))
    ancho_util = max(ancho - 8, font_size * 3)
    if stringWidth(texto, "Helvetica", font_size) > ancho_util:
        while texto and stringWidth(f"{texto}…", "Helvetica", font_size) > ancho_util:
            limite = texto.rfind(" ")
            if limite > len(texto) // 2:
                texto = texto[:limite].rstrip(" ,;:-")
            else:
                texto = texto[:-1].rstrip()
        texto += "…"
    return escape(texto).replace("\n", "<br/>")


def _ajustar_linea_contacto(
    texto: str,
    ancho: float,
    font_name: str,
    font_size: float,
) -> list[str]:
    if stringWidth(texto, font_name, font_size) <= ancho:
        return [texto]

    palabras = texto.split()
    if "@" in texto:
        local, dominio = texto.rsplit("@", 1)
        palabras = [f"{local}@", dominio]

    lineas = []
    linea = ""
    for palabra in palabras:
        candidata = f"{linea} {palabra}".strip()
        if linea and stringWidth(candidata, font_name, font_size) > ancho:
            lineas.append(linea)
            linea = palabra
        else:
            linea = candidata
    if linea:
        lineas.append(linea)

    return lineas


def _dibujar_ondas(pagina: canvas.Canvas, ancho: float):
    ruta_azul = pagina.beginPath()
    ruta_azul.moveTo(0, 0)
    ruta_azul.lineTo(ancho, 0)
    ruta_azul.lineTo(ancho, 12 * mm)
    ruta_azul.curveTo(
        ancho * 0.78,
        19 * mm,
        ancho * 0.53,
        5 * mm,
        ancho * 0.29,
        10 * mm,
    )
    ruta_azul.curveTo(ancho * 0.16, 13 * mm, ancho * 0.08, 7 * mm, 0, 9 * mm)
    ruta_azul.close()
    pagina.setFillColor(COLOR_AZUL_MARINO)
    pagina.drawPath(ruta_azul, fill=1, stroke=0)

    ruta_naranja = pagina.beginPath()
    ruta_naranja.moveTo(0, 9 * mm)
    ruta_naranja.curveTo(
        ancho * 0.18,
        13 * mm,
        ancho * 0.34,
        7 * mm,
        ancho * 0.52,
        9 * mm,
    )
    ruta_naranja.curveTo(
        ancho * 0.72,
        11 * mm,
        ancho * 0.83,
        17 * mm,
        ancho,
        14 * mm,
    )
    ruta_naranja.lineTo(ancho, 12 * mm)
    ruta_naranja.curveTo(
        ancho * 0.81,
        15 * mm,
        ancho * 0.70,
        9 * mm,
        ancho * 0.52,
        7 * mm,
    )
    ruta_naranja.curveTo(
        ancho * 0.33,
        5 * mm,
        ancho * 0.15,
        11 * mm,
        0,
        7 * mm,
    )
    ruta_naranja.close()
    pagina.setFillColor(COLOR_NARANJA)
    pagina.drawPath(ruta_naranja, fill=1, stroke=0)


def _dibujar_encabezado(
    pagina: canvas.Canvas,
    documento,
    titulo: str,
    subtitulo: str,
    etiqueta_registros: str,
    logo_path: str | Path | None,
):
    ancho, alto = documento.pagesize
    margen = 20 * mm
    ruta_logo = Path(logo_path) if logo_path else LOGO_OPL

    if not ruta_logo.is_file():
        raise FileNotFoundError(f"No se encontró el logo para el PDF: {ruta_logo}")
    alto_encabezado = 33 * mm
    pagina.setFillColor(COLOR_AZUL_MARINO)
    pagina.rect(0, alto - alto_encabezado, ancho, alto_encabezado, fill=1, stroke=0)
    pagina.drawImage(
        str(ruta_logo),
        5 * mm,
        alto - 31 * mm,
        width=45 * mm,
        height=30 * mm,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )

    x_texto = 53 * mm
    pagina.setFillColor(COLOR_BLANCO)
    tamano_titulo = min(
        16,
        max(
            12,
            16
            * (ancho - margen - x_texto)
            / max(stringWidth(titulo.upper(), "Helvetica-Bold", 16), 1),
        ),
    )
    pagina.setFont("Helvetica-Bold", tamano_titulo)
    pagina.drawString(x_texto, alto - 12 * mm, titulo.upper())
    pagina.setFont("Helvetica", 9.5)
    pagina.drawString(x_texto, alto - 19 * mm, subtitulo)

    pagina.setFont("Helvetica", 8.5)
    pagina.setFillColor(COLOR_BLANCO)
    pagina.drawString(
        x_texto,
        alto - 28 * mm,
        f"Fecha de exportación: {datetime.now().strftime('%d/%m/%Y')}",
    )
    ancho_etiqueta = stringWidth(etiqueta_registros, "Helvetica-Bold", 8.5)
    x_etiqueta = max(
        x_texto + 66 * mm,
        ancho - margen - ancho_etiqueta,
    )
    pagina.setFont("Helvetica-Bold", 8.5)
    pagina.setFillColor(COLOR_BLANCO)
    pagina.drawString(x_etiqueta, alto - 28 * mm, etiqueta_registros)

    y_linea = alto - alto_encabezado
    pagina.setFillColor(COLOR_NARANJA)
    pagina.rect(0, y_linea - 1.2 * mm, ancho, 1.2 * mm, fill=1, stroke=0)


def _dibujar_pie(
    pagina: canvas.Canvas,
    documento,
    total_registros: int,
    nombre_registro: str,
):
    ancho, _ = documento.pagesize
    margen = 20 * mm
    _dibujar_ondas(pagina, ancho)

    ancho_columna = (ancho - 2 * margen) / 3
    pagina.setStrokeColor(_aclarar_color(COLOR_AZUL, 0.72))
    pagina.setLineWidth(0.6)
    pagina.line(margen, 53 * mm, ancho - margen, 53 * mm)

    columnas = (
        (
            "Contacto",
            (
                "Calle Parque Industrial MZ F,",
                "Lote 34, Puerto Chiapas,",
                "Chiapas, México.",
            ),
        ),
        (
            "Teléfonos",
            ("+52 (962) 181 0755", "+52 (962) 153 8654"),
        ),
        (
            "Correo",
            (
                "alexis.castro@olpacifico.com",
                "francisco.aguilar@olpacifico.com",
            ),
        ),
    )
    for indice, (titulo, lineas) in enumerate(columnas):
        x = margen + indice * ancho_columna + 6 * mm
        y_icono = 44.5 * mm
        texto_x = x + 9 * mm
        ancho_texto = margen + (indice + 1) * ancho_columna - texto_x
        pagina.setFillColor(COLOR_NARANJA)
        pagina.setStrokeColor(COLOR_NARANJA)
        pagina.setLineWidth(1.8)
        if indice == 0:
            pagina.circle(x + 2.5 * mm, y_icono + 1.5 * mm, 1.8 * mm, fill=0, stroke=1)
            ruta = pagina.beginPath()
            ruta.moveTo(x + 0.9 * mm, y_icono)
            ruta.lineTo(x + 2.5 * mm, y_icono - 2.5 * mm)
            ruta.lineTo(x + 4.1 * mm, y_icono)
            pagina.drawPath(ruta, fill=0, stroke=1)
        elif indice == 1:
            pagina.roundRect(
                x,
                y_icono - 2 * mm,
                5 * mm,
                6 * mm,
                1.2 * mm,
                fill=0,
                stroke=1,
            )
            pagina.line(
                x + 1.2 * mm,
                y_icono + 1.5 * mm,
                x + 3.8 * mm,
                y_icono + 1.5 * mm,
            )
        else:
            pagina.roundRect(
                x,
                y_icono - 1.5 * mm,
                6 * mm,
                4.5 * mm,
                0.8 * mm,
                fill=0,
                stroke=1,
            )
            pagina.line(x, y_icono + 3 * mm, x + 3 * mm, y_icono + 0.8 * mm)
            pagina.line(x + 6 * mm, y_icono + 3 * mm, x + 3 * mm, y_icono + 0.8 * mm)

        pagina.setFillColor(COLOR_NARANJA)
        pagina.setFont("Helvetica-Bold", 15)
        pagina.drawString(texto_x, y_icono + 2 * mm, titulo)
        pagina.setFillColor(COLOR_SIDEBAR)
        pagina.setFont("Helvetica", 13)
        lineas_ajustadas = [
            linea_ajustada
            for linea in lineas
            for linea_ajustada in _ajustar_linea_contacto(
                linea,
                ancho_texto,
                "Helvetica",
                13,
            )
        ]
        for numero, linea in enumerate(lineas_ajustadas):
            pagina.drawString(
                texto_x,
                y_icono - 4 * mm - numero * 4.3 * mm,
                linea,
            )

        if indice < len(columnas) - 1:
            x_divisor = margen + (indice + 1) * ancho_columna
            pagina.setStrokeColor(_aclarar_color(COLOR_AZUL, 0.72))
            pagina.line(x_divisor, 31 * mm, x_divisor, 49 * mm)

    pagina.setFillColor(COLOR_BLANCO)
    pagina.setFont("Helvetica-Bold", 8.5)
    numero_pagina = pagina.getPageNumber()
    inicio = (numero_pagina - 1) * TAMANO_PAGINA_REGISTROS + 1
    fin = min(numero_pagina * TAMANO_PAGINA_REGISTROS, total_registros)
    texto_registros = (
        f"Mostrando {inicio}–{fin} de {total_registros} {nombre_registro}"
        if total_registros
        else f"Mostrando 0 de 0 {nombre_registro}"
    )
    pagina.drawString(margen, 6 * mm, texto_registros)


def crear_pdf(
    registros: Iterable[Any],
    columnas: Mapping[str, ValorColumna],
    titulo: str,
    subtitulo: str = "",
    etiqueta_registros: str | None = None,
    metricas: Mapping[str, object] | None = None,
    logo_path: str | Path | None = None,
    orientacion: str = "portrait",
    proporciones_columnas: Sequence[float] | None = None,
    columnas_centradas: Iterable[str] = (),
    nombre_registro: str = "registros",
    envolver_texto_celdas: bool = True,
) -> bytes:
    if not columnas:
        raise ValueError("Debe especificarse al menos una columna.")

    filas = list(registros)
    etiqueta = etiqueta_registros or f"Registros: {len(filas)}"
    orientacion = orientacion.lower()
    if orientacion not in {"portrait", "landscape"}:
        raise ValueError("La orientación debe ser 'portrait' o 'landscape'.")
    paginas = landscape(A4) if orientacion == "landscape" else A4
    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida,
        pagesize=paginas,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=42 * mm,
        bottomMargin=55 * mm,
        title=titulo,
        author="OPL Pacífico Sur",
    )

    estilo_encabezado = ParagraphStyle(
        "EncabezadoPDF",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=9.5,
        textColor=COLOR_BLANCO,
        alignment=TA_CENTER,
    )
    estilo_celda = ParagraphStyle(
        "CeldaPDF",
        fontName="Helvetica",
        fontSize=7.8,
        leading=9.2,
        textColor=COLOR_SIDEBAR,
        alignment=TA_LEFT,
        splitLongWords=True,
    )
    estilo_celda_centrada = ParagraphStyle(
        "CeldaPDFCentrada",
        parent=estilo_celda,
        alignment=TA_CENTER,
    )
    estilos_estado = {
        "activo": ParagraphStyle(
            "EstadoActivoPDF",
            parent=estilo_celda_centrada,
            textColor=COLOR_VERDE,
            backColor=_aclarar_color(COLOR_VERDE, 0.88),
            borderColor=_aclarar_color(COLOR_VERDE, 0.25),
            borderWidth=0.7,
            borderPadding=(1.5, 3, 1.5, 3),
        ),
        "inactivo": ParagraphStyle(
            "EstadoInactivoPDF",
            parent=estilo_celda_centrada,
            textColor=COLOR_ROJO,
            backColor=_aclarar_color(COLOR_ROJO, 0.88),
            borderColor=_aclarar_color(COLOR_ROJO, 0.25),
            borderWidth=0.7,
            borderPadding=(1.5, 3, 1.5, 3),
        ),
    }
    columnas_centradas = set(columnas_centradas)
    ancho_tabla = documento.width
    if proporciones_columnas is None:
        anchos = [ancho_tabla / len(columnas)] * len(columnas)
    else:
        if (
            len(proporciones_columnas) != len(columnas)
            or any(proporcion <= 0 for proporcion in proporciones_columnas)
        ):
            raise ValueError(
                "Debe indicarse una proporción positiva por cada columna."
            )
        total_proporciones = sum(proporciones_columnas)
        anchos = [
            ancho_tabla * proporcion / total_proporciones
            for proporcion in proporciones_columnas
        ]

    historia = []
    metricas_lista = list((metricas or {}).items())
    if metricas_lista:
        celdas_metricas = []
        iconos_metricas = ("total", "activo", "inactivo")
        for indice, (nombre, valor) in enumerate(metricas_lista):
            celdas_metricas.append(
                _TarjetaMetrica(
                    (ancho_tabla / len(metricas_lista)) - 4,
                    valor,
                    nombre,
                    (
                        _aclarar_color(COLOR_AZUL)
                        if indice == 0
                        else _aclarar_color(COLOR_VERDE)
                        if indice == 1
                        else _aclarar_color(COLOR_ROJO)
                        if indice == 2
                        else _aclarar_color(COLOR_AZUL)
                    ),
                    (
                        COLOR_AZUL_INTENSO
                        if indice == 0
                        else COLOR_VERDE
                        if indice == 1
                        else COLOR_ROJO
                        if indice == 2
                        else COLOR_AZUL_INTENSO
                    ),
                    (
                        ft.Icons.GROUPS
                        if indice == 0
                        else iconos_metricas[min(indice, len(iconos_metricas) - 1)]
                    ),
                )
            )
        tabla_metricas = Table(
            [celdas_metricas],
            colWidths=[ancho_tabla / len(celdas_metricas)] * len(celdas_metricas),
            hAlign="LEFT",
        )
        tabla_metricas.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 0),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        historia.extend([tabla_metricas, Spacer(1, 4 * mm)])

    grupos_filas = [
        filas[inicio:inicio + TAMANO_PAGINA_REGISTROS]
        for inicio in range(0, len(filas), TAMANO_PAGINA_REGISTROS)
    ] or [[]]
    for indice_grupo, grupo_filas in enumerate(grupos_filas):
        if indice_grupo:
            historia.append(PageBreak())
        tabla_datos = [
            [
                Paragraph(_texto(titulo_columna), estilo_encabezado)
                for titulo_columna in columnas
            ]
        ]
        for registro in grupo_filas:
            celdas = []
            for indice_columna, (titulo_columna, valor_columna) in enumerate(
                columnas.items()
            ):
                valor = _obtener_valor(registro, valor_columna)
                estilo = (
                    estilo_celda_centrada
                    if titulo_columna in columnas_centradas
                    else estilo_celda
                )
                if titulo_columna == "Estado":
                    texto_estado = str(getattr(valor, "value", valor)).strip().casefold()
                    if texto_estado in estilos_estado:
                        estilo = estilos_estado[texto_estado]
                celdas.append(
                    Paragraph(
                        _texto_celda(
                            valor,
                            anchos[indice_columna],
                            estilo_celda.fontSize,
                            envolver=envolver_texto_celdas,
                        ),
                        estilo,
                    )
                )
            tabla_datos.append(celdas)

        if not grupo_filas:
            tabla_datos.append(
                [Paragraph("No hay registros para mostrar.", estilo_celda)]
                + ["" for _ in range(len(columnas) - 1)]
            )

        tabla_registros = LongTable(
            tabla_datos,
            colWidths=anchos,
            repeatRows=1,
            hAlign="LEFT",
            splitByRow=1,
        )
        tabla_registros.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_AZUL_MARINO),
                    ("TEXTCOLOR", (0, 0), (-1, 0), COLOR_BLANCO),
                    (
                        "ROWBACKGROUNDS",
                        (0, 1),
                        (-1, -1),
                        [COLOR_BLANCO, _aclarar_color(COLOR_AZUL, 0.94)],
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.5,
                        _aclarar_color(COLOR_AZUL, 0.72),
                    ),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )
        historia.append(tabla_registros)

    def dibujar_pagina(pagina, doc):
        _dibujar_encabezado(
            pagina,
            doc,
            titulo,
            subtitulo,
            etiqueta,
            logo_path,
        )
        _dibujar_pie(pagina, doc, len(filas), nombre_registro)

    documento.build(
        historia,
        onFirstPage=dibujar_pagina,
        onLaterPages=dibujar_pagina,
        canvasmaker=_CanvasNumerado,
    )
    return salida.getvalue()


async def exportar_pdf(
    page: ft.Page,
    registros: Iterable[Any],
    columnas: Mapping[str, ValorColumna],
    nombre_archivo: str,
    **opciones_pdf,
) -> bool:
    contenido = crear_pdf(registros, columnas, **opciones_pdf)
    if not nombre_archivo.lower().endswith(".pdf"):
        nombre_archivo = f"{nombre_archivo}.pdf"

    selector = obtener_selector_archivos(page)
    ruta = await selector.save_file(
        dialog_title="Exportar a PDF",
        file_name=nombre_archivo,
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["pdf"],
        src_bytes=contenido,
    )
    return ruta is not None


def crear_pdf_proforma(cotizacion: Any) -> bytes:
    if cotizacion is None:
        raise ValueError("La proforma no puede ser nula.")

    logo_proforma = (
        Path(__file__).resolve().parents[2] / "assets" / "logo_opl.png"
    )
    if not logo_proforma.is_file():
        raise FileNotFoundError(
            f"No se encontró el logo para la proforma: {logo_proforma}"
        )

    salida = BytesIO()
    documento = SimpleDocTemplate(
        salida,
        pagesize=legal,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        topMargin=8 * mm,
        bottomMargin=8 * mm,
        title=f"Proforma {getattr(cotizacion, 'folio', '')}",
        author="OPL Pacífico Sur",
    )
    ancho = documento.width
    estilo_seccion = ParagraphStyle(
        "SeccionProforma",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        textColor=COLOR_BLANCO,
    )
    estilo_celda = ParagraphStyle(
        "CeldaProforma",
        fontName="Helvetica",
        fontSize=7,
        leading=8.5,
        textColor=COLOR_SIDEBAR,
        splitLongWords=True,
    )
    estilo_celda_negrita = ParagraphStyle(
        "CeldaProformaNegrita",
        parent=estilo_celda,
        fontName="Helvetica-Bold",
    )
    estilo_celda_centrada = ParagraphStyle(
        "CeldaProformaCentrada",
        parent=estilo_celda,
        alignment=TA_CENTER,
    )
    estilo_encabezado_tabla = ParagraphStyle(
        "EncabezadoTablaProforma",
        fontName="Helvetica-Bold",
        fontSize=5.8,
        leading=7,
        textColor=COLOR_BLANCO,
        alignment=TA_CENTER,
    )
    estilo_adicional_titulo = ParagraphStyle(
        "TituloAdicionalProforma",
        fontName="Helvetica-Bold",
        fontSize=6.7,
        leading=8,
        textColor=COLOR_NARANJA,
        spaceBefore=1.5 * mm,
        spaceAfter=0.5 * mm,
    )
    estilo_adicional_texto = ParagraphStyle(
        "TextoAdicionalProforma",
        fontName="Helvetica",
        fontSize=6.2,
        leading=7.3,
        textColor=COLOR_SIDEBAR,
        spaceAfter=0.5 * mm,
    )

    def parrafo(valor: object, estilo=estilo_celda) -> Paragraph:
        return Paragraph(_texto(valor), estilo)

    def fecha_proforma(valor: object) -> str:
        if isinstance(valor, (date, datetime)):
            return valor.strftime("%d/%m/%Y")
        return _texto(valor)

    def seccion(texto: str) -> Table:
        tabla_seccion = Table(
            [[Paragraph(_texto(texto), estilo_seccion)]],
            colWidths=[ancho],
        )
        tabla_seccion.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), COLOR_AZUL_MARINO),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return tabla_seccion

    def tabla_informacion_compacta(
        filas: list[list[tuple[str, object]]],
        anchos_columna: list[float],
    ) -> Table:
        datos = []
        for fila in filas:
            celdas = []
            for etiqueta, valor in fila:
                celdas.extend(
                    [
                        parrafo(etiqueta, estilo_celda_negrita),
                        parrafo(valor),
                    ]
                )
            while len(celdas) < len(anchos_columna):
                celdas.extend([parrafo(""), parrafo("")])
            datos.append(celdas)
        tabla_info = Table(datos, colWidths=anchos_columna, hAlign="LEFT")
        tabla_info.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.4, _aclarar_color(COLOR_AZUL, 0.7)),
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, -1),
                        _aclarar_color(COLOR_AZUL, 0.96),
                    ),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 3),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 3),
                    ("TOPPADDING", (0, 0), (-1, -1), 1.5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
                ]
            )
        )
        return tabla_info

    class EncabezadoProforma(Flowable):
        def __init__(self):
            super().__init__()
            self.width = ancho
            self.height = 27 * mm

        def draw(self):
            lienzo = self.canv
            alto = self.height
            ancho_logo = 49 * mm
            lienzo.setFillColor(COLOR_AZUL_MARINO)
            lienzo.roundRect(0, 0, ancho_logo, alto, 2 * mm, fill=1, stroke=0)
            lienzo.drawImage(
                ImageReader(str(logo_proforma)),
                1.5 * mm,
                1.5 * mm,
                width=ancho_logo - 3 * mm,
                height=alto - 3 * mm,
                preserveAspectRatio=True,
                anchor="c",
                mask="auto",
            )

            x_titulo = 54 * mm
            lienzo.setFillColor(COLOR_SIDEBAR)
            lienzo.setFont("Helvetica-Bold", 14)
            lienzo.drawString(x_titulo, alto - 8 * mm, "PORT DISBURSEMENT")
            lienzo.drawString(x_titulo, alto - 15 * mm, "ACCOUNT (PDA)")
            lienzo.setFillColor(COLOR_GRIS)
            lienzo.setFont("Helvetica", 7)
            lienzo.drawString(x_titulo, 3 * mm, "Proforma de Gastos Portuarios")

            x_datos = ancho - 43 * mm
            lienzo.setFillColor(COLOR_SIDEBAR)
            lienzo.setFont("Helvetica-Bold", 6.5)
            lienzo.drawString(x_datos, alto - 5 * mm, "Folio / Reference")
            lienzo.setFillColor(COLOR_NARANJA)
            lienzo.setFont("Helvetica-Bold", 11)
            lienzo.drawString(
                x_datos,
                alto - 11 * mm,
                str(getattr(cotizacion, "folio", "") or ""),
            )
            lienzo.setFillColor(COLOR_SIDEBAR)
            lienzo.setFont("Helvetica-Bold", 6.5)
            lienzo.drawString(x_datos, alto - 17 * mm, "Fecha / Date")
            lienzo.setFont("Helvetica", 7)
            lienzo.drawString(
                x_datos,
                alto - 23 * mm,
                fecha_proforma(fecha),
            )

    cliente = getattr(cotizacion, "cliente", None)
    buque = getattr(cotizacion, "buque", None)
    categoria_buque = getattr(buque, "categoria_buque", None)
    moneda = _texto(getattr(cotizacion, "moneda", "MXN"))
    fecha = getattr(cotizacion, "creado_en", None) or getattr(
        cotizacion, "fecha_arribo", None
    )
    encabezado = EncabezadoProforma()

    datos_cliente = tabla_informacion_compacta(
        [
            [
                ("Cliente / Customer", getattr(cliente, "razon_social", "—")),
                ("Fecha / Date", fecha_proforma(fecha)),
            ],
            [
                ("Dirección / Address", getattr(cliente, "direccion", "—")),
                (
                    "Arribo / ETA",
                    fecha_proforma(getattr(cotizacion, "fecha_arribo", None)),
                ),
            ],
            [
                (
                    "Zarpe / ETD",
                    fecha_proforma(getattr(cotizacion, "fecha_zarpe", None)),
                ),
                ("", ""),
            ],
        ],
        [25 * mm, 67 * mm, 22 * mm, ancho - 114 * mm],
    )
    tipo_buque = getattr(categoria_buque, "categoria", "—")
    subtipo = getattr(buque, "subtipo_descripcion", None)
    if subtipo:
        tipo_buque = f"{tipo_buque} · {subtipo}"
    datos_buque = tabla_informacion_compacta(
        [
            [
                ("Buque / Vessel", getattr(buque, "nombre", "—")),
                ("IMO", getattr(buque, "numero_imo", "—")),
                ("Tipo / Type", tipo_buque),
            ],
            [
                ("UAB / GRT", getattr(buque, "trb", "—")),
                ("Eslora / LOA (m)", getattr(buque, "eslora", "—")),
                ("Calado / Draft (m)", getattr(buque, "calado", "—")),
            ],
        ],
        [23 * mm, 44 * mm, 12 * mm, 24 * mm, 22 * mm, ancho - 125 * mm],
    )

    titulos_detalle = (
        "#",
        "Categoría / Category",
        "Descripción / Description",
        "Proveedor / Supplier",
        "Subtotal",
        "IVA / TAX",
        "Total",
        "Factura / Invoice",
        "Observaciones / Observations",
    )
    anchos_columnas = [
        ancho * proporcion
        for proporcion in (0.035, 0.105, 0.19, 0.16, 0.105, 0.075, 0.105, 0.09, 0.135)
    ]
    filas_detalle = [
        [Paragraph(_texto(titulo), estilo_encabezado_tabla) for titulo in titulos_detalle]
    ]
    for indice, detalle in enumerate(
        getattr(cotizacion, "detalles", None) or [], start=1
    ):
        concepto = getattr(detalle, "concepto", None)
        categoria = getattr(
            getattr(concepto, "categoria_pda", None), "nombre", "—"
        )
        proveedores = getattr(concepto, "proveedores", None) or []
        proveedor = ", ".join(
            p.nombre for p in proveedores if getattr(p, "nombre", None)
        ) or "—"
        descripcion = getattr(concepto, "nombre_es", None) or (
            f"Concepto #{getattr(detalle, 'concepto_id', '')}"
        )
        subtotal = Decimal(str(getattr(detalle, "subtotal", 0) or 0))
        iva = Decimal(str(getattr(detalle, "iva", 0) or 0))
        total = subtotal + iva
        filas_detalle.append(
            [
                parrafo(indice, estilo_celda_centrada),
                parrafo(categoria),
                parrafo(descripcion),
                parrafo(proveedor),
                parrafo(f"$ {subtotal:,.2f} {moneda}", estilo_celda_centrada),
                parrafo(
                    f"$ {iva:,.2f} {moneda}" if iva else "—",
                    estilo_celda_centrada,
                ),
                parrafo(f"$ {total:,.2f} {moneda}", estilo_celda_centrada),
                parrafo(getattr(detalle, "factura", None) or "—"),
                parrafo(getattr(detalle, "observaciones", None) or "—"),
            ]
        )

    tabla_detalles = LongTable(
        filas_detalle,
        colWidths=anchos_columnas,
        repeatRows=1,
        hAlign="LEFT",
        splitByRow=1,
    )
    tabla_detalles.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), COLOR_AZUL_MARINO),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [COLOR_BLANCO, _aclarar_color(COLOR_AZUL, 0.95)],
                ),
                ("GRID", (0, 0), (-1, -1), 0.35, _aclarar_color(COLOR_AZUL, 0.68)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )

    total_cotizacion = Decimal(str(getattr(cotizacion, "total", 0) or 0))
    estilo_total = ParagraphStyle(
        "TotalProforma",
        parent=estilo_celda_negrita,
        fontSize=10,
        leading=12,
        alignment=TA_RIGHT,
    )
    texto_adicional = [
        Paragraph("Otros servicios que el puerto ofrece:", estilo_adicional_titulo),
        Paragraph(
            _texto(
                "Tendido de barreras anti-derrames, suministro de diésel y gasolina, "
                "flete de combustibles, suministro de sal para refrigeración, "
                "avituallamiento, mantenimiento (soldadura), descarga y lancha para "
                "embarque y desembarque de tripulación."
            ),
            estilo_adicional_texto,
        ),
        Paragraph("Other Services Offered by the Port:", estilo_adicional_titulo),
        Paragraph(
            _texto(
                "Boom containment, supply of diesel and gasoline fuel, fuel freight, "
                "salt for refrigeration, provisioning, maintenance (welding), "
                "unloading, and crew embarkation and disembarkation boat."
            ),
            estilo_adicional_texto,
        ),
        Paragraph("Condiciones / Conditions", estilo_adicional_titulo),
        Paragraph(
            _texto(
                "1. Anticipo 100% para procesar pedido / 100% advance payment to "
                "process the order."
            ),
            estilo_adicional_texto,
        ),
        Paragraph(
            _texto(
                "2. Pago 0% a crédito por 5 días naturales / 0% interest on credit "
                "for 5 calendar days."
            ),
            estilo_adicional_texto,
        ),
        Paragraph(
            "Métodos de pago en MXN / Payment methods in MXN",
            estilo_adicional_titulo,
        ),
        Paragraph(
            _texto(
                "Transferencia bancaria / Bank transfer · Banco / Bank: "
                "SANTANDER MÉXICO, S.A. · Clave interbancaria / Account: "
                "014133655161133348 · Beneficiario / Beneficiary: "
                "OPL PACÍFICO SUR S.A.P.I. DE C.V."
            ),
            estilo_adicional_texto,
        ),
        Paragraph(
            "Métodos de pago en USD / Payment methods in USD",
            estilo_adicional_titulo,
        ),
        Paragraph(
            _texto(
                "Transferencia bancaria / Bank transfer · Banco / Bank: BANCO "
                "NACIONAL DE MÉXICO, S.A. (BANAMEX) · Cuenta / Account: "
                "002133055293368042 · Código SWIFT: BNMXMXMMXXX · Beneficiario / "
                "Beneficiary: OPL PACÍFICO SUR S.A.P.I. DE C.V."
            ),
            estilo_adicional_texto,
        ),
        Paragraph("Inicio del proyecto", estilo_adicional_titulo),
        Paragraph(
            _texto("Una vez confirmado el anticipo."),
            estilo_adicional_texto,
        ),
    ]

    class BloqueFirma(Flowable):
        def __init__(self):
            super().__init__()
            self.width = ancho
            self.height = 24 * mm

        def draw(self):
            lienzo = self.canv
            inicio = ancho * 0.57
            centro = inicio + (ancho - inicio) / 2
            lienzo.setStrokeColor(COLOR_SIDEBAR)
            lienzo.setLineWidth(0.7)
            lienzo.line(inicio, 18 * mm, ancho, 18 * mm)
            lienzo.setFillColor(COLOR_SIDEBAR)
            lienzo.setFont("Helvetica-Bold", 6.5)
            lienzo.drawCentredString(
                centro, 14 * mm, "CAPITÁN Y/O ARMADOR DEL BUQUE"
            )
            lienzo.drawCentredString(
                centro, 11 * mm, "CAPTAIN / SHIPOWNER"
            )
            lienzo.setFont("Helvetica", 5.2)
            lienzo.drawCentredString(
                centro,
                6.5 * mm,
                "Se aceptan esta proforma, notas aclaratorias y condiciones de servicio.",
            )
            lienzo.drawCentredString(
                centro,
                3.5 * mm,
                "This proforma, explanatory notes and service conditions are accepted.",
            )

    bloque_final = KeepTogether(
        [
            Paragraph(
                f"TOTAL / TOTAL: $ {total_cotizacion:,.2f} {moneda}",
                estilo_total,
            ),
            Spacer(1, 1 * mm),
            *texto_adicional,
            Spacer(1, 2 * mm),
            BloqueFirma(),
        ]
    )
    historia = [
        encabezado,
        Spacer(1, 2 * mm),
        seccion("Cliente / Customer"),
        datos_cliente,
        Spacer(1, 1.5 * mm),
        seccion("Información del buque / Vessel's Information"),
        datos_buque,
        Spacer(1, 1.5 * mm),
        seccion("Servicios y conceptos / Services and items"),
        tabla_detalles,
        Spacer(1, 1 * mm),
        bloque_final,
    ]
    documento.build(historia)
    return salida.getvalue()


async def exportar_proforma_pdf(page: ft.Page, cotizacion: Any) -> bool:
    contenido = crear_pdf_proforma(cotizacion)
    nombre_archivo = f"{getattr(cotizacion, 'folio', 'proforma')}.pdf"
    selector = obtener_selector_archivos(page)
    ruta = await selector.save_file(
        dialog_title="Descargar proforma",
        file_name=nombre_archivo,
        file_type=ft.FilePickerFileType.CUSTOM,
        allowed_extensions=["pdf"],
        src_bytes=contenido,
    )
    return ruta is not None
