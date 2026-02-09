from neo4j import Driver
from typing import List

class InsufficientSchemaError(Exception):
    pass

class SchemaValidator:
    """
    Validates that the define schema elements (Labels, Relationship Types) 
    exist in the database buffer validation.
    """
    def __init__(self, connector):
        self.driver = connector.driver
        
    def validate_node_labels(self, labels: List[str]):
        """
        Checks if the provided labels exist in the database.
        """
        with self.driver.session() as session:
            result = session.run("CALL db.labels()")
            existing_labels = {record["label"] for record in result}
            
        missing = [l for l in labels if l not in existing_labels]
        if missing:
            raise InsufficientSchemaError(f"Labels not found in database: {missing}. Please apply schema constraints/indexes first.")

    def validate_relationship_types(self, types: List[str]):
        """
        Checks if the provided relationship types exist in the database.
        """
        with self.driver.session() as session:
            result = session.run("CALL db.relationshipTypes()")
            existing_types = {record["relationshipType"] for record in result}
            
        missing = [t for t in types if t not in existing_types]
        if missing:
            raise InsufficientSchemaError(f"Relationship types not found in database: {missing}.")
