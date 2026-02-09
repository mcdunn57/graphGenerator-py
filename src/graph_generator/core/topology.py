import networkx as nx
from typing import Optional

class Topology:
    """
    Integrates with NetworkX to apply graph-generative models ensuring 
    structural fidelity (e.g., Small World networks).
    """
    def __init__(self):
        self.graph = nx.Graph()

    def generate_watts_strogatz(self, n: int, k: int, p: float) -> nx.Graph:
        """
        Generates a Watts-Strogatz small-world graph.
        
        :param n: The number of nodes
        :param k: Each node is joined with its k nearest neighbors in a ring topology.
        :param p: The probability of rewiring each edge.
        """
        self.graph = nx.watts_strogatz_graph(n, k, p)
        return self.graph

    def generate_barabasi_albert(self, n: int, m: int) -> nx.Graph:
        """
        Generates a Barabasi-Albert preferential attachment graph.
        
        :param n: Number of nodes
        :param m: Number of edges to attach from a new node to existing nodes
        """
        self.graph = nx.barabasi_albert_graph(n, m)
        return self.graph
