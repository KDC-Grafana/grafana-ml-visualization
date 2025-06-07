from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class PointValue:
    id_source: int
    id_point: int
    id_feature: int
    numeric_value: Optional[float] = None
    string_value: Optional[str] = None
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_source = Utils.to_native(self.id_source)
        self.id_point = Utils.to_native(self.id_point)
        self.id_feature = Utils.to_native(self.id_feature)
        self.numeric_value = Utils.to_native(self.numeric_value)