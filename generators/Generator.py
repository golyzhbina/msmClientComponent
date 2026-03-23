import yaml
from collections import OrderedDict

class Generator:
    map_cm_to_code: dict = None
    subgraph: OrderedDict = None

    def __init__(self, filename: str, subgraph: OrderedDict, reversed_subgraph: dict):
        # потенциальная ошибка
        with open(filename, "r") as f:
            self.map_cm_to_code = yaml.safe_load(f)

        self.subgraph: OrderedDict = subgraph
        self.variables: dict = reversed_subgraph
    
    def get_inputs(self) -> OrderedDict:
        
        inputs = OrderedDict()
        added_vars = []
        for op in self.subgraph:
            inputs[op] = dict()
            map_info = self.map_cm_to_code[op]
            for v_name, v_info in map_info["variables"].items():
                map_name = v_info.get("name", None)
                var_id = map_name

                if var_id  in added_vars:
                    continue

                if map_name in self.variables and \
                   len(self.variables[map_name]["output_from"]) == 0  or \
                   map_name not in self.variables:
                    var_id = var_id if var_id else f"{op}_{v_name}"
                    inputs[op][v_name] = v_info
                    inputs[op][v_name].pop("name", None)
                    inputs[op][v_name]["id"] = var_id
                    added_vars.append(var_id)

        return inputs
    
    def get_operation_description(self, op_name): 
        return self.map_cm_to_code[op_name].get("description", "")
    
    @staticmethod
    def get_var_id(op: str, var: str):
        return f"{op}__{var}"