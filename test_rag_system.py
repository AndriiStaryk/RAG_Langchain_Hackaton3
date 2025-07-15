#!/usr/bin/env python3
"""
Test script to verify RAG system functionality and data presence.
"""

import os
import logging
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vectorstore(vectorstore_path: str, name: str):
    """Test if a vectorstore exists and contains data."""
    print(f"\n🔍 Testing {name} at: {vectorstore_path}")
    
    if not os.path.exists(vectorstore_path):
        print(f"❌ {name} directory does not exist!")
        return False
    
    try:
        # Load the vectorstore
        vectorstore = Chroma(
            persist_directory=vectorstore_path,
            embedding_function=OpenAIEmbeddings()
        )
        
        # Get all documents
        docs = vectorstore.get()
        document_count = len(docs["documents"])
        
        print(f"📊 {name} contains {document_count} documents")
        
        if document_count == 0:
            print(f"⚠️  {name} is empty!")
            return False
        
        # Show sample documents
        print(f"📄 Sample documents from {name}:")
        for i in range(min(3, document_count)):
            doc = docs["documents"][i]
            meta = docs["metadatas"][i]
            print(f"  Doc {i+1}:")
            print(f"    Content preview: {doc[:100]}...")
            print(f"    Metadata: {meta}")
            print()
        
        # Test a simple query
        try:
            results = vectorstore.similarity_search("test", k=1)
            print(f"✅ {name} query test successful - found {len(results)} results")
        except Exception as e:
            print(f"❌ {name} query test failed: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing {name}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Test all vectorstores."""
    load_dotenv()
    
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables!")
        return
    
    print("🧪 Testing RAG System")
    print("=" * 50)
    
    # Test all vectorstores
    vectorstores = [
        ("./vector_db", "Main Vector Store"),
        ("./file_structure_tree_db", "File Structure Tree DB"),
        ("./component_vector_db", "Component Vector DB")
    ]
    
    results = {}
    for path, name in vectorstores:
        results[name] = test_vectorstore(path, name)
    
    print("\n📋 Summary:")
    print("=" * 50)
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {name}")
    
    # Check if any vectorstore has data
    if any(results.values()):
        print("\n🎉 At least one vectorstore is working!")
    else:
        print("\n💥 All vectorstores are empty or not working!")

if __name__ == "__main__":
    main() 