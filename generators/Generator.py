import yaml
from collections import OrderedDict

class Generator:
    map_cm_to_code: dict = None
    subgraph: OrderedDict = None

    def __init__(self, filename: str, subgraph: OrderedDict):
        with open(filename, "r") as f:
            self.map_cm_to_code = yaml.safe_load(f)

        self.subgraph = subgraph
    
    def get_inputs(self) -> OrderedDict:
        
        inputs = OrderedDict()
        variables = {}

        for op_name, op_descr in self.subgraph.items():
            for v in op_descr[0] + op_descr[1]:
                variables[v] = {"output_from": [], "input_to" : []}
        
        for op_name, op_descr in self.subgraph.items():
            for v in op_descr[0]:
                variables[v]["input_to"].append(v)
            for v in op_descr[1]:
                variables[v]["output_from"].append(v)
            inputs[op_name] = dict()

        print(variables)

        for op in self.subgraph:
            map_info = self.map_cm_to_code[op]
            for v_name, v_info in map_info["variables"].items():
                map_name = v_info.get("name", None)
                if map_name in variables and \
                   len(variables[map_name]["output_from"]) == 0  or \
                   map_name not in variables:
                    inputs[op][v_name] = v_info
                    inputs[op][v_name].pop("name", None)


        return inputs
                    
    
    def get_declaration_file(filrname: str) -> None:
        pass
    
