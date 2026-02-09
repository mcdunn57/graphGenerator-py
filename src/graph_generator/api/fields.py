from typing import Any, Callable, Optional, Union, Dict
from ..core.provider import Provider

class Field:
    """
    Descriptor for defining node properties with formatters, constraints, and reference bindings.
    """
    def __init__(
        self, 
        formatter: Optional[str] = None, 
        unique: bool = False, 
        rule: Optional[str] = None,
        min: Optional[int] = None,
        max: Optional[int] = None,
        source: Optional[str] = None,
        strategy: Optional[str] = None,
        reference: Any = None,
        column: Optional[str] = None,
        **kwargs
    ):
        self.formatter = formatter
        self.unique = unique
        self.rule = rule
        self.min = min
        self.max = max
        self.source = source
        self.strategy = strategy
        self.reference = reference
        self.column = column
        self.kwargs = kwargs

    def generate(self, provider: Provider) -> Any:
        # Simple generation logic calling the provider
        if self.formatter:
            kwargs = self.kwargs.copy()
            if self.min is not None: kwargs['min'] = self.min
            if self.max is not None: kwargs['max'] = self.max
            return provider.generic(self.formatter, **kwargs)
        return None

class ComputedField:
    """
    Field calculated based on other fields in the same node (intra-node calculation).
    """
    def __init__(self, fn: Callable[[Any], Any]):
        self.fn = fn

    def compute(self, instance: Any) -> Any:
        return self.fn(instance)
