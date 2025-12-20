from typing import List, Dict
from .Operation import Operation, OpClass, OpType

class SubgraphAnalyzer:
    def group_operations(self, ops: List[Dict]):
        classes = {}

        for op in ops:
            classes[op["op_descr"]["op_class"]] = []

        for op in ops:
            classes[op["op_descr"]["op_class"]].append(op)

        return classes
    
    def check_conflicts(self, classes: Dict[OpClass, List[Operation]], ops: List[str]):
        
        for _, class_ops in classes.items():
            if len(class_ops) > 1:
                if class_ops[0]["op_descr"]["op_type"] == OpType.SINGLE.value:
                    print("Выберите одну из операций")
                    for i, op in enumerate(class_ops):
                        print(f"{i} - {op['op_name']}")

                    idx = int(input("Введите номер операции: "))
                    single_op = class_ops[idx]
                    for op in class_ops:
                        if op != single_op:
                            ops.remove(op)
                else:
                    print("Выберите нужные операции")
                    for i, op in enumerate(class_ops):
                        print(f"{i} - {op['op_name']}")

                    ids = [int(v) for v in input("Введите их номера через пробел в порядке выполнения: ").split()]
                    multiple_ops = [class_ops[i] for i in ids]
                    for op in class_ops:
                        if op not in multiple_ops:
                            ops.remove(op)

                    start_idx = min(list(map(lambda x: ops.index(x), multiple_ops)))
                    for op in multiple_ops:
                        ops.remove(op)

                    for i in range(len(ids)):
                        ops.insert(i + start_idx, multiple_ops[i])

    def create_variable_dict(self, ops: List[Dict]):

        variables = {}

        for op in ops:
            for var in op["op_descr"]["inputs"] + op["op_descr"]["outputs"]:
                variables[var] = {"input_for" : [], "output_from" : []}

        for op in ops:
            for var in op["op_descr"]["inputs"]:
                variables[var]["input_for"].append(op["op_name"])
            for var in op["op_descr"]["outputs"]:
                variables[var]["output_from"].append(op["op_name"])

        return variables

        

            


                    
            
                

