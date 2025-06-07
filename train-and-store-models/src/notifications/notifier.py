from pathlib import Path

from plyer import notification

class Notifier:
    def __init__(self, app_name='ControllerMLGRafana'):
        """
        Inicializa el notificador con configuraciones por defecto.
        
        :param app_name: Nombre de la aplicación para mostrar en notificaciones
        """
        
        current_dir = (Path(__file__).resolve()).parent
        icon_path = current_dir / "icon.ico"
        
        self.app_name = app_name
        self.icon = str(icon_path)
        
    def send(self, title, message, duration=5):
        """
        Envía una notificación al sistema operativo.
        
        :param title: Título de la notificación
        :param message: Contenido del mensaje
        :param duration: Tiempo en segundos que se muestra (default: 3)
        """
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=self.app_name,
                app_icon=self.icon,
                timeout=duration
            )
        except Exception as e:
            print(f"Error enviando notificación: {e}")
