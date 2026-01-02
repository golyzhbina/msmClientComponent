from collections import defaultdict, deque


class Graph:
    #def __init__(self):
    operations: dict = {}  # имя операции -> (inputs, outputs)
    forward_graph: defaultdict  = defaultdict(list) # прямой граф: переменная/операция -> соседи
    reverse_graph: defaultdict  = defaultdict(list) # обратный граф

    def __init__(self, relationship):
        
        self.operations = relationship

        for op, vars in self.operations.items():
            inputs, outputs = vars
            for var in inputs:
                self.forward_graph[var].append(op)
                self.reverse_graph[op].append(var)
            
        
            for var in outputs:
                self.forward_graph[op].append(var)
                self.reverse_graph[var].append(op)
    

    def bfs_forward(self, start_nodes):
        
        visited = set()
        queue = deque(start_nodes)
        
        while queue:
            node = queue.popleft()

            if node not in visited:
                visited.add(node)
                
                for neighbor in self.forward_graph.get(node, []):

                    all_inputs = True
                    if neighbor in self.operations:
                        for input_var in self.operations[neighbor][0]:
                            all_inputs = all_inputs and  input_var in visited
                        
                    if neighbor not in visited and all_inputs:
                        queue.append(neighbor)
        
        return visited
    
    def bfs_backward(self, start_nodes, reachable_set):
    
        visited = set()
        queue = deque(start_nodes)
        
        while queue:
            node = queue.popleft()
            
            if node in reachable_set and node not in visited:
                visited.add(node)
               
                for predecessor in self.reverse_graph.get(node, []):
                    if predecessor not in visited:
                        queue.append(predecessor)
        
        return visited