from typing import List

from ..entities.clustering_hierarchical_entity import ClusteringHierarchicalE
from .repository import Repository


class ClusteringHierarchicalRepository(Repository[ClusteringHierarchicalE]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> ClusteringHierarchicalE:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_model, name, height, id_parent, id_point, id FROM grafana_ml_model_clustering_hierarchical WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe ClusteringHierarchical con id {id}")
            return ClusteringHierarchicalE(*row)

    def get_all(self) -> List[ClusteringHierarchicalE]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_model, name, height, id_parent, id_point, id FROM grafana_ml_model_clustering_hierarchical")
            return [ClusteringHierarchicalE(*row) for row in cursor.fetchall()]

    def add(self, item: ClusteringHierarchicalE) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_clustering_hierarchical (id_model, name, height, id_parent, id_point) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (item.id_model, item.name, item.height, item.id_parent, item.id_point)
            )
            item.id = cursor.fetchone()[0]

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_clustering_hierarchical WHERE id = %s", (id,))
            
    
    def delete_by_model(self, id_model: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_clustering_hierarchical WHERE id_model = %s", (id_model,))