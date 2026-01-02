from .Generator import Generator
from collections import OrderedDict

class DAGGenerator(Generator):

    def __init__(self, filename: str, subgraph: OrderedDict, use_parallelism: bool = False):
        super().__init__(filename, subgraph)
        self.use_parallelism = use_parallelism

