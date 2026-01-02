from typing import Union

class CharactDescr:
    _name: str = None
    _class: str = None
    _from: Union[int, float] = None
    _to: Union[int, float] = None

    def __init__(self, name: str, op_class: str, from_value: Union[int, float], to: Union[int, float]):
        self._name = name
        self._class = op_class,
        self._from = from_value,
        self._to = to
        
        

