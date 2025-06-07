from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class DecisionTreeNode:
    id_model: Optional[int] = None
    id_node: Optional[int] = None
    parent_node: Optional[int] = None
    feature: Optional[str] = None 
    threshold: Optional[float] = None 
    left_node: Optional[int] = None
    right_node: Optional[int] = None
    is_leaf: bool = False
    prediction_value: Optional[int] = None 
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_model = Utils.to_native(self.id_model)
        self.id_node = Utils.to_native(self.id_node)
        self.parent_node = Utils.to_native(self.parent_node)
        self.threshold = Utils.to_native(self.threshold)
        self.left_node = Utils.to_native(self.left_node)
        self.right_node = Utils.to_native(self.right_node)
        self.is_leaf = Utils.to_native(self.is_leaf)
        self.prediction_value = Utils.to_native(self.prediction_value)
