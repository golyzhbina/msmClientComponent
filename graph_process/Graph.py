from dataclasses import dataclass
from typing import Dict, List
from collections import defaultdict


class Graph:


    def __init__(self):
        self.operations: dict = {}  # имя операции -> (inputs, outputs)
        self.graph: defaultdict  = defaultdict(list) # прямой граф: переменная/операция -> соседи
        self.reverse_graph: defaultdict  = defaultdict(list) # обратный граф