from typing import List, Tuple

import numpy as np

from src.da.entities.association_rule_entity import AssociationRule
from src.da.repositories.base_repository import BaseRepository

from ...exceptions.exceptions import NotEnoughVariablesException, SourceNotFoundException


class AssociationRuleRepository(BaseRepository[AssociationRule]):
    def __init__(self) -> None:
        super().__init__()

    def create(self, item: AssociationRule) -> AssociationRule:
        """Agrega una nueva AssociationRule y actualiza su id."""
        with self.connect() as cursor:
            cursor.execute(
                """
                INSERT INTO grafana_ml_model_association_rules
                (id_model, antecedent, consequent, support, confidence, lift)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    item.id_model,
                    item.antecedent,
                    item.consequent,
                    item.support,
                    item.confidence,
                    item.lift,
                )
            )
            item.id = cursor.fetchone()[0]
        return item

    def get(self, id: int) -> AssociationRule:
        """Obtiene una AssociationRule por su id."""
        with self.connect() as cursor:
            cursor.execute(
                """
                SELECT id_model, id, antecedent, consequent, support, confidence, lift
                FROM grafana_ml_model_association_rules
                WHERE id = %s
                """,
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe AssociationRule con id {id}")
            return AssociationRule(*row)

    def update(self, id: int, **kwargs: object) -> None:
        """Actualiza campos de una AssociationRule."""
        allowed = ["id_model", "antecedent", "consequent", "support", "confidence", "lift"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id)
        with self.connect() as cursor:
            cursor.execute(
                f"""
                UPDATE grafana_ml_model_association_rules
                SET {', '.join(fields)}
                WHERE id = %s
                """,
                tuple(values)
            )

    def delete(self, id: int) -> None:
        """Elimina una AssociationRule por su id."""
        with self.connect() as cursor:
            cursor.execute(
                "DELETE FROM grafana_ml_model_association_rules WHERE id = %s",
                (id,)
            )

    def delete_by_model(self, id_model: int) -> None:
        """Elimina todas las AssociationRules asociadas a un id_model."""
        with self.connect() as cursor:
            cursor.execute(
                "DELETE FROM grafana_ml_model_association_rules WHERE id_model = %s",
                (id_model,)
            )

    def list(self) -> List[AssociationRule]:
        """Lista todas las AssociationRules."""
        with self.connect() as cursor:
            cursor.execute(
                """
                SELECT id_model, id, antecedent, consequent, support, confidence, lift
                FROM grafana_ml_model_association_rules
                """
            )
            return [AssociationRule(*row) for row in cursor.fetchall()]
        
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