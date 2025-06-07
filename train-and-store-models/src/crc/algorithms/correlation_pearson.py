import json
from typing import Dict

import numpy as np
import scipy.stats as stats

from ...task.task_entity import TaskCreateModel
from ..entities.correlation_entity import Correlation
from ..entities.index_entity import ModelIndex
from ..repositories.correlation_repository import CorrelationRepository
from ..repositories.model_index_repository import ModelIndexRepository
from ..source_builder.source_builder import SourceBuilder


class CorrelationPearson:
    def __init__(self):
        self.model_index_repo = ModelIndexRepository()
        self.correlation_repo = CorrelationRepository()

    def execute(self, task: TaskCreateModel) -> int:
        # Obtener los puntos (matriz) y las características
        points, _, feature_ids, _ = SourceBuilder.build_numeric_data(task.id_source)
        points = np.array(points)

        # Guardar modelo
        params = {}
        id_model = self._save_model(task.id_source, params)

        # Calcular correlación para cada par de características
        n = len(feature_ids)
        for i in range(n):
            for j in range(i + 1, n):
                coef, _ = stats.pearsonr(points[:, i], points[:, j])
                correlation = Correlation(
                    id_model=id_model,
                    id_feature1=feature_ids[i],
                    id_feature2=feature_ids[j],
                    value=float(coef),
                )
                self.correlation_repo.add(correlation)
                
        return id_model        

    def _save_model(self, id_source: int, parameters: Dict) -> int:
        parameters_json = json.dumps(parameters)
        model = ModelIndex(
            id_source=id_source,
            algorithm="c_pearson",
            parameters=parameters_json
        )
        self.model_index_repo.add(model)
        return model.id

    def delete(self, id_model: int) -> None:
        self.correlation_repo.delete_by_model(id_model)
        self.model_index_repo.delete(id_model)