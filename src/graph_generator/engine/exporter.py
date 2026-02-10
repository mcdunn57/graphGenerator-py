import csv
import os
from typing import List, Dict, Any

class CSVExporter:
    """
    Handles exporting generated data to CSV files.
    """
    def __init__(self, output_dir: str = "generator_output"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        
        # Track which files have initialized headers
        self._initialized_files = set()

    def _get_file_path(self, filename: str) -> str:
        return os.path.join(self.output_dir, filename)

    def _write_batch(self, filename: str, batch: List[Dict[str, Any]], fieldnames: List[str]):
        if not batch:
            return
            
        file_path = self._get_file_path(filename)
        mode = 'a'
        write_header = False
        
        if file_path not in self._initialized_files:
            # Check if file exists to determine if we need header (e.g. if restarting)
            # But normally we overwrite or append during a single run?
            # Let's assume a single run session.
            if not os.path.exists(file_path):
                write_header = True
            self._initialized_files.add(file_path)

        with open(file_path, mode, newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if write_header:
                writer.writeheader()
            writer.writerows(batch)

    def export_nodes(self, label: str, batch: List[Dict[str, Any]]):
        """
        Export a batch of nodes to CSV.
        Filename: Node_<Label>.csv
        """
        if not batch:
            return
            
        filename = f"Node_{label}.csv"
        # Determine fieldnames from first item. 
        # Filter out internal keys starting with '_'
        fieldnames = [k for k in batch[0].keys() if not k.startswith('_')]
        
        # Prepare batch (filter keys)
        clean_batch = [{k: v for k, v in item.items() if k in fieldnames} for item in batch]
        
        self._write_batch(filename, clean_batch, fieldnames)

    def export_relationships(self, rel_type: str, from_label: str, to_label: str, batch: List[Dict[str, Any]]):
        """
        Export a batch of relationships to CSV.
        Filename: Rel_<Type>.csv (or Rel_<Type>_<From>_<To>.csv to be specific)
        """
        if not batch:
            return
            
        filename = f"Rel_{rel_type}_{from_label}_{to_label}.csv"
        
        # Prepare batch items
        # Standardize source_id/target_id
        clean_batch = []
        fieldnames = set()
        
        for item in batch:
            clean_item = {
                ':START_ID': item['_source_id'], # Neo4j import compatible 
                ':END_ID': item['_target_id']
            }
            # Add properties
            for k, v in item.items():
                if not k.startswith('_'):
                    clean_item[k] = v
                    fieldnames.add(k)
            clean_batch.append(clean_item)
            
        # Ensure :START_ID and :END_ID are first
        ordered_fieldnames = [':START_ID', ':END_ID'] + sorted(list(fieldnames))
        
        self._write_batch(filename, clean_batch, ordered_fieldnames)
