from collections import deque
from .Graph import Graph

class SubgraphGetter:    
    def __init__(self, graph: Graph):

        self.graph = graph 
    
    
    def find_minimal_subgraph(self, input_vars, output_vars):
        """
        Находит минимальный связный подграф, содержащий все входные и выходные переменные
        """
        reachable_from_inputs = self._bfs_forward(input_vars)

        for var in output_vars:
            if var not in reachable_from_inputs:
                raise Exception("При данных входных переменных выходные переменные недостижимы")
        
        necessary_nodes = self._bfs_backward(output_vars, reachable_from_inputs)

        return necessary_nodes
    
    def bfs_forward(self, start_nodes):
        visited = set()
        queue = deque(start_nodes)
        
        while queue:
            node = queue.popleft()

            if node not in visited:
                visited.add(node)
                
                for neighbor in self.graph.graph.get(node, []):

                    all_inputs = True
                    if neighbor in self.graph.operations:
                        for input_var in self.graph.operations[neighbor][0]:
                            all_inputs = all_inputs and input_var in visited
                        
                    if neighbor not in visited and all_inputs:
                        queue.append(neighbor)
        
        return visited
    
    def _bfs_backward(self, start_nodes, reachable_set):
        """BFS от стартовых узлов по обратному графу, но только в пределах reachable_set"""
        visited = set()
        queue = deque(start_nodes)
        
        while queue:
            node = queue.popleft()
            
            if node in reachable_set and node not in visited:
                visited.add(node)
               
                for predecessor in self.graph.reverse_graph.get(node, []):
                    if predecessor not in visited:
                        queue.append(predecessor)
        
        return visited
    
    def get_operations_in_subgraph(self, nodes):
        """Получить операции, входящие в подграф"""
        return [node for node in nodes if node in self.graph.operations]
    
    def get_variables_in_subgraph(self, nodes):
        """Получить переменные, входящие в подграф"""
        return [node for node in nodes if node not in self.graph.operations]
    
    def get_execution_order(self, nodes):
        """Получить порядок выполнения операций в подграфе"""
        operations = self.get_operations_in_subgraph(nodes)
        
        # Простой топологический порядок (можно улучшить)
        execution_order = []
        visited = set()
        
        def visit(op):
            if op not in visited:
                visited.add(op)
                inputs, _ = self.graph.operations[op]
                # Сначала посещаем зависимости
                for input_var in inputs:
                    if input_var in self.graph.reverse_graph:
                        for pred_op in self.graph.reverse_graph[input_var]:
                            if pred_op in operations:
                                visit(pred_op)
                execution_order.append(op)
        
        for op in operations:
            visit(op)
            
        return execution_order