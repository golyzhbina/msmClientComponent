from comp_model.ComputeModel import ComputeModel
from generators.DAGGenerator import DAGGenerator
# from analyze_variable.VariablesAnalyzer import VariablesAnalyzer
# from generate_yaml.DAGGenerator import DAGGenerator
# from manage_dag.DAGHttpClient import DAGHttpClient

import os
from pathlib import Path
import time
import json


path = Path(os.path.dirname(os.path.abspath(__file__))) / "data" / "yaml" 
path_to_graph = path / "graph.yaml"
cm = ComputeModel(path_to_graph)

inputs = ["veldata_path", "rec_coords_path", "region_coords", "traces_path"]
outputs = ["cube_wo_tm", "df", "maxes"]

subgraph = cm.get_algoritm(inputs, outputs)
#print(subgraph)

genetor = DAGGenerator(path / "mapModelToCode.yaml", subgraph)
inputs = genetor.get_inputs()
for key, value in inputs.items():
    print(key)
    for v1, k1 in value.items():
        print("\t", v1, ":", k1),
        

# vars_descr = analyzer.create_variable_dict(ops)
# var_analyzer = VariablesAnalyzer(path_json / "map_vars.json")
# descr = var_analyzer.get_vars_descr({"variables" : vars_descr, "operations" : ops})


# values = None
# with open(path_json / "test_values.json") as f:
#     values = json.load(f)

# var_analyzer.insert_values(descr, values)
# dag_generator = DAGGenerator(path_json / "dag_template.json")
# dag_generator.gen_yaml_DAG({"variables" : vars_descr, "operations" : ops}, descr, "/home/golub/airflow/dags/OUT.yaml")

# dag_http_cli = DAGHttpClient("http://192.168.49.43:8080", "admin", "1234")
# status, body = dag_http_cli.trigger_dag("msm_dag_yaml", '/home/golub/msm/data/out')
# dag_id = "msm_dag_yaml"
# dag_run_id = body["dag_run_id"]

# while True:
#     response = dag_http_cli.get_task_instances(dag_id, dag_run_id)
#     os.system('clear')
#     print(*sorted(list(map(lambda x: f"{x['task_display_name']} {x['state']}", response['task_instances']))), sep="\n")
#     time.sleep(1)
    

