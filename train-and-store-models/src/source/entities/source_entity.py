from dataclasses import dataclass
from typing import Optional

from ...utils.utils import Utils


@dataclass
class Source:
    name: str
    source: str
    creator: Optional[str] = None 
    description: Optional[str] = None  
    id: Optional[int] = None  
    
    def __post_init__(self):
        # Convertir los valores de tipo NumPy a tipos nativos de Python
        self.creator = Utils.to_native(self.creator) 
        self.description = Utils.to_native(self.description)  
        self.id = Utils.to_native(self.id)