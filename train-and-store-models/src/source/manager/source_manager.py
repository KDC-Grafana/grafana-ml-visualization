import numbers

import numpy as np
from psycopg2.errors import ForeignKeyViolation

from ...database.database_connection import DatabaseConnection
from ...database.unit_of_work import UnitOfWork
from ..entities.feature_entity import Feature
from ..entities.point_entity import Point
from ..entities.point_value_entity import PointValue
from ..entities.prediction_value_entity import PredictionValue
from ..entities.source_entity import Source
from ..repositories.feature_repository import FeatureRepository
from ..repositories.point_repository import PointRepository
from ..repositories.point_value_repository import PointValueRepository
from ..repositories.prediction_value_repository import \
    PredictionValueRepository
from ..repositories.source_repository import SourceRepository
from .table_loader import TableLoader


class SourceManager:
    def __init__(self):
        self.table_loader = TableLoader()
        self.database = DatabaseConnection()
        self.source_repo = SourceRepository()
        self.point_repo = PointRepository()
        self.point_value_repo = PointValueRepository()
        self.feature_repo = FeatureRepository()
        self.prediction_value_repo = PredictionValueRepository()

    def create(self, source_name: str, source_description: str, creator: str, target_column: str, source: str):
        """ Crea una fuente y carga puntos, características y valores desde una tabla. """
        new_source = Source(
            name=source_name,
            source=source,
            description=source_description,
            creator=creator
        )
        self.source_repo.add(new_source)
        source_id = new_source.id

        df = self.table_loader.load_dataframe(source, target_column)

        points = []
        for index in df.index:
            point = Point(id_source=source_id, name=f"point_{index + 1}")
            self.point_repo.add(point)
            points.append(point.id)

        features = []
        for column in df.columns:
            is_target = column == target_column
            feature = Feature(id_source=source_id, name=column, is_target=is_target)
            self.feature_repo.add(feature)
            features.append(feature)

        for i, row in df.iterrows():
                for feature in features:
                    value = row[feature.name]

                    # Convertir a tipo int o float si es un tipo numpy
                    if isinstance(value, (np.integer, np.floating)):
                        value = value.item()  # Convierte numpy.int64, numpy.float64, etc., a un tipo nativo de Python

                    # Determinar si el valor es numérico (incluye tipos de numpy y nativos de Python)
                    if isinstance(value, (numbers.Number)):
                        numeric_value = value
                        string_value = None
                    elif isinstance(value, str):
                        numeric_value = None
                        string_value = value
                    else:
                        # Si el valor no es ni numérico ni cadena, se descarta
                        numeric_value = None
                        string_value = None

                    # Crear el objeto PointValue
                    point_value = PointValue(
                        id_source=source_id,
                        id_point=points[i],
                        id_feature=feature.id,
                        numeric_value=numeric_value,
                        string_value=string_value
                    )

                    # Guardar el objeto PointValue en el repositorio
                    self.point_value_repo.add(point_value)
                

        # Guardar los valores posibles de la variable objetivo (categórica o binaria)
        target_feature = next((f for f in features if f.is_target), None)
        if target_feature:
            target_values = df[target_feature.name].dropna().unique()

            if all(isinstance(v, str) for v in target_values):
                # Caso categórico
                for class_value in target_values:
                    prediction = PredictionValue(
                        id_source=source_id,
                        class_name=class_value
                    )
                    self.prediction_value_repo.add(prediction)

            elif all(isinstance(v, (int, float, np.integer, np.floating)) for v in target_values):
                # Caso binario (solo 2 valores distintos)
                bin_classes = set(target_values)
                if len(bin_classes) == 2:
                    for class_value in sorted(bin_classes):
                        prediction = PredictionValue(
                            id_source=source_id,
                            class_name=str(class_value)  
                        )
                        self.prediction_value_repo.add(prediction)

        return new_source.id 

    def delete(self, source_id: int):
        # Verificar existencia antes de iniciar la transacción
        if not self.source_repo.get(source_id):
            raise ValueError(f"No existe la fuente con id {source_id}.")
    
        with UnitOfWork(self.database.connection):
            self.prediction_value_repo.delete_by_source(source_id)
            self.point_value_repo.delete_by_source(source_id)
            self.point_repo.delete_by_source(source_id)
            self.feature_repo.delete_by_source(source_id)
            self.source_repo.delete(source_id)
