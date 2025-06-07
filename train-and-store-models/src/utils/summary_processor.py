import os
from datetime import datetime

class SummaryProcessor:
    def __init__(self, resumen, notify=None, use_notifications=True):
        self.resumen = resumen
        self.notify = notify
        self.use_notifications = use_notifications

        self.base_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '..', '..')
        )

    def procesar(self):
        resumen = self.resumen
        total = sum(len(resumen[k]) for k in resumen if k != "errores")
        errores = len(resumen["errores"])

        mensaje = f"Tareas ejecutadas: {total}\nErrores encontrados: {errores}"
        if total == 0 and errores == 0:
            mensaje = "No hay tareas pendientes por ejecutar."

        if self.use_notifications and self.notify:
            self.notify("GrafanaML", mensaje)

        log_folder = os.path.join(self.base_path, "logs")
        os.makedirs(log_folder, exist_ok=True)

        # Archivo por día
        fecha_str = datetime.now().strftime("%Y-%m-%d")
        filename = os.path.join(log_folder, f"resumen_{fecha_str}.txt")

        # Abrir en modo append para agregar al archivo diario
        with open(filename, "a", encoding="utf-8") as f:
            f.write("\n" + "-" * 60 + "\n")  # Línea separadora
            f.write(f"\nResumen de tareas ejecutado el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            if resumen["modelos_creados"]:
                f.write(f"Modelos creados: {', '.join(map(str, resumen['modelos_creados']))}\n")
            if resumen["modelos_eliminados"]:
                f.write(f"Modelos eliminados: {', '.join(map(str, resumen['modelos_eliminados']))}\n")
            if resumen["fuentes_creadas"]:
                f.write(f"Fuentes creadas: {', '.join(map(str, resumen['fuentes_creadas']))}\n")
            if resumen["fuentes_eliminadas"]:
                f.write(f"Fuentes eliminadas: {', '.join(map(str, resumen['fuentes_eliminadas']))}\n")

            if errores:
                f.write("Errores encontrados:\n")
                for err in resumen["errores"]:
                    f.write(f" - {err['mensaje']}\n")
            elif total == 0:
                f.write("No hay tareas pendientes por ejecutar.\n")
