import yaml
import json
from collections import OrderedDict


class OrderedDumper(yaml.Dumper):
        pass

def _dict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        data.items())

OrderedDumper.add_representer(OrderedDict, _dict_representer)

class DAGGenerator:


    def __init__(self, dag_template):
        self.dag_template = dag_template
       

    def gen_yaml_DAG(self, graph: dict, descr: dict, out_file: str):
        template = {}

        with open(self.dag_template, "r") as f:
            template = json.load(f)

        ops = graph["operations"]
        template["msm_dag_yaml"]["tasks"] = OrderedDict()
        for op in ops:
            template["msm_dag_yaml"]["tasks"][op["op_name"]] = OrderedDict()
            template["msm_dag_yaml"]["tasks"][op["op_name"]]["decorator"] = "airflow.decorators.task"
            template["msm_dag_yaml"]["tasks"][op["op_name"]]["python_callable"] = op["op_descr"]["func_path"]

            for var_name, var_descr in descr[op["op_name"]].items(): 
                if var_descr["get"] == "from value":
                    template["msm_dag_yaml"]["tasks"][op["op_name"]][var_name] = var_descr["value"]
                else:
                    template["msm_dag_yaml"]["tasks"][op["op_name"]][var_name] = "+" + var_descr["value"]

        with open(out_file, "w") as f:
            yaml.dump(template, f, OrderedDumper, default_flow_style=False, allow_unicode=True)





