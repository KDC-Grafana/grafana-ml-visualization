from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class Regression:
    id_model: int
    id_feature: Optional[int] 
    coeff: float
    std_err: float
    value: float
    p_value: float
    id: Optional[int] = None
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_model = Utils.to_native(self.id_model)
        self.id_feature = Utils.to_native(self.id_feature)
        self.coeff = Utils.to_native(self.coeff)
        self.std_err = Utils.to_native(self.std_err)
        self.value = Utils.to_native(self.value)
        self.p_value = Utils.to_native(self.p_value)
        self.id = Utils.to_native(self.id)