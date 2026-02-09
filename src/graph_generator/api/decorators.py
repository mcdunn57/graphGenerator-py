from typing import Any, Callable, Optional, Union, Dict

def node(label: str, count: int = 1):
    """
    Decorator to define a Node in the graph schema.
    """
    def decorator(cls):
        cls._is_node = True
        cls._label = label
        cls._count = count
        return cls
    return decorator

def relationship(type: str, from_node: str, to_node: str):
    """
    Decorator to define a Relationship between nodes.
    """
    def decorator(cls):
        cls._is_relationship = True
        cls._type = type
        cls._from_node = from_node
        cls._to_node = to_node
        return cls
    return decorator

class ConditionalRule:
    """
    Defines conditional cardinality logic.
    """
    def __init__(self, condition: Callable, if_true: int, if_false: int):
        self.condition = condition
        self.if_true = if_true
        self.if_false = if_false

class ReferenceSource:
    """
    Placeholder for ReferenceSource to be used in decorators.
    Will be fully implemented in the Ingestor module.
    """
    def __init__(self, path: str, sampling: str = "weighted"):
        self.path = path
        self.sampling = sampling
