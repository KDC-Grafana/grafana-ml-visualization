from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class AssociationRule:
    id_model: int
    antecedent: str
    consequent: str
    support: float
    confidence: float
    lift: float
    id: Optional[int] = None 
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_model = Utils.to_native(self.id_model)
        self.support = Utils.to_native(self.support)
        self.confidence = Utils.to_native(self.confidence)
        self.lift = Utils.to_native(self.lift)
        self.id = Utils.to_native(self.id)

