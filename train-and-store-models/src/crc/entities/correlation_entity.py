from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class Correlation:
    id_model: int
    id_feature1: int
    id_feature2: int
    value: float
    id: Optional[int] = None
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_model = Utils.to_native(self.id_model)
        self.id_feature1 = Utils.to_native(self.id_feature1)
        self.id_feature2 = Utils.to_native(self.id_feature2)
        self.value = Utils.to_native(self.value)
        self.id = Utils.to_native(self.id)