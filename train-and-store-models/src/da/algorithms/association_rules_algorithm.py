import logging

import numpy as np
import pandas as pd

from src.da.core.controller import Controller
from src.da.repositories.manager_repository import ManagerRepository


class AssociationRulesAlgorithm:
    def __init__(self):
        self.manager_repo = ManagerRepository()
        self.controlador = Controller()
        
    def execute(self, tarea):
        """Ejecuta el algoritmo de reglas de asociación"""
        try:
            # 1. Obtener datos del repositorio
            data, features = self.manager_repo.get_association_rule_repository().get_binary_data(tarea.id_source)

            # 2. Crear DataFrame con columnas _1 (presencia) y _0 (ausencia)
            df = pd.DataFrame()
            column_names = [f['name'] for f in features]
            binary_data = np.array(data)  # Asume que data es una lista de listas o array

            ## Columnas _1 (presencia)
            df_1 = pd.DataFrame(binary_data, columns=[f"{name}_1" for name in column_names])
            ## Columnas _0 (ausencia)
            df_0 = pd.DataFrame(1 - binary_data, columns=[f"{name}_0" for name in column_names])
        
            ## Combinar ambos DataFrames
            df = pd.concat([df_1, df_0], axis=1)

            # 3. Preparar los parámetros
            parameters = tarea.parameters if hasattr(tarea, 'parameters') else {}

            ## Valores por defecto 
            min_support = float(parameters.get("min_support", 0.1))  # 0.1 si no existe
            min_confidence = float(parameters.get("min_confidence", 0.7))  # 0.7 si no existe

            ### Validar valores de los parámetros
            #### min_support 
            if not (0.0 < float(min_support) < 1.0):
                raise ValueError("'min_support' debe estar entre 0 y 1")
            
            #### min_confidence 
            if not (0.0 < float(min_confidence) < 1.0):
                raise ValueError("'min_confidence' debe estar entre 0 y 1")

            # 4. Ejecutar entrenamiento y almacenamiento de las reglas
            return self.controlador.train_and_store_rules(
                id_source=tarea.id_source, datos=df, min_support= min_support, 
                min_confidence= min_confidence, parameters=parameters
            )

        except Exception as e:
            logging.error(f"Error en execute_algorithm_rule: {str(e)}")
            raise
     
    def delete(self, id_model: int):
        self.manager_repo.get_association_rule_repository().delete_by_model(id_model)
        self.manager_repo.get_index_repository().delete(id_model)