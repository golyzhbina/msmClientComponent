import yaml
from collections import OrderedDict

class Generator:
    map_cm_to_code: dict = None
    subgraph: OrderedDict = None

    def __init__(self, filename: str, subgraph: OrderedDict):
        with open(filename, "r") as f:
            self.map_cm_to_code = yaml.safe_load(f)

        self.subgraph = subgraph
        self._get_variables_dependecies()

    def _get_variables_dependecies(self):
        self.variables = {}

        for _, op_descr in self.subgraph.items():
            for v in op_descr[0] + op_descr[1]:
                self.variables[v] = {"output_from": [], "input_to" : []}
        
        for op_name, op_descr in self.subgraph.items():
            for v in op_descr[0]:
                self.variables[v]["input_to"].append(op_name)
            for v in op_descr[1]:
                self.variables[v]["output_from"].append(op_name)
    
    def get_inputs(self) -> OrderedDict:
        
        inputs = OrderedDict()
        added_vars = []
        for op in self.subgraph:
            inputs[op] = dict()
            map_info = self.map_cm_to_code[op]
            for v_name, v_info in map_info["variables"].items():
                map_name = v_info.get("name", None)
                var_id = map_name if map_name else v_name

                if var_id  in added_vars:
                    continue

                if map_name in self.variables and \
                   len(self.variables[map_name]["output_from"]) == 0  or \
                   map_name not in self.variables:
                    inputs[op][v_name] = v_info
                    inputs[op][v_name].pop("name", None)
                    inputs[op][v_name]["id"] = var_id
                    added_vars.append(var_id)

        return inputs
    
    def get_operation_description(self, op_name): 
        return self.map_cm_to_code[op_name].get("description", "")
    
    # def get_declaration_file(filrname: str) -> None:
    #     pass
    
