class ControladorDashboard:
    def __init__(self):
        pass

    def obtener_metricas(self):
        
        return {
            "pendientes": "12",
            "aprobadas": "28",
            "rechazadas": "6",
            "monto_mensual": "$1,286,500 MXN"
        }

    def obtener_ultimas_cotizaciones(self):
        
        return [
            {
                "folio": "COT-2026-0048", 
                "fecha": "04/09/2026", 
                "buque": "MSC ORION", 
                "cliente": "MSC Shipping S.A.", 
                "monto": "$245,800.00", 
                "estado": "Pendiente",
                "color_estado": "naranja"
            }
        ]