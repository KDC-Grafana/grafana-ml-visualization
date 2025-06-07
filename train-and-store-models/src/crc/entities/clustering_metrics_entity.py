from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class ClusteringMetrics:
    id_model: int
    inertia: Optional[float] = None
    silhouette_coefficient: Optional[float] = None
    davies_bouldin_index: Optional[float] = None
    id: Optional[int] = None
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_model = Utils.to_native(self.id_model)
        self.inertia = Utils.to_native(self.inertia)
        self.silhouette_coefficient = Utils.to_native(self.silhouette_coefficient)
        self.davies_bouldin_index = Utils.to_native(self.davies_bouldin_index)
        self.id = Utils.to_native(self.id)