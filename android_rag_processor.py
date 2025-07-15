import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AndroidProjectRAGProcessor:
    """
    A RAG processor specifically designed for Android projects.
    Processes all relevant files in the Android project and stores them in a vector database.
    """
    
    def __init__(self, project_path: str = "ANDROID_APP"):
        load_dotenv()
        
        self.project_path = Path(project_path)
        self.vector_db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = int(os.getenv("CHUNK_OVERLAP", "200"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "4000"))
        
        # File extensions to include
        self.include_extensions = os.getenv("INCLUDE_EXTENSIONS", ".kt,.xml,.json,.txt,.md").split(",")
        
        # Patterns to exclude
        self.exclude_patterns = os.getenv("EXCLUDE_PATTERNS", "__pycache__,*.pyc,.git,node_modules").split(",")
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small"
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize vector store
        self.vector_store = None
        
    def get_relevant_files(self) -> List[Path]:
        """
        Recursively find all relevant files in the Android project.
        """
        relevant_files = []
        
        if not self.project_path.exists():
            logger.error(f"Project path {self.project_path} does not exist!")
            return relevant_files
            
        for file_path in self.project_path.rglob("*"):
            if file_path.is_file():
                # Check if file extension is in include list
                if any(file_path.suffix.lower() in ext.lower() for ext in self.include_extensions):
                    # Check if file should be excluded
                    if not any(pattern in str(file_path) for pattern in self.exclude_patterns):
                        relevant_files.append(file_path)
                        
        logger.info(f"Found {len(relevant_files)} relevant files to process")
        return relevant_files
    
    def read_file_content(self, file_path: Path) -> Optional[str]:
        """
        Read file content with proper encoding handling.
        """
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                logger.warning(f"Could not read file {file_path}: {e}")
                return None
        except Exception as e:
            logger.warning(f"Error reading file {file_path}: {e}")
            return None
    
    def create_document_metadata(self, file_path: Path, content: str) -> Dict[str, Any]:
        """
        Create metadata for the document.
        """
        relative_path = file_path.relative_to(self.project_path)
        
        return {
            "file_path": str(relative_path),
            "file_name": file_path.name,
            "file_extension": file_path.suffix,
            "file_size": len(content),
            "project_type": "Android",
            "language": self._detect_language(file_path.suffix),
            "directory": str(file_path.parent.relative_to(self.project_path))
        }
    
    def _detect_language(self, extension: str) -> str:
        """
        Detect programming language based on file extension.
        """
        language_map = {
            ".kt": "Kotlin",
            ".java": "Java",
            ".xml": "XML",
            ".json": "JSON",
            ".txt": "Text",
            ".md": "Markdown",
            ".gradle": "Gradle",
            ".properties": "Properties"
        }
        return language_map.get(extension.lower(), "Unknown")
    
    def process_file(self, file_path: Path) -> List[Document]:
        """
        Process a single file and return a list of Document objects.
        """
        content = self.read_file_content(file_path)
        if not content:
            return []
        
        # Create metadata
        metadata = self.create_document_metadata(file_path, content)
        
        # Split content into chunks
        try:
            chunks = self.text_splitter.split_text(content)
        except Exception as e:
            logger.warning(f"Error splitting text for {file_path}: {e}")
            # If splitting fails, use the whole content as one chunk
            chunks = [content]
        
        # Create Document objects
        documents = []
        for i, chunk in enumerate(chunks):
            doc_metadata = metadata.copy()
            doc_metadata["chunk_index"] = i
            doc_metadata["total_chunks"] = len(chunks)
            
            document = Document(
                page_content=chunk,
                metadata=doc_metadata
            )
            documents.append(document)
        
        return documents
    
    def process_project(self) -> List[Document]:
        """
        Process all relevant files in the Android project.
        """
        relevant_files = self.get_relevant_files()
        all_documents = []
        
        logger.info(f"Processing {len(relevant_files)} files...")
        
        for file_path in tqdm.tqdm(relevant_files, desc="Processing files"):
            try:
                documents = self.process_file(file_path)
                all_documents.extend(documents)
                logger.debug(f"Processed {file_path}: {len(documents)} chunks")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        logger.info(f"Total documents created: {len(all_documents)}")
        return all_documents
    
    def create_vector_store(self, documents: List[Document]) -> Chroma:
        """
        Create and populate the vector store with documents.
        """
        logger.info("Creating vector store...")
        
        # Create vector store
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=self.embeddings,
            persist_directory=self.vector_db_path
        )
        
        # Persist the vector store
        vector_store.persist()
        
        logger.info(f"Vector store created and persisted to {self.vector_db_path}")
        return vector_store
    
    def load_vector_store(self) -> Chroma:
        """
        Load existing vector store.
        """
        if os.path.exists(self.vector_db_path):
            vector_store = Chroma(
                persist_directory=self.vector_db_path,
                embedding_function=self.embeddings
            )
            logger.info("Loaded existing vector store")
            return vector_store
        else:
            logger.warning("No existing vector store found")
            return None
    
    def query_knowledge_base(self, query: str, k: int = 5) -> List[Document]:
        """
        Query the knowledge base for relevant documents.
        """
        vector_store = self.load_vector_store()
        if not vector_store:
            logger.error("No vector store available")
            return []
        
        try:
            results = vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            logger.error(f"Error querying vector store: {e}")
            return []
    
    def get_project_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the processed project.
        """
        vector_store = self.load_vector_store()
        if not vector_store:
            return {"error": "No vector store available"}
        
        try:
            # Get collection info
            collection = vector_store._collection
            count = collection.count()
            
            # Get unique file types
            file_types = set()
            file_count = 0
            
            # This is a simplified approach - in practice you'd query the metadata
            # For now, we'll return basic info
            summary = {
                "total_documents": count,
                "vector_db_path": self.vector_db_path,
                "project_path": str(self.project_path),
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting project summary: {e}")
            return {"error": str(e)}
    
    def generate_file_structure_tree(self) -> str:
        """
        Generate a string representation of the file structure tree.
        """
        tree_lines = []
        for root, dirs, files in os.walk(self.project_path):
            level = os.path.relpath(root, self.project_path).count(os.sep)
            indent = "    " * level
            tree_lines.append(f"{indent}{os.path.basename(root)}/")
            subindent = "    " * (level + 1)
            for f in files:
                tree_lines.append(f"{subindent}{f}")
        return "\n".join(tree_lines)

    def create_file_structure_document(self) -> Document:
        """
        Create a Document object for the file structure tree.
        """
        tree_str = self.generate_file_structure_tree()
        metadata = {
            "file_path": "FILE_STRUCTURE_TREE",
            "file_name": "FILE_STRUCTURE_TREE",
            "file_extension": ".txt",
            "file_size": len(tree_str),
            "project_type": "Android",
            "language": "Text",
            "directory": "",
            "description": "This document contains the file structure tree of the project."
        }
        return Document(page_content=tree_str, metadata=metadata)

    def create_file_structure_vector_store(self, file_structure_doc: Document) -> Chroma:
        """
        Create and persist a vector store for the file structure tree document only.
        """
        # Save in a separate directory at the same level as the main vector_db
        file_structure_db_path = "./file_structure_tree_db"
        logger.info(f"Creating file structure tree vector store at {file_structure_db_path}...")
        
        try:
            # Create directory if it doesn't exist
            os.makedirs(file_structure_db_path, exist_ok=True)
            
            logger.info(f"File structure tree content length: {len(file_structure_doc.page_content)}")
            logger.info(f"File structure tree metadata: {file_structure_doc.metadata}")
            
            vector_store = Chroma.from_documents(
                documents=[file_structure_doc],
                embedding=self.embeddings,
                persist_directory=file_structure_db_path
            )
            vector_store.persist()
            
            # Verify the store has documents
            output_docs = vector_store.get()
            logger.info(f"File structure tree vector store created and persisted to {file_structure_db_path}")
            logger.info(f"File structure tree store has {len(output_docs['documents'])} documents")
            
            return vector_store
            
        except Exception as e:
            logger.error(f"Error creating file structure tree vector store: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def run_full_processing(self):
        """
        Run the complete RAG processing pipeline.
        """
        logger.info("Starting Android project RAG processing...")
        
        # Process all files
        documents = self.process_project()
        
        if not documents:
            logger.error("No documents were processed!")
            return
        
        # Add file structure tree as a special document to the main RAG
        file_structure_doc = self.create_file_structure_document()
        documents.append(file_structure_doc)
        
        # Create vector store for all documents (including file structure tree)
        self.vector_store = self.create_vector_store(documents)
        
        # Also create a separate vector store for just the file structure tree
        self.create_file_structure_vector_store(file_structure_doc)
        
        # Reindex components to create component-aware vectorstore
        from vector_db_manager import reindex_components_to_vectorstore
        reindex_components_to_vectorstore()
        
        # Translate components to Swift
        from kotlin_to_swift_translator import KotlinToSwiftTranslator
        translator = KotlinToSwiftTranslator()
        translations = translator.translate_all_components()
        
        if translations:
            logger.info(f"✅ Successfully translated {len(translations)} components to Swift!")
            logger.info(f"📁 Swift files saved to: ./swift_output/")
        else:
            logger.warning("⚠️ No components were translated to Swift")
        
        # Get summary
        summary = self.get_project_summary()
        logger.info(f"Processing complete! Summary: {summary}")
        
        return self.vector_store

def main():
    """
    Main function to run the RAG processor.
    """
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment variables!")
        logger.info("Please set your OpenAI API key in the .env file")
        return
    
    # Initialize processor
    processor = AndroidProjectRAGProcessor()
    
    # Run full processing
    vector_store = processor.run_full_processing()
    
    if vector_store:
        logger.info("✅ RAG processing completed successfully!")
        logger.info("You can now query the knowledge base using the query_knowledge_base method")
    else:
        logger.error("❌ RAG processing failed!")

if __name__ == "__main__":
    main() 