from comp_model.ComputeModel import ComputeModel
from generators import DAGGenerator, WorkflowGenerator, Generator
import yaml

import os
from pathlib import Path

path = Path(os.path.dirname(os.path.abspath(__file__)))
path_to_yamls = path / "data" / "yaml" 
path_to_graph = path_to_yamls / "graph.yaml"
path_to_map_code = path_to_yamls / "mapModelToCode.yaml"

with open(path_to_graph, "r") as f:
    graph_data = yaml.safe_load(f)

cm = ComputeModel(graph_data)
inputs = ["traces_path"]
outputs = ["hilb_traces"]

subgraph, all_paths = cm.get_paths(inputs, outputs)

use_paths = cm.clear_paths_filtration(outputs, subgraph, all_paths)
algo = min(all_paths, key=lambda x: x["characts"]["diff"])
rel_algo = cm.cvrt_to_relations(algo["nodes"], algo["edges"])
ordered_sg = cm.get_ordered_subgraph(rel_algo)
ordered_sg = cm.delete_fictive_ops(ordered_sg)
reversed_rel = cm.get_reversed_relations(ordered_sg)

inputs = {
    'traces_path': ["/home/golub/msm/data/sgy/SY_seismic_data.sgy", "/home/golub/msm/data/sgy/SY_seismic_data2.sgy"], 
    'read_traces__normalize': False,
}

with open(path_to_map_code, "r") as f:
    map_data = yaml.safe_load(f)

wf_generator = WorkflowGenerator(map_data, ordered_sg, reversed_rel, True)
var_map = wf_generator.get_declaration_file(
    path,
    "/home/golub/execucore_ops/",
    inputs,
    "msm"
)

wf_generator.get_application_file(
    path,
    "test",
    "golub",
    "file://localhost/home/golub/execucore_ops/declaration.toml",
    1,
    inputs,
    {
        "name": "executor",
        "execucore ops path" : "/home/golub/execucore_ops/",
        "type": "ssh",
        "config": {
            "name": "executor",
            "config_path": "~/.ssh/config"
        },
        "workload_manager": "execucore"
    },
    {
        "nodes_limit": 1,
        "cpu_limit": 2,
        "memory_limit": "4G",
        "time_limit": "00-00:30:00"
    },
    var_map
) 

dag_generator = DAGGenerator(map_data, ordered_sg, reversed_rel, True)
dag_generator.get_declaration_file(
    "test_dag.yaml",
    inputs, 
    "/home/golub/msm/data/out",
    "test_dag"
)
