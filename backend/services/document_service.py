"""
Document processing service using IBM Docling.
Handles document upload, text extraction, chunking, and RAG retrieval.
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4

try:
    from docling.document_converter import DocumentConverter
    DOCLING_AVAILABLE = True
except ImportError:
    DOCLING_AVAILABLE = False
    print("⚠️  Docling not installed. Document processing will use mock mode.")


class DocumentChunk:
    """Represents a chunk of text extracted from a document."""
    
    def __init__(
        self,
        chunk_id: str,
        document_id: str,
        text: str,
        page_number: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.chunk_id = chunk_id
        self.document_id = document_id
        self.text = text
        self.page_number = page_number
        self.metadata = metadata or {}
        self.created_at = datetime.now()


class DocumentService:
    """
    Service for document processing with IBM Docling.
    Handles PDF/DOCX parsing, text extraction, and chunking for RAG.
    """
    
    def __init__(self):
        """Initialize document service."""
        # In-memory document store
        self.documents: Dict[str, Dict[str, Any]] = {}
        self.chunks: Dict[str, DocumentChunk] = {}  # chunk_id -> chunk
        self.document_chunks: Dict[str, List[str]] = {}  # document_id -> [chunk_ids]
        
        # Initialize Docling converter if available
        if DOCLING_AVAILABLE:
            try:
                # Initialize DocumentConverter (simpler approach without pipeline_options)
                self.converter = DocumentConverter()
                print("✓ Docling initialized successfully")
            except Exception as e:
                print(f"⚠️  Docling initialization failed: {e}")
                self.converter = None
        else:
            self.converter = None
    
    def is_available(self) -> bool:
        """Check if Docling is available and initialized."""
        return DOCLING_AVAILABLE and self.converter is not None
    
    def process_document(
        self,
        file_path: str,
        filename: str,
        file_type: str,
        size_bytes: int,
    ) -> Dict[str, Any]:
        """
        Process a document using Docling and extract text chunks.
        
        Args:
            file_path: Path to the document file
            filename: Original filename
            file_type: File type (PDF, DOCX, etc.)
            size_bytes: File size in bytes
            
        Returns:
            Dictionary with document metadata and processing results
        """
        document_id = str(uuid4())
        
        # Store document metadata
        doc_metadata = {
            "id": document_id,
            "filename": filename,
            "file_type": file_type,
            "size_bytes": size_bytes,
            "uploaded_at": datetime.now(),
            "processed": False,
            "chunk_count": 0,
            "file_path": file_path,
        }
        
        self.documents[document_id] = doc_metadata
        
        # Process with Docling if available and file is not markdown
        if self.is_available() and file_type not in ["MD", "TXT"]:
            try:
                chunks = self._extract_chunks_with_docling(document_id, file_path)
                doc_metadata["processed"] = True
                doc_metadata["chunk_count"] = len(chunks)
                doc_metadata["processing_status"] = "processed"
                
                return {
                    "document_id": document_id,
                    "chunks_extracted": len(chunks),
                    "status": "processed",
                }
            except Exception as e:
                print(f"✗ Docling processing failed: {e}")
                # Fall through to mock mode on error
                
        # Use mock chunks for MD/TXT files or when Docling unavailable
        chunks = self._create_mock_chunks(document_id, filename)
        doc_metadata["processed"] = True
        doc_metadata["chunk_count"] = len(chunks)
        doc_metadata["processing_status"] = "mock" if self.is_available() else "no-docling"
        
        return {
            "document_id": document_id,
            "chunks_extracted": len(chunks),
            "status": "processed",
        }
    
    def _extract_chunks_with_docling(
        self,
        document_id: str,
        file_path: str,
        chunk_size: int = 500,
    ) -> List[DocumentChunk]:
        """
        Extract text chunks from document using Docling.
        
        Args:
            document_id: Document UUID
            file_path: Path to document
            chunk_size: Target chunk size in words
            
        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        
        # Convert document
        result = self.converter.convert(file_path)
        
        # Extract text and metadata
        doc = result.document
        
        # Process each page
        current_chunk = []
        current_word_count = 0
        
        for page_num, page in enumerate(doc.pages, start=1):
            # Get text from page
            page_text = page.export_to_markdown()
            
            # Split into words
            words = page_text.split()
            
            for word in words:
                current_chunk.append(word)
                current_word_count += 1
                
                # Create chunk when size reached
                if current_word_count >= chunk_size:
                    chunk_text = " ".join(current_chunk)
                    chunk_id = str(uuid4())
                    
                    chunk = DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=document_id,
                        text=chunk_text,
                        page_number=page_num,
                        metadata={"extraction_method": "docling"},
                    )
                    
                    chunks.append(chunk)
                    self.chunks[chunk_id] = chunk
                    
                    # Reset for next chunk
                    current_chunk = []
                    current_word_count = 0
        
        # Add remaining text as final chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_id = str(uuid4())
            
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                text=chunk_text,
                metadata={"extraction_method": "docling"},
            )
            
            chunks.append(chunk)
            self.chunks[chunk_id] = chunk
        
        # Store document-chunk mapping
        self.document_chunks[document_id] = [c.chunk_id for c in chunks]
        
        print(f"✓ Extracted {len(chunks)} chunks from document {document_id}")
        
        return chunks
    
    def _create_mock_chunks(self, document_id: str, filename: str) -> List[DocumentChunk]:
        """Create mock compliance document chunks for testing."""
        mock_content = {
            "AML Policy": [
                "Anti-Money Laundering (AML) Policy: All financial institutions must implement robust AML controls. Transactions exceeding $10,000 USD require enhanced due diligence (EDD). High-risk jurisdictions include countries with weak regulatory frameworks or known for financial crime.",
                "Customer Due Diligence (CDD): Financial institutions must verify customer identity, understand the nature of their business, and assess the purpose of transactions. Enhanced due diligence is required for politically exposed persons (PEPs) and high-risk countries.",
                "Suspicious Activity Reporting (SAR): Any transaction that appears unusual or lacks clear economic rationale must be reported to the Financial Intelligence Unit (FIU) within 24 hours. Patterns indicating potential money laundering include structuring, rapid movement of funds, and transactions with sanctioned entities.",
            ],
            "KYC Guidelines": [
                "Know Your Customer (KYC) Requirements: Before establishing a business relationship, institutions must collect and verify: full legal name, date of birth, residential address, government-issued identification, and source of funds. For corporate clients, beneficial ownership must be identified.",
                "Risk-Based Approach: Customer risk ratings should be assigned based on: country of residence, transaction volume, nature of business, and expected account activity. High-risk customers require more frequent monitoring and periodic review.",
                "Ongoing Monitoring: All customer relationships must be subject to continuous monitoring. Unusual patterns, significant deviations from expected behavior, or changes in risk profile trigger immediate review and potential escalation.",
            ],
            "Sanctions Compliance": [
                "Sanctions Screening: All transactions must be screened against OFAC, UN, EU, and local sanctions lists before processing. Real-time screening is required for wire transfers and cross-border payments.",
                "Country Risk Assessment: Transactions involving high-risk jurisdictions (e.g., Iran, North Korea, Syria) are prohibited. Transactions with medium-risk countries require additional compliance checks and senior management approval.",
                "Embargo Enforcement: Financial institutions must block and report any transactions involving sanctioned individuals, entities, or countries. Penalties for violations include fines up to $1 million and criminal prosecution.",
            ],
        }
        
        # Determine document type from filename
        doc_type = "General Compliance"
        for key in mock_content.keys():
            if key.lower().replace(" ", "_") in filename.lower():
                doc_type = key
                break
        
        chunks = []
        content_list = mock_content.get(doc_type, mock_content["AML Policy"])
        
        for idx, text in enumerate(content_list):
            chunk_id = str(uuid4())
            chunk = DocumentChunk(
                chunk_id=chunk_id,
                document_id=document_id,
                text=text,
                page_number=idx + 1,
                metadata={"source": doc_type, "extraction_method": "mock"},
            )
            chunks.append(chunk)
            self.chunks[chunk_id] = chunk
        
        # Store document-chunk mapping
        self.document_chunks[document_id] = [c.chunk_id for c in chunks]
        
        return chunks
    
    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[DocumentChunk]:
        """
        Retrieve most relevant document chunks for a query.
        Uses simple keyword matching (in production, use embeddings).
        
        Args:
            query: Search query
            top_k: Number of chunks to return
            
        Returns:
            List of most relevant DocumentChunk objects
        """
        if not self.chunks:
            return []
        
        # Simple keyword matching (in production, use embeddings)
        query_terms = set(query.lower().split())
        
        # Score each chunk
        scored_chunks = []
        for chunk_id, chunk in self.chunks.items():
            chunk_terms = set(chunk.text.lower().split())
            overlap = len(query_terms.intersection(chunk_terms))
            if overlap > 0:
                scored_chunks.append((overlap, chunk))
        
        # Sort by score and return top_k
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in scored_chunks[:top_k]]
    
    def get_document_metadata(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Get document metadata by ID."""
        return self.documents.get(document_id)
    
    def list_documents(self) -> List[Dict[str, Any]]:
        """List all uploaded documents."""
        return list(self.documents.values())
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks."""
        if document_id not in self.documents:
            return False
        
        # Delete chunks
        chunk_ids = self.document_chunks.get(document_id, [])
        for chunk_id in chunk_ids:
            self.chunks.pop(chunk_id, None)
        
        # Delete document
        self.documents.pop(document_id, None)
        self.document_chunks.pop(document_id, None)
        
        return True
    
    def get_all_chunks_text(self) -> str:
        """Get concatenated text from all chunks for RAG context."""
        if not self.chunks:
            return ""
        
        # Group chunks by document for better organization
        doc_texts = []
        for doc_id, chunk_ids in self.document_chunks.items():
            doc_meta = self.documents.get(doc_id, {})
            doc_name = doc_meta.get("filename", "Unknown Document")
            
            chunk_texts = []
            for chunk_id in chunk_ids:
                chunk = self.chunks.get(chunk_id)
                if chunk:
                    chunk_texts.append(chunk.text)
            
            if chunk_texts:
                doc_texts.append(f"=== {doc_name} ===\n" + "\n\n".join(chunk_texts))
        
        return "\n\n---\n\n".join(doc_texts)


# Global instance
document_service = DocumentService()

