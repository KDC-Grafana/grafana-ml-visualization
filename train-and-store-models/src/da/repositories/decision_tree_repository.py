from typing import List, Tuple

import numpy as np

from src.da.entities.decision_tree_entity import DecisionTreeNode
from src.da.repositories.base_repository import BaseRepository

from ...exceptions.exceptions import SourceNotFoundException


class DecisionTreeRepository(BaseRepository[DecisionTreeNode]):
    def __init__(self) -> None:
        super().__init__()

    def create(self, entity: DecisionTreeNode) -> DecisionTreeNode:
        """Agrega un nuevo DecisionTreeNode y actualiza su id."""
        with self.connect() as cursor:
            cursor.execute(
                """
                INSERT INTO grafana_ml_model_decision_tree 
                (id_model, parent_node, feature, threshold, left_node, right_node, is_leaf, prediction_value)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_node
                """,
                (
                    entity.id_model,
                    entity.parent_node,
                    entity.feature,
                    entity.threshold,
                    entity.left_node,
                    entity.right_node,
                    entity.is_leaf,
                    entity.prediction_value,
                )
            )
            entity.id_node = cursor.fetchone()[0]
        return entity.id_node

    def get(self, id_node: int) -> DecisionTreeNode:
        """Obtiene un DecisionTreeNode por su id."""
        with self.connect() as cursor:
            cursor.execute(
                """
                SELECT id_model, id_node, parent_node, feature, threshold, left_node, right_node, is_leaf, prediction_value
                FROM grafana_ml_model_decision_tree 
                WHERE id_node = %s
                """,
                (id_node,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe nodo con id {id_node}")
            return DecisionTreeNode(*row)

    def update(self, id_node: int, **kwargs: object) -> DecisionTreeNode:
        """Actualiza campos de un DecisionTreeNode."""
        allowed = ["id_model", "parent_node", "feature", "threshold", "left_node", "right_node", "is_leaf", "prediction_value"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id_node)
        with self.connect() as cursor:
            cursor.execute(
                f"""
                UPDATE grafana_ml_model_decision_tree
                SET {', '.join(fields)}
                WHERE id_node = %s
                """,
                tuple(values)
            )
        return self.get(id_node)

    def delete(self, id_node: int) -> None:
        """Elimina un DecisionTreeNode por su id."""
        with self.connect() as cursor:
            cursor.execute(
                "DELETE FROM grafana_ml_model_decision_tree WHERE id_node = %s",
                (id_node,)
            )

    def delete_by_model(self, id_model: int) -> None:
        """Elimina todos los DecisionTreeNodes asociados a un id_model."""
        with self.connect() as cursor:
            cursor.execute(
                "DELETE FROM grafana_ml_model_decision_tree WHERE id_model = %s",
                (id_model,)
            )

    def list(self) -> List[DecisionTreeNode]:
        """Lista todos los DecisionTreeNode."""
        with self.connect() as cursor:
            cursor.execute(
                """
                SELECT id_model, id_node, parent_node, feature, threshold, left_node, right_node, is_leaf, prediction_value
                FROM grafana_ml_model_decision_tree
                """
            )
            return [DecisionTreeNode(*row) for row in cursor.fetchall()]
        
    def update_node_relations(self, id_node: int, parent_node: int, left_node: int, right_node: int) -> None:
        """Actualizar relaciones de un nodo en la tabla."""
        with self.connect() as cursor:
            cursor.execute(
                """
                UPDATE grafana_ml_model_decision_tree
                SET parent_node = %s, left_node = %s, right_node = %s
                WHERE id_node = %s
                """,
                (parent_node, left_node, right_node, id_node)
            )

    def update_id_model(self, id_node: int, id_model: int) -> None:
        """Asigna un id_model a un nodo existente del árbol de decisión."""
        with self.connect() as cursor:
            cursor.execute(
                """
                UPDATE grafana_ml_model_decision_tree
                SET id_model = %s
                WHERE id_node = %s
                """,
                (id_model, id_node)
            )

    def get_feature_id(self, id_source: int, name: str) -> int:
        """Devuelve el ID de una característica a partir de su nombre y fuente de datos."""
        with self.connect() as cursor:
            cursor.execute(
                """
                SELECT id
                FROM grafana_ml_model_feature
                WHERE id_source = %s AND name = %s
                """,
                (id_source, name)
            )
            result = cursor.fetchone()
            return result[0] if result else None

    def get_prediction_value_id(self, id_source: int, class_name: str) -> int:
        """Devuelve el ID de un valor de predicción a partir de su nombre de clase y fuente de datos."""
        with self.connect() as cursor:
            cursor.execute(
                """
                SELECT id_prediction
                FROM grafana_ml_model_prediction_values
                WHERE id_source = %s AND class_name = %s
                """,
                (id_source, class_name)
            )
            result = cursor.fetchone()
            return result[0] if result else None
    
    def get_data(self, id_source: int) -> Tuple[np.ndarray, np.ndarray, List[dict], List[dict]]:
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