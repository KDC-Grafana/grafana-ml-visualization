from typing import List

from ..entities.index_entity import ModelIndex
from .repository import Repository


class ModelIndexRepository(Repository[ModelIndex]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> ModelIndex:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_source, algorithm, parameters, id FROM grafana_ml_model_index WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe el modelo con id {id}")
            return ModelIndex(*row)

    def get_all(self) -> List[ModelIndex]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_source, algorithm, parameters, id FROM grafana_ml_model_index")
            return [ModelIndex(*row) for row in cursor.fetchall()]

    def add(self, item: ModelIndex) -> None:
        """Agrega un nuevo ModelIndex y actualiza su id."""
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_index (id_source, algorithm, parameters) VALUES (%s, %s, %s) RETURNING id",
                (item.id_source, item.algorithm, item.parameters)
            )
            item.id = cursor.fetchone()[0]

    def update(self, id: int, **kwargs: object) -> None:
        allowed = ["id_source", "algorithm", "parameters"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id)
        with self.connect() as cursor:
            cursor.execute(
                f"UPDATE grafana_ml_model_index SET {', '.join(fields)} WHERE id = %s",
                tuple(values)
            )

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_index WHERE id = %s", (id,))

