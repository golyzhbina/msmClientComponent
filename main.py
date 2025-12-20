from graph_process.GraphCreator import GraphCreator
from graph_process.SubgraphGetter import SubgraphGetter
from graph_process.SubgraphAnalyzer import SubgraphAnalyzer
from analyze_variable.VariablesAnalyzer import VariablesAnalyzer
from generate_yaml.DAGGenerator import DAGGenerator
from manage_dag.DAGHttpClient import DAGHttpClient

import os
from pathlib import Path
import time
import json

path = Path(os.path.dirname(os.path.abspath(__file__)))
path_json = path / "data" / "json"
creator = GraphCreator(path_json / "graph.json")
builder = SubgraphGetter(creator.get_graph())

inputs1 = ["veldata_path", "rec_coords_path", "region_coords", "traces_path", "use_cumsum"]
outputs1 = ["gr_df", "maxes_at_square", "maxes_at_timeline",  "slices"]
minimal1 = builder.find_minimal_subgraph(inputs1, outputs1)
ordered_ops = builder.get_execution_order(minimal1)
print("Порядок выполнения:", ordered_ops)

ops = creator.get_ops_descr(ordered_ops)
analyzer = SubgraphAnalyzer()

vars_descr = analyzer.create_variable_dict(ops)
var_analyzer = VariablesAnalyzer(path_json / "map_vars.json")
descr = var_analyzer.get_vars_descr({"variables" : vars_descr, "operations" : ops})


values = None
with open(path_json / "test_values.json") as f:
    values = json.load(f)

var_analyzer.insert_values(descr, values)
dag_generator = DAGGenerator(path_json / "dag_template.json")
dag_generator.gen_yaml_DAG({"variables" : vars_descr, "operations" : ops}, descr, "/home/golub/airflow/dags/OUT.yaml")

dag_http_cli = DAGHttpClient("http://192.168.49.43:8080", "admin", "1234")
status, body = dag_http_cli.trigger_dag("msm_dag_yaml", '/home/golub/msm/data/out')
dag_id = "msm_dag_yaml"
dag_run_id = body["dag_run_id"]

while True:
    response = dag_http_cli.get_task_instances(dag_id, dag_run_id)
    os.system('clear')
    print(*sorted(list(map(lambda x: f"{x['task_display_name']} {x['state']}", response['task_instances']))), sep="\n")
    time.sleep(1)
    

