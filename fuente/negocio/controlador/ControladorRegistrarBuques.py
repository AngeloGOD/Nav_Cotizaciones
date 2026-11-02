from fuente.negocio.controlador.ControladorBuque import ControladorBuque


class ControladorRegistrarBuques:

    def __init__(self, servicio_buque):
        self.controlador_buque = ControladorBuque(servicio_buque)

    def obtener_datos(self, pantalla):
        return {
            "nombre": (pantalla.nombre.value or "").strip(),
            "numero_imo": (pantalla.numero_imo.value or "").strip(),
            "cliente_id": pantalla.cliente_busqueda.cliente_id_seleccionado,
            "categoria_buque": (pantalla.categoria_buque.value or "").strip(),
            "subtipo_descripcion": (pantalla.subtipo_descripcion.value or "").strip(),
            "bandera_pais": (pantalla.bandera_pais.value or "").strip(),
            "trb_arqueo_bruto": (pantalla.trb_arqueo_bruto.value or "").strip(),
            "eslora_metros": (pantalla.eslora_metros.value or "").strip(),
            "calado_metros": (pantalla.calado_metros.value or "").strip(),
            "es_autopropulsado": bool(pantalla.es_autopropulsado.value),
            "propulsores_proa_popa": bool(pantalla.propulsores_proa_popa.value),
            "activo": bool(pantalla.activo.value),
        }

    def validar_datos(self, datos):
        if not datos["nombre"]:
            return False, "El nombre del buque es obligatorio."
        if not datos["categoria_buque"]:
            return False, "Selecciona la categoría del buque."
        if not datos["trb_arqueo_bruto"]:
            return False, "El arqueo bruto es obligatorio."
        if not datos["eslora_metros"]:
            return False, "La eslora del buque es obligatoria."
        return True, ""

    def guardar_buque(self, datos, buque_a_editar=None):
        valido, mensaje = self.validar_datos(datos)
        if not valido:
            return False, mensaje
        try:
            if buque_a_editar is not None:
                self.controlador_buque.modificar_buque(
                    buque=buque_a_editar,
                    **datos
                )
                return True, "Buque modificado correctamente."
            self.controlador_buque.registrar_buque(**datos)
            return True, "Buque registrado correctamente."
        except Exception as error:
            print(f"Error al guardar el buque: {error}")
            return False, "No se pudieron guardar los cambios del buque."
