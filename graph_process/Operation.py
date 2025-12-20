from dataclasses import dataclass
from typing import List
from enum import Enum
from .Variable import Variable


class OpClass(Enum):
    READ_TRACES = "read_traces"
    FILT_TRACES = "filt_traces"

    GET_STAT_CORS = "get_stat_cors"
    ADD_STAT_CORS = "add_stat_cors"

    READ_VELDATA = "read_veldata"
    CREATE_VELMODEL = "create_velmodel"

    CREATE_REGION = "create_region"

    READ_RECS = "read_recs"
    GET_NET_COORDS = "get_net_coords"

    SOLVE_EIKONAL = "solve_eikonal"

    GET_TRAVEL_TIME = "get_travel_time"

    ROTATE_TENSOR = "rotate_tensor"
    GENERATE_TENSORS = "generate_tensors"

    GET_CUBE = "get_cube"

    GET_DF = "get_df"

    GET_MAXES = "get_maxes"
    FILT_MAXES = "filt_maxes"

    PLOT_DF = "plot_df"
    PLOT_MAXES_AT_DF = "plot_maxes_at_df"
    PLOT_SLICE = "plot_slice"
    PLOT_ALL_MAXES_ON_TIMELINE = "plot_all_maxes_on_timeline"
    PLOT_ALL_MAXES_ON_PLANE = "plot_all_maxes_on_plane"




class OpType(Enum):
    SINGLE = "single"
    MULTIPLE = "multiple"


@dataclass
class Operation:
    name: str
    inputs: List[Variable]
    outputs: List[Variable]
    func_path: str 
    op_class: OpClass
    op_type: OpType


