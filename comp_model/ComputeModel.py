from .Graph import Graph
from .Variable import Variable
from .Operation import Operation
from .FictiveOperation import FictiveOperation
from .Characteristic import Characteristic
import yaml


from typing import Dict, Tuple, List, Union
from collections import OrderedDict, deque
from copy import deepcopy

from sympy import sympify, to_dnf

class ComputeModel:
    def __init__(self, path_to_model: str):

        with open(path_to_model, "r") as f:
            model_dict = yaml.safe_load(f)

        self.nodes: Dict[str, Union[Variable, Operation]] = dict()
        self.relationship: Dict[str, Tuple] = dict()
        self.__read_graph(model_dict["graph"])        
        self.graph: Graph = Graph(self.relationship) 

        self.characteristics: Dict[str, Characteristic] = dict()
        self.__read_characteristics(model_dict["operation_characteristics"])

    def __read_characteristics(self, characters_dict: dict):
        for charc_name, charc_info in characters_dict.items():
            self.characteristics[charc_name] = Characteristic(charc_name, charc_info["default"])

    def __read_graph(self, graph_dict: dict):
        var_classes: Dict[str, List[str]] = dict()

        for var_name, var_descr in graph_dict["variables"].items():
            self.nodes[var_name] = Variable(var_name, var_descr["class"])

            if not var_descr["class"] in var_classes:
                var_classes[var_descr["class"]] = []

            var_classes[var_descr["class"]].append(var_name)
        

        for op_name, op_descr in graph_dict["operations"].items():
            op = Operation(op_name, op_descr["class"], op_descr["characters"])
            self.nodes[op_name] = op

            inputs = []
            for var_name, var_descr in op_descr["inputs"].items():
                inputs.append(var_name)

            outputs = []
            for var_name in op_descr["outputs"]:
                outputs.append(var_name)

            self.relationship[op_name] = [inputs, outputs]

        
        for var_class, var_list in var_classes.items():
            if len(var_list) == 1 and var_list[0] != var_class:
                self.relationship[f"{var}_to_{var_class}"] = [[var_list[0]], [var_class]]
                self.nodes[f"{var}_to_{var_class}"] = FictiveOperation(f"{var}_to_{var_class}")
            elif len(var_list) > 1:
                for var in var_list:
                    self.relationship[f"{var}_to_{var_class}"] = [[var], [var_class]]  
                    self.nodes[f"{var}_to_{var_class}"] = FictiveOperation(f"{var}_to_{var_class}")          
    
    def is_reachable_from_inputs(self, inputs: List[str], outputs: List[str]):
        reachable_from_inputs = self.graph.bfs_forward(inputs)
        for var in outputs:
            if var not in reachable_from_inputs:
                return (False, f"При данных входных переменных выходная переменная {var} недостижима")
        return (True, "")
    
    def get_ordered_subgraph(self, nodes: list):
        operations = list(filter(lambda x: x in self.relationship, nodes))
    
        execution_order = []
        visited = set()
        
        def visit(op):
            if op not in visited:
                visited.add(op)
                inputs, _ = self.graph.operations[op]
                for input_var in inputs:
                    if input_var in self.graph.reverse_graph:
                        for pred_op in self.graph.reverse_graph[input_var]:
                            if pred_op in operations:
                                visit(pred_op)
                execution_order.append(op)
        
        for op in operations:
            visit(op)
    
        subgraph_rel = OrderedDict()

        for op in execution_order:
            subgraph_rel[op] = self.relationship[op]
        return subgraph_rel
    
    def get_paths(self, inputs: List[str], outputs: List[str]) -> OrderedDict:

        reachable_from_inputs = self.graph.bfs_forward(inputs)
        for var in outputs:
            if var not in reachable_from_inputs:
                raise Exception(f"При данных входных переменных выходная переменная {var} недостижима")
    
        necessary_nodes = self.graph.bfs_backward(outputs, reachable_from_inputs)

        subgraph_rel = {}
        for node in necessary_nodes:
            if node in self.relationship:
                subgraph_rel[node] = self.relationship[node]

        all_paths = self.__get_all_paths(subgraph_rel, outputs)
        all_cnvrt_paths = []
        for path in all_paths:
            characts = self.__get_path_characteristics(path)
            nodes, edges = self.cvrt_to_graph(path)
            all_cnvrt_paths.append({"nodes": nodes, "edges": edges, "characts": characts})         

        nodes, edges = self.cvrt_to_graph(subgraph_rel)
        return {"nodes": nodes, "edges": edges}, all_cnvrt_paths
    
    def __build_knf(self, outputs: List[str], forward_graph: Dict[str, str], reverse_graph: Dict[str, str]):
        map_name_in_formula = {}
        for i, name in enumerate(forward_graph.keys()):
            name_in_formula = f"x{i}"
            map_name_in_formula[name] = name_in_formula
            map_name_in_formula[name_in_formula] = name

        knf_list = []

        q = deque(outputs)
        visited = set()

        while q:
            var = q.popleft()
            visited.add(var)

            if len(reverse_graph[var]["output from"]):
                knf_list.append("(")

            for op in reverse_graph[var]["output from"]:
                knf_list.append(f"{map_name_in_formula[op]}")
                knf_list.append("|")
            
                for v in forward_graph[op][0]:
                    if v not in visited:
                        q.append(v)

            if len(reverse_graph[var]["output from"]):
                knf_list[-1] = ")"
                knf_list.append("&")

        knf_list.pop()

        knf = sympify("".join(knf_list), evaluate=False)
        
        return knf, map_name_in_formula
    
    def __get_paths_from_dnf(self, dnf: str, map_fomula_names: Dict[str, str], outputs: List[str]):

        paths = []
        if " | " in dnf:
            paths = str(dnf).split(" | ")
            paths = [v[1:-1] for v in paths]
        else:
            paths = [dnf]

        paths = [v.split(" & ") for v in paths]
        paths = [[map_fomula_names[v] for v in path] for path in paths]

        path_rels = []
        for path in paths:
            path_rel = {}
            r_set =  set(path)
            for op in path:
                path_rel[op] = self.relationship[op]
                r_set.update(self.relationship[op][0])
                r_set.update(self.relationship[op][1])
            graph = Graph(path_rel)
            visited = set(filter(lambda x: x in self.relationship, graph.bfs_backward(outputs, r_set)))
            unneed_nodes = set(path_rel.keys()) - visited

            for node in unneed_nodes:
                del path_rel[node]
            path_rels.append(path_rel)

        return path_rels
    
    def __get_all_paths(self, subgraph: OrderedDict, outputs: List[str]):
        reversed_relations = {}
        
        for op, vars in subgraph.items():
            for var in vars[0] + vars[1]:
                reversed_relations[var] = {"input to": [], "output from": []}
        
        for op, vars in subgraph.items():
            for var in vars[0]:
                reversed_relations[var]["input to"].append(op)

            for var in vars[1]:
                reversed_relations[var]["output from"].append(op)

        knf, map_formula_names = self.__build_knf(outputs, subgraph, reversed_relations)
        dnf = str(to_dnf(knf, simplify=True, force=True))
        paths = self.__get_paths_from_dnf(dnf, map_formula_names, outputs)
        return paths
    
    def __get_path_characteristics(self, path: Dict[str, str]):
        characts = {}
        for charact in self.characteristics:
            characts[charact] = 0
        
        for node in path:
            if type(self.nodes[node]) == Operation:
                for name, value in self.nodes[node]._characters.items():
                    characts[name] += value 

        return characts

    def cvrt_to_graph(self, relations):
        
        nodes = {}
        edges = []
        for op in relations:
            nodes[op] = "operation"
            for var in relations[op][0]:
                nodes[var] = "variable"
                edges.append({"from": var, "to": op})

            for var in relations[op][1]:
                nodes[var] = "variable"
                edges.append({"from": op, "to": var})
        return nodes, edges
    
    def get_graph(self):
        return self.cvrt_to_graph(self.relationship)

    def delete_fictive_ops(self, graph: OrderedDict):

        graph_copy = deepcopy(graph)
        replace_map = {}
        op_to_delete = []

        for op_name in graph:
            if type(self.nodes[op_name]) == FictiveOperation:
                replace_map[graph[op_name][1][0]] = graph[op_name][0][0]
                op_to_delete.append(op_name)

        for op_name in op_to_delete:
            del graph_copy[op_name]
        
        for op_name in graph_copy:
            for i, var_name in enumerate(graph[op_name][1]):
                if var_name in replace_map:
                    graph_copy[op_name][1][i] = replace_map[var_name]
        return graph_copy
        

        



        
        








        
