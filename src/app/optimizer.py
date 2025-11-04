from app import db  # ✅ Correct import for database
from app.models import School, TransportationCost  # ✅ Correct model imports
from app import sp  # ✅ Import your sp module
from typing import Dict, List, Optional, Union, Tuple, Any


class ResourceOptimizer:
    """
    Optimizes resource distribution between schools using Dijkstra's algorithm.
    Finds the lowest-cost path for transferring resources.
    
    Attributes:
        graph (Dict[int, Dict[int, int]]): Graph representation of school connections
        school_names (Dict[int, str]): Mapping of school IDs to names
        bidirectional (bool): Whether to treat routes as bidirectional
    """
    def __init__(self, bidirectional: bool = False) -> None:
        """
        Initialize optimizer with empty graph.
        
        Args:
            bidirectional (bool): If True, creates bidirectional edges for routes
        """
        # Initialize optimizer with empty graph
        self.graph: Dict[int, Dict[int, int]] = {}
        self.school_names: Dict[int, str] = {}
        self.bidirectional: bool = bidirectional
    
    def build_graph_from_database(self) -> Dict[int, Dict[int, int]]:
        """
        Build graph representation from database transportation costs.
        
        Queries all schools and transportation costs to create a graph
        where nodes are schools and edges are transportation costs.
        
        Returns:
            Dict[int, Dict[int, int]]: Graph with school IDs as keys and 
                                     connected schools with costs as values
        """
        # Fresh rebuild each call
        self.graph.clear()
        self.school_names.clear()

        # Query all schools from database
        schools: List[School] = School.query.all()
        
        # Initialize graph with school nodes
        for school in schools:
            self.graph[school.id] = {}  # Empty dict for each school
            self.school_names[school.id] = school.name  # Store names for display
        
        # Query all transportation costs
        costs: List[TransportationCost] = TransportationCost.query.all()
        
        # Add edges (connections) with costs
        for cost in costs:
            if cost.from_school_id in self.graph:
                self.graph[cost.from_school_id][cost.to_school_id] = cost.cost
            if self.bidirectional and cost.to_school_id in self.graph:
                # only add reverse if not defined
                self.graph[cost.to_school_id].setdefault(cost.from_school_id, cost.cost)
        
        return self.graph
    
    def find_optimal_path(self, source_school_id: int, target_school_id: int) -> Dict[str, Any]:
        """
        Find the optimal (lowest cost) path between two schools.
        
        Uses Dijkstra's algorithm to calculate the shortest path based on
        transportation costs between schools.
        
        Args:
            source_school_id (int): Starting school ID
            target_school_id (int): Destination school ID
            
        Returns:
            Dict[str, Any]: Result dictionary containing:
                - success (bool): Whether path was found successfully
                - message (str): Status or error message
                - path (List[int]): School IDs in optimal path (if successful)
                - path_names (List[str]): School names in optimal path (if successful)
                - total_cost (int): Total transportation cost (if successful)
                - num_transfers (int): Number of transfers required (if successful)
                - debug (Dict): Debug information with distances and SPF tree (if successful)
        """
        if source_school_id == target_school_id:
            return {'success': False, 'message': 'Source and target schools cannot be the same.'}

        self.build_graph_from_database()
        
        try:
            assert source_school_id in self.graph, f'Source school (ID: {source_school_id}) not found in system.'
            assert target_school_id in self.graph, f'Target school (ID: {target_school_id}) not found in system.'
            
            total_cost: int
            path: List[int]
            total_cost, path = sp.dijkstra(self.graph, source_school_id, target_school_id)
            assert path, 'No valid path exists between these schools. Check transportation costs.'
            
            all_distances: Dict[int, int]
            spf: Dict[int, List[int]]
            all_distances, spf = sp.dijkstra(self.graph, source_school_id, None)
            
        except AssertionError as e:
            return {'success': False, 'message': str(e)}
        except Exception as e:
            return {'success': False, 'message': f'Error calculating optimal path: {e}'}

        path_names: List[str] = [self.school_names.get(sid, f'Unknown School (ID: {sid})') for sid in path]
        
        spf_names: Dict[str, List[str]] = {}
        for node_id, path_list in spf.items():
            node_name: str = self.school_names.get(node_id, f'ID:{node_id}')
            spf_names[node_name] = [self.school_names.get(p, f'ID:{p}') for p in path_list]

        return {
            'success': True,
            'path': path,
            'path_names': path_names,
            'total_cost': total_cost,
            'num_transfers': len(path) - 1,
            'message': f'Optimal path found with {len(path) - 1} transfer(s).',
            'debug': {
                'distances': all_distances,
                'spf': spf_names,
                'source_id': source_school_id
            }
        }