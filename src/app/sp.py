import sys
from heapq import heappush, heappop

def dijkstra(graph: dict, source: int, target: int = None):
    """
    Find the shortest path between schools.
    
    Args:
        graph (dict): School connections with costs
        source (int): Starting school ID
        target (int): Ending school ID (optional)
    
    Returns:
        If target given: (cost, path)
        If no target: (all distances, all paths)
    """
    distances: dict = {node: float('inf') for node in graph}
    distances[source] = 0
    spf: dict = {source: []}  # shortest path forest
    pq: list = [(0, source)]
    visited: set = set()
    
    while pq:
        current_dist: int
        current: int
        current_dist, current = heappop(pq)
        
        if current in visited:
            continue
        visited.add(current)
        
        if target and current == target:
            break
            
        for neighbor, weight in graph[current].items():
            distance: int = current_dist + weight
            
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                spf[neighbor] = spf[current] + [current]
                heappush(pq, (distance, neighbor))
    
    # If target specified, return path to target
    if target:
        if distances[target] == float('inf'):
            return None, []
        path: list = spf[target] + [target]
        return distances[target], path
    
    # ✅ Return all distances and SPF for debugging
    return distances, spf