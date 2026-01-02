from .Graph import Graph
from .Variable import Variable
from .Operation import Operation
import yaml

from typing import Dict, Tuple, List, Callable
from collections import OrderedDict

import networkx as nx

class ComputeModel:
    #characts_descr: List[CharactDescr]

    fictive_op_class = "fictive"

    def __init__(self, path_to_model: str):

        with open(path_to_model, "r") as f:
            graph_dict = yaml.safe_load(f)


        self.variables: Dict[str, Variable] = dict()
        self.operations: Dict[str, Operation] = dict()
        self.relationship: Dict[str, Tuple] = dict()

        for var_name, var_descr in graph_dict["graph"]["variables"].items():
            self.variables[var_name] = Variable(var_name, var_descr["class"])
        
        for op_name, op_descr in graph_dict["graph"]["operations"].items():

            if op_descr["class"] == self.fictive_op_class:
                raise ValueError(f"operation class \"{self.fictive_op_class}\" is builtin module class")
            
            op = Operation(op_name, op_descr["class"], op_descr["characters"])
            self.operations[op_name] = op

            inputs = []
            for var_name, var_descr in op_descr["inputs"].items():
                inputs.append(var_name)

            outputs = []
            for var_name in op_descr["outputs"]:
                outputs.append(var_name)

            self.relationship[op_name] = [inputs, outputs]

        
        self._add_fictive_ops()
        self.graph: Graph = Graph(self.relationship)

    def _add_fictive_ops(self):

        var_classes = {}

        for _, var_obj in self.variables.items():
            if var_obj._class not in var_classes:
                var_classes[var_obj._class] = []
            
            var_classes[var_obj._class].append(var_obj._name)

        for _class, vars in var_classes.items():
            if len(vars) > 1:
                for var in vars:
                    self.relationship[f"map_{var}_to_{_class}"] = [[var], [_class]]
                    self.operations[f"map_{var}_to_{_class}"] = Operation(f"map_{var}_to_{_class}", self.fictive_op_class, {})

    def _delete_fictive_ops(self, graph_rel: OrderedDict):

        replace_map = {}
        op_to_delete = []
        for op_name in graph_rel:
            if self.operations[op_name]._class == self.fictive_op_class:
                replace_map[graph_rel[op_name][0][0]] = graph_rel[op_name][1][0]
                op_to_delete.append(op_name)

        for op_name in op_to_delete:
            del graph_rel[op_name]
        
        for op_name in graph_rel:
            for i, var_name in enumerate(graph_rel[op_name][1]):
                if var_name in replace_map:
                    graph_rel[op_name][1][i] = replace_map[var_name]
        

    def get_execution_order(self, nodes) -> List[str]:
        """Получить порядок выполнения операций в подграфе"""
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
            
        return execution_order
    
    def get_algoritm(self, inputs: List[str], outputs: List[str]) -> OrderedDict:

        reachable_from_inputs = self.graph.bfs_forward(inputs)
        for var in outputs:
            if var not in reachable_from_inputs:
                raise Exception("При данных входных переменных выходные переменные недостижимы")
        
        necessary_nodes = self.graph.bfs_backward(outputs, reachable_from_inputs)
        
        ops_order = self.get_execution_order(necessary_nodes)
        subgraph_rel = OrderedDict()

        for op in ops_order:
            subgraph_rel[op] = self.relationship[op]

        self._delete_fictive_ops(subgraph_rel)
        return subgraph_rel


        # subgraph = nx.Graph()
        # for node in necessary_nodes:
        #     subgraph.add_node(node)
        
        # for node in necessary_nodes:
        #     if node in self.relationship:
        #         for inp_var in self.relationship[node][0]:
        #             subgraph.add_edge(inp_var, node)
        #         for out_var in self.relationship[node][1]:
        #             subgraph.add_edge(node, out_var)


        # edges = steinertree.steiner_tree(subgraph, inputs + outputs)
    
        # subgraph_rel = {}



        
        








        
