from urllib.error import URLError, HTTPError
from urllib.request import Request, urlopen
import json


class ServicioPaises:
    URL_PAISES = (
        "https://countries.dev/countries"
        "?fields=name,alpha2Code,flag&sort=name"
    )
    URL_BANDERA = "https://countries.dev/flags/{codigo}.svg"
    _paises_cache = None

    @classmethod
    def obtener_paises(cls, forzar_actualizacion=False):
        if cls._paises_cache is not None and not forzar_actualizacion:
            return list(cls._paises_cache)

        solicitud = Request(
            cls.URL_PAISES,
            headers={"Accept": "application/json", "User-Agent": "Nav-Cotizaciones/1.0"},
            method="GET",
        )
        try:
            with urlopen(solicitud, timeout=12) as respuesta:
                datos = json.loads(respuesta.read().decode("utf-8"))
            if not isinstance(datos, list):
                raise ValueError("La respuesta de países no tiene el formato esperado.")

            paises = []
            for item in datos:
                if not isinstance(item, dict):
                    continue
                nombre = (item.get("name") or "").strip()
                codigo = (item.get("alpha2Code") or "").strip().upper()
                emoji = (item.get("flag") or "").strip()
                if not nombre or len(codigo) != 2:
                    continue
                paises.append({
                    "nombre": nombre,
                    "codigo": codigo,
                    "emoji": emoji,
                    "bandera_url": cls.URL_BANDERA.format(codigo=codigo.lower()),
                })
            if not paises:
                raise ValueError("La API no devolvió países válidos.")
            paises.sort(key=lambda pais: pais["nombre"].casefold())
            cls._paises_cache = paises
            return list(paises)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as error:
            if cls._paises_cache is not None:
                return list(cls._paises_cache)
            raise RuntimeError(
                "No fue posible cargar la lista de países. Comprueba tu conexión a Internet."
            ) from error

    @classmethod
    def buscar_paises(cls, texto):
        termino = (texto or "").strip().casefold()
        paises = cls.obtener_paises()
        if not termino:
            return paises
        return [
            pais for pais in paises
            if termino in pais["nombre"].casefold()
            or termino == pais["codigo"].casefold()
        ]

    @classmethod
    def obtener_por_nombre(cls, nombre):
        buscado = (nombre or "").strip().casefold()
        if not buscado:
            return None
        for pais in cls.obtener_paises():
            if pais["nombre"].casefold() == buscado:
                return pais
        return None

    @classmethod
    def limpiar_cache(cls):
        cls._paises_cache = None
