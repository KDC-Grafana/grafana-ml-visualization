from psycopg2.errors import ForeignKeyViolation

from ..database.database_connection import DatabaseConnection
from ..utils.utils import Utils
from ..utils.summary_processor import SummaryProcessor
from ..notifications.notifier import Notifier
from .model_executor import ModelExecutor
from .source_executor import SourceExecutor
from .task_query import TaskQuery

class TaskScheduler:
    def __init__(self, auto_run=True, notify=None):
        # Cargar configuración desde config.ini
        flags = Utils.load_feature_flags()
        self.task_notifications = flags.get("task_notifications", True)
        self.general_notifications = flags.get("general_notifications", True)
        self.use_summary = flags.get("generate_summary", False)

        self.table_model_create = 'grafana_ml_model_task_create'
        self.table_model_delete = 'grafana_ml_model_task_delete'
        self.table_source_create = 'grafana_ml_model_source_create'
        self.table_source_delete = 'grafana_ml_model_source_delete'

        self.task_query = TaskQuery()
        self.model_executor = ModelExecutor()
        self.source_executor = SourceExecutor()
        self.conn = DatabaseConnection().connection

        self.notify = notify or Notifier().send
        self.resumen = self._init_summary() if self.use_summary else None
        
        if auto_run:
            self.run()

    def _init_summary(self):
        return {
            "modelos_creados": [],
            "modelos_eliminados": [],
            "fuentes_creadas": [],
            "fuentes_eliminadas": [],
            "errores": []
        }

    def _notify(self, title, message, duration=5):
        if self.task_notifications:
            self.notify(title, message, duration)

    def _add_error(self, message):
        if self.use_summary:
            self.resumen["errores"].append({"mensaje": message})

    def run(self):
        if self.general_notifications:
             self.notify("🕒 GrafanaML", "Ejecutando tareas pendientes...")
            
        self._handle_create_sources()
        self._handle_create_models()
        self._handle_delete_models()
        self._handle_delete_sources()
        
        if self.use_summary:
            SummaryProcessor(
            resumen=self.resumen,
            notify=self.notify,
            use_notifications=self.general_notifications).procesar()

    def _handle_create_models(self):
        for task in self.task_query.get_pending_create_model_tasks():
            try:
                self.task_query.mark_task_running(self.table_model_create, task.id)
                model_id = self.model_executor.create_model(task)
                self.task_query.bind_model_to_task(task.id, model_id)
                self.task_query.mark_task_done(self.table_model_create, task.id)
                
                self._notify(f"✅ Tarea {task.id}", f"Modelo creado con ID: {model_id}")
                if self.use_summary:
                    self.resumen["modelos_creados"].append(model_id)
                    
            except Exception as e:
                self.conn.rollback()
                self.task_query.mark_task_failed(self.table_model_create, task.id)
                msg = f"Error al crear modelo en tarea {task.id}: {str(e)}"
                
                self._notify(f"❌ Tarea {task.id}", msg, 6)
                self._add_error(msg)

    def _handle_delete_models(self):
        for task in self.task_query.get_pending_delete_model_tasks():
            try:
                self.task_query.mark_task_running(self.table_model_delete, task.id)
                self.model_executor.delete_model(task)
                self.task_query.mark_task_done(self.table_model_delete, task.id)
                self.task_query.mark_task_eliminated(task.id_model)
                
                self._notify(f"✅ Tarea {task.id}", "Modelo eliminado exitosamente")
                if self.use_summary:
                    self.resumen["modelos_eliminados"].append(task.id)
                    
            except Exception as e:
                self.conn.rollback()
                self.task_query.mark_task_failed(self.table_model_delete, task.id)
                msg = f"Error al eliminar modelo en tarea {task.id}: {str(e)}"
                
                self._notify(f"❌ Tarea {task.id}", msg, 6)
                self._add_error(msg)

    def _handle_create_sources(self):
        for task in self.task_query.get_pending_create_source_tasks():
            try:
                self.task_query.mark_task_running(self.table_source_create, task.id)
                source_id = self.source_executor.create_source(task)
                self.task_query.bind_source_to_task(task.id, source_id)
                self.task_query.mark_task_done(self.table_source_create, task.id)
                
                self._notify(f"✅ Tarea {task.id}", f"Fuente creada con ID: {source_id}")
                if self.use_summary:
                    self.resumen["fuentes_creadas"].append(source_id)
                    
            except Exception as e:
                self.conn.rollback()
                self.task_query.mark_task_failed(self.table_source_create, task.id)
                msg = f"Error al crear fuente en tarea {task.id}: {str(e)}"
                
                self._notify(f"❌ Tarea {task.id}", msg, 6)
                self._add_error(msg)

    def _handle_delete_sources(self):
        for task in self.task_query.get_pending_delete_source_tasks():
            try:
                self.task_query.mark_task_running(self.table_source_delete, task.id)
                self.source_executor.delete_source(task)
                self.task_query.mark_task_done(self.table_source_delete, task.id)
                self.task_query.mark_source_eliminated(task.id_source)
                
                self._notify(f"✅ Tarea {task.id}", "Fuente eliminada exitosamente")
                if self.use_summary:
                    self.resumen["fuentes_eliminadas"].append(task.id)
                    
            except ForeignKeyViolation:
                self.task_query.mark_task_failed(self.table_source_delete, task.id)
                msg = (f"Error al eliminar fuente en tarea {task.id}: "
                       "Está referenciada por otros registros. Elimine primero los registros asociados.")
                
                self._notify(f"❌ Tarea {task.id}", msg, 6)
                self._add_error(msg)
                    
            except Exception as e:
                self.conn.rollback()
                self.task_query.mark_task_failed(self.table_source_delete, task.id)
                msg = f"Error al eliminar fuente en tarea {task.id}: {str(e)}"
                
                self._notify(f"❌ Tarea {task.id}", msg, 6)
                self._add_error(msg)

                
if __name__ == "__main__":
    TaskScheduler()