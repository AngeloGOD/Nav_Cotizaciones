from fuente.negocio.modelo.Embarcacion import Embarcacion

class ControladorEmbarcaciones:
    def __init__(self):
        # 15 Datos simulados para probar la paginación (> 10 registros)
        self.embarcaciones = [
            Embarcacion(
                id_embarcacion=1, id_cliente=1, nombre="CAPE BRETON", matricula="0701012334-7",
                imo="7803255", bandera="Canadá", tipo_embarcacion="TUNA PURSE SEINER",
                loa=73.50, gtr=2019.00, trb=605.00, tonelaje=1500.00, manga=12.00, puntual=5.50, calado_draft=6.80, volumen_cubico=3500.00
            ),
            Embarcacion(
                id_embarcacion=2, id_cliente=2, nombre="M/V SOL OCEÁNICO", matricula="MAT-9982",
                imo="9123456", bandera="Panamá", tipo_embarcacion="Portacontenedores",
                loa=120.00, gtr=5000.00, trb=4800.00, tonelaje=8500.00, manga=20.00, puntual=10.00, calado_draft=8.50, volumen_cubico=15000.00
            ),
            Embarcacion(
                id_embarcacion=3, id_cliente=3, nombre="OCEAN EXPLORER", matricula="MAT-1023",
                imo="9345123", bandera="Liberia", tipo_embarcacion="Granelero",
                loa=180.50, gtr=25000.00, trb=15000.00, tonelaje=30000.00, manga=30.00, puntual=15.00, calado_draft=11.20, volumen_cubico=45000.00
            ),
            Embarcacion(
                id_embarcacion=4, id_cliente=1, nombre="PACIFIC BREEZE", matricula="MAT-4455",
                imo="9876543", bandera="Islas Marshall", tipo_embarcacion="Tanque Químico",
                loa=145.20, gtr=12000.00, trb=8500.00, tonelaje=18000.00, manga=22.50, puntual=12.00, calado_draft=9.50, volumen_cubico=22000.00
            ),
            Embarcacion(
                id_embarcacion=5, id_cliente=4, nombre="MSC ISABELLA", matricula="MAT-MSC01",
                imo="9836828", bandera="Panamá", tipo_embarcacion="Portacontenedores",
                loa=399.90, gtr=228283.00, trb=110000.00, tonelaje=228000.00, manga=61.00, puntual=33.20, calado_draft=16.00, volumen_cubico=250000.00
            ),
            Embarcacion(
                id_embarcacion=6, id_cliente=2, nombre="MAERSK MC-KINNEY", matricula="MAT-MK01",
                imo="9619907", bandera="Dinamarca", tipo_embarcacion="Portacontenedores",
                loa=399.00, gtr=194849.00, trb=98000.00, tonelaje=194000.00, manga=59.00, puntual=30.00, calado_draft=15.50, volumen_cubico=210000.00
            ),
            Embarcacion(
                id_embarcacion=7, id_cliente=3, nombre="SEASPAN ZAMBEZI", matricula="MAT-SZ09",
                imo="9686871", bandera="Hong Kong", tipo_embarcacion="Portacontenedores",
                loa=336.00, gtr=113000.00, trb=65000.00, tonelaje=118000.00, manga=48.20, puntual=25.00, calado_draft=13.00, volumen_cubico=130000.00
            ),
            Embarcacion(
                id_embarcacion=8, id_cliente=1, nombre="CMA CGM JACQUES SAADE", matricula="MAT-CMA1",
                imo="9839131", bandera="Francia", tipo_embarcacion="Portacontenedores GNL",
                loa=399.90, gtr=236583.00, trb=120000.00, tonelaje=236000.00, manga=61.00, puntual=35.00, calado_draft=16.00, volumen_cubico=260000.00
            ),
            Embarcacion(
                id_embarcacion=9, id_cliente=4, nombre="HAPAG-LLOYD EXPRESS", matricula="MAT-HL02",
                imo="9708813", bandera="Alemania", tipo_embarcacion="Portacontenedores",
                loa=366.00, gtr=145000.00, trb=80000.00, tonelaje=145000.00, manga=48.00, puntual=28.00, calado_draft=14.50, volumen_cubico=160000.00
            ),
            Embarcacion(
                id_embarcacion=10, id_cliente=2, nombre="COSCO SHIPPING UNIVERSE", matricula="MAT-CO01",
                imo="9795610", bandera="Hong Kong", tipo_embarcacion="Portacontenedores",
                loa=399.90, gtr=215553.00, trb=105000.00, tonelaje=215000.00, manga=58.60, puntual=32.00, calado_draft=16.00, volumen_cubico=240000.00
            ),
            Embarcacion(
                id_embarcacion=11, id_cliente=3, nombre="EVER GIVEN", matricula="MAT-EG99",
                imo="9811000", bandera="Panamá", tipo_embarcacion="Portacontenedores",
                loa=399.94, gtr=219079.00, trb=100000.00, tonelaje=220000.00, manga=58.80, puntual=32.90, calado_draft=15.70, volumen_cubico=230000.00
            ),
            Embarcacion(
                id_embarcacion=12, id_cliente=1, nombre="HYUNDAI HOPE", matricula="MAT-HH04",
                imo="9625342", bandera="Corea del Sur", tipo_embarcacion="Portacontenedores",
                loa=366.00, gtr=141000.00, trb=75000.00, tonelaje=140000.00, manga=48.20, puntual=29.00, calado_draft=14.50, volumen_cubico=155000.00
            ),
            Embarcacion(
                id_embarcacion=13, id_cliente=4, nombre="OOCL HONG KONG", matricula="MAT-OOCL1",
                imo="9776171", bandera="Hong Kong", tipo_embarcacion="Portacontenedores",
                loa=399.87, gtr=210890.00, trb=98000.00, tonelaje=210000.00, manga=58.80, puntual=32.50, calado_draft=16.00, volumen_cubico=220000.00
            ),
            Embarcacion(
                id_embarcacion=14, id_cliente=2, nombre="ONE APUS", matricula="MAT-ONE1",
                imo="9806079", bandera="Japón", tipo_embarcacion="Portacontenedores",
                loa=364.00, gtr=146694.00, trb=85000.00, tonelaje=146000.00, manga=51.00, puntual=30.00, calado_draft=15.00, volumen_cubico=165000.00
            ),
            Embarcacion(
                id_embarcacion=15, id_cliente=3, nombre="M/V DON CARLOS", matricula="MAT-RO01",
                imo="9138329", bandera="Singapur", tipo_embarcacion="Ro-Ro Cargo",
                loa=227.80, gtr=67140.00, trb=30000.00, tonelaje=28000.00, manga=32.26, puntual=20.00, calado_draft=10.50, volumen_cubico=75000.00
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