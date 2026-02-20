from comp_model.ComputeModel import ComputeModel
from generators.DAGGenerator import DAGGenerator

import os
from pathlib import Path
import json


path = Path(os.path.dirname(os.path.abspath(__file__))) / "data" / "yaml" 
path_to_graph = path / "graph.yaml"
cm = ComputeModel(path_to_graph)

inputs = ["veldata_path", "rec_coords_path", "region_coords", "traces_path", "tensor"]
outputs = ["df"]

all_paths = cm.get_paths(inputs, outputs)


     

