from typing import List, Tuple

import numpy as np

from ...source.repositories.source_repository import SourceRepository


class SourceBuilder:

    @staticmethod
    def build_numeric_data(id_source: int) -> Tuple[np.ndarray, List[int], List[int]]:
        """
        Devuelve tres listas:
        - Una lista de características numéricas por punto.
        - Una lista de los IDs de los puntos.
        - Una lista de los IDs de las características.
        """
        # Crear el repositorio dentro del método
        source_repository = SourceRepository()

        # Obtener los datos numéricos usando el repositorio
        data, features = source_repository.get_numeric_data(id_source)

        # Extraer las características numéricas por punto
        point_features = np.array([row['features'] for row in data]) 
        
        # Obtener los IDs de los puntos
        point_ids = [row['id_point'] for row in data]
        
        # Obtener los nombres de los puntos
        point_names = [row['name'] for row in data]

        # Obtener los IDs de las características
        feature_ids = [row['id_feature'] for row in features]

        return point_features, point_ids, feature_ids, point_names
    
    @staticmethod
    def build_numeric_data_with_numeric_target(id_source: int) -> Tuple[np.ndarray, np.ndarray, List[int]]:
        """
        Devuelve:
        - X: matriz de características (sin la variable objetivo)
        - y: vector objetivo numérico
        - feature_ids: lista de id_feature (sin el target)
        """
        source_repository = SourceRepository()
        data, features = source_repository.get_numeric_data_with_target(id_source)

        # Obtener la matriz de características
        X = np.array([row['features'] for row in data])

        # Obtener la variable objetivo
        y = np.array([row['target'] for row in data], dtype=float)

        # Obtener los ids de las características excluyendo el target
        feature_ids = [f['id_feature'] for f in features]

        return X, y, feature_ids
    
    @staticmethod
    def build_numeric_data_with_binary_target(id_source: int) -> Tuple[np.ndarray, np.ndarray, List[int]]:
        """
        Devuelve:
        - X: matriz de características (sin la variable objetivo)
        - y: vector objetivo binario (0 y 1)
        - feature_ids: lista de id_feature (sin el target)
        """
        source_repository = SourceRepository()
        data, features = source_repository.get_numeric_data_with_target(id_source)

        # Obtener las características
        X = np.array([row['features'] for row in data])

        # Obtener el target (que está en un campo separado)
        y = np.array([row['target'] for row in data])

        # Verificar si la variable objetivo es binaria
        unique_values = np.unique(y)
        if unique_values.shape[0] != 2:
            raise ValueError(f"La variable objetivo no es binaria. Valores únicos encontrados: {unique_values}")

        # Conversión a 0 y 1 si no lo son
        if not np.array_equal(unique_values, [0, 1]):
            y = np.where(y == unique_values[0], 0, 1)

        # Obtener los ids de las características sin incluir el target
        feature_ids = [f['id_feature'] for f in features]

        return X, y, feature_ids