#!/usr/bin/env python3
"""
Component Extractor for Android Projects
Extracts and categorizes Android components from the main vector database
and stores them in component_vector_db with proper metadata.
"""

import os
import re
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComponentExtractor:
    """
    Extracts and categorizes Android components from the main vector database.
    """
    
    def __init__(self, main_db_path: str = "./vector_db", component_db_path: str = "./component_vector_db"):
        load_dotenv()
        
        self.main_db_path = main_db_path
        self.component_db_path = component_db_path
        
        # Component detection patterns
        self.component_patterns = {
            "Model": [
                r'data class (\w+)',
                r'class (\w+)\s*:\s*(\w+)',
                r'@Entity',
                r'@Serializable',
                r'@Parcelize'
            ],
            "View": [
                r'@Composable',
                r'fun (\w+)\s*\([^)]*\)\s*:\s*Unit',
                r'@Preview',
                r'androidx\.compose\.',
                r'Column\(',
                r'Row\(',
                r'Text\(',
                r'Button\('
            ],
            "ViewModel": [
                r'class (\w+)\s*:\s*ViewModel',
                r'class (\w+)\s*:\s*AndroidViewModel',
                r'LiveData<',
                r'MutableLiveData<',
                r'viewModelScope',
                r'@HiltViewModel'
            ],
            "Repository": [
                r'class (\w+)\s*:\s*Repository',
                r'interface (\w+)\s*Repository',
                r'@Repository',
                r'suspend fun',
                r'@Inject'
            ],
            "Activity": [
                r'class (\w+)\s*:\s*AppCompatActivity',
                r'class (\w+)\s*:\s*Activity',
                r'@AndroidEntryPoint',
                r'onCreate\(',
                r'setContentView\('
            ],
            "Fragment": [
                r'class (\w+)\s*:\s*Fragment',
                r'onCreateView\(',
                r'onViewCreated\(',
                r'@AndroidEntryPoint'
            ]
        }
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="text-embedding-3-small"
        )
    
    def load_main_database(self) -> Optional[Chroma]:
        """Load the main vector database."""
        if not os.path.exists(self.main_db_path):
            logger.error(f"Main database not found at: {self.main_db_path}")
            return None
        
        try:
            vectorstore = Chroma(
                persist_directory=self.main_db_path,
                embedding_function=self.embeddings
            )
            logger.info(f"Loaded main database with {vectorstore._collection.count()} documents")
            return vectorstore
        except Exception as e:
            logger.error(f"Error loading main database: {e}")
            return None
    
    def detect_component_type(self, content: str, file_path: str) -> str:
        """Detect the type of component based on content and file path."""
        content_lower = content.lower()
        file_path_lower = file_path.lower()
        
        # Check file path patterns first
        if 'viewmodel' in file_path_lower or 'view_model' in file_path_lower:
            return "ViewModel"
        elif 'model' in file_path_lower or 'data' in file_path_lower:
            return "Model"
        elif 'view' in file_path_lower or 'ui' in file_path_lower or 'compose' in file_path_lower:
            return "View"
        elif 'repository' in file_path_lower:
            return "Repository"
        elif 'activity' in file_path_lower:
            return "Activity"
        elif 'fragment' in file_path_lower:
            return "Fragment"
        
        # Check content patterns
        for component_type, patterns in self.component_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    return component_type
        
        # Default based on file extension
        if file_path.endswith('.kt'):
            if 'Activity' in content or 'AppCompatActivity' in content:
                return "Activity"
            elif 'Fragment' in content:
                return "Fragment"
            elif 'ViewModel' in content or 'LiveData' in content:
                return "ViewModel"
            elif 'data class' in content or '@Entity' in content:
                return "Model"
            elif '@Composable' in content:
                return "View"
            else:
                return "Unknown"
        
        return "Unknown"
    
    def extract_component_name(self, content: str, component_type: str) -> str:
        """Extract the component name from content."""
        if component_type == "Model":
            # Look for data class or class declarations
            match = re.search(r'(?:data class|class)\s+(\w+)', content)
            if match:
                return match.group(1)
        elif component_type == "ViewModel":
            # Look for ViewModel class declarations
            match = re.search(r'class\s+(\w+)\s*:\s*.*ViewModel', content)
            if match:
                return match.group(1)
        elif component_type == "View":
            # Look for Composable function names
            match = re.search(r'@Composable\s+fun\s+(\w+)', content)
            if match:
                return match.group(1)
        elif component_type == "Repository":
            # Look for Repository class declarations
            match = re.search(r'class\s+(\w+)\s*:\s*.*Repository', content)
            if match:
                return match.group(1)
        elif component_type == "Activity":
            # Look for Activity class declarations
            match = re.search(r'class\s+(\w+)\s*:\s*.*Activity', content)
            if match:
                return match.group(1)
        elif component_type == "Fragment":
            # Look for Fragment class declarations
            match = re.search(r'class\s+(\w+)\s*:\s*.*Fragment', content)
            if match:
                return match.group(1)
        
        # Fallback: extract any class name
        match = re.search(r'class\s+(\w+)', content)
        if match:
            return match.group(1)
        
        return "Unknown"
    
    def extract_components(self) -> List[Document]:
        """Extract and categorize components from the main database."""
        vectorstore = self.load_main_database()
        if not vectorstore:
            return []
        
        try:
            # Get all documents from main database
            docs = vectorstore.get()
            documents = docs["documents"]
            metadatas = docs["metadatas"]
            
            components = []
            
            for doc_text, meta in zip(documents, metadatas):
                file_path = meta.get("file_path", "")
                file_name = meta.get("file_name", "")
                
                # Skip non-Kotlin files
                if not file_path.endswith('.kt'):
                    continue
                
                # Detect component type
                component_type = self.detect_component_type(doc_text, file_path)
                
                # Extract component name
                component_name = self.extract_component_name(doc_text, component_type)
                
                # Create component metadata
                component_meta = {
                    "component_type": component_type,
                    "name": component_name,
                    "original_file": file_path,
                    "filename": file_name,
                    "language": "Kotlin",
                    "file_path": file_path,
                    "file_name": file_name,
                    "file_extension": ".kt",
                    "project_type": "Android",
                    "directory": meta.get("directory", ""),
                    "file_size": meta.get("file_size", 0),
                    "total_chunks": meta.get("total_chunks", 1),
                    "chunk_index": meta.get("chunk_index", 0)
                }
                
                # Create component document
                component_doc = Document(
                    page_content=doc_text,
                    metadata=component_meta
                )
                
                components.append(component_doc)
                
                logger.info(f"Extracted {component_type}: {component_name} from {file_path}")
            
            logger.info(f"Extracted {len(components)} components")
            return components
            
        except Exception as e:
            logger.error(f"Error extracting components: {e}")
            return []
    
    def create_component_database(self, components: List[Document]) -> bool:
        """Create the component vector database."""
        if not components:
            logger.error("No components to store")
            return False
        
        try:
            # Create component database
            component_vectorstore = Chroma(
                persist_directory=self.component_db_path,
                embedding_function=self.embeddings
            )
            
            # Add components to database
            texts = [doc.page_content for doc in components]
            metadatas = [doc.metadata for doc in components]
            
            component_vectorstore.add_texts(texts=texts, metadatas=metadatas)
            
            logger.info(f"Created component database with {len(components)} components")
            return True
            
        except Exception as e:
            logger.error(f"Error creating component database: {e}")
            return False
    
    def run_extraction(self):
        """Run the complete component extraction process."""
        print("🔍 Extracting Android Components")
        print("=" * 40)
        
        # Check if main database exists
        if not os.path.exists(self.main_db_path):
            print("❌ Main database not found!")
            print(f"Please run the RAG processor first to create the database at: {self.main_db_path}")
            return
        
        # Extract components
        print("📦 Extracting components from main database...")
        components = self.extract_components()
        
        if not components:
            print("❌ No components found!")
            return
        
        # Group components by type for summary
        component_types = {}
        for component in components:
            comp_type = component.metadata.get("component_type", "Unknown")
            if comp_type not in component_types:
                component_types[comp_type] = []
            component_types[comp_type].append(component.metadata.get("name", "Unknown"))
        
        print("\n📊 Component Summary:")
        for comp_type, names in component_types.items():
            print(f"  {comp_type}: {len(names)} components")
            for name in names[:3]:  # Show first 3 names
                print(f"    - {name}")
            if len(names) > 3:
                print(f"    ... and {len(names) - 3} more")
        
        # Create component database
        print("\n💾 Creating component database...")
        success = self.create_component_database(components)
        
        if success:
            print(f"✅ Successfully created component database at: {self.component_db_path}")
            print(f"📁 Contains {len(components)} components")
        else:
            print("❌ Failed to create component database!")

def main():
    """Main function to run the component extractor."""
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment variables!")
        return
    
    extractor = ComponentExtractor()
    extractor.run_extraction()

if __name__ == "__main__":
    main() 