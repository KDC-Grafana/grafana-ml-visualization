from typing import List

from ..entities.kmeans_point_entity import KMeansPoint
from .repository import Repository


class KMeansPointRepository(Repository[KMeansPoint]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> KMeansPoint:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_model, id_point, id_cluster, id FROM grafana_ml_model_kmeans_point WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe KMeansPoint con id {id}")
            return KMeansPoint(*row)

    def get_all(self) -> List[KMeansPoint]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_model, id_point, id_cluster, id FROM grafana_ml_model_kmeans_point")
            return [KMeansPoint(*row) for row in cursor.fetchall()]

    def add(self, item: KMeansPoint) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_kmeans_point (id_model, id_point, id_cluster) VALUES (%s, %s, %s) RETURNING id",
                (item.id_model, item.id_point, item.id_cluster)
            )
            item.id = cursor.fetchone()[0]

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_kmeans_point WHERE id = %s", (id,))
            
    def delete_by_model(self, id_model: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_kmeans_point WHERE id_model = %s", (id_model,))