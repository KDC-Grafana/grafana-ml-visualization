import contextlib
from abc import abstractmethod
from typing import Generic, List, Optional, TypeVar

from ...database.database_connection import DatabaseConnection

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """
    Repositorio base abstracto. Define la interfaz CRUD que las subclases deben implementar.
    """
    def __init__(self):
        # Crear una instancia de la conexión a la base de datos
        self.db = DatabaseConnection()

    @contextlib.contextmanager
    def connect(self,  autocommit=True):
        # Usa directamente la conexión almacenada en self.db.connection
        cursor = self.db.connection.cursor()
        try:
            yield cursor
            if autocommit:
                self.db.connection.commit()
        except Exception:
            self.db.connection.rollback()  
            raise  
        finally:
            cursor.close()  
        
    @abstractmethod
    def create(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def get(self, id: int) -> Optional[T]:
        raise NotImplementedError

    @abstractmethod
    def update(self, id: int, **fields) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete(self, id: int) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> List[T]:
        raise NotImplementedError