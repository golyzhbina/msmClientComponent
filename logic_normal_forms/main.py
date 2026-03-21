from pyeda.inter import expr
import re

from typing import Dict, Tuple, List
from collections import deque

def build_knf(inputs: List[str], outputs: List[str], 
                forward_graph: Dict[str, str], 
                reverse_graph: Dict[str, str]) -> Tuple[str, Dict[str, str]]:
    map_name_in_formula = {}
    for i, name in enumerate(forward_graph.keys()):
        name_in_formula = f"x{i}"
        map_name_in_formula[name] = name_in_formula
        map_name_in_formula[name_in_formula] = name

    knf_list = []

    q = deque(outputs)
    visited = set()

    while q:
        var = q.popleft()
        visited.add(var)

        if var in inputs:
            continue

        if len(reverse_graph[var]["output_from"]):
            knf_list.append("(")

        for op in reverse_graph[var]["output_from"]:
            knf_list.append(f"{map_name_in_formula[op]}")
            knf_list.append("|")
        
            for v in forward_graph[op][0]:
                if v not in visited:
                    q.append(v)

        if len(reverse_graph[var]["output_from"]):
            knf_list[-1] = ")"
            knf_list.append("&")

    knf_list.pop()

    knf = expr("".join(knf_list))
    
    return knf, map_name_in_formula
    
def parse_dnf(dnf: str, map_fomula_names: Dict[str, str], relationship: Dict[str, List]) -> List[Dict[str, List]]:

    if not ("And" in dnf) and not ("Or" in dnf):
        paths = [dnf]
    elif not ("And" in dnf) and  ("Or" in dnf):
        paths = [dnf[3:-1]]
    else:
        regexpr = r"And\(([^)]+)\)"
        paths = re.findall(regexpr, dnf)

    paths = [v.split(", ") for v in paths]
    
    paths = [[map_fomula_names[v] for v in path] for path in paths]

    path_rels = [{op : relationship[op] for op in path} for path in paths]
    for path in paths:

        path_rel = {}
        for op in path:
            path_rel[op] = relationship[op]

        path_rels.append(path_rel)

    return path_rels