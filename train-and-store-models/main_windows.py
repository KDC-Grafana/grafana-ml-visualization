import time
import logging
import os
import sys
import ctypes
import ctypes
import psutil
import win32com.client
import win32gui
import win32con
import win32process
from threading import Thread
from src.task.task_scheduler import TaskScheduler
from src.notifications.notifier import Notifier
from src.utils.utils import Utils

# Constantes para hotkey
MOD_CTRL = 0x0002
MOD_SHIFT = 0x0004
VK_Q = 0x51
HOTKEY_ID = 1

def prompt_startup_confirmation():
    """Muestra una ventana de confirmación al inicio del sistema"""
    result = ctypes.windll.user32.MessageBoxW(
        0, # No se especifica ventana padre
        "¿Desea ejecutar el servicio GrafanaML?",
        "Confirmación de inicio",
        4  # MB_YESNO (4) -- Código de Windows para mostrar los botones [Sí] y [No]
    )
    return result == 6  # IDYES = 6 -- 6 → El usuario presionó Sí (IDYES) /  7 → El usuario presionó No (IDNO)

def prompt_exit_confirmation():
    """Ventana de salida al presionar Ctrl+Shift+Q"""
    result = ctypes.windll.user32.MessageBoxW(
        0,
        "¿Desea detener el servicio GrafanaML?",
        "Confirmación de salida",
        4  # MB_YESNO
    )
    return result == 6  # IDYES

def register_hotkey():
    """Registra Ctrl+Shift+Q como atajo global"""
    success = ctypes.windll.user32.RegisterHotKey(
        None,
        HOTKEY_ID,
        MOD_CTRL | MOD_SHIFT,
        VK_Q
    )
    if not success:
        logging.error("No se pudo registrar el hotkey. Puede estar en uso.")
    else:
        logging.info("Hotkey Ctrl+Shift+Q registrado correctamente")


# Configuración inicial de logging
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)  # Crear la carpeta si no existe

log_path = os.path.join(log_dir, 'cron_python.log')

# Limpiar configuración previa
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)
    
#log_path = os.path.join(os.path.dirname(__file__), 'cron_python.log')
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class Main:
    def __init__(self):  
        self.hidden_pid = None  # Guardar PID de la ventana oculta    
        self.configure_autostart() # Configurar autoarranque
        register_hotkey()

    def configure_autostart(self):
        """Configura el script para ejecutarse al inicio del sistema"""
        script_path = os.path.abspath(sys.argv[0])
        startup_folder = os.path.join(
            os.getenv('APPDATA'),
            'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup'
        )
        shortcut_path = os.path.join(startup_folder, "Cron.lnk")

        if not os.path.exists(shortcut_path):
            shell = win32com.client.Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(shortcut_path)
            shortcut.TargetPath = sys.executable # Ejecutar con python.exe
            shortcut.Arguments = f'"{script_path}"'
            shortcut.WorkingDirectory = os.path.dirname(script_path)
            shortcut.IconLocation = script_path
            shortcut.save()
            logging.info("Acceso directo añadido al inicio de Windows")

    def run_program(self):
        """Función principal que se ejecuta periódicamente"""
        try:
            logging.info("Buscando tareas pendientes...")
            
            # Ejecutar lógica de TaskScheduler (modelo y fuentes)
            task_scheduler = TaskScheduler(auto_run=False, notify=Notifier().send)
            task_scheduler.run()
                    
        except Exception as e:
            logging.error(f"Error en run_program: {str(e)}")

    def cron_loop(self):
        """Loop de tareas cron"""
        interval_minutes = Utils.get_scheduler_interval()
        interval_seconds = interval_minutes * 60

        logging.info(f"Intervalo configurado: {interval_minutes} minutos ({interval_seconds} segundos)")

        while True:
            self.run_program()
            logging.info(f"Esperando {interval_minutes} minutos antes de la próxima ejecución...")
            time.sleep(interval_seconds)

    def hide_active_window(self):
        """Oculta la ventana activa y guarda el PID"""
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                _, pid = win32process.GetWindowThreadProcessId(hwnd)
                self.hidden_pid = pid
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
                logging.info(f"Ventana oculta. PID: {pid}")
            else:
                logging.warning("No hay ventana en primer plano para ocultar.")
        except Exception as e:
            logging.warning(f"No se pudo ocultar la ventana: {e}")
    
    def shutdown_hidden_process(self):
        """Cierra el proceso oculto si sigue activo"""
        if self.hidden_pid:
            try:
                p = psutil.Process(self.hidden_pid)
                nombre = p.name().lower()

                if not nombre.startswith("system"):
                    logging.info(f"Cerrando proceso oculto: {p.name()} (PID {p.pid})")
                    p.terminate()
                else:
                    logging.warning(f"Se detectó un proceso del sistema, no se cerrará: {p.name()} (PID {p.pid})")

            except Exception as e:
                logging.warning(f"No se pudo cerrar el proceso oculto: {e}")

    def listen_for_hotkey(self):
        """Escucha la pulsación del hotkey"""
        msg = ctypes.wintypes.MSG()
        while True:
            ret = ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if ret == -1:
                logging.error("Error en GetMessageW")
                break
            elif ret == 0:
                logging.info("GetMessageW devolvió 0 (WM_QUIT)")
                break
            elif msg.message == 0x0312: # WM_HOTKEY
                try:
                    # Asegurarse de que wParam no es null
                    wparam = getattr(msg, 'wParam', None)
                    if wparam is not None and int(wparam) == HOTKEY_ID:
                        logging.info(f"Hotkey {HOTKEY_ID} presionado.")
                        if prompt_exit_confirmation():
                            logging.info("Servicio detenido por hotkey Ctrl+Shift+Q")
                            logging.info("Cerrando el servicio...")
                            time.sleep(1)
                            self.shutdown_hidden_process()
                            ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID) # Desregistrar hotkey antes de salir
                            ctypes.windll.user32.PostQuitMessage(0)
                            sys.exit(0)
                except (TypeError, ValueError) as e:
                    logging.warning(f"Error al procesar wParam: {e}")
                    continue  # Ignorar mensaje corrupto
            
            ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
            ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
    
    def start_service(self):
        """Inicia el servicio"""
        logging.info("Iniciando servicio de Cron...")

        if os.name == 'nt':
           self.hide_active_window()

        # Ejecutar el cron en un hilo separado
        Thread(target=self.cron_loop, daemon=True).start()

        # Escuchar hotkey en el hilo principal
        self.listen_for_hotkey()


if __name__ == "__main__":
    if prompt_startup_confirmation():
        service = Main()
        service.start_service()
    else:
        logging.info("El usuario canceló la ejecución al inicio.")
        sys.exit(0)    