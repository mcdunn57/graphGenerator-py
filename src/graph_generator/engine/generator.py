from typing import Any, Dict, List, Type, Generator
import random
from ..core.provider import Provider
from ..core.registry import Registry
from ..api.fields import Field, ComputedField
from ..api.decorators import ConditionalRule
from ..ingestor.reference import ReferenceStore, ReferenceSource

class BatchGenerator:
    """
    Engine to map Python objects to batched dictionary structures for Neo4j ingestion.
    """
    def __init__(self, provider: Provider, registry: Registry):
        self.provider = provider
        self.registry = registry
        self.ref_store = ReferenceStore()

    def generate_nodes(self, node_def: Type, batch_size: int = 1000) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Generates batches of node data based on the @node definition.
        """
        if not hasattr(node_def, '_is_node'):
            raise ValueError(f"{node_def} is not a valid @node definition")
        
        count = getattr(node_def, '_count', 0)
        label = getattr(node_def, '_label', 'Unknown')
        
        # Inspect class for Fields
        fields = {k: v for k, v in node_def.__dict__.items() if isinstance(v, Field)}
        computed = {k: v for k, v in node_def.__dict__.items() if isinstance(v, ComputedField)}
        
        batch = []
        for _ in range(count):
            node_data = {}
            instance = node_def() # Instantiate for context/computed fields
            
            # 1. Generate standard fields
            for name, field in fields.items():
                val = None
                
                # Check for Reference Binding
                if field.reference or field.source:
                    source_obj = None
                    if isinstance(field.reference, ReferenceSource):
                        source_obj = field.reference
                    elif field.source:
                        # Resolve string path via store
                        source_obj = self.ref_store.get_source(field.source, sampling=field.strategy or "weighted")
                    
                    if source_obj:
                         # Sample from source
                         col = field.column or name # Use field name as column if not specified? Or error?
                         # The sample method returns a list, take first item
                         try:
                             val = source_obj.sample(col, count=1)[0]
                         except Exception as e:
                             # Fallback or re-raise?
                             raise ValueError(f"Failed to sample reference for field {name}: {e}")

                # If no reference or failed (though we raised), use provider
                if val is None:
                    val = field.generate(self.provider)
                
                node_data[name] = val
                setattr(instance, name, val)
                
                # If identifier/unique, register it
                if field.unique:
                    self.registry.register(label, val)
            
            # 2. Compute calculated fields
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



# ... existing code ...

    def generate_relationships(self, rel_def: Type, batch_size: int = 1000) -> Generator[List[Dict[str, Any]], None, None]:
        """
        Generates batches of relationship data based on the @relationship definition.
        """
        if not hasattr(rel_def, '_is_relationship'):
            raise ValueError(f"{rel_def} is not a valid @relationship definition")
            
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
        fields = {k: v for k, v in rel_def.__dict__.items() if isinstance(v, Field)}
        
        for source_id in source_ids:
            # Determine number of relationships
            num_rels = 1 # Default
            
            if isinstance(cardinality, dict):
                min_rels = cardinality.get('min', 1)
                max_rels = cardinality.get('max', 1)
                num_rels = random.randint(min_rels, max_rels)
            elif isinstance(cardinality, ConditionalRule):
                # TODO: To clear evaluating the condition, we need the SOURCE NODE instance/properties.
                # The Registry currently only stores IDs.
                # For now, we fall back to 'if_false' or use a callback mechanism if implemented.
                # Assuming 'if_true' requires context we don't have yet in this bulk mode.
                num_rels = cardinality.if_false 
                # Ideally: node = self.registry.get_node(source_id) -> num_rels = rule.evaluate(node)
            else:
                 num_rels = random.randint(1, 3) # Fallback

            targets = random.sample(target_ids, min(len(target_ids), num_rels))
            
            for target_id in targets:
                rel_data = {
                    '_source_id': source_id,
                    '_target_id': target_id
                }
                instance = rel_def()
                
                # Generate properties
                for name, field in fields.items():
                    val = field.generate(self.provider)
                    rel_data[name] = val
                    setattr(instance, name, val)
                    
                batch.append(rel_data)
                
                if len(batch) >= batch_size:
                    yield batch
                    batch = []
                    
        if batch:
            yield batch
