from fuente.negocio.modelo.Cliente import Cliente

class ControladorClientes:
    def __init__(self):
        self.clientes = [
            Cliente(
                1,
                "MSC Shipping S.A.",
                "MSH180624KQ2",
                "Parque Industrial, Puerto Chiapas, Tapachula, Chiapas",
                "+52 833 210 4580",
                "operaciones@mscshipping.mx",
                "Agencia naviera",
            ),
            Cliente(
                2,
                "Maersk Line México, S.A. de C.V.",
                "MLM920815A71",
                "Puerto Chiapas, Tapachula, Chiapas",
                "+52 833 210 9080",
                "contacto@maersk.mx",
                "Agencia naviera",
            ),
            Cliente(
                3,
                "Navios Maritime Holdings",
                "NMH0503118D4",
                "Tapachula, Chiapas",
                "+52 833 260 1442",
                "navios@empresa.mx",
                "Armador",
            ),
            Cliente(
                4,
                "Oceanic Traders, S.A. de C.V.",
                "OTA190423P32",
                "Puerto Chiapas, Tapachula, Chiapas",
                "+52 833 198 7620",
                "administracion@oceanic.mx",
                "Cliente comercial",
            ),
            Cliente(
                5,
                "Iglesia JOSE,P.H",
                "JOSEPH6767",
                "Santa Clara,Tapachula,Chiapas",
                "+6767676767",
                "Josesitohd4k@gmail.com",
                "Cliente Fiel"
            ),
            Cliente(
                6,
                "Iglesia JOSE,P.H",
                "JOSEPH6767",
                "Santa Clara,Tapachula,Chiapas",
                "+6767676767",
                "Josesitohd4k@gmail.com",
                "Cliente Fiel"
            ),
            Cliente(
                7,
                "Iglesia JOSE,P.H",
                "JOSEPH6767",
                "Santa Clara,Tapachula,Chiapas",
                "+6767676767",
                "Josesitohd4k@gmail.com",
                "Cliente Fiel"
            ),
            Cliente(
                8,
                "Iglesia JOSE,P.H",
                "JOSEPH6767",
                "Santa Clara,Tapachula,Chiapas",
                "+6767676767",
                "Josesitohd4k@gmail.com",
                "Cliente Fiel"
            ),
            Cliente(
                9,
                "Iglesia JOSE,P.H",
                "JOSEPH6767",
                "Santa Clara,Tapachula,Chiapas",
                "+6767676767",
                "Josesitohd4k@gmail.com",
                "Cliente Fiel"
            ),
            Cliente(
                10,
                "Iglesia JOSE,P.H",
                "JOSEPH6767",
                "Santa Clara,Tapachula,Chiapas",
                "+6767676767",
                "Josesitohd4k@gmail.com",
                "Cliente Fiel"
            ),
            Cliente(
                11,
                "Iglesia JOSE,P.H",
                "JOSEPH6767",
                "Santa Clara,Tapachula,Chiapas",
                "+6767676767",
                "Josesitohd4k@gmail.com",
                "Cliente Fiel"
            ),
            Cliente(
                12,
                "Iglesia JOSE,P.H",
                "JOSEPH6767",
                "Santa Clara,Tapachula,Chiapas",
                "+6767676767",
                "Josesitohd4k@gmail.com",
                "Cliente Fiel"
            ),
        ]

    def obtener_clientes(self, texto="", limit=10, offset=0):
        texto = texto.strip().lower()

        clientes = self.clientes

        if texto:
            clientes = [
                cliente
                for cliente in clientes
                if texto in cliente.nombre.lower()
                or texto in cliente.rfc.lower()
                or texto in cliente.direccion_fiscal.lower()
                or texto in cliente.telefono.lower()
                or texto in cliente.correo_elect.lower()
            ]

        total = len(clientes)
        datos = clientes[offset:offset + limit]

        return datos, total

    def obtener_cliente(self, id_cliente):
        return next(
            (cliente for cliente in self.clientes if cliente.id_cliente == id_cliente),
            None,
        )

    def agregar_cliente(self, cliente):
        nuevo_id = max(
            (cliente.id_cliente for cliente in self.clientes),
            default=0,
        ) + 1

        cliente.id_cliente = nuevo_id
        self.clientes.append(cliente)

    def actualizar_cliente(self, cliente_actualizado):
        for i, cliente in enumerate(self.clientes):
            if cliente.id_cliente == cliente_actualizado.id_cliente:
                self.clientes[i] = cliente_actualizado
                return True

        return False

    def eliminar_cliente(self, id_cliente):
        for i, cliente in enumerate(self.clientes):
            if cliente.id_cliente == id_cliente:
                self.clientes.pop(i)
                return True

        return False