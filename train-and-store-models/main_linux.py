import configparser
import os
import sys
import shlex
import subprocess
import logging

from crontab import CronTab
from src.notifications.notifier import Notifier
from src.utils.utils import Utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_SCRIPT_PATH = os.path.join(BASE_DIR, 'src', 'task', 'task_scheduler.py')
DEFAULT_LOG_PATH = os.path.join(BASE_DIR, 'logs', 'app.log')
PYTHON_BIN = os.path.join(BASE_DIR, 'ml', 'bin', 'python')
FLOCK_BIN = '/usr/bin/flock'
LOCKFILE_DIR = '/tmp'
CRON_COMMENT = 'Script para la gestión de tareas de aprendizaje automático en Grafana'

# Configurar logging
logging.basicConfig(
    filename=DEFAULT_LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def detect_display():
    try:
        output = subprocess.check_output("w", universal_newlines=True)
        for line in output.splitlines():
            if ':' in line:
                parts = line.split()
                for p in parts:
                    if p.startswith(':'):
                        return p
    except Exception as e:
        logging.warning(f"No se pudo detectar DISPLAY dinámicamente: {e}")
    return ':0'

def detect_dbus():
    uid = os.getuid()
    return f'unix:path=/run/user/{uid}/bus'

DISPLAY = detect_display()
DBUS = detect_dbus()

def build_lockfile_name(name):
    return os.path.join('/tmp', f"{name}.lockfile")

def build_cron_command(script_module='src.task.task_scheduler', log_path=DEFAULT_LOG_PATH):
    lockfile = build_lockfile_name(script_module.replace('.', '_'))
    project_root = BASE_DIR
    return (
        f"{shlex.quote(FLOCK_BIN)} -n {shlex.quote(lockfile)} "
        f"env PYTHONPATH={shlex.quote(project_root)} DISPLAY={shlex.quote(DISPLAY)} DBUS_SESSION_BUS_ADDRESS={shlex.quote(DBUS)} "
        f"{shlex.quote(PYTHON_BIN)} -m {shlex.quote(script_module)} >> "
        f"{shlex.quote(log_path)} 2>&1"
    )

def create_cron(script_module='src.task.task_scheduler', log_path=DEFAULT_LOG_PATH):
    cron = CronTab(user=True)
    cron.remove_all(comment=CRON_COMMENT)
    command = build_cron_command(script_module, log_path)
    job = cron.new(command=command, comment=CRON_COMMENT)
    interval = Utils.get_scheduler_interval()
    job.minute.every(interval)
    cron.write()
    plural = "minuto" if interval == 1 else "minutos"
    logging.info(f"Tarea cron creada para módulo {script_module} con intervalo de {interval} {plural}")

def delete_cron():
    cron = CronTab(user=True)
    cron.remove_all(comment=CRON_COMMENT)
    cron.write()
    logging.info("Tarea cron eliminada.")

def print_usage():
    usage_text = (
        "Uso:\n"
        "  python main_linux.py create        # Crear tarea cron\n"
        "  python main_linux.py delete        # Eliminar tarea cron"
    )
    logging.info(usage_text)
    print(usage_text)

if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in ('create', 'delete'):
        print_usage()
        sys.exit(1)

    action = sys.argv[1]
    notifier = Notifier(app_name='GestorTareasML')

    if action == 'create':
        interval = Utils.get_scheduler_interval()
        plural = "minuto" if interval == 1 else "minutos"
        notifier.send(
            "Cron iniciado",
             f"Se ejecutarán las tareas de aprendizaje automático cada {interval} {plural}.",
            5
        )
        create_cron()
    else:
        notifier.send(
            "Cron detenido",
            "Se ha cancelado la ejecución periódica de las tareas de aprendizaje automático.",
            5
        )
        delete_cron()