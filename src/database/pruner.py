import chromadb
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from src.database.metadata import MetadataManager

class SchemaPruner:
    def __init__(self, persist_directory: str = "./db/chroma"):
        self.metadata_mgr = MetadataManager()
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vector_db = None
        self.persist_directory = persist_directory

    def initialize_pruner(self):
        """Build the vector DB from table descriptions."""
        texts = []
        metadatas = []
        for table, details in self.metadata_mgr.metadata.get("tables", {}).items():
            desc = details.get("description", "")
            texts.append(f"Table: {table}. Description: {desc}")
            metadatas.append({"table_name": table})
        
        self.vector_db = Chroma.from_texts(
            texts=texts,
            embedding=self.embeddings,
            metadatas=metadatas,
            persist_directory=self.persist_directory
        )

    def prune_schema(self, question: str, k: int = 3):
        """Retrieve relevant tables for a given question."""
        if not self.vector_db:
            self.initialize_pruner()
        
        results = self.vector_db.similarity_search(question, k=k)
        relevant_tables = [res.metadata["table_name"] for res in results]
        return relevant_tables
