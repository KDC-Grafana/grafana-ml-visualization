import json
from typing import Dict, List, Tuple

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_samples

from ...notifications.notifier import Notifier
from ...task.task_entity import TaskCreateModel
from ..entities.clustering_cluster_entity import ClusteringCluster
from ..entities.clustering_metrics_entity import ClusteringMetrics
from ..entities.index_entity import ModelIndex
from ..entities.kmeans_centroid_entity import KMeansCentroid
from ..entities.kmeans_point_entity import KMeansPoint
from ..repositories.clustering_cluster_repository import \
    ClusteringClusterRepository
from ..repositories.clustering_metrics_repository import \
    ClusteringMetricsRepository
from ..repositories.kmeans_centroid_repository import KMeansCentroidRepository
from ..repositories.kmeans_point_repository import KMeansPointRepository
from ..repositories.model_index_repository import ModelIndexRepository
from ..source_builder.source_builder import SourceBuilder


class ClusteringKMeans:
    def __init__(self):
        self.model_index_repo = ModelIndexRepository()
        self.clustering_cluster_repo = ClusteringClusterRepository()
        self.kmeans_point_repo = KMeansPointRepository()
        self.kmeans_centroid_repo = KMeansCentroidRepository()
        self.clustering_metrics_repo = ClusteringMetricsRepository()
        self.notifier = Notifier()

    def execute(self, task: TaskCreateModel) -> int:
        # Cargar los puntos y metadatos
        points, point_ids, feature_ids, _ = SourceBuilder.build_numeric_data(task.id_source)
        
        params =  self._get_parameters(task.parameters) 
    
        # Guardar nuevo modelo  
        id_model = self._save_model(task.id_source, params)

        # Entrenar modelo KMeans
        kmeans = KMeans(**params, random_state=42)
        kmeans.fit(points)
        
        # Guardar clusters individuales y recolectar métricas
        total_inertia, total_silhouette, cluster_id_map = self._save_clusters(id_model, kmeans, points)

        # Guardar asignaciones de puntos
        self._save_point_assignments(id_model, kmeans.labels_, point_ids, cluster_id_map)

        # Guardar centroides 
        self._save_centroids(id_model, kmeans, feature_ids, cluster_id_map)

        # Guardar métricas globales
        self._save_clustering_metrics(id_model, total_inertia, total_silhouette, params['n_clusters'], kmeans, points)
        
        return id_model
        
    def delete(self, id_model: int) -> None:
        self.kmeans_point_repo.delete_by_model(id_model)
        self.kmeans_centroid_repo.delete_by_model(id_model)
        self.clustering_cluster_repo.delete_by_model(id_model)
        self.clustering_metrics_repo.delete_by_model(id_model)
        self.model_index_repo.delete(id_model)

    def _save_model(self, id_source: int, parameters: Dict) -> int:
        parameters_json = json.dumps(parameters) 
        model = ModelIndex(
            id_source=id_source,
            algorithm="a_kmedias",
            parameters=parameters_json 
        )
        self.model_index_repo.add(model)
        return model.id

    def _save_centroids(self, id_model: int, kmeans: KMeans, feature_ids: List[int], cluster_id_map: dict) -> None:
        for i, center in enumerate(kmeans.cluster_centers_):
            cluster_id = cluster_id_map[i]
            for j, value in enumerate(center):
                centroid = KMeansCentroid(
                    id_model=id_model,
                    id_cluster=cluster_id,
                    id_feature=feature_ids[j],
                    value=float(value)
                )
                self.kmeans_centroid_repo.add(centroid)

    def _save_point_assignments(self, id_model: int, labels: np.ndarray, point_ids: List[int], cluster_id_map: dict) -> None:
        for point_id, cluster_number in zip(point_ids, labels):
            point = KMeansPoint(
                id_model=id_model,
                id_point=point_id,
                id_cluster=cluster_id_map[int(cluster_number)] 
            )
            self.kmeans_point_repo.add(point)
            
    def _save_clusters(self, id_model: int, kmeans: KMeans, points: np.ndarray) -> Tuple[float, float, dict]:
        total_inertia = 0.0
        total_silhouette = 0.0
        labels = kmeans.labels_
        sample_silhouette = silhouette_samples(points, labels)
        
        cluster_id_map = {}  # Para mapear number -> id real en DB

        for i in range(kmeans.n_clusters):
            cluster_mask = labels == i
            cluster_points = points[cluster_mask]
            center = kmeans.cluster_centers_[i]

            inertia_i = np.sum(np.linalg.norm(cluster_points - center, axis=1) ** 2)
            silhouette_i = float(np.mean(sample_silhouette[cluster_mask])) if len(cluster_points) >= 2 else 0.0

            cluster = ClusteringCluster(
                id_model=id_model,
                number=i,
                inertia=inertia_i,
                silhouette_coefficient=silhouette_i
            )
            self.clustering_cluster_repo.add(cluster)
            cluster_id_map[i] = cluster.id 

            total_inertia += inertia_i
            total_silhouette += silhouette_i

        return total_inertia, total_silhouette, cluster_id_map

    def _save_clustering_metrics(self, id_model: int, total_inertia: float, total_silhouette: float,
                                 n_clusters: int, kmeans: KMeans, points: np.ndarray) -> None:
        silhouette_avg = total_silhouette / n_clusters
        db_index = float(davies_bouldin_score(points, kmeans.labels_))

        metrics = ClusteringMetrics(
            id_model=id_model,
            inertia=total_inertia,
            silhouette_coefficient=silhouette_avg,
            davies_bouldin_index=db_index
        )
        self.clustering_metrics_repo.add(metrics)

    def _get_parameters(self, configuration_json):
        default_parameters = {
            "n_clusters": 3,
            "init": "k-means++",    # "k-means++" o "random"
            "algorithm": "lloyd",   # "lloyd" o "elkan"
            "n_init": "auto"        # valor por defecto para evitar warning
        }

        # Validadores para cada parámetro
        def is_valid_n_clusters(v):
            return isinstance(v, int) and v > 0

        def is_valid_init(v):
            return v in ["k-means++", "random"]

        def is_valid_algorithm(v):
            return v in ["lloyd", "elkan"]

        def is_valid_n_init(v):
            # n_init puede ser 'auto' o un entero positivo
            return v == 'auto' or (isinstance(v, int) and v > 0)

        validators = {
            "n_clusters": is_valid_n_clusters,
            "init": is_valid_init,
            "algorithm": is_valid_algorithm,
            "n_init": is_valid_n_init
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