from .Graph import Graph
from .Variable import Variable
from .Operation import Operation
from .FictiveOperation import FictiveOperation
from .Characteristic import Characteristic
from logic_normal_forms import build_knf, parse_dnf

from typing import Dict, Tuple, List, Union, TypeAlias
from collections import OrderedDict, deque
from copy import deepcopy
from enum import Enum

import yaml

Variables: TypeAlias = List[str]

class NodeType(Enum):
    OPERATION = "operation"
    VARIABLE = "variable"
    FICTIVE_OPERATION = "fictiveOperation"

class ComputeModel:

    def __init__(self, path_to_model: str):

        with open(path_to_model, "r") as f:
            model_dict = yaml.safe_load(f)

        self.characteristics: Dict[str, Characteristic] = \
        self.__read_characteristics(model_dict["operation_characteristics"])

        self.relationship, self.nodes = self.__read_graph(model_dict["graph"])

        self.graph: Graph = Graph(self.relationship) 

    def __get_fictive_operation_name(self, var_name, var_class):
        return f"{var_name}_to_{var_class}"

    def __read_characteristics(self, characters_dict: dict) -> Dict[str, Characteristic]:
        return {charc_name : Characteristic(charc_name, charc_info["default"]) 
                for charc_name, charc_info in characters_dict.items()}

    def __read_graph(self, graph_dict: dict) -> Tuple[
                                                    Dict[str, List[Variables]], 
                                                    Dict[str, Union[Variable, Operation]]
                                                ]:

        relationship: Dict[str, List[Variables]] = dict()
        nodes: Dict[str, Union[Variable, Operation]] = dict()

        var_classes: Dict[str, List[str]] = dict()

        for var_name, var_descr in graph_dict["variables"].items():
            nodes[var_name] = Variable(var_name, var_descr)

            for cl in var_descr:
                if not (cl in var_classes):
                    var_classes[cl] = []

                var_classes[cl].append(var_name)

        for op_name, op_descr in graph_dict["operations"].items():
            op = Operation(op_name, op_descr.get("class", op_name), op_descr.get("characters", {}))
            nodes[op_name] = op
            relationship[op_name] = [op_descr["inputs"], op_descr["outputs"]]

        
        for var_class, var_list in var_classes.items():
            if len(var_list) == 1 and var_list[0] != var_class:
                op_name = self.__get_fictive_operation_name(var_list[0], var_class)
                relationship[op_name] = [[var_list[0]], [var_class]]
                nodes[op_name] = FictiveOperation(op_name)
            
            elif len(var_list) > 1:
                for var in var_list:
                    op_name = self.__get_fictive_operation_name(var, var_class)
                    relationship[op_name] = [[var], [var_class]]  
                    nodes[op_name] = FictiveOperation(op_name)  

        return relationship, nodes        
    
    def is_reachable_from_inputs(self, graph: Graph, inputs: List[str], outputs: List[str]) -> Tuple[bool, str]:
        reachable_from_inputs = graph.bfs_forward(inputs)
        for var in outputs:
            if var not in reachable_from_inputs:
                return (False, f"При данных входных переменных выходная переменная {var} недостижима")
        return (True, "")
    
    def get_ordered_subgraph(self, graph_rel: dict) -> OrderedDict[str , List[Variables]]:
        operations = list(filter(lambda x: x in self.relationship, graph_rel.keys()))
    
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
    
        ordered_graph = OrderedDict()

        for op in execution_order:
            ordered_graph[op] = graph_rel[op]

        return ordered_graph
    
    def get_paths(self, inputs: List[str], outputs: List[str]) -> OrderedDict[str , List[Variables]]:

        reachable_from_inputs = self.graph.bfs_forward(inputs)
        for var in outputs:
            if var not in reachable_from_inputs:
                raise Exception(f"При данных входных переменных выходная переменная {var} недостижима")
    
        necessary_nodes = self.graph.bfs_backward(outputs, reachable_from_inputs)

        subgraph_rel = {node : self.relationship[node] for node in necessary_nodes if node in self.relationship}

        all_paths = self.__get_all_paths(subgraph_rel, inputs, outputs)

        all_cnvrt_paths = []
        for path in all_paths:
            characts = self.__get_path_characteristics(path)
            nodes, edges = self.cvrt_to_graph(path)
            all_cnvrt_paths.append({"nodes": nodes, "edges": edges, "characts": characts})     

        nodes, edges = self.cvrt_to_graph(subgraph_rel)
        return {"nodes": nodes, "edges": edges}, all_cnvrt_paths
    
    def __get_all_paths(self, subgraph: OrderedDict, inputs: List[str], outputs: List[str]) -> \
                            List[Dict[str, List[Variables]]]:
        reversed_relations = self.get_reversed_relations(subgraph)
        knf, map_formula_names = build_knf(inputs, outputs, subgraph, reversed_relations)
        dnf = str(knf.to_dnf())
        paths = parse_dnf(dnf, map_formula_names, self.relationship)   
        paths = self.__filter_paths(paths, outputs)        
        return paths
    
    def __filter_paths(self, paths_relations: List[Dict], outputs: List[str]) -> \
                                                    List[Dict[str, List[Variables]]]:
        filtered_paths = []
        unique_paths = []
        for relations in paths_relations:
            graph = Graph(relations)
            r_set =  set()
            for op in relations:
                r_set.update(self.relationship[op][0])
                r_set.update(self.relationship[op][1])
                r_set.add(op)

            visited = set(filter(lambda x: x in self.relationship, graph.bfs_backward(outputs, r_set)))
            unneed_nodes = set(relations.keys()) - visited

            for node in unneed_nodes:
                del relations[node]

            unique_ops = set(relations.keys())
            if unique_ops in unique_paths:
                continue

            unique_paths.append(unique_ops)
            filtered_paths.append(relations)
        return filtered_paths
    
    def __get_path_characteristics(self, path: Dict[str, str]) -> Dict[str, int]:
        characts = {}
        for charact in self.characteristics:
            characts[charact] = 0
        
        for node in path:
            if type(self.nodes[node]) == Operation:
                for charact in self.characteristics:
                    characts[charact] += \
                        self.nodes[node]._characters \
                        .get(charact, self.characteristics[charact].default)
       

        return characts

    def cvrt_to_graph(self, relations) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
        
        nodes = {}
        edges = []
        for op in relations:
            if type(self.nodes[op]) == FictiveOperation:
                nodes[op] = NodeType.FICTIVE_OPERATION.value
            else:
                nodes[op] = NodeType.OPERATION.value
            
            for var in relations[op][0]:
                nodes[var] = NodeType.VARIABLE.value
                edges.append({"from": var, "to": op})

            for var in relations[op][1]:
                nodes[var] = NodeType.VARIABLE.value
                edges.append({"from": op, "to": var})
        return nodes, edges
    
    def cvrt_to_relations(self, nodes, edges) -> Dict: 
        relationship = {}

        for node, tpe in nodes.items():
            if tpe  in [NodeType.OPERATION.value, NodeType.FICTIVE_OPERATION.value]:
                relationship[node] = [[], []]
        
        for edge in edges:
            
            if nodes[edge["to"]] in [NodeType.OPERATION.value, NodeType.FICTIVE_OPERATION.value]:
                relationship[edge["to"]][0].append(edge["from"])
            else:
                relationship[edge["from"]][1].append(edge["to"])
        return relationship
    
    def get_reversed_relations(self, relations) -> Dict:
        reversed_rel = {}

        for op in relations:
            for var in relations[op][0] + relations[op][1]:
                reversed_rel[var] = {"input_to": [], "output_from": []}
        
        for op in  relations:
            for var in relations[op][0]:
                reversed_rel[var]["input_to"].append(op)

            for var in relations[op][1]:
                reversed_rel[var]["output_from"].append(op)
        return reversed_rel
    
    def get_graph(self):
        return self.cvrt_to_graph(self.relationship)

    def delete_fictive_ops(self, graph: OrderedDict) -> OrderedDict:

        graph_copy = deepcopy(graph)
        replace_map = {}
        op_to_delete = []

        for op_name in graph:
            if type(self.nodes[op_name]) == FictiveOperation:
                replace_map[graph[op_name][0][0]] = graph[op_name][1][0]
                op_to_delete.append(op_name)

        for op_name in op_to_delete:
            del graph_copy[op_name]
        
        for op_name in graph_copy:
            for i, var_name in enumerate(graph[op_name][1]):
                if var_name in replace_map:
                    graph_copy[op_name][1][i] = replace_map[var_name]
        return graph_copy
    
    def clear_paths_filtration(self, outputs: List[str], subgraph: dict, paths: List[dict]) -> List[int]:

        subgraph_rel = self.cvrt_to_relations(subgraph["nodes"], subgraph["edges"])
        subgraph_rev_rel = self.get_reversed_relations(subgraph_rel)

        is_end_node_in_sg = {}
        for out_var in outputs:
            is_end_node_in_sg[out_var] = False

            if not len(subgraph_rev_rel[out_var]["input_to"]):
                is_end_node_in_sg[out_var] = True

        use_paths_id = [i for i in range(len(paths))]
        for i, path in enumerate(paths):
            relations = self.cvrt_to_relations(path["nodes"], path["edges"])
            reversed_relations = self.get_reversed_relations(relations)

            is_end_node = {}
            for out_var in outputs:
                is_end_node[out_var] = False
                if not len(reversed_relations[out_var]["input_to"]):
                    is_end_node[out_var] = True

            for out_var in outputs:
                if is_end_node[out_var] and not is_end_node_in_sg[out_var]:
                    use_paths_id.remove(i)
                    break

        return use_paths_id

    def get_characts(self) -> List[str]:
        return list(self.characteristics.keys())
