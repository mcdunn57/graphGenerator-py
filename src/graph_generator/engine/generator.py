from typing import Any, Dict, List, Type, Generator, Union
import random
from ..core.provider import Provider
from ..core.registry import Registry
from ..api.fields import Field, ComputedField
from ..api.decorators import ConditionalRule
from ..ingestor.reference import ReferenceStore, ReferenceSource
from ..schema.loader import NodeDefinition, RelationshipDefinition

class BatchGenerator:
    """
    Engine to map Python objects to batched dictionary structures for Neo4j ingestion.
    """
    def __init__(self, provider: Provider, registry: Registry):
        self.provider = provider
        self.registry = registry
        self.ref_store = ReferenceStore()

    def generate_nodes(self, node_def: Union[Type, NodeDefinition], batch_size: int = 1000) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Generates batches of node data based on the @node definition or dynamic NodeDefinition.
        """
        if not hasattr(node_def, '_is_node'):
            raise ValueError(f"{node_def} is not a valid node definition")
        
        count = getattr(node_def, '_count', 0)
        label = getattr(node_def, '_label', 'Unknown')
        
        # Determine accessible fields
        fields = {}
        computed = {}
        is_dynamic = isinstance(node_def, NodeDefinition)

        if is_dynamic:
            fields = node_def.fields
            # Computed fields not supported in dynamic CSV definition yet
        else:
            fields = {k: v for k, v in node_def.__dict__.items() if isinstance(v, Field)}
            computed = {k: v for k, v in node_def.__dict__.items() if isinstance(v, ComputedField)}
        
        # Optimization for CSV-driven nodes (Dynamic)
        source_obj = None
        if is_dynamic and node_def.source_path:
             # Ensure loaded
             source_obj = self.ref_store.get_source(node_def.source_path, sampling="sequential")

        batch = []
        for i in range(count):
            node_data = {}
            instance = None
            if not is_dynamic:
                instance = node_def() # Instantiate for context/computed fields
            
            row_data = {}
            if source_obj:
                try:
                    row_data = source_obj.get_row(i)
                except Exception as e:
                    # If we overshoot, break or error. SchemaLoader should have set count correctly.
                    # But if SchemaLoader used file line count, it includes header?
                    # SchemaLoader: sum(1 for line) - 1. So it should be exact.
                    raise ValueError(f"Failed to fetch row {i} for {node_def.label}: {e}")

            # 1. Generate standard fields
            for name, field in fields.items():
                val = None
                
                # Dynamic Node Optimization: Use pre-fetched row
                if is_dynamic and source_obj and field.column in row_data:
                    val = row_data[field.column]
                else:
                    # Check for Reference Binding (Standard logic)
                    if field.reference or field.source:
                        ref_source = None
                        if isinstance(field.reference, ReferenceSource):
                            ref_source = field.reference
                        elif field.source:
                            # Resolve string path via store
                            ref_source = self.ref_store.get_source(field.source, sampling=field.strategy or "weighted")
                        
                        if ref_source:
                             # Sample from source
                             # Note: If is_dynamic and we already have source_obj == ref_source, we shouldn't sample again!
                             # But here we are in "else" or if field.column not in row_data.
                             # If field.source != node_def.source_path, we sample.
                             if is_dynamic and field.source == node_def.source_path:
                                  # Should have been caught above. If not in row_data, maybe error?
                                  pass
                             else:
                                 col = field.column or name 
                                 try:
                                     val = ref_source.sample(col, count=1)[0]
                                 except Exception as e:
                                     raise ValueError(f"Failed to sample reference for field {name}: {e}")

                    # If no reference or failed (though we raised), use provider
                    if val is None:
                        val = field.generate(self.provider)
                
                node_data[name] = val
                if instance:
                    setattr(instance, name, val)
                
                # If identifier/unique, register it
                if field.unique:
                    self.registry.register(label, val)
            
            # 2. Compute calculated fields (Only for class-based)
            if not is_dynamic:
                for name, field in computed.items():
                    val = field.compute(instance)
                    node_data[name] = val
                    setattr(instance, name, val)

            batch.append(node_data)
            
            if len(batch) >= batch_size:
                yield batch
                batch = []
        
        if batch:
            yield batch

    def generate_relationships(self, rel_def: Union[Type, RelationshipDefinition], batch_size: int = 1000) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Generates batches of relationship data based on the definition.
        """
        if not hasattr(rel_def, '_is_relationship'):
            raise ValueError(f"{rel_def} is not a valid relationship definition")
            
        rel_type = getattr(rel_def, '_type')
        from_node = getattr(rel_def, '_from_node')
        to_node = getattr(rel_def, '_to_node')
        
        # Check for explicit cardinality dictionary or ConditionalRule
        cardinality = getattr(rel_def, 'cardinality', None)

        source_ids = self.registry.get_all(from_node)
        target_ids = self.registry.get_all(to_node)
        
        if not source_ids or not target_ids:
            return

        batch = []
        fields = {}
        is_dynamic = isinstance(rel_def, RelationshipDefinition)
        
        if is_dynamic:
            fields = rel_def.fields
        else:
            fields = {k: v for k, v in rel_def.__dict__.items() if isinstance(v, Field)}
        
        for source_id in source_ids:
            # Determine number of relationships
            num_rels = 1 # Default
            
            if isinstance(cardinality, dict):
                min_rels = cardinality.get('min', 1)
                max_rels = cardinality.get('max', 1)
                num_rels = random.randint(min_rels, max_rels)
            elif isinstance(cardinality, ConditionalRule):
                num_rels = cardinality.if_false 
            else:
                 num_rels = random.randint(1, 3) # Fallback

            targets = random.sample(target_ids, min(len(target_ids), num_rels))
            
            for target_id in targets:
                rel_data = {
                    '_source_id': source_id,
                    '_target_id': target_id
                }
                instance = None
                if not is_dynamic:
                    instance = rel_def()
                
                # Generate properties
                for name, field in fields.items():
                    val = field.generate(self.provider)
                    rel_data[name] = val
                    if instance:
                        setattr(instance, name, val)
                    
                batch.append(rel_data)
                
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
                    
        if batch:
            yield batch
