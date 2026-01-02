from comp_model.ComputeModel import ComputeModel
from generators.DAGGenerator import DAGGenerator

import os
from pathlib import Path


path = Path(os.path.dirname(os.path.abspath(__file__))) / "data" / "yaml" 
path_to_graph = path / "graph.yaml"
cm = ComputeModel(path_to_graph)

inputs = ["veldata_path", "rec_coords_path", "region_coords", "traces_path"]
outputs = ["cube_wo_tm", "df", "maxes"]

subgraph = cm.get_algoritm(inputs, outputs)
genetor = DAGGenerator(path / "mapModelToCode.yaml", subgraph)
inputs = genetor.get_inputs()
     

