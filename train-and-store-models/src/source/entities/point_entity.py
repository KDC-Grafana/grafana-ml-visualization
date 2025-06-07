from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class Point:
    id_source: int
    name: str
    id: Optional[int] = None
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.id_source = Utils.to_native(self.id_source)
        self.id = Utils.to_native(self.id)