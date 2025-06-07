import contextlib
import json

from ..database.database_connection import DatabaseConnection
from .task_entity import (TaskCreateModel, TaskCreateSource, TaskDeleteModel,
                          TaskDeleteSource)


class TaskQuery:
    def __init__(self):
        self.db = DatabaseConnection()

    @contextlib.contextmanager
    def connect(self):
        conn = self.db.connection
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        finally:
            cursor.close()

    def get_pending_create_model_tasks(self):
        with self.connect() as cursor:
            query = """
            SELECT id, id_source, algorithm, parameters, state
            FROM grafana_ml_model_task_create
            WHERE state = 'pendiente';
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return [TaskCreateModel(*row) for row in results]
            
    def get_pending_create_source_tasks(self):
        with self.connect() as cursor:
            query = """
            SELECT id, name, description, creator, source, target, state
            FROM grafana_ml_model_source_create
            WHERE state = 'pendiente';
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return [TaskCreateSource(*row) for row in results]
        
    def get_pending_delete_model_tasks(self):
        with self.connect() as cursor:
            query = """
            SELECT id, id_model, state, date
            FROM grafana_ml_model_task_delete
            WHERE state = 'pendiente';
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return [TaskDeleteModel(*row) for row in results]

    def get_pending_delete_source_tasks(self):
        with self.connect() as cursor:
            query = """
            SELECT id, id_source, state, date
            FROM grafana_ml_model_source_delete
            WHERE state = 'pendiente';
            """
            cursor.execute(query)
            results = cursor.fetchall()
            return [TaskDeleteSource(*row) for row in results]
        
    def mark_task_done(self, table_name, task_id):
        with self.connect() as cursor:
            query = f"""
            UPDATE {table_name}
            SET state = 'listo'
            WHERE id = %s;
            """
            cursor.execute(query, (task_id,))

    def mark_task_running(self, table_name, task_id):
        with self.connect() as cursor:
            query = f"""
            UPDATE {table_name}
            SET state = 'en_ejecucion'
            WHERE id = %s;
            """
            cursor.execute(query, (task_id,))

    def mark_task_failed(self, table_name, task_id):
        with self.connect() as cursor:
            query = f"""
            UPDATE {table_name}
            SET state = 'ejecucion_fallida'
            WHERE id = %s;
            """
            cursor.execute(query, (task_id,))
            
    def mark_task_eliminated(self, model_id):
        with self.connect() as cursor:
            query = """
            UPDATE grafana_ml_model_task_create
            SET state = 'eliminado'
            WHERE id_model = %s;
            """
            cursor.execute(query, (model_id,))

    def mark_source_eliminated(self, source_id):
        with self.connect() as cursor:
            query = """
            UPDATE grafana_ml_model_source_create
            SET state = 'eliminado'
            WHERE id_source = %s;
            """
            cursor.execute(query, (source_id,))

    def get_algorithm_by_model_id(self, model_id):
        with self.connect() as cursor:
            query = """
            SELECT algorithm
            FROM grafana_ml_model_index
            WHERE id = %s;
            """
            cursor.execute(query, (model_id,))
            result = cursor.fetchone()
            
        if result is None:
            raise ValueError(f"No se encontró ningún modelo con id = {model_id}")
        
        return result[0]
    
    def bind_model_to_task(self, task_id, model_id):
        """
        Guarda la relación entre la tarea de creación y el modelo creado.
        """
        with self.connect() as cursor:
            query = """
            UPDATE grafana_ml_model_task_create
            SET id_model = %s
            WHERE id = %s;
            """
            cursor.execute(query, (model_id, task_id))

    def bind_source_to_task(self, task_id, source_id):
        """
        Guarda la relación entre la tarea de creación y la fuente creada.
        """
        with self.connect() as cursor:
            query = """
            UPDATE grafana_ml_model_source_create
            SET id_source = %s
            WHERE id = %s;
            """
            cursor.execute(query, (source_id, task_id))