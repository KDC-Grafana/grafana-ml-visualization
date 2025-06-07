import json
from typing import Dict

from scipy.cluster.hierarchy import linkage, to_tree

from ...notifications.notifier import Notifier
from ...task.task_entity import TaskCreateModel
from ..entities.clustering_hierarchical_entity import ClusteringHierarchicalE
from ..entities.index_entity import ModelIndex
from ..repositories.clustering_hierarchical_repository import \
    ClusteringHierarchicalRepository
from ..repositories.model_index_repository import ModelIndexRepository
from ..source_builder.source_builder import SourceBuilder


class ClusteringHierarchical:
    def __init__(self):
        self.model_index_repo = ModelIndexRepository()
        self.hierarchical_repo = ClusteringHierarchicalRepository()
        self.notifier = Notifier()

    def execute(self, task: TaskCreateModel) -> int:
        # Cargar los puntos y metadatos
        points, point_ids, _, point_names = SourceBuilder.build_numeric_data(task.id_source)
        
        # Guardar modelo
        params = self._get_parameters(task.parameters) 
        id_model = self._save_model(task.id_source, params)

        # Calcular linkage jerárquico
        Z = linkage(points, **params)

        # Construir árbol y guardar nodos
        root_node, _ = to_tree(Z, rd=True)
        node_map = {}
        self._save_tree(root_node, id_model, point_ids, point_names, node_map)
        
        return id_model
    
    def delete(self, id_model: int) -> None:
        # Eliminar nodos del árbol jerárquico
        self.hierarchical_repo.delete_by_model(id_model)
        # Eliminar entrada del modelo
        self.model_index_repo.delete(id_model)

    def _save_model(self, id_source: int, parameters: Dict) -> int:
        parameters_json = json.dumps(parameters)
        model = ModelIndex(
            id_source=id_source,
            algorithm="a_jerarquico",
            parameters=parameters_json
        )
        self.model_index_repo.add(model)
        return model.id

    def _save_tree(self, node, id_model: int, point_ids: list, point_names: list, node_map: dict, parent_id: int = None) -> int:
        if node.is_leaf():
            id_point = point_ids[node.id]
            name = point_names[node.id]
            height = 0.0
        else:
            id_point = None
            name = f"node_{node.id}"
            height = node.dist

        h_node = ClusteringHierarchicalE(
            id_model=id_model,
            name=name,
            height=height,
            id_parent=parent_id,
            id_point=id_point
        )
        self.hierarchical_repo.add(h_node)
        node_map[node.id] = h_node.id

        if not node.is_leaf():
            self._save_tree(node.get_left(), id_model, point_ids, point_names, node_map, h_node.id)
            self._save_tree(node.get_right(), id_model, point_ids, point_names, node_map, h_node.id)

        return h_node.id
    
    def _get_parameters(self, configuration_json):
        # Valores por defecto con clave 'method' en lugar de 'linkage'
        default_parameters = {
            "metric": "euclidean",    # Métrica de distancia a usar
            "method": "ward"          # Criterio de enlace para linkage()
        }

        # Renombrar 'linkage' a 'method' si aparece en la configuración
        configuration_json = {
            ("method" if k == "linkage" else k): v
            for k, v in configuration_json.items()
        }

        # Validadores para cada parámetro
        def is_valid_metric(v):
            # Puedes ajustar esta lista según las métricas que soporte tu implementación
            return v in ["euclidean", "manhattan", "cosine"]

        def is_valid_method(v):
            # Métodos comunes en linkage
            return v in ["ward", "complete", "average", "single"]

        validators = {
            "metric": is_valid_metric,
            "method": is_valid_method
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