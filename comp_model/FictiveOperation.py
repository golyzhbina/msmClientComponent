from dataclasses import dataclass
from .Operation import Operation

@dataclass
class FictiveOperation(Operation):
    def __init__(self, _name, _class = "fictive", _characters = {}):
        super().__init__(_name, _class, _characters)