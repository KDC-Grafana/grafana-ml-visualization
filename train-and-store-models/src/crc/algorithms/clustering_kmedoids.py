import json
from typing import Dict, List, Tuple

import numpy as np
from sklearn.metrics import davies_bouldin_score, silhouette_samples
from sklearn_extra.cluster import KMedoids

from ...notifications.notifier import Notifier
from ...task.task_entity import TaskCreateModel
from ..entities.clustering_cluster_entity import ClusteringCluster
from ..entities.clustering_metrics_entity import ClusteringMetrics
from ..entities.index_entity import ModelIndex
from ..entities.kmedoids_point_entity import KMedoidsPoint
from ..repositories.clustering_cluster_repository import \
    ClusteringClusterRepository
from ..repositories.clustering_metrics_repository import \
    ClusteringMetricsRepository
from ..repositories.kmedoids_point_repository import KMedoidsPointRepository
from ..repositories.model_index_repository import ModelIndexRepository
from ..source_builder.source_builder import SourceBuilder


class ClusteringKMedoids:
    def __init__(self):
        self.model_index_repo = ModelIndexRepository()
        self.clustering_cluster_repo = ClusteringClusterRepository()
        self.kmedoids_point_repo = KMedoidsPointRepository()
        self.clustering_metrics_repo = ClusteringMetricsRepository()
        self.notifier = Notifier()

    def execute(self, task: TaskCreateModel) -> int:
        points, point_ids, _, _  = SourceBuilder.build_numeric_data(task.id_source)
        params = self._get_parameters(task.parameters)

        id_model = self._save_model(task.id_source, params)

        kmedoids = KMedoids(**params, random_state=42)
        kmedoids.fit(points)

        total_dispersion, total_silhouette, cluster_id_map = self._save_clusters(id_model, kmedoids, points)
        self._save_point_assignments(id_model, kmedoids.labels_, point_ids, cluster_id_map, kmedoids.medoid_indices_)
        self._save_clustering_metrics(id_model, total_dispersion, total_silhouette, params['n_clusters'], kmedoids, points)
        
        return id_model
        
    def delete(self, id_model: int) -> None:
        self.kmedoids_point_repo.delete_by_model(id_model)
        self.clustering_cluster_repo.delete_by_model(id_model)
        self.clustering_metrics_repo.delete_by_model(id_model)
        self.model_index_repo.delete(id_model)

    def _save_model(self, id_source: int, parameters: Dict) -> int:
        parameters_json = json.dumps(parameters)
        model = ModelIndex(
            id_source=id_source,
            algorithm="a_kmedoides",
            parameters=parameters_json
        )
        self.model_index_repo.add(model)
        return model.id

    def _save_point_assignments(self, id_model: int, labels: np.ndarray, point_ids: List[int], cluster_id_map: dict, medoid_indices: np.ndarray) -> None:
        medoid_point_ids = set([point_ids[i] for i in medoid_indices])
        for point_id, cluster_number in zip(point_ids, labels):
            is_medoid = point_id in medoid_point_ids
            point = KMedoidsPoint(
                id_model=id_model,
                id_point=point_id,
                id_cluster=cluster_id_map[int(cluster_number)],
                is_medoid=is_medoid
            )
            self.kmedoids_point_repo.add(point)

    def _save_clusters(self, id_model: int, kmedoids: KMedoids, points: np.ndarray) -> Tuple[float, float, dict]:
        labels = kmedoids.labels_
        sample_silhouette = silhouette_samples(points, labels)
        total_dispersion = 0.0
        total_silhouette = 0.0
        cluster_id_map = {}

        for i in range(kmedoids.n_clusters):
            cluster_mask = labels == i
            cluster_points = points[cluster_mask]
            medoid = points[kmedoids.medoid_indices_[i]]

            dispersion_i = np.sum(np.linalg.norm(cluster_points - medoid, axis=1))
            silhouette_i = float(np.mean(sample_silhouette[cluster_mask])) if len(cluster_points) >= 2 else 0.0

            cluster = ClusteringCluster(
                id_model=id_model,
                number=i,
                inertia=dispersion_i,
                silhouette_coefficient=silhouette_i
            )
            self.clustering_cluster_repo.add(cluster)
            cluster_id_map[i] = cluster.id

            total_dispersion += dispersion_i
            total_silhouette += silhouette_i

        return total_dispersion, total_silhouette, cluster_id_map

    def _save_clustering_metrics(self, id_model: int, total_dispersion: float, total_silhouette: float,
                                 n_clusters: int, kmedoids: KMedoids, points: np.ndarray) -> None:
        silhouette_avg = total_silhouette / n_clusters
        db_index = float(davies_bouldin_score(points, kmedoids.labels_))

        metrics = ClusteringMetrics(
            id_model=id_model,
            inertia=total_dispersion,
            silhouette_coefficient=silhouette_avg,
            davies_bouldin_index=db_index
        )
        self.clustering_metrics_repo.add(metrics)


    def _get_parameters(self, configuration_json):
        default_parameters = {
            "n_clusters": 3,
            "metric": "euclidean",          # comúnmente 'euclidean', 'manhattan', etc.
            "method": "alternate",          # 'alternate' o 'pam'
            "init": "k-medoids++",            # 'random', 'heuristic', 'k-medoids++', 'build'
        }

        # Validadores por parámetro
        def is_valid_n_clusters(v):
            return isinstance(v, int) and v > 0

        def is_valid_metric(v):
            # Podrías ampliar la lista según lo que acepte tu implementación
            return v in ["euclidean", "manhattan", "cosine"]

        def is_valid_method(v):
            return v in ["alternate", "pam"]

        def is_valid_init(v):
            return v in ["random", "heuristic", "k-medoids++", "build"]

        validators = {
            "n_clusters": is_valid_n_clusters,
            "metric": is_valid_metric,
            "method": is_valid_method,
            "init": is_valid_init,
        }

        final_parameters = {}

        for key, default_value in default_parameters.items():
            user_value = configuration_json.get(key, default_value)
            if validators[key](user_value):
                final_parameters[key] = user_value
            else:
                self.notifier.send(
                f"⚠️ Parámetro '{key}' inválido",
                f"'{user_value}' no es válido. Se usará el valor por defecto '{default_value}'.",
                5
                )
                final_parameters[key] = default_value

        return final_parameters