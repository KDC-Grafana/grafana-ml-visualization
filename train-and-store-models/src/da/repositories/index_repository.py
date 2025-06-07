import json
from typing import List

from src.da.entities.index_entity import Index
from src.da.repositories.base_repository import BaseRepository


class IndexRepository(BaseRepository[Index]):
    def __init__(self) -> None:
        super().__init__()

    def create(self, entity: Index) -> Index:
        """Agrega un nuevo Index y actualiza su id."""
        
        parameters = json.dumps(entity.parameters)
        
        with self.connect() as cursor:
            cursor.execute(
                """
                INSERT INTO grafana_ml_model_index 
                (id_source, algorithm, parameters)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (
                    entity.id_source,
                    entity.algorithm,
                    parameters,
                )
            )
            entity.id = cursor.fetchone()[0]
        return entity

    def get(self, id: int) -> Index:
        """Obtiene un Index por su id."""
        with self.connect() as cursor:
            cursor.execute(
                """
                SELECT id, id_source, algorithm, parameters
                FROM grafana_ml_model_index
                WHERE id = %s
                """,
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe índice con id {id}")
            return Index(*row)

    def update(self, id: int, **kwargs: object) -> Index:
        """Actualiza campos de un Index."""
        allowed = ["id_source", "algorithm", "parameters"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id)
        with self.connect() as cursor:
            cursor.execute(
                f"""
                UPDATE grafana_ml_model_index
                SET {', '.join(fields)}
                WHERE id = %s
                """,
                tuple(values)
            )
        return self.get(id)

    def delete(self, id: int) -> None:
        """Elimina un Index por su id."""
        with self.connect() as cursor:
            cursor.execute(
                "DELETE FROM grafana_ml_model_index WHERE id = %s",
                (id,)
            )

    def list(self) -> List[Index]:
        """Lista todos los Index."""
        with self.connect() as cursor:
            cursor.execute(
                """
                SELECT id, id_source, algorithm, parameters
                FROM grafana_ml_model_index
                """
            )
            return [Index(*row) for row in cursor.fetchall()]    