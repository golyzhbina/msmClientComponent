from .Generator import Generator
from collections import OrderedDict
import toml
import json
from pathlib import Path

class WorkflowGenerator(Generator):
    def __init__(self, filename: str, subgraph: OrderedDict, use_parallelism: bool = False):
        super().__init__(filename, subgraph)
        self.use_parallelism = use_parallelism
    
    def __get_toml_name(self, op, var):
        return f"{op}__{var}"

    def get_declaration_file(
        self,
        path_to_declaration: str, 
        inputs: dict, 
        domain: str,
        declarations_url: str = "file://localhost/$PWD/dtypes"
    ):
        path_to_declaration  = Path(path_to_declaration)
        workflow_declaration_dict = OrderedDict()
        workflow_declaration_dict["domain"] = domain
        workflow_declaration_dict["declarations_url"] = declarations_url
        workflow_declaration_dict["variables"] = OrderedDict()
        workflow_declaration_dict["operations"] = OrderedDict()
        
        unique_variables_map = {}
        map_cm_vars_to_ops_vars = {}

        for op in self.subgraph:
            
            for var, data in self.map_cm_to_code[op]["variables"].items():
                if data.get("name", None):
                    unique_variables_map[self.__get_toml_name(op, var)] = data["name"]
            
            for var in self.subgraph[op][1]:
                unique_variables_map[self.__get_toml_name(op, var)] = var
        
        for op in self.subgraph:
            map_cm_vars_to_ops_vars[op] = {}

            for var, data in self.map_cm_to_code[op]["variables"].items():
                if data.get("name", None):
                    map_cm_vars_to_ops_vars[op][data.get("name")] = self.__get_toml_name(op, var)

            for var in self.subgraph[op][1]:
                map_cm_vars_to_ops_vars[op][var] = self.__get_toml_name(op, var)

        for var, descr in self.variables.items():
            
            if len(descr["input_to"]) and len(descr["output_from"]):
                out_from = descr["output_from"][0]
                for op in descr["input_to"]:
                    unique_variables_map[map_cm_vars_to_ops_vars[op][var]] \
                    = map_cm_vars_to_ops_vars[out_from][var]

            elif len(descr["input_to"]) and not len(descr["output_from"]):
                for op in descr["input_to"]:
                    unique_variables_map[map_cm_vars_to_ops_vars[op][var]] \
                    = map_cm_vars_to_ops_vars[op][var]

            elif not len(descr["input_to"]) and len(descr["output_from"]):
                for op in descr["output_from"]:
                    unique_variables_map[map_cm_vars_to_ops_vars[op][var]] \
                    = map_cm_vars_to_ops_vars[op][var]
        
        for op in self.subgraph:
            for var, data in self.map_cm_to_code[op]["variables"].items():

                var_descr = {"type": data["type"]}

                if var in inputs.get(op, {}):
                    var_descr["is_input"] = True
                
                workflow_declaration_dict["variables"][self.__get_toml_name(op, var)] = var_descr
            
            for var in self.subgraph[op][1]:
                var_descr = {"type": data["type"]}
                workflow_declaration_dict["variables"][self.__get_toml_name(op, var)] = var_descr

        
        workflow_declaration_dict["variables"]["map_vars_file"] = {"type" : "str", "is_input": True}

        for op in self.subgraph:
            op_inputs = [self.__get_toml_name(op, var) for  var in list(self.map_cm_to_code[op]["variables"].keys())]
            op_inputs.append("map_vars_file")
            op_outputs = [self.__get_toml_name(op, var) for  var in self.subgraph[op][1]]

            for i in range(len(op_inputs)):
                if op_inputs[i] in unique_variables_map:
                    op_inputs[i] = unique_variables_map[op_inputs[i]]

            workflow_declaration_dict["operations"][op] = OrderedDict()
            workflow_declaration_dict["operations"][op]["type"] = self.map_cm_to_code[op]["type"]
            workflow_declaration_dict["operations"][op]["declaration_url"] = self.map_cm_to_code[op]["declaration_url"]
            workflow_declaration_dict["operations"][op]["inputs"] = op_inputs
            workflow_declaration_dict["operations"][op]["outputs"] = op_outputs
        

        with open(path_to_declaration / "declaration.toml", "w") as toml_file:
            toml.dump(workflow_declaration_dict, toml_file)
        
        return unique_variables_map



    def get_application_file(
            self, 
            path_to_app: str,
            workflow_name: str,
            user_name: str,
            declaration_url: str,
            experiments_number: int,
            inputs: dict,
            remote_settings: dict,
            hardware_requirements: dict,
            unique_variables_map: dict
    ):
        workflow_app_dict= OrderedDict()
        workflow_app_dict["name"] = workflow_name
        workflow_app_dict["username"] = user_name
        workflow_app_dict["declaration_url"] = declaration_url
        workflow_app_dict["experiments_number"] = experiments_number
        
        inputs_dict = {}
        for op in inputs:
            for var, value in inputs[op].items():
                inputs_dict[self.__get_toml_name(op, var)] = value
        inputs_dict["map_vars_file"] = str(path_to_app / "map_vars_file.json")
        
        workflow_app_dict["inputs"] = inputs_dict
        ordered_remote_settings = OrderedDict()
        ordered_remote_settings["name"] = remote_settings["name"]
        ordered_remote_settings["type"] = remote_settings["type"]
        ordered_remote_settings["config"] = remote_settings["config"]
        ordered_remote_settings["workload_manager"] = remote_settings["workload_manager"]

        workflow_app_dict["remote"] = [ordered_remote_settings]

        workflow_app_dict["hardware_requirements"] = {remote_settings["name"] : hardware_requirements}  

        with open(path_to_app / "workflow-app.toml", "w") as toml_file:
            toml.dump(workflow_app_dict, toml_file)
        
        with open(path_to_app / "map_vars_file.json", "w") as map_vars_file:
            json.dump(unique_variables_map, map_vars_file)
