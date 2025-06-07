from ..crc.algorithms.clustering_hierarchical import ClusteringHierarchical
from ..crc.algorithms.clustering_kmeans import ClusteringKMeans
from ..crc.algorithms.clustering_kmedoids import ClusteringKMedoids
from ..crc.algorithms.correlation_pearson import CorrelationPearson
from ..crc.algorithms.correlation_spearman import CorrelationSpearman
from ..crc.algorithms.regression_linear import RegressionLinear
from ..crc.algorithms.regression_logistic import RegressionLogistic
from ..da.algorithms.association_rules_algorithm import \
    AssociationRulesAlgorithm
from ..da.algorithms.decision_tree_algorithm import DecisionTreeAlgorithm
from .task_entity import TaskCreateModel, TaskDeleteModel
from .task_query import TaskQuery


class ModelExecutor:
    def __init__(self):
        self.task_query = TaskQuery()
        self.algorithms = {
            'a_kmedias': ClusteringKMeans(),
            'a_kmedoides': ClusteringKMedoids(),
            'a_jerarquico': ClusteringHierarchical(),
            'c_pearson': CorrelationPearson(),
            'c_spearman': CorrelationSpearman(),
            'r_lineal': RegressionLinear(),
            'r_logistica': RegressionLogistic(),
            'reglas_asociacion': AssociationRulesAlgorithm(),
            'arbol_decision': DecisionTreeAlgorithm()
        }

    def create_model(self, task: TaskCreateModel):
        model = self.algorithms.get(task.algorithm)
        if model:
            return model.execute(task)
        raise ValueError(f"Algoritmo no soportado: {task.algorithm}")

    def delete_model(self, task: TaskDeleteModel):
        algorithm = self.task_query.get_algorithm_by_model_id(task.id_model)
        model = self.algorithms.get(algorithm)
        if model:
            return model.delete(task.id_model)
        raise ValueError(f"Algoritmo no soportado: {algorithm}")