import json
from typing import Dict

import statsmodels.api as sm

from ...task.task_entity import TaskCreateModel
from ..entities.index_entity import ModelIndex
from ..entities.regression_entity import Regression
from ..repositories.model_index_repository import ModelIndexRepository
from ..repositories.regression_repository import RegressionRepository
from ..source_builder.source_builder import SourceBuilder


class RegressionLinear:
    def __init__(self):
        self.model_index_repo = ModelIndexRepository()
        self.regression_repo = RegressionRepository()

    def execute(self, task: TaskCreateModel) -> int:
        # Cargar datos: X sin el target, y es el target
        X, y, feature_ids = SourceBuilder.build_numeric_data_with_numeric_target(task.id_source)

        # Añadir constante (intercepto)
        X = sm.add_constant(X)

        # Guardar el modelo en la tabla index
        params = {}
        id_model = self._save_model(task.id_source, params)

        # Ajustar modelo OLS
        model = sm.OLS(y, X).fit()

        # Coeficientes: primero el intercepto
        coeffs = model.params
        std_errs = model.bse
        t_values = model.tvalues
        p_values = model.pvalues

        # Guardar el intercepto (id_feature = None)
        intercept = Regression(
            id_model=id_model,
            id_feature=None,
            coeff=float(coeffs[0]),
            std_err=float(std_errs[0]),
            value=float(t_values[0]),
            p_value=float(p_values[0])
        )
        self.regression_repo.add(intercept)

        # Guardar los coeficientes de las características
        for i, id_feature in enumerate(feature_ids):
            regression = Regression(
                id_model=id_model,
                id_feature=id_feature,
                coeff=float(coeffs[i + 1]),
                std_err=float(std_errs[i + 1]),
                value=float(t_values[i + 1]),
                p_value=float(p_values[i + 1])
            )
            self.regression_repo.add(regression)
            
        return id_model

    def delete(self, id_model: int) -> None:
        self.regression_repo.delete_by_model(id_model)
        self.model_index_repo.delete(id_model)

    def _save_model(self, id_source: int, parameters: Dict) -> int:
        parameters_json = json.dumps(parameters)
        model = ModelIndex(
            id_source=id_source,
            algorithm="r_lineal",
            parameters=parameters_json
        )
        self.model_index_repo.add(model)
        return model.id

