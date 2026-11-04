import flet as ft


def obtener_selector_archivos(page: ft.Page) -> ft.FilePicker:
    for servicio in page.services:
        if isinstance(servicio, ft.FilePicker):
            return servicio

    selector = ft.FilePicker()
    page.services.append(selector)
    return selector
