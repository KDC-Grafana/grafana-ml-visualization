from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class KMeansCentroid:
    id_model: int
    id_cluster: int
    id_feature: int
    value: float
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_model = Utils.to_native(self.id_model)
        self.id_cluster = Utils.to_native(self.id_cluster)
        self.id_feature = Utils.to_native(self.id_feature)
        self.value = Utils.to_native(self.value)