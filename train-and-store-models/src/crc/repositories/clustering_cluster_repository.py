from typing import List

from ..entities.clustering_cluster_entity import ClusteringCluster
from .repository import Repository


class ClusteringClusterRepository(Repository[ClusteringCluster]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> ClusteringCluster:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_model, number, inertia, silhouette_coefficient, id FROM grafana_ml_model_clustering_cluster WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe ClusteringCluster con id {id}")
            return ClusteringCluster(*row)

    def get_all(self) -> List[ClusteringCluster]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_model, number, inertia, silhouette_coefficient, id FROM grafana_ml_model_clustering_cluster")
            return [ClusteringCluster(*row) for row in cursor.fetchall()]

    def add(self, item: ClusteringCluster) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_clustering_cluster (id_model, number, inertia, silhouette_coefficient) VALUES (%s, %s, %s, %s) RETURNING id",
                (item.id_model, item.number, item.inertia, item.silhouette_coefficient)
            )
            item.id = cursor.fetchone()[0]

    def update(self, id: int, **kwargs: object) -> None:
        allowed = ["id_model", "number", "inertia", "silhouette_coefficient"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id)
        with self.connect() as cursor:
            cursor.execute(
                f"UPDATE grafana_ml_model_clustering_cluster SET {', '.join(fields)} WHERE id = %s",
                tuple(values)
            )

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_clustering_cluster WHERE id = %s", (id,))

    def delete_by_model(self, id_model: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_clustering_cluster WHERE id_model = %s", (id_model,))
