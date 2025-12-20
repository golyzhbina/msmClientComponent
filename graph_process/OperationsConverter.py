from typing import List
from .Operation import Operation, OpClass, OpType
from .Variable import Variable

class OprerationsConverter:

    @staticmethod
    def convert_to_ops(ops_descr: dict):

        ops = []
        for op_name, op_descr in ops_descr.items():
            ops.append(Operation(
                name=op_name, 
                inputs=[Variable(name) for name in op_descr["inputs"]],
                outputs=[Variable(name) for name in op_descr["outputs"]],
                func_path=op_descr["func_path"],
                op_class=OpClass(op_descr["op_class"]), 
                op_type=OpType(op_descr["op_type"])
            ))

        return ops