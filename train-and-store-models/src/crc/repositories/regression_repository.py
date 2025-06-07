from typing import List

from ..entities.regression_entity import Regression
from .repository import Repository


class RegressionRepository(Repository[Regression]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> Regression:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_model, id_feature, coeff, std_err, value, p_value, id FROM grafana_ml_model_regression WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe Regression con id {id}")
            return Regression(*row)

    def get_all(self) -> List[Regression]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_model, id_feature, coeff, std_err, value, p_value, id FROM grafana_ml_model_regression")
            return [Regression(*row) for row in cursor.fetchall()]

    def add(self, item: Regression) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_regression (id_model, id_feature, coeff, std_err, value, p_value) VALUES (%s, %s, %s, %s, %s, %s) RETURNING id",
                (item.id_model, item.id_feature, item.coeff, item.std_err, item.value, item.p_value)
            )
            item.id = cursor.fetchone()[0]

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_regression WHERE id = %s", (id,))
            
    def delete_by_model(self, id_model: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_regression WHERE id_model = %s", (id_model,))