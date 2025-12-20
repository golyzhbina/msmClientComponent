from typing import List
from pathlib import Path
import json
from .Graph import Graph


class GraphCreator:

    graph: Graph = Graph()
    graph_dict = {}

    def __init__(self, path_to_graph: Path):
        
       
        with open(path_to_graph, "r") as f:
            self.graph_dict = json.load(f)

        for op_name, descr in self.graph_dict["operations"].items():
            self.add_operation(op_name, descr["inputs"], descr["outputs"])
        

    def add_operation(self, op: str, input_vars: List[str], output_vars: List[str]) -> None:
        """
        Добавляет операцию в граф
        
        Args:
            op_name: имя операции
            input_vars: список входных переменных
            output_vars: список выходных переменных
        """
        input_vars = list(map(lambda x: tuple(x) if type(x) == type(list()) else x, input_vars))
        # Сохраняем информацию об операции
        self.graph.operations[op] = [input_vars, output_vars] 
          
        # Добавляем ребра от входных переменных к операции
        for var in input_vars:
            if type(var) == type(tuple()):
                for v in var:
                    self.graph.graph[v].append(op)
                    self.graph.reverse_graph[op].append()
            else:
                self.graph.graph[var].append(op)
                self.graph.reverse_graph[op].append(var)
        
        # Добавляем ребра от операции к выходным переменным
        for var in output_vars:
            self.graph.graph[op].append(var)
            self.graph.reverse_graph[var].append(op)


    def get_graph(self) -> Graph:
        return self.graph
    
    def get_ops_descr(self, ops_names):
        descr = []

        for name in ops_names:
            descr.append({"op_name" : name, "op_descr" : self.graph_dict["operations"][name]})

        return descr