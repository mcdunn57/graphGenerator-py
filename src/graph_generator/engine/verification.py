from neo4j import GraphDatabase
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class GraphVerifier:
    """
    Suite of validation gates to confirm the generated graph's health and consistency.
    """
    def __init__(self, uri: str, auth: tuple):
        self.driver = GraphDatabase.driver(uri, auth=auth)
        
    def close(self):
        self.driver.close()

    def check_path_integrity(self, start_label: str, end_label: str, rel_type: str, max_depth: int = 5) -> Dict[str, Any]:
        """
        Verifies connectivity between critical node types using shortestPath.
        Returns the number of paths found.
        """
        query = f"""
        MATCH (start:{start_label}), (end:{end_label})
        MATCH p = shortestPath((start)-[:{rel_type}*..{max_depth}]->(end))
        RETURN count(p) as path_count
        """
        try:
            with self.driver.session() as session:
                result = session.run(query).single()
                count = result["path_count"]
                logger.info(f"Path Integrity Check ({start_label}->{end_label}): Found {count} paths.")
                return {"connected_paths": count}
        except Exception as e:
            logger.error(f"Path Integrity Check failed: {e}")
            return {"error": str(e)}

    def check_temporal_consistency(self, start_label: str, rel_type: str, start_date_prop: str, rel_date_prop: str):
        """
        Ensures relationship timestamps are legally after the node creation timestamp.
        Returns count of violations.
        """
        query = f"""
        MATCH (n:{start_label})-[r:{rel_type}]->(m)
        WHERE r.{rel_date_prop} < n.{start_date_prop}
        RETURN count(r) as violations
        """
        try:
            with self.driver.session() as session:
                result = session.run(query).single()
                violations = result["violations"]
                if violations > 0:
                    logger.warning(f"Temporal Consistency Violation: {violations} relationships predate their source node.")
                return violations
        except Exception as e:
            logger.error(f"Temporal Consistency Check failed: {e}")
            return -1

    def check_cardinality(self, start_label: str, rel_type: str, min_count: int, max_count: int):
        """
        Verifies that nodes have the expected number of relationships.
        Returns stats on nodes violating constraints.
        """
        query = f"""
        MATCH (n:{start_label})
        OPTIONAL MATCH (n)-[r:{rel_type}]->()
        WITH n, count(r) as rel_count
        WHERE rel_count < {min_count} OR rel_count > {max_count}
        RETURN count(n) as violations, avg(rel_count) as avg_rels
        """
        try:
            with self.driver.session() as session:
                result = session.run(query).single()
                return {
                    "violations": result["violations"],
                    "avg_rels": result["avg_rels"]
                }
        except Exception as e:
            logger.error(f"Cardinality Check failed: {e}")
            return {}

    def mock_audit(self, validation_query: str):
        """
        Runs a custom domain-specific validation query (Mock Audit).
        e.g., matching sums across related nodes.
        """
        try:
            with self.driver.session() as session:
                result = session.run(validation_query)
                # Assume query returns violations or stats
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Mock Audit failed: {e}")
            return []
            
    def check_pii_collision(self, label: str, pii_prop: str, blacklist: List[str]):
        """
        Checks if any generated values match a provided blacklist of real PII.
        This is a client-side check fetching data or server-side if blacklist is small.
        For large blacklists, this approach needs optimization (e.g. load blacklist to DB).
        """
        if not blacklist:
            return 0
            
        # Unwind blacklist parameter
        query = f"""
        UNWIND $blacklist as forbidden
        MATCH (n:{label})
        WHERE n.{pii_prop} = forbidden
        RETURN count(n) as collisions
        """
        try:
            with self.driver.session() as session:
                result = session.run(query, blacklist=blacklist).single()
                collisions = result["collisions"]
                if collisions > 0:
                    logger.critical(f"PII COLLISION DETECTED: {collisions} records match blacklist!")
                return collisions
        except Exception as e:
            logger.error(f"PII Check failed: {e}")
            return -1
