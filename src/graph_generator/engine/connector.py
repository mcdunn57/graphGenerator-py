from neo4j import GraphDatabase, Driver
from typing import List, Dict, Any, Optional

class Neo4jConnector:
    """
    Handles connection to Neo4j and executes batched ingestion queries using UNWIND.
    """
    def __init__(self, uri: str, auth: tuple):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        
    def close(self):
        self.driver.close()
        
    def verify_connectivity(self):
        self.driver.verify_connectivity()

    def ingest_nodes(self, label: str, batch: List[Dict[str, Any]]):
        """
        Ingest a batch of nodes using UNWIND.
        """
        if not batch:
            return

        # Prepare properties string dynamically based on keys in the first item
        # (Assuming homogeneous batch)
        keys = [k for k in batch[0].keys() if not k.startswith('_')]
        
        # SET n += row, but we need to match keys properly if strictly typed?
        # SET n = row replaces everything.
        # SET n += row updates/adds properties.
        
        query = f"""
        UNWIND $batch AS row
        CREATE (n:{label})
        SET n += row
        """
        
        # Filter out internal keys (underscored) from the batch before sending?
        # Or let Neo4j handle it? Usually better to clean up.
        cleaned_batch = [{k: v for k, v in item.items() if not k.startswith('_')} for item in batch]
        
        with self.driver.session() as session:
            session.run(query, batch=cleaned_batch)
            
    def ingest_relationships(self, rel_type: str, from_label: str, to_label: str, batch: List[Dict[str, Any]]):
        """
        Ingest a batch of relationships using UNWIND.
        Expects _source_id and _target_id in the batch items.
        Assumes 'id' property on nodes for matching.
        """
        if not batch:
            return

        query = f"""
        UNWIND $batch AS row
        MATCH (source:{from_label} {{id: row._source_id}})
        MATCH (target:{to_label} {{id: row._target_id}})
        CREATE (source)-[r:{rel_type}]->(target)
        SET r += row.properties
        """
        
        # Prepare properties sub-dictionary
        clean_batch = []
        for item in batch:
            props = {k: v for k, v in item.items() if not k.startswith('_')}
            clean_item = {
                '_source_id': item['_source_id'],
                '_target_id': item['_target_id'],
                'properties': props
            }
            clean_batch.append(clean_item)
        
        with self.driver.session() as session:
            session.run(query, batch=clean_batch)
