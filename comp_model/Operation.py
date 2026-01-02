from dataclasses import dataclass

@dataclass
class Operation:

    _name: str 
    _class: str 
    _characters: dict
    
    # def __init__(self, name: str, op_class: str, characts: List[Characteristic]):
    #     self._name = name
    #     self._class = op_class
    #     self._characters = characts
        