from typing import List

from ...crc.repositories.repository import Repository
from ..entities.feature_entity import Feature


class FeatureRepository(Repository[Feature]):
    def __init__(self) -> None:
        super().__init__() 

    def get(self, id: int) -> Feature:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_source, name, is_target, id FROM grafana_ml_model_feature WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe feature con id {id}")
            return Feature(*row)

    def get_all(self) -> List[Feature]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_source, name, is_target, id FROM grafana_ml_model_feature")
            return [Feature(*row) for row in cursor.fetchall()]

    def add(self, item: Feature) -> None:
        """Agrega un nuevo Feature y actualiza su id."""
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_feature (id_source, name, is_target) VALUES (%s, %s, %s) RETURNING id",
                (item.id_source, item.name, item.is_target)
            )
            item.id = cursor.fetchone()[0]

    def update(self, id: int, **kwargs: object) -> None:
        allowed = ["id_source", "name", "is_target"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id)
        with self.connect() as cursor:
            cursor.execute(
                f"UPDATE grafana_ml_model_feature SET {', '.join(fields)} WHERE id = %s",
                tuple(values)
            )

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_feature WHERE id = %s", (id,))

    def delete_by_source(self, source_id: int) -> None:
        """Elimina todas las características asociadas a un id_source."""
        with self.connect(autocommit=False) as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_feature WHERE id_source = %s", (source_id,))
            
            
            