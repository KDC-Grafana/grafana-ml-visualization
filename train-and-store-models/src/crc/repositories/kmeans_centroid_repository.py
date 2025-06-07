from typing import List

from ..entities.kmeans_centroid_entity import KMeansCentroid
from .repository import Repository


class KMeansCentroidRepository(Repository[KMeansCentroid]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> KMeansCentroid:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_model, id_cluster, id_feature, value FROM grafana_ml_model_kmeans_centroid WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe KMeansCentroid con id {id}")
            return KMeansCentroid(*row)

    def get_all(self) -> List[KMeansCentroid]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_model, id_cluster, id_feature, value FROM grafana_ml_model_kmeans_centroid")
            return [KMeansCentroid(*row) for row in cursor.fetchall()]

    def add(self, item: KMeansCentroid) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_kmeans_centroid (id_model, id_cluster, id_feature, value) VALUES (%s, %s, %s, %s)",
                (item.id_model, item.id_cluster, item.id_feature, item.value)
            )

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_kmeans_centroid WHERE id = %s", (id,))
            
    def delete_by_model(self, id_model: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_kmeans_centroid WHERE id_model = %s", (id_model,))