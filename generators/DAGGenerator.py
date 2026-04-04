from .Generator import Generator
from collections import OrderedDict
import yaml
from pathlib import Path

class OrderedDumper(yaml.Dumper):
        pass

def _dict_representer(dumper, data):
    return dumper.represent_mapping(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        data.items())

OrderedDumper.add_representer(OrderedDict, _dict_representer)

class DAGGenerator(Generator):

    def __init__(self, filename: str, subgraph: OrderedDict, reversed_subgraph: dict, use_parallelism: bool = False):
        super().__init__(filename, subgraph, reversed_subgraph, use_parallelism)
        self.use_parallelism = use_parallelism

    def __get_var_value(self, inputs, op, var):
        var_id = self.map_cm_to_code[op]["variables"][var].get("name", Generator.get_var_id(op, var))
        if var_id in inputs:
            return inputs[var_id]
        else:
            return "+" + self.variables[var_id]["output_from"][0]


    def get_declaration_file(
            self,
            filename: str, 
            inputs: dict, 
            home_dir: str,
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
        dag[dag_id]["params"] = {}
        dag[dag_id]["params"]["home_dir"] = home_dir
        dag[dag_id]["tags"] = tags
        dag[dag_id]["tasks"] = OrderedDict()

        for op in self.subgraph:
            dag[dag_id]["tasks"][op] = OrderedDict()
            dag[dag_id]["tasks"][op]["decorator"] = "airflow.decorators.task"
            dag[dag_id]["tasks"][op]["python_callable"] = self.map_cm_to_code[op]["airflow"]["scalar_wrapper"]

            if self.use_parallelism and self.map_cm_to_code[op].get("expand"):
                
                dag[dag_id]["tasks"][op]["params"] = OrderedDict()
                dag[dag_id]["tasks"][op]["expand"] = OrderedDict()
            
                expand_var = self.map_cm_to_code[op].get("expand")

                for var in self.map_cm_to_code[op]["variables"]:
                    if var == expand_var:
                        continue
                    dag[dag_id]["tasks"][op]["params"][var] = self.__get_var_value(inputs, op, var)
                
                dag[dag_id]["tasks"][op]["expand"] = {expand_var: self.__get_var_value(inputs, op, expand_var)}

                if not len(dag[dag_id]["tasks"][op]["params"]):
                    del dag[dag_id]["tasks"][op]["params"]

            else:
                for var in self.map_cm_to_code[op]["variables"]:
                    dag[dag_id]["tasks"][op][var] = self.__get_var_value(inputs, op, var)

        with open(filename, "w") as f:
            yaml.dump(dag, f, OrderedDumper, default_flow_style=False, allow_unicode=True)

    def get_py_file(
            self,
            path_to_dags: str,
            dag_yaml_name: str
    ):
        path_to_py = Path(path_to_dags) / Path(f"{dag_yaml_name}.py")
        path_to_yaml = Path(path_to_dags) / Path(f"{dag_yaml_name}.yaml")
        code = \
        f"""
import dagfactory

config_file = \"{path_to_yaml}\"
example_dag_factory = dagfactory.DagFactory(config_file)
example_dag_factory.clean_dags(globals())
example_dag_factory.generate_dags(globals())
        """

        with open(path_to_py, "w") as f:
            f.write(code)


    @staticmethod
    def get_common_params():
        return [
                {   
                    "name" : "path",
                    "type": "str",
                    "description" : "path to airflow dags",
                    "default" : "/home/golub/airflow/dags"
                },

                {   
                    "name" : "YAML file name",
                    "type" : "str",
                    "default" : "test_msm_dag"
                },

                {
                    "name" : "dag_id",
                    "type" : "str",
                    "default" : "test_msm"
                },

                {
                    "name" : "out_dir",
                    "type" : "str",
                    "description" :  "path to out files",
                    "default" : "/home/golub/msm/data/out"
                },

                {
                    "name" : "schedule_interval",
                    "type" : "str",
                    "default" : "@once"
                },  

                {
                    "name" : "owner",
                    "type" : "str",
                    "default" : "airflow"
                }, 

                {
                    "name" : "start_date",
                    "type" : "str",
                    "default" : "2023-01-01",
                    "description" : "format: yyyy-mm-dd"
                }, 

                {
                    "name" : "tags", 
                    "type" : "List[str]",
                    "descrtption" : "еnter tags separated by commas",
                    "default" : "msm"
                }
            ]
