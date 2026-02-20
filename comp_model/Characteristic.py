from typing import Union
from dataclasses import dataclass

@dataclass
class Characteristic:
    name: str = None
    default: Union[int, float] = None
    
        

