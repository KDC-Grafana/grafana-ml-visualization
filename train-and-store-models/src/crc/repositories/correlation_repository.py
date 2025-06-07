from typing import List

from ..entities.correlation_entity import Correlation
from .repository import Repository


class CorrelationRepository(Repository[Correlation]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> Correlation:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_model, id_feature1, id_feature2, value, id FROM grafana_ml_model_correlation WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe Correlation con id {id}")
            return Correlation(*row)

    def get_all(self) -> List[Correlation]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_model, id_feature1, id_feature2, value, id FROM grafana_ml_model_correlation")
            return [Correlation(*row) for row in cursor.fetchall()]

    def add(self, item: Correlation) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_correlation (id_model, id_feature1, id_feature2, value) VALUES (%s, %s, %s, %s) RETURNING id",
                (item.id_model, item.id_feature1, item.id_feature2, item.value)
            )
            item.id = cursor.fetchone()[0]

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_correlation WHERE id = %s", (id,))
            
    def delete_by_model(self, id_model: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_correlation WHERE id_model = %s", (id_model,))