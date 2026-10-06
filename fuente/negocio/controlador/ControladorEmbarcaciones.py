from fuente.negocio.modelo.Embarcacion import Embarcacion

class ControladorEmbarcaciones:
    def __init__(self):
        # Datos simulados basados exactamente en los atributos de la clase SQLAlchemy
        self.embarcaciones = [
            Embarcacion(
                id_embarcacion=1,
                id_cliente=1,
                nombre="CAPE BRETON",
                matricula="0701012334-7",
                imo="7803255",
                bandera="Canadá",
                tipo_embarcacion="TUNA PURSE SEINER",
                loa=73.50,
                gtr=2019.00,
                trb=2019.00,
                tonelaje=1500.00,
                manga=12.00,
                puntual=5.50,
                calado_draft=6.80,
                volumen_cubico=3500.00
            ),
            Embarcacion(
                id_embarcacion=2,
                id_cliente=2,
                nombre="M/V SOL OCEÁNICO",
                matricula="MAT-9982",
                imo="9123456",
                bandera="Panamá",
                tipo_embarcacion="Portacontenedores",
                loa=120.00,
                gtr=5000.00,
                trb=4800.00,
                tonelaje=8500.00,
                manga=20.00,
                puntual=10.00,
                calado_draft=8.50,
                volumen_cubico=15000.00
            )
        ]

    def obtener_embarcaciones(self, texto="", limit=10, offset=0):
        texto = texto.strip().lower()
        embarcaciones = self.embarcaciones

        if texto:
            embarcaciones = [
                emb for emb in embarcaciones
                if texto in emb.nombre.lower()
                or (emb.imo and texto in emb.imo.lower())
                or (emb.matricula and texto in emb.matricula.lower())
                or (emb.bandera and texto in emb.bandera.lower())
            ]

        total = len(embarcaciones)
        datos = embarcaciones[offset:offset + limit]

        return datos, total

    def obtener_embarcacion(self, id_embarcacion):
        return next(
            (emb for emb in self.embarcaciones if emb.id_embarcacion == id_embarcacion),
            None,
        )

    def agregar_embarcacion(self, embarcacion):
        nuevo_id = max(
            (emb.id_embarcacion for emb in self.embarcaciones),
            default=0,
        ) + 1

        embarcacion.id_embarcacion = nuevo_id
        self.embarcaciones.append(embarcacion)

    def actualizar_embarcacion(self, embarcacion_actualizada):
        for i, emb in enumerate(self.embarcaciones):
            if emb.id_embarcacion == embarcacion_actualizada.id_embarcacion:
                self.embarcaciones[i] = embarcacion_actualizada
                return True
        return False

    def eliminar_embarcacion(self, id_embarcacion):
        for i, emb in enumerate(self.embarcaciones):
            if emb.id_embarcacion == id_embarcacion:
                self.embarcaciones.pop(i)
                return True
        return False