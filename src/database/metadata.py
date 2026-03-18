import yaml
from pathlib import Path

class MetadataManager:
    def __init__(self, dictionary_path: str = "data/dictionary.yaml"):
        self.dictionary_path = Path(dictionary_path)
        self.metadata = self._load_dictionary()

    def _load_dictionary(self):
        if not self.dictionary_path.exists():
            return {}
        with open(self.dictionary_path, "r") as f:
            return yaml.safe_load(f)

    def get_table_description(self, table_name: str):
        return self.metadata.get("tables", {}).get(table_name, {}).get("description", "")

    def get_column_description(self, table_name: str, column_name: str):
        return self.metadata.get("tables", {}).get(table_name, {}).get("columns", {}).get(column_name, "")

    def get_full_context(self):
        """Returns a string representation of the dictionary for the LLM prompt."""
        context = "Database Dictionary Context:\n"
        for table, details in self.metadata.get("tables", {}).items():
            context += f"Table '{table}': {details.get('description', '')}\n"
            for col, col_desc in details.get("columns", {}).items():
                context += f"  - Column '{col}': {col_desc}\n"
        return context
