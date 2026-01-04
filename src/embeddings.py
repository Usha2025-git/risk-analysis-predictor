"""
Embeddings and Vector Store Management Module.
Uses ChromaDB for vector storage and semantic search.
"""
import logging
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import numpy as np
from pathlib import Path

logger = logging.getLogger(__name__)

# Note: In production, use actual embedding models like:
# from sentence_transformers import SentenceTransformer
# For now, we'll use a simple mock implementation for demonstration


class SimpleEmbedding:
    """Simple mock embedding for demonstration (replace with real embeddings in production)."""
    
    def __init__(self, dimension: int = 768):
        self.dimension = dimension
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate a mock embedding for text."""
        # In production, use actual embeddings from sentence-transformers or OpenAI
        np.random.seed(hash(text) % (2 ** 32))
        return np.random.randn(self.dimension).astype(np.float32)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a batch of texts."""
        return np.array([self.embed_text(text) for text in texts])


class VectorStore:
    """Vector store for managing project embeddings and semantic search."""
    
    def __init__(self, embedding_dim: int = 768, persist_dir: str = ".vector_store"):
        self.embedding_dim = embedding_dim
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(exist_ok=True)
        
        self.embedder = SimpleEmbedding(embedding_dim)
        self.documents: Dict[str, Dict] = {}  # document_id -> {text, embedding, metadata}
        self.metadata_store: Dict[str, Dict] = {}  # document_id -> metadata
        
        logger.info(f"Initialized VectorStore with {embedding_dim}-dim embeddings")
    
    def add_document(
        self,
        doc_id: str,
        text: str,
        metadata: Dict = None
    ) -> None:
        """Add a document with its embedding."""
        embedding = self.embedder.embed_text(text)
        
        self.documents[doc_id] = {
            'text': text,
            'embedding': embedding,
            'metadata': metadata or {}
        }
        
        self.metadata_store[doc_id] = metadata or {}
        # Per-document logging is noisy and can slow down large ingestions.
        logger.debug(f"Added document {doc_id}")
    
    def add_documents_batch(
        self,
        documents: List[Tuple[str, str, Dict]]
    ) -> None:
        """Add multiple documents (doc_id, text, metadata) in batch."""
        for doc_id, text, metadata in documents:
            self.add_document(doc_id, text, metadata)
        logger.info(f"Added {len(documents)} documents in batch")
    
    def search(
        self,
        query_text: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Tuple[str, float, Dict]]:
        """
        Semantic search for similar documents.
        Returns list of (doc_id, similarity_score, metadata) tuples.
        """
        if not self.documents:
            return []
        
        query_embedding = self.embedder.embed_text(query_text)
        
        # Calculate similarity scores
        results = []
        for doc_id, doc_data in self.documents.items():
            # Check metadata filter
            if filter_metadata:
                if not self._matches_filter(doc_data['metadata'], filter_metadata):
                    continue
            
            # Calculate cosine similarity
            doc_embedding = doc_data['embedding']
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            results.append((doc_id, similarity, doc_data['metadata']))
        
        # Sort by similarity and return top_k
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]
    
    def get_document(self, doc_id: str) -> Optional[Dict]:
        """Retrieve a document by ID."""
        return self.documents.get(doc_id)
    
    def get_metadata(self, doc_id: str) -> Optional[Dict]:
        """Retrieve metadata for a document."""
        return self.metadata_store.get(doc_id)
    
    def update_metadata(self, doc_id: str, metadata: Dict) -> None:
        """Update metadata for a document."""
        if doc_id in self.documents:
            self.documents[doc_id]['metadata'].update(metadata)
            self.metadata_store[doc_id].update(metadata)
            logger.info(f"Updated metadata for document {doc_id}")
    
    def delete_document(self, doc_id: str) -> None:
        """Delete a document."""
        if doc_id in self.documents:
            del self.documents[doc_id]
            del self.metadata_store[doc_id]
            logger.info(f"Deleted document {doc_id}")
    
    def filter_by_metadata(self, filter_dict: Dict) -> List[str]:
        """Get all documents matching metadata filter."""
        matching_docs = []
        for doc_id, metadata in self.metadata_store.items():
            if self._matches_filter(metadata, filter_dict):
                matching_docs.append(doc_id)
        return matching_docs
    
    def save(self) -> None:
        """Persist vector store to disk."""
        # Save metadata (embeddings can be regenerated)
        metadata_file = self.persist_dir / "metadata.json"
        
        serializable_metadata = {}
        for doc_id, metadata in self.metadata_store.items():
            serializable_metadata[doc_id] = metadata
        
        with open(metadata_file, 'w') as f:
            json.dump(serializable_metadata, f, indent=2, default=str)
        
        logger.info(f"Saved vector store to {self.persist_dir}")
    
    def load(self) -> None:
        """Load vector store from disk."""
        metadata_file = self.persist_dir / "metadata.json"
        
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                serializable_metadata = json.load(f)
            
            # Note: embeddings will be regenerated as needed
            self.metadata_store = serializable_metadata
            logger.info(f"Loaded vector store from {self.persist_dir}")
    
    def clear(self) -> None:
        """Clear all documents."""
        self.documents.clear()
        self.metadata_store.clear()
        logger.info("Cleared vector store")
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    @staticmethod
    def _matches_filter(metadata: Dict, filter_dict: Dict) -> bool:
        """Check if metadata matches all filter criteria."""
        for key, value in filter_dict.items():
            if key not in metadata:
                return False
            
            if isinstance(value, list):
                if metadata[key] not in value:
                    return False
            else:
                if metadata[key] != value:
                    return False
        
        return True
    
    def get_stats(self) -> Dict:
        """Get statistics about the vector store."""
        return {
            'total_documents': len(self.documents),
            'embedding_dimension': self.embedding_dim,
            'persist_directory': str(self.persist_dir),
        }


class ProjectEmbedder:
    """Manages embeddings for project data."""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
    
    def embed_projects(self, projects: List[Dict]) -> None:
        """Embed project data and add to vector store."""
        documents_to_add = []
        
        for project in projects:
            project_id = project.get('project_id', '')
            
            # Create comprehensive text representation
            text = self._create_project_text(project)
            
            # Create metadata
            metadata = {
                'project_id': project_id,
                'project_name': project.get('project_name', ''),
                'industry': project.get('industry', ''),
                'team_size': int(project.get('team_size', 0)),
                'budget': float(project.get('budget', 0)),
                'delays_days': int(project.get('delays_days', 0)),
                'timestamp': datetime.now().isoformat()
            }
            
            documents_to_add.append((project_id, text, metadata))
        
        self.vector_store.add_documents_batch(documents_to_add)
        logger.info(f"Embedded {len(projects)} projects")
    
    def embed_incidents(self, incidents: List[Dict]) -> None:
        """Embed incident data and add to vector store."""
        documents_to_add = []
        
        for incident in incidents:
            incident_id = incident.get('incident_id', '')
            text = incident.get('description', '') + " " + incident.get('impact', '')
            
            metadata = {
                'incident_id': incident_id,
                'project_id': incident.get('project_id', ''),
                'severity': incident.get('severity', ''),
                'category': incident.get('category', ''),
                'timestamp': datetime.now().isoformat()
            }
            
            documents_to_add.append((incident_id, text, metadata))
        
        self.vector_store.add_documents_batch(documents_to_add)
        logger.info(f"Embedded {len(incidents)} incidents")
    
    @staticmethod
    def _create_project_text(project: Dict) -> str:
        """Create text representation of project."""
        parts = [
            project.get('project_name', ''),
            project.get('risk_description', ''),
            project.get('resolution', ''),
            f"industry {project.get('industry', '')}",
            f"team size {project.get('team_size', '')}",
        ]
        
        return ' '.join([str(p) for p in parts if p])
    
    def search_similar_projects(
        self,
        project_text: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Tuple[str, float]]:
        """Search for similar projects."""
        results = self.vector_store.search(
            project_text,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        return [(doc_id, score) for doc_id, score, _ in results]
    
    def search_incidents(
        self,
        query: str,
        top_k: int = 5,
        category: Optional[str] = None
    ) -> List[Dict]:
        """Search for similar incidents."""
        filter_metadata = {'category': category} if category else None
        
        results = self.vector_store.search(
            query,
            top_k=top_k,
            filter_metadata=filter_metadata
        )
        
        return [metadata for _, _, metadata in results]


logger.info("Vector Store module initialized")
