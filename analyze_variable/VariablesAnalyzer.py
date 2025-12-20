import json

import importlib
import inspect

import os
import sys
from pathlib import Path

#import msm_ops

class VariablesAnalyzer:
    
    map_names = {}
    def __init__(self, path_to_map_info):
        with open(path_to_map_info, "r") as f:
            self.map_names = json.load(f)

    def get_vars_descr(self, graph: dict): 

        sys.path.append('/home/golub/airflow/dags')
        types = {
            Path : "path", 
            int : "int", 
            list : "list", 
            tuple : "tuple", 
            float : "float", 
            inspect.Parameter.empty: "", 
            bool : "bool"
        }

        descr = {}

        ops = graph["operations"]
        vars = graph["variables"]


        for op in ops:
            parts = op["op_descr"]["func_path"].split(".")
            module_name = ".".join(parts[:-1])
            func_name = parts[-1]
            module = importlib.import_module(module_name)
            function = getattr(module, func_name)
            sig = inspect.signature(function)
            args = {}

            for name, param in sig.parameters.items():
                if name == 'context':
                    continue

                if name in self.map_names[func_name]:
                    graph_var = self.map_names[func_name][name]
                    if len(vars[graph_var]["output_from"]) != 0:
                        args[name] = { "value" : vars[graph_var]["output_from"][0], 
                                       "type" : "",
                                       "get" : "from task"}
                        continue
                
                default_val = param.default
                if default_val == inspect.Parameter.empty:
                    default_val = ""
                args[name] = { "value" : "input", 
                              "type" : types.get(param.annotation, "unknown type"), 
                              "default": default_val, 
                              "get" : "from value"}

            descr[op["op_name"]] = args

        sys.path.pop()
        return descr
    
    
    def insert_values(self, descr: dict, var_values: dict):

        for op_name, vars in var_values.items():
            try:
                for var_name, var_val in vars.items(): 
                    descr[op_name][var_name]["value"] = var_val
            except KeyError:
                print(f'key error on descr[{op_name}][{var_name}]["value"]' )
                
    
    #def get_graph_with_values(graph: dict, values: dict):




            


            
