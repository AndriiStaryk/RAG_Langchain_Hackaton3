#!/usr/bin/env python3
"""
Kotlin to Swift Translator for Android Components
Loads components from component_vector_db and translates them to Swift.
"""

import os
import logging
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class KotlinToSwiftTranslator:
    """
    Translates Kotlin Android components to Swift iOS components.
    """
    
    def __init__(self, component_db_path: str = "./component_vector_db"):
        load_dotenv()
        
        self.component_db_path = component_db_path
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Kotlin to Swift mapping patterns
        self.kotlin_swift_patterns = {
            # Data classes
            r'data class (\w+)(\([^)]*\))?\s*\{': r'struct \1 {',
            
            # Function declarations
            r'fun (\w+)(\([^)]*\))(\s*:\s*[^{]+)?\s*\{': r'func \1\2 {',
            
            # Variable declarations
            r'val (\w+)\s*:\s*([^=]+?)(\s*=\s*[^;]+)?;?': r'let \1: \2',
            r'var (\w+)\s*:\s*([^=]+?)(\s*=\s*[^;]+)?;?': r'var \1: \2',
            
            # Type conversions
            r': String': ': String',
            r': Int': ': Int',
            r': Boolean': ': Bool',
            r': Double': ': Double',
            r': Float': ': Float',
            r': List<([^>]+)>': r': [\1]',
            r': Array<([^>]+)>': r': [\1]',
            r': Map<([^,]+),\s*([^>]+)>': r': [\1: \2]',
            
            # Android specific to iOS
            r'@Composable': r'struct',
            r'@Preview': r'#Preview',
            r'androidx\.compose\.': r'',
            r'androidx\.': r'',
            r'kotlinx\.': r'',
            
            # Common patterns
            r'println\(': r'print(',
            r'System\.out\.println\(': r'print(',
        }
        
        # Component-specific translation templates
        self.component_templates = {
            "Model": self._translate_model,
            "View": self._translate_view,
            "ViewModel": self._translate_viewmodel,
            "Repository": self._translate_repository,
            "Unknown": self._translate_generic
        }
    
    def load_component_database(self) -> Optional[Chroma]:
        """Load the component vector database."""
        if not os.path.exists(self.component_db_path):
            logger.error(f"Component database not found at: {self.component_db_path}")
            return None
        
        try:
            vectorstore = Chroma(
                persist_directory=self.component_db_path,
                embedding_function=OpenAIEmbeddings()
            )
            logger.info(f"Loaded component database with {vectorstore._collection.count()} documents")
            return vectorstore
        except Exception as e:
            logger.error(f"Error loading component database: {e}")
            return None
    
    def get_components_by_type(self, component_type: str = None) -> List[Document]:
        """Get components from the database, optionally filtered by type."""
        vectorstore = self.load_component_database()
        if not vectorstore:
            return []
        
        try:
            # Get all documents
            docs = vectorstore.get()
            documents = docs["documents"]
            metadatas = docs["metadatas"]
            
            components = []
            for doc_text, meta in zip(documents, metadatas):
                if component_type is None or meta.get("component_type") == component_type:
                    components.append(Document(
                        page_content=doc_text,
                        metadata=meta
                    ))
            
            logger.info(f"Found {len(components)} components (type filter: {component_type})")
            return components
            
        except Exception as e:
            logger.error(f"Error getting components: {e}")
            return []
    
    def translate_component(self, component_doc: Document) -> str:
        """Translate a single component from Kotlin to Swift."""
        content = component_doc.page_content
        metadata = component_doc.metadata
        component_type = metadata.get("component_type", "Unknown")
        component_name = metadata.get("name", "Unknown")
        
        logger.info(f"Translating {component_type}: {component_name}")
        
        # Use component-specific translation
        translator_func = self.component_templates.get(component_type, self._translate_generic)
        swift_code = translator_func(content, metadata)
        
        return swift_code
    
    def _translate_model(self, kotlin_code: str, metadata: Dict) -> str:
        """Translate a data model from Kotlin to Swift."""
        prompt = f"""
Translate this Kotlin data class to Swift struct:

Kotlin code:
{kotlin_code}

Requirements:
1. Convert 'data class' to 'struct'
2. Convert Kotlin types to Swift types (String, Int, Boolean -> Bool, etc.)
3. Convert List<T> to [T]
4. Convert Map<K,V> to [K: V]
5. Remove Kotlin-specific annotations
6. Add proper Swift syntax
7. Include Codable conformance if needed
8. Add proper documentation comments

Swift code:
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error translating model: {e}")
            return self._basic_translation(kotlin_code)
    
    def _translate_view(self, kotlin_code: str, metadata: Dict) -> str:
        """Translate a UI view from Kotlin/Compose to Swift/SwiftUI."""
        prompt = f"""
Translate this Kotlin/Android Compose view to Swift/SwiftUI:

Kotlin code:
{kotlin_code}

Requirements:
1. Convert @Composable functions to SwiftUI structs
2. Convert Compose UI elements to SwiftUI equivalents:
   - Text() -> Text()
   - Button() -> Button()
   - Column() -> VStack()
   - Row() -> HStack()
   - Box() -> ZStack()
   - LazyColumn() -> List()
3. Convert state management (remember/mutableStateOf -> @State)
4. Convert preview annotations (@Preview -> #Preview)
5. Add proper SwiftUI imports
6. Convert Kotlin syntax to Swift syntax
7. Handle navigation if present

Swift code:
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error translating view: {e}")
            return self._basic_translation(kotlin_code)
    
    def _translate_viewmodel(self, kotlin_code: str, metadata: Dict) -> str:
        """Translate a ViewModel from Kotlin to Swift."""
        prompt = f"""
Translate this Kotlin ViewModel to Swift ObservableObject:

Kotlin code:
{kotlin_code}

Requirements:
1. Convert ViewModel class to ObservableObject
2. Convert LiveData to @Published properties
3. Convert MutableLiveData to @Published var
4. Convert viewModelScope to async/await or Combine
5. Convert Kotlin coroutines to Swift async/await
6. Convert suspend functions to async functions
7. Add proper Swift imports (Foundation, Combine)
8. Convert Kotlin syntax to Swift syntax
9. Handle error handling appropriately

Swift code:
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error translating viewmodel: {e}")
            return self._basic_translation(kotlin_code)
    
    def _translate_repository(self, kotlin_code: str, metadata: Dict) -> str:
        """Translate a Repository from Kotlin to Swift."""
        prompt = f"""
Translate this Kotlin Repository to Swift:

Kotlin code:
{kotlin_code}

Requirements:
1. Convert repository class to Swift class/struct
2. Convert suspend functions to async functions
3. Convert Kotlin coroutines to Swift async/await
4. Convert Kotlin types to Swift types
5. Add proper error handling
6. Convert dependency injection if present
7. Add proper Swift imports
8. Convert Kotlin syntax to Swift syntax

Swift code:
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error translating repository: {e}")
            return self._basic_translation(kotlin_code)
    
    def _translate_generic(self, kotlin_code: str, metadata: Dict) -> str:
        """Generic translation for unknown component types."""
        prompt = f"""
Translate this Kotlin code to Swift:

Kotlin code:
{kotlin_code}

Requirements:
1. Convert Kotlin syntax to Swift syntax
2. Convert Kotlin types to Swift types
3. Convert function declarations (fun -> func)
4. Convert variable declarations (val/var -> let/var)
5. Convert Kotlin-specific features to Swift equivalents
6. Add proper Swift imports
7. Handle any platform-specific code appropriately

Swift code:
"""
        
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error translating generic component: {e}")
            return self._basic_translation(kotlin_code)
    
    def _basic_translation(self, kotlin_code: str) -> str:
        """Basic pattern-based translation as fallback."""
        swift_code = kotlin_code
        
        # Apply pattern replacements
        for kotlin_pattern, swift_pattern in self.kotlin_swift_patterns.items():
            swift_code = re.sub(kotlin_pattern, swift_pattern, swift_code)
        
        # Add Swift imports
        swift_code = "import Foundation\nimport SwiftUI\n\n" + swift_code
        
        return swift_code
    
    def _clean_swift_code(self, code: str) -> str:
        """Extract only Swift code from LLM output, removing all markdown formatting."""
        import re
        
        # First, try to extract code blocks marked as swift
        swift_blocks = re.findall(r"```swift(.*?)```", code, re.DOTALL)
        if swift_blocks:
            # Join all swift code blocks
            cleaned = "\n".join(block.strip() for block in swift_blocks)
        else:
            # If no swift code blocks, remove markdown formatting
            lines = code.splitlines()
            cleaned_lines = []
            in_code_block = False
            
            for line in lines:
                # Skip markdown code fences
                if line.strip().startswith("```"):
                    in_code_block = not in_code_block
                    continue
                
                # Skip language tags (swift, kotlin, etc.)
                if line.strip().lower() in ["swift", "kotlin", "```"]:
                    continue
                
                # Skip markdown headers
                if line.strip().startswith("#"):
                    continue
                
                # Skip empty lines at the beginning and end
                if not cleaned_lines and not line.strip():
                    continue
                
                cleaned_lines.append(line)
            
            # Remove trailing empty lines
            while cleaned_lines and not cleaned_lines[-1].strip():
                cleaned_lines.pop()
            
            cleaned = "\n".join(cleaned_lines)
        
        # Additional cleanup: remove any remaining markdown artifacts
        cleaned = re.sub(r'^```.*$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^#+\s*.*$', '', cleaned, flags=re.MULTILINE)
        cleaned = re.sub(r'^\*\*.*\*\*$', '', cleaned, flags=re.MULTILINE)
        
        # Remove extra blank lines
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        
        return cleaned.strip()

    def translate_all_components(self, output_dir: str = "./swift_output") -> Dict[str, str]:
        """Translate all components and save to files. Group by component name and concatenate content."""
        components = self.get_components_by_type()
        if not components:
            logger.error("No components found to translate")
            return {}

        os.makedirs(output_dir, exist_ok=True)
        translations = {}
        used_names = set()

        from collections import defaultdict
        grouped = defaultdict(list)
        for component in components:
            name = component.metadata.get("name") or "Unknown"
            grouped[name].append(component.page_content)

        for idx, (component_name, chunks) in enumerate(grouped.items()):
            try:
                full_content = "\n".join(chunks)
                # Use the first component's metadata for type, etc.
                first_component = next(c for c in components if (c.metadata.get("name") or "Unknown") == component_name)
                component_type = first_component.metadata.get("component_type", "Unknown")

                swift_code = self.translate_component(
                    Document(page_content=full_content, metadata=first_component.metadata)
                )
                swift_code = self._clean_swift_code(swift_code)

                # Ensure unique filenames
                base_name = component_name or f"Component_{idx}"
                file_name = base_name
                if file_name in used_names:
                    file_name = f"{base_name}_{idx}"
                used_names.add(file_name)

                filename = f"{file_name}.swift"
                filepath = os.path.join(output_dir, filename)

                header = f"""//
//  {file_name}.swift
//  Generated from Kotlin {component_type}
//
//  Original component: {first_component.metadata.get('filename', 'Unknown')}
//  Component type: {component_type}
//  Language: {first_component.metadata.get('language', 'Unknown')}
//

"""
                swift_code = header + swift_code

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(swift_code)

                translations[file_name] = swift_code
                logger.info(f"Translated {file_name} -> {filepath}")

            except Exception as e:
                logger.error(f"Error translating component {component_name}: {e}")

        logger.info(f"Translated {len(translations)} components to {output_dir}")
        return translations
    
    def translate_by_type(self, component_type: str, output_dir: str = "./swift_output") -> Dict[str, str]:
        """Translate components of a specific type."""
        components = self.get_components_by_type(component_type)
        
        if not components:
            logger.error(f"No {component_type} components found")
            return {}
        
        # Create type-specific output directory
        type_output_dir = os.path.join(output_dir, component_type.lower())
        os.makedirs(type_output_dir, exist_ok=True)
        
        translations = {}
        
        for component in components:
            try:
                swift_code = self.translate_component(component)
                component_name = component.metadata.get("name", "Unknown")
                
                filename = f"{component_name}.swift"
                filepath = os.path.join(type_output_dir, filename)
                
                # Add header comment
                header = f"""//
//  {component_name}.swift
//  Generated from Kotlin {component_type}
//
//  Original component: {component.metadata.get('filename', 'Unknown')}
//  Component type: {component_type}
//  Language: {component.metadata.get('language', 'Unknown')}
//

"""
                swift_code = header + swift_code
                
                # Save to file
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(swift_code)
                
                translations[component_name] = swift_code
                logger.info(f"Translated {component_type}: {component_name} -> {filepath}")
                
            except Exception as e:
                logger.error(f"Error translating {component_type} {component.metadata.get('name', 'Unknown')}: {e}")
        
        logger.info(f"Translated {len(translations)} {component_type} components to {type_output_dir}")
        return translations

def main():
    """Main function to run the translator."""
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment variables!")
        return
    
    translator = KotlinToSwiftTranslator()
    
    print("🔄 Kotlin to Swift Translator")
    print("=" * 40)
    
    # Check if component database exists
    if not os.path.exists("./component_vector_db"):
        print("❌ Component database not found!")
        print("Please run the RAG processor first to create the component database.")
        return
    
    # Get available component types
    vectorstore = translator.load_component_database()
    if vectorstore:
        docs = vectorstore.get()
        component_types = set()
        for meta in docs["metadatas"]:
            component_types.add(meta.get("component_type", "Unknown"))
        
        print(f"📦 Available component types: {', '.join(component_types)}")
        
        # Translate all components
        print("\n🔄 Translating all components...")
        translations = translator.translate_all_components()
        
        if translations:
            print(f"✅ Successfully translated {len(translations)} components!")
            print(f"📁 Output saved to: ./swift_output/")
        else:
            print("❌ No components were translated!")
    else:
        print("❌ Could not load component database!")

if __name__ == "__main__":
    main() 