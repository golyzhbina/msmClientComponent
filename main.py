from comp_model.ComputeModel import ComputeModel
from generators import DAGGenerator, WorkflowGenerator

import os
from pathlib import Path
import json


path = Path(os.path.dirname(os.path.abspath(__file__)))
path_to_yamls = path / "data" / "yaml" 
path_to_graph = path_to_yamls / "graph.yaml"

cm = ComputeModel(path_to_graph)
inputs = ["traces_path"]
outputs = ["hilb_traces"]

subgraph, all_paths = cm.get_paths(inputs, outputs)

use_paths = cm.clear_paths_filtration(outputs, subgraph, all_paths)
rel_algo = cm.cvrt_to_relations(all_paths[0]["nodes"], all_paths[0]["edges"])
ordered_sg = cm.get_ordered_subgraph(rel_algo)
ordered_sg = cm.delete_fictive_ops(ordered_sg)
reversed_rel = cm.get_reversed_relations(ordered_sg)

wf_generator = WorkflowGenerator(path_to_yamls / "mapModelToWFOps.yaml", ordered_sg, reversed_rel)
inputs = {
    'read_traces':  
     {'filename': "/home/golub/msm/data/sgy/SY_seismic_data.sgy", 
      'normalize': False}
    }

var_map = wf_generator.get_declaration_file(
    path,
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

dag_generator = DAGGenerator(path_to_yamls / "mapModelToCode.yaml", ordered_sg, reversed_rel)
dag_generator.get_declaration_file(
    "test_dag.yaml",
    inputs, 
    "test_dag"
)
