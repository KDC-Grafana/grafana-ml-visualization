from dataclasses import dataclass
from typing import Any, Dict, Optional

from ...utils.utils import Utils


@dataclass
class Index:
    id_source: int 
    algorithm: str
    parameters: Optional[Dict[str, Any]] = None 
    id: Optional[int] = None
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_source = Utils.to_native(self.id_source)
        self.id = Utils.to_native(self.id)