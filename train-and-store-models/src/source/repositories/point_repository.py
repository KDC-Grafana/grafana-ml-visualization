from typing import List

from psycopg2.errors import ForeignKeyViolation

from ...crc.repositories.repository import Repository
from ..entities.point_entity import Point


class PointRepository(Repository[Point]):
    def __init__(self) -> None:
        super().__init__()

    def get(self, id: int) -> Point:
        with self.connect() as cursor:
            cursor.execute(
                "SELECT id_source, name, id FROM grafana_ml_model_point WHERE id = %s",
                (id,)
            )
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"No existe point con id {id}")
            return Point(*row)

    def get_all(self) -> List[Point]:
        with self.connect() as cursor:
            cursor.execute("SELECT id_source, name, id FROM grafana_ml_model_point")
            return [Point(*row) for row in cursor.fetchall()]

    def add(self, item: Point) -> None:
        """Agrega un nuevo Point y actualiza su id."""
        with self.connect() as cursor:
            cursor.execute(
                "INSERT INTO grafana_ml_model_point (id_source, name) VALUES (%s, %s) RETURNING id",
                (item.id_source, item.name)
            )
            item.id = cursor.fetchone()[0]
            
    def update(self, id: int, **kwargs: object) -> None:
        allowed = ["id_source", "name"]
        fields = [f"{k} = %s" for k in allowed if k in kwargs]
        values = [kwargs[k] for k in allowed if k in kwargs]
        if not fields:
            raise ValueError("No se proporcionaron campos para actualizar.")
        values.append(id)
        with self.connect() as cursor:
            cursor.execute(
                f"UPDATE grafana_ml_model_point SET {', '.join(fields)} WHERE id = %s",
                tuple(values)
            )

    def delete(self, id: int) -> None:
        with self.connect() as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_point WHERE id = %s", (id,))
            
    def delete_by_source(self, source_id: int) -> None:
        """Elimina todos los puntos asociados a un id_source."""
        with self.connect(autocommit=False) as cursor:
            cursor.execute("DELETE FROM grafana_ml_model_point WHERE id_source = %s", (source_id,))

        