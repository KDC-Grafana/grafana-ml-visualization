from typing import List

from ...crc.repositories.repository import Repository
from ..entities.prediction_value_entity import PredictionValue


class PredictionValueRepository(Repository[PredictionValue]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id_prediction: int) -> PredictionValue:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_source, class_name, id_prediction FROM grafana_ml_model_prediction_values WHERE id_prediction = %s",
                (id_prediction,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe PredictionValue con id_prediction {id_prediction}")
            return PredictionValue(*row)

    def get_all(self) -> List[PredictionValue]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_source, class_name, id_prediction FROM grafana_ml_model_prediction_values")
            return [PredictionValue(*row) for row in cursor.fetchall()]

    def add(self, item: PredictionValue) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_prediction_values (id_source, class_name) VALUES (%s, %s) RETURNING id_prediction",
                (item.id_source, item.class_name)
            )
            item.id_prediction = cursor.fetchone()[0]

    def update(self, id_prediction: int, **kwargs: object) -> None:
        allowed = ["id_source", "class_name"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id_prediction)
        with self.connect() as cursor:
            cursor.execute(
                f"UPDATE grafana_ml_model_prediction_values SET {', '.join(fields)} WHERE id_prediction = %s",
                tuple(values)
            )

    def delete(self, id_prediction: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_prediction_values WHERE id_prediction = %s", (id_prediction,))

    def delete_by_source(self, source_id: int) -> None:
        """Elimina todos los valores de predicción asociados a un id_source."""
        with self.connect(autocommit=False) as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_prediction_values WHERE id_source = %s", (source_id,))
