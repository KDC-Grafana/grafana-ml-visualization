from typing import List, Tuple

import numpy as np

from ...crc.repositories.repository import Repository
from ...exceptions.exceptions import (NoTargetException,
                                      NotEnoughVariablesException,
                                      SourceNotFoundException)
from ..entities.source_entity import Source


class SourceRepository(Repository[Source]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> Source:
        """Obtiene un Source por su ID."""
        with self.connect() as cursor:
            cursor.execute(
                "SELECT name, source, creator, description, id FROM grafana_ml_model_source WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe source con id {id}")
            return Source(*row)

    def get_all(self) -> List[Source]:
        """Obtiene todos los Sources."""
        with self.connect() as cursor:
            cursor.execute("SELECT name, source, creator, description, id FROM grafana_ml_model_source")
            return [Source(*row) for row in cursor.fetchall()]

    def add(self, item: Source) -> None:
        """Agrega un nuevo Source y actualiza su id con el valor generado por la base de datos."""
        with self.connect() as cursor:
            cursor.execute(
                """
                INSERT INTO grafana_ml_model_source (name, source, creator, description)
                VALUES (%s, %s, %s, %s) RETURNING id
                """,
                (item.name, item.source, item.creator, item.description)
            )
            item.id = cursor.fetchone()[0]
        
    def update(self, id: int, **kwargs: object) -> None:
        """Actualiza un Source por su ID."""
        allowed = ["name", "source", "creator", "description"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id)
        with self.connect() as cursor:
            cursor.execute(
                f"UPDATE grafana_ml_model_source SET {', '.join(fields)} WHERE id = %s",
                tuple(values)
            )

    def delete(self, id: int) -> None:
        """Elimina un Source por su ID."""
        with self.connect(autocommit=False) as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_source WHERE id = %s", (id,))
    
    def get_numeric_data(self, id_source: int) -> Tuple[List[dict], List[dict]]:
        with self.connect() as cursor:
            # Verificar si existe la fuente
            cursor.execute("SELECT 1 FROM grafana_ml_model_source WHERE id = %s", (id_source,))
            if cursor.fetchone() is None:
                raise SourceNotFoundException(f"No existe la fuente con id {id_source}.")
        
            # Obtener valores numéricos por punto
            cursor.execute("""
                SELECT
                    pv.id_point,
                    p.name,
                    array_agg(pv.numeric_value ORDER BY f.id) AS features
                FROM grafana_ml_model_point_value pv
                JOIN grafana_ml_model_feature f ON pv.id_feature = f.id
                JOIN grafana_ml_model_point p ON p.id = pv.id_point
                WHERE pv.id_source = %s AND pv.numeric_value IS NOT NULL
                GROUP BY pv.id_point, p.name
                ORDER BY pv.id_point
            """, (id_source,))
            data = [{'id_point': row[0], 'name': row[1], 'features': row[2]} for row in cursor.fetchall()]

            # Obtener características numéricas 
            cursor.execute("""
                SELECT DISTINCT f.id, f.name
                FROM grafana_ml_model_feature f
                JOIN grafana_ml_model_point_value pv ON f.id = pv.id_feature
                WHERE f.id_source = %s AND pv.numeric_value IS NOT NULL
                ORDER BY f.id
            """, (id_source,))
            features = [{'id_feature': row[0], 'name': row[1]} for row in cursor.fetchall()]

        if len(features) < 2:
            raise NotEnoughVariablesException("Se requieren al menos dos características numéricas para ejecutar el algoritmo.")

        return data, features
    
    def get_numeric_data_with_numeric_target(self, id_source: int) -> Tuple[List[dict], List[dict]]:
        with self.connect() as cursor:
            # Verificar si existe la fuente
            cursor.execute("SELECT 1 FROM grafana_ml_model_source WHERE id = %s", (id_source,))
            if cursor.fetchone() is None:
                raise SourceNotFoundException(f"No existe la fuente con id {id_source}.")
            
            # Obtener características numéricas
            cursor.execute("""
                SELECT DISTINCT f.id, f.name, f.is_target
                FROM grafana_ml_model_feature f
                JOIN grafana_ml_model_point_value pv ON f.id = pv.id_feature
                WHERE f.id_source = %s AND pv.numeric_value IS NOT NULL
                ORDER BY f.id
            """, (id_source,))
            features = [{'id_feature': f[0], 'name': f[1], 'is_target': f[2]} for f in cursor.fetchall()]

            if not any(f['is_target'] for f in features):
                raise NoTargetException("No se encontró una variable objetivo numérica en las características.")
            if not any(not f['is_target'] for f in features):
                raise NotEnoughVariablesException("Se requiere al menos una característica numérica para ejecutar el algoritmo.")

            # Obtener valores por punto, incluyendo el target
            cursor.execute("""
                SELECT
                    pv.id_point,
                    array_agg(pv.numeric_value ORDER BY f.id) AS features,
                    MAX(pv.numeric_value) FILTER (WHERE f.is_target) AS target_numeric
                FROM grafana_ml_model_point_value pv
                JOIN grafana_ml_model_feature f ON pv.id_feature = f.id
                WHERE pv.id_source = %s AND pv.numeric_value IS NOT NULL
                GROUP BY pv.id_point
                ORDER BY pv.id_point
            """, (id_source,))
            data = [
                {'id_point': row[0], 'features': row[1], 'target': row[2]}
                for row in cursor.fetchall()
            ]
            
        features = [f for f in features if not f['is_target']]

        return data, features
        
    def get_numeric_data_with_target(self, id_source: int) -> Tuple[List[dict], List[dict]]:
        with self.connect() as cursor:
            # Verificar si existe la fuente
            cursor.execute("SELECT 1 FROM grafana_ml_model_source WHERE id = %s", (id_source,))
            if cursor.fetchone() is None:
                raise SourceNotFoundException(f"No existe la fuente con id {id_source}.")
            
            # Obtener metadatos de características
            cursor.execute("""
                SELECT id, name, is_target
                FROM grafana_ml_model_feature
                WHERE id_source = %s
                ORDER BY id
            """, (id_source,))
            features = [{'id_feature': row[0], 'name': row[1], 'is_target': row[2]} for row in cursor.fetchall()]
            
            if not any(not f['is_target'] for f in features):
                raise NotEnoughVariablesException("Se requiere al menos una característica numérica para ejecutar el algoritmo.")
            if not any(f['is_target'] for f in features):
                raise NoTargetException("No se encontró una variable objetivo en las características.")

            # Obtener valores por punto
            cursor.execute("""
                SELECT
                    pv.id_point,
                    array_agg(pv.numeric_value ORDER BY f.id) FILTER (WHERE NOT f.is_target) AS numeric_features,
                    MAX(pv.numeric_value) FILTER (WHERE f.is_target) AS target_numeric,
                    MAX(pv.string_value) FILTER (WHERE f.is_target) AS target_string
                FROM grafana_ml_model_point_value pv
                JOIN grafana_ml_model_feature f ON pv.id_feature = f.id
                WHERE pv.id_source = %s
                GROUP BY pv.id_point
                ORDER BY pv.id_point
            """, (id_source,))
            data = [
                {'id_point': row[0], 'features': row[1], 'target': row[2] if row[2] is not None else row[3]}
                for row in cursor.fetchall()
            ]
            
        features = [f for f in features if not f['is_target']]

        return data, features

    def get_data_for_classification(self, id_source: int) -> Tuple[np.ndarray, np.ndarray, List[dict], List[dict]]:
        with self.connect() as cursor:
            # Verificar si existe la fuente
            cursor.execute("SELECT 1 FROM grafana_ml_model_source WHERE id = %s", (id_source,))
            if cursor.fetchone() is None:
                raise SourceNotFoundException(f"No existe la fuente con id {id_source}.")
            
            # Obtener características 
            cursor.execute("""
                SELECT id, name, is_target
                FROM grafana_ml_model_feature
                WHERE id_source = %s
                ORDER BY id
            """, (id_source,))
        
            rows = cursor.fetchall()
            features = []
            target_id = None
            for id, name, is_target in rows:
                if is_target:
                    target_id = id
                else:
                    features.append({'id_feature': id, 'name': name})

            if target_id is None:
                raise ValueError("No se encontró una variable objetivo.")

            # Determinar el tipo de la variable objetivo
            cursor.execute("""
                SELECT DISTINCT numeric_value, string_value
                FROM grafana_ml_model_point_value
                WHERE id_source = %s AND id_feature = %s
            """, (id_source, target_id))
            
            values = cursor.fetchall()
            numeric_values = {v[0] for v in values if v[0] is not None}
            string_values = {v[1] for v in values if v[1] is not None}

            if not string_values and len(numeric_values) != 2:
                raise ValueError("La variable objetivo debe ser categórica o numérica binaria.")

            # Obtener datos: características numéricas + objetivo
            cursor.execute("""
                SELECT
                    pv.id_point,
                    array_agg(pv.numeric_value ORDER BY f.id) FILTER (WHERE NOT f.is_target) AS numeric_features,
                    MAX(COALESCE(pv.string_value, pv.numeric_value::text)) FILTER (WHERE f.id = %s) AS target_value
                FROM grafana_ml_model_point_value pv
                JOIN grafana_ml_model_feature f ON pv.id_feature = f.id
                WHERE pv.id_source = %s
                GROUP BY pv.id_point
                ORDER BY pv.id_point
            """, (target_id, id_source))
            
            rows = cursor.fetchall()
            X = np.array([row[1] for row in rows])
            y = np.array([row[2] for row in rows])

            # Obtener lista de clases 
            cursor.execute("""
                SELECT id_prediction AS id, class_name AS name
                FROM grafana_ml_model_prediction_values
                WHERE id_source = %s
                ORDER BY id_prediction
            """, (id_source,))
            class_list = [{'id_prediction': row[0], 'name': row[1]} for row in cursor.fetchall()]

            return X, y, features, class_list

    def get_binary_data(self, id_source: int) -> Tuple[np.ndarray, List[dict]]:
        with self.connect() as cursor:
            # Verificar si existe la fuente
            cursor.execute("SELECT 1 FROM grafana_ml_model_source WHERE id = %s", (id_source,))
            if cursor.fetchone() is None:
                raise SourceNotFoundException(f"No existe la fuente con id {id_source}.")
            
            # Consulta para obtener las características numéricas por punto
            cursor.execute("""
                SELECT
                    array_agg(pv.numeric_value ORDER BY f.id) AS features
                FROM grafana_ml_model_point_value pv
                JOIN grafana_ml_model_feature f ON pv.id_feature = f.id
                WHERE pv.id_source = %s AND pv.numeric_value IS NOT NULL
                GROUP BY pv.id_point
                ORDER BY pv.id_point
            """, (id_source,))
            features_by_point = cursor.fetchall()

            # Consulta para obtener los nombres de las características
            cursor.execute("""
                SELECT id, name
                FROM grafana_ml_model_feature
                WHERE id_source = %s AND id IN (
                    SELECT DISTINCT id_feature
                    FROM grafana_ml_model_point_value
                    WHERE id_source = %s AND numeric_value IS NOT NULL
                )
                ORDER BY id
            """, (id_source, id_source))
            feature_names = cursor.fetchall()
            
        features_by_point = [list(row[0]) for row in features_by_point]

        # Filtrar características binarias (que solo tienen valores 0 y 1)
        binary_features_by_point = []
        binary_feature_names = []

        for col_idx in range(len(features_by_point[0])):
            column_values = [row[col_idx] for row in features_by_point]  # Extraer la columna

            if all(value in [0, 1] for value in column_values):
                binary_features_by_point.append([row[col_idx] for row in features_by_point])  
                binary_feature_names.append(feature_names[col_idx])

        # Comprobar si hay al menos 2 características binarias
        if len(binary_feature_names) < 2:
            raise NotEnoughVariablesException("Se requieren al menos dos características binarias para ejecutar el algoritmo.")

        data = np.array(binary_features_by_point).T  # Transponer los datos para tener puntos como filas
        features = [
            {'id_feature': row[0], 'name': row[1]}
            for row in binary_feature_names
        ]

        return data, features





