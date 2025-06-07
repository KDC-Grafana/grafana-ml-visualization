from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class ClusteringHierarchicalE:
    id_model: int
    name: str
    height: float
    id_parent: Optional[int] = None
    id_point: Optional[int] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_model = Utils.to_native(self.id_model)
        self.height = Utils.to_native(self.height)
        self.id_parent = Utils.to_native(self.id_parent)
        self.id_point = Utils.to_native(self.id_point)
        self.id = Utils.to_native(self.id)