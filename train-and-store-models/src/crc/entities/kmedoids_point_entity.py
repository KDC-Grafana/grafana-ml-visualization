from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class KMedoidsPoint:
    id_model: int
    id_point: int
    id_cluster: int
    is_medoid: bool
    id: Optional[int] = None
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_model = Utils.to_native(self.id_model)
        self.id_point = Utils.to_native(self.id_point)
        self.id_cluster = Utils.to_native(self.id_cluster)
        self.is_medoid = Utils.to_native(self.is_medoid)
        self.id = Utils.to_native(self.id)