import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import Document
from android_rag_processor import AndroidProjectRAGProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AndroidProjectQueryInterface:
    """
    Interface for querying the Android project knowledge base.
    """
    
    def __init__(self):
        load_dotenv()
        
        # Initialize the RAG processor
        self.rag_processor = AndroidProjectRAGProcessor()
        
        # Initialize OpenAI chat model
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model="gpt-3.5-turbo",
            temperature=0.1
        )
    
    def query_project(self, query: str, k: int = 5, use_llm: bool = True) -> Dict[str, Any]:
        """
        Query the Android project knowledge base.
        
        Args:
            query: Natural language query about the project
            k: Number of relevant documents to retrieve
            use_llm: Whether to use LLM to generate a response
            
        Returns:
            Dictionary containing query results and response
        """
        try:
            # Get relevant documents from vector store
            relevant_docs = self.rag_processor.query_knowledge_base(query, k=k)
            
            if not relevant_docs:
                return {
                    "error": "No relevant documents found",
                    "query": query,
                    "documents": []
                }
            
            # Prepare context from relevant documents
            context = self._prepare_context(relevant_docs)
            
            result = {
                "query": query,
                "documents": relevant_docs,
                "context": context,
                "document_count": len(relevant_docs)
            }
            
            # Generate LLM response if requested
            if use_llm:
                llm_response = self._generate_llm_response(query, context)
                result["llm_response"] = llm_response
            
            return result
            
        except Exception as e:
            logger.error(f"Error querying project: {e}")
            return {"error": str(e), "query": query}
    
    def _prepare_context(self, documents: List[Document]) -> str:
        """
        Prepare context string from relevant documents.
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            metadata = doc.metadata
            content = doc.page_content
            
            # Create a formatted context entry
            context_entry = f"""
Document {i}:
File: {metadata.get('file_path', 'Unknown')}
Language: {metadata.get('language', 'Unknown')}
Directory: {metadata.get('directory', 'Unknown')}
Content:
{content[:500]}{'...' if len(content) > 500 else ''}
"""
            context_parts.append(context_entry)
        
        return "\n".join(context_parts)
    
    def _generate_llm_response(self, query: str, context: str) -> str:
        """
        Generate a response using the LLM based on the query and context.
        """
        try:
            prompt = f"""
You are an AI assistant with access to an Android project's codebase. 
Based on the following context from the project files, please answer the user's question.

Context from the Android project:
{context}

User Question: {query}

Please provide a comprehensive answer based on the context provided. If the context doesn't contain enough information to answer the question, please say so. Focus on providing accurate information about the Android project structure, code, and functionality.
"""
            
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            return f"Error generating response: {str(e)}"
    
    def get_project_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the processed project.
        """
        return self.rag_processor.get_project_summary()
    
    def search_by_file_type(self, file_type: str, query: str = "", k: int = 5) -> Dict[str, Any]:
        """
        Search for documents of a specific file type.
        """
        try:
            # Get all documents
            all_docs = self.rag_processor.query_knowledge_base(query or file_type, k=k*2)
            
            # Filter by file type
            filtered_docs = [
                doc for doc in all_docs 
                if doc.metadata.get('file_extension', '').lower() == file_type.lower()
            ]
            
            return {
                "file_type": file_type,
                "query": query,
                "documents": filtered_docs[:k],
                "total_found": len(filtered_docs)
            }
            
        except Exception as e:
            logger.error(f"Error searching by file type: {e}")
            return {"error": str(e)}
    
    def search_by_directory(self, directory: str, query: str = "", k: int = 5) -> Dict[str, Any]:
        """
        Search for documents in a specific directory.
        """
        try:
            # Get all documents
            all_docs = self.rag_processor.query_knowledge_base(query or directory, k=k*2)
            
            # Filter by directory
            filtered_docs = [
                doc for doc in all_docs 
                if directory.lower() in doc.metadata.get('directory', '').lower()
            ]
            
            return {
                "directory": directory,
                "query": query,
                "documents": filtered_docs[:k],
                "total_found": len(filtered_docs)
            }
            
        except Exception as e:
            logger.error(f"Error searching by directory: {e}")
            return {"error": str(e)}

def interactive_query():
    """
    Interactive query interface for the Android project.
    """
    print("🤖 Android Project RAG Query Interface")
    print("=" * 50)
    
    # Initialize query interface
    query_interface = AndroidProjectQueryInterface()
    
    # Get project summary
    summary = query_interface.get_project_summary()
    if "error" in summary:
        print(f"❌ Error: {summary['error']}")
        print("Please run the RAG processor first using: python android_rag_processor.py")
        return
    
    print(f"📊 Project Summary:")
    print(f"   Total documents: {summary.get('total_documents', 'Unknown')}")
    print(f"   Vector DB path: {summary.get('vector_db_path', 'Unknown')}")
    print(f"   Project path: {summary.get('project_path', 'Unknown')}")
    print()
    
    print("💡 Example queries:")
    print("   - 'How does the quiz functionality work?'")
    print("   - 'What activities are in the app?'")
    print("   - 'Show me the data models'")
    print("   - 'How is the UI structured?'")
    print("   - 'What sports are supported?'")
    print()
    
    while True:
        try:
            # Get user query
            query = input("🔍 Enter your query (or 'quit' to exit): ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not query:
                continue
            
            print(f"\n🔍 Searching for: '{query}'")
            print("-" * 50)
            
            # Query the knowledge base
            result = query_interface.query_project(query, k=5, use_llm=True)
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
                continue
            
            # Display results
            print(f"📄 Found {result['document_count']} relevant documents:")
            print()
            
            for i, doc in enumerate(result['documents'], 1):
                metadata = doc.metadata
                print(f"{i}. 📁 {metadata.get('file_path', 'Unknown')}")
                print(f"   📂 Directory: {metadata.get('directory', 'Unknown')}")
                print(f"   🔤 Language: {metadata.get('language', 'Unknown')}")
                print(f"   📝 Content preview: {doc.page_content[:100]}...")
                print()
            
            # Display LLM response
            if "llm_response" in result:
                print("🤖 AI Response:")
                print("=" * 50)
                print(result["llm_response"])
                print("=" * 50)
            
            print()
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue

def main():
    """
    Main function to run the query interface.
    """
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables!")
        print("Please set your OpenAI API key in the .env file")
        return
    
    # Run interactive query interface
    interactive_query()

if __name__ == "__main__":
    main() 