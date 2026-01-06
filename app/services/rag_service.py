"""
RAG Service - Handles document loading, embedding, and retrieval using FAISS.
"""
import os
import logging
from typing import List, Optional
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if RAGService._initialized:
            return
        
        self.embeddings = None
        self.vector_store = None
        self.docs_path = settings.DOCS_PATH
        self.index_path = settings.FAISS_INDEX_PATH
        RAGService._initialized = True

    def initialize(self) -> bool:
        """Initialize the RAG system - load embeddings and vector store."""
        try:
            logger.info("Initializing RAG service...")
            
            # Initialize embeddings model
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            
            # Check if FAISS index exists
            if os.path.exists(self.index_path):
                logger.info(f"Loading existing FAISS index from {self.index_path}")
                self.vector_store = FAISS.load_local(
                    self.index_path, 
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
            else:
                # Create new index from documents
                self._build_index()
            
            logger.info("RAG service initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG service: {e}")
            return False

    def _build_index(self) -> None:
        """Build FAISS index from documents in the docs folder."""
        if not os.path.exists(self.docs_path):
            os.makedirs(self.docs_path)
            logger.warning(f"Created empty docs directory: {self.docs_path}")
            # Create a placeholder document
            placeholder_path = os.path.join(self.docs_path, "welcome.txt")
            with open(placeholder_path, "w") as f:
                f.write("Welcome to LegalLink! Upload your legal documents to this folder for AI-powered assistance.")
        
        documents = []
        
        # Load PDF files
        pdf_loader = DirectoryLoader(
            self.docs_path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            show_progress=True
        )
        try:
            documents.extend(pdf_loader.load())
        except Exception as e:
            logger.warning(f"Error loading PDFs: {e}")
        
        # Load text files
        txt_loader = DirectoryLoader(
            self.docs_path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            show_progress=True
        )
        try:
            documents.extend(txt_loader.load())
        except Exception as e:
            logger.warning(f"Error loading text files: {e}")
        
        if not documents:
            logger.warning("No documents found. Creating empty vector store.")
            # Create a minimal document to initialize the store
            documents = [Document(page_content="LegalLink knowledge base initialized.", metadata={"source": "system"})]
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
        chunks = text_splitter.split_documents(documents)
        
        logger.info(f"Created {len(chunks)} chunks from {len(documents)} documents")
        
        # Create FAISS index
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        
        # Save the index
        self.vector_store.save_local(self.index_path)
        logger.info(f"FAISS index saved to {self.index_path}")

    def search(self, query: str, k: int = 6, relevance_threshold: float = 0.4) -> List[str]:
        """
        Search for relevant documents with relevance filtering.
        
        Args:
            query: The search query
            k: Maximum number of chunks to retrieve (before filtering)
            relevance_threshold: Minimum similarity score (0-1) to include a chunk.
                                 Higher = stricter filtering. Default 0.4 for lenient matching.
        
        Returns:
            List of relevant document chunks that pass the threshold.
        """
        if not self.vector_store:
            logger.warning("Vector store not initialized - no documents loaded")
            return []
        
        try:
            # Get results with similarity scores
            # FAISS returns (document, score) where lower score = more similar
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
            
            if not docs_with_scores:
                logger.warning("No documents found in vector store")
                return []
            
            # Filter by relevance threshold
            # FAISS L2 distance: convert to similarity (lower distance = higher similarity)
            # Typical L2 distances range from 0-2, we normalize: similarity = 1 / (1 + distance)
            relevant_chunks = []
            for doc, distance in docs_with_scores:
                # Convert L2 distance to similarity score (0 to 1)
                similarity = 1 / (1 + distance)
                
                logger.info(f"Chunk similarity: {similarity:.3f} - {doc.page_content[:80]}...")
                
                if similarity >= relevance_threshold:
                    relevant_chunks.append(doc.page_content)
                else:
                    logger.debug(f"Filtered out chunk with similarity {similarity:.3f} (threshold: {relevance_threshold})")
            
            logger.info(f"RAG search: {len(relevant_chunks)}/{len(docs_with_scores)} chunks passed relevance threshold ({relevance_threshold})")
            
            return relevant_chunks
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []

    def search_with_scores(self, query: str, k: int = 6) -> List[dict]:
        """
        Search and return chunks with their relevance scores.
        Useful for debugging and transparency.
        """
        if not self.vector_store:
            return []
        
        try:
            docs_with_scores = self.vector_store.similarity_search_with_score(query, k=k)
            results = []
            for doc, distance in docs_with_scores:
                similarity = 1 / (1 + distance)
                results.append({
                    "content": doc.page_content,
                    "similarity_score": round(similarity, 4),
                    "source": doc.metadata.get("source", "unknown")
                })
            return results
        except Exception as e:
            logger.error(f"Search with scores error: {e}")
            return []


    def add_documents(self, texts: List[str], metadatas: Optional[List[dict]] = None) -> bool:
        """Add new documents to the vector store."""
        try:
            if not self.vector_store:
                return False
            
            self.vector_store.add_texts(texts, metadatas=metadatas)
            self.vector_store.save_local(self.index_path)
            return True
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False

    def rebuild_index(self) -> bool:
        """Force rebuild the FAISS index from documents."""
        try:
            self._build_index()
            return True
        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False


# Singleton instance
rag_service = RAGService()
