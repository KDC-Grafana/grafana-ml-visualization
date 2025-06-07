from typing import List

from ..entities.kmedoids_point_entity import KMedoidsPoint
from .repository import Repository


class KMedoidsPointRepository(Repository[KMedoidsPoint]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> KMedoidsPoint:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_model, id_point, id_cluster, is_medoid, id FROM grafana_ml_model_kmedoids_point WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe KMedoidsPoint con id {id}")
            return KMedoidsPoint(*row)

    def get_all(self) -> List[KMedoidsPoint]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_model, id_point, id_cluster, is_medoid, id FROM grafana_ml_model_kmedoids_point")
            return [KMedoidsPoint(*row) for row in cursor.fetchall()]

    def add(self, item: KMedoidsPoint) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_kmedoids_point (id_model, id_point, id_cluster, is_medoid) VALUES (%s, %s, %s, %s) RETURNING id",
                (item.id_model, item.id_point, item.id_cluster, item.is_medoid)
            )
            item.id = cursor.fetchone()[0]

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_kmedoids_point WHERE id = %s", (id,))

    def delete_by_model(self, id_model: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_kmedoids_point WHERE id_model = %s", (id_model,))