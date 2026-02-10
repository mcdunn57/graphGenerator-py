import os
import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from ..api.fields import Field

@dataclass
class NodeDefinition:
    label: str
    source_path: str
    count: int = 0
    fields: Dict[str, Field] = field(default_factory=dict)
    # To mimic the decorated class interface for now
    _is_node: bool = True
    
    @property
    def _label(self): return self.label
    
    @property
    def _count(self): return self.count

@dataclass
class RelationshipDefinition:
    type: str
    source_path: str
    from_node: str
    to_node: str
    cardinality: Any = None # Placeholder
    fields: Dict[str, Field] = field(default_factory=dict)
    _is_relationship: bool = True
    
    @property
    def _type(self): return self.type
    
    @property
    def _from_node(self): return self.from_node

    @property
    def _to_node(self): return self.to_node

class SchemaLoader:
    """
    Scans a directory for CSV files to infer schema definitions.
    Expects specific naming conventions or config to distinguish Nodes vs Rels.
    Default Convention:
    - Nodes: Node_<Label>.csv
    - Rels: Rel_<Type>_<From>_<To>.csv (Simplified for now: Rel_<Type>.csv and we might need metadata for from/to)
    
    For now, let's assume a metadata file or strictly inferred simple convention.
    Refactoring Plan didn't specify strict naming, so I'll implement a flexible one.
    """
    def __init__(self, key_column: str = "id"):
        self.nodes: List[NodeDefinition] = []
        self.relationships: List[RelationshipDefinition] = []

    def load_from_directory(self, path: str):
        if not os.path.isdir(path):
            raise ValueError(f"Path is not a directory: {path}")

        files = [f for f in os.listdir(path) if f.endswith('.csv')]
        
        for f in files:
            full_path = os.path.join(path, f)
            # Naive heuristics for now
            if f.startswith("Node_"):
                self._load_node(full_path, f)
            elif f.startswith("Rel_"):
                self._load_rel(full_path, f)
            else:
                # Default to Node if ambiguous? Or skip?
                # Let's assume Node if not specified.
                pass

    def _load_node(self, path: str, filename: str):
        # Filename format: Node_<Label>.csv
        label = filename.replace("Node_", "").replace(".csv", "")
        
        # Read header only to determine fields
        df = pd.read_csv(path, nrows=0)
        columns = df.columns.tolist()
        
        # Count rows efficiently?
        # For large files, maybe don't count everything or lazy load. 
        # But we need count for the loop.
        # Let's just count.
        with open(path) as f:
             count = sum(1 for line in f) - 1 # minus header
        
        fields = {}
        for col in columns:
            # Create a Field that points to this file/column
            # source=path, column=col, strategy="sequential" (to replicate file rows)
            fields[col] = Field(source=path, column=col, strategy="sequential")
            
        def_node = NodeDefinition(
            label=label,
            source_path=path,
            count=count,
            fields=fields
        )
        self.nodes.append(def_node)

    def _load_rel(self, path: str, filename: str):
        # Filename format: Rel_<Type>.csv
        # Problem: We need From/To nodes. 
        # Solution: Expect columns '_from' and '_to' in the CSV? 
        # Or require filename convention Rel_<Type>_<From>_<To>.csv
        
        name_parts = filename.replace("Rel_", "").replace(".csv", "").split("_")
        if len(name_parts) >= 3:
            rel_type = name_parts[0]
            from_node = name_parts[1]
            to_node = name_parts[2]
        else:
            # Fallback or error?
            rel_type = name_parts[0]
            from_node = "Unknown" 
            to_node = "Unknown"
            # This is risky, but let's proceed.

        df = pd.read_csv(path, nrows=0)
        columns = df.columns.tolist()
        
        fields = {}
        for col in columns:
            if col.lower() in ['_from', '_to', '_start', '_end']:
                continue
            fields[col] = Field(source=path, column=col, strategy="sequential")

        def_rel = RelationshipDefinition(
            type=rel_type,
            source_path=path,
            from_node=from_node,
            to_node=to_node,
            fields=fields
        )
        self.relationships.append(def_rel)
