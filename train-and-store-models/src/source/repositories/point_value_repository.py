from typing import List

from ...crc.repositories.repository import Repository
from ..entities.point_value_entity import PointValue


class PointValueRepository(Repository[PointValue]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id_point: int, id_feature: int) -> PointValue:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_source, id_point, id_feature, numeric_value, string_value FROM grafana_ml_model_point_value WHERE id_point = %s AND id_feature = %s",
                (id_point, id_feature)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe point value con id_point {id_point} y id_feature {id_feature}")
            return PointValue(*row)

    def get_all(self) -> List[PointValue]:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_source, id_point, id_feature, numeric_value, string_value FROM grafana_ml_model_point_value"
            )
            return [PointValue(*row) for row in cursor.fetchall()]

    def add(self, item: PointValue) -> None:
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_point_value (id_source, id_point, id_feature, numeric_value, string_value) VALUES (%s, %s, %s, %s, %s)",
                (item.id_source, item.id_point, item.id_feature, item.numeric_value, item.string_value)
            )

    def update(self, id_point: int, id_feature: int, **kwargs: object) -> None:
        allowed = ["id_source", "id_point", "id_feature", "numeric_value", "string_value"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id_point)
        values.append(id_feature)
        with self.connect() as cursor:
            cursor.execute(
                f"UPDATE grafana_ml_model_point_value SET {', '.join(fields)} WHERE id_point = %s AND id_feature = %s",
                tuple(values)
            )

    def delete(self, id_point: int, id_feature: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_point_value WHERE id_point = %s AND id_feature = %s", 
                           (id_point, id_feature))
            
    def delete_by_source(self, source_id: int) -> None:
        """Elimina todos los valores de punto asociados a un id_source."""
        with self.connect(autocommit=False) as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_point_value WHERE id_source = %s", (source_id,))
                

    