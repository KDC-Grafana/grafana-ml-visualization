from ..source.manager.source_manager import SourceManager
from .task_entity import TaskCreateSource, TaskDeleteSource
from .task_query import TaskQuery


class SourceExecutor:
    def __init__(self):
        self.task_query = TaskQuery()
        self.source_manager = SourceManager()
        
    def create_source(self, task: TaskCreateSource):
        return self.source_manager.create(task.name, task.description, task.creator, task.target, task.source)

    def delete_source(self, task: TaskDeleteSource):
        self.source_manager.delete(task.id_source)