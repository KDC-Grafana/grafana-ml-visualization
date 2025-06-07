import contextlib
from abc import ABC, abstractmethod
from typing import Generic, List, TypeVar

from ...database.database_connection import DatabaseConnection

T = TypeVar('T')

class Repository(ABC, Generic[T]):
    def __init__(self):
        # Crear una instancia de la conexión a la base de datos
        self.db = DatabaseConnection()
    
    @contextlib.contextmanager
    def connect(self, autocommit=True):
        conn = self.db.connection
        try:
            with conn.cursor() as cursor:
                yield cursor
            if autocommit:  
                conn.commit()
        finally:
            cursor.close()
            
    @abstractmethod
    def get(self, id: int) -> T:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> List[T]:
        raise NotImplementedError

    @abstractmethod
    def add(self, **kwargs: object) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: int) -> None:
        raise NotImplementedError