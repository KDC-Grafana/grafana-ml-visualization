from typing import List

from ..entities.clustering_metrics_entity import ClusteringMetrics
from .repository import Repository


class ClusteringMetricsRepository(Repository[ClusteringMetrics]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> ClusteringMetrics:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_model, inertia, silhouette_coefficient, davies_bouldin_index, id FROM grafana_ml_model_clustering_metrics WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe ClusteringMetrics con id {id}")
            return ClusteringMetrics(*row)

    def get_all(self) -> List[ClusteringMetrics]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_model, inertia, silhouette_coefficient, davies_bouldin_index, id FROM grafana_ml_model_clustering_metrics")
            return [ClusteringMetrics(*row) for row in cursor.fetchall()]

    def add(self, item: ClusteringMetrics) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_clustering_metrics (id_model, inertia, silhouette_coefficient, davies_bouldin_index) VALUES (%s, %s, %s, %s) RETURNING id",
                (item.id_model, item.inertia, item.silhouette_coefficient, item.davies_bouldin_index)
            )
            item.id = cursor.fetchone()[0]

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_clustering_metrics WHERE id = %s", (id,))
            
    def delete_by_model(self, id_model: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_clustering_metrics WHERE id_model = %s", (id_model,))