from .Generator import Generator
from collections import OrderedDict
import yaml

class OrderedDumper(yaml.Dumper):
        pass

def _dict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        data.items())

OrderedDumper.add_representer(OrderedDict, _dict_representer)

class DAGGenerator(Generator):

    def __init__(self, filename: str, subgraph: OrderedDict, use_parallelism: bool = False):
        super().__init__(filename, subgraph)
        self.use_parallelism = use_parallelism


    def get_declaration_file(
            self,
            filename: str, 
            inputs: dict, 
            dag_id: str,
            schedule_interval: str = "@once",  
            owner: str = "airflow", 
            start_date: str = "2023-01-01",
            tags: list = []
        ):

        dag = {dag_id: OrderedDict()}
        dag[dag_id]["schedule_interval"] = schedule_interval
        dag[dag_id]["default_args"] = {
            "owner" : owner,
            "start_date" : start_date
        }
        dag[dag_id]["tags"] = tags
        dag[dag_id]["tasks"] = OrderedDict()

        for op in self.subgraph:
            dag[dag_id]["tasks"][op] = OrderedDict()
            dag[dag_id]["tasks"][op]["decorator"] = "airflow.decorators.task"
            dag[dag_id]["tasks"][op]["python_callable"] = self.map_cm_to_code[op]["func_path"]
            for var in self.map_cm_to_code[op]["variables"]:
                print(op)
                print(self.map_cm_to_code[op]["variables"])
                if var in inputs[op]:
                    dag[dag_id]["tasks"][op][var] = inputs[op][var]
                else:
                    print(var)
                    map_name = self.map_cm_to_code[op]["variables"][var]["name"]
                    dag [dag_id]["tasks"][op][var] = "+" + self.variables[map_name]["output_from"][0]

        with open(filename, "w") as f:
            yaml.dump(dag, f, OrderedDumper, default_flow_style=False, allow_unicode=True)

