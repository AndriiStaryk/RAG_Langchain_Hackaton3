#!/usr/bin/env python3
"""
Test script for the Android Project RAG System.
This script tests the main components to ensure everything works correctly.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def test_environment():
    """Test environment setup."""
    print("🔧 Testing environment setup...")
    
    # Load environment variables
    load_dotenv()
    
    # Check OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("❌ OPENAI_API_KEY not set or using default value")
        print("   Please set your OpenAI API key in the .env file")
        return False
    else:
        print("✅ OpenAI API key found")
    
    # Check Android project directory
    android_project = Path("ANDROID_APP")
    if not android_project.exists():
        print("❌ ANDROID_APP directory not found")
        return False
    else:
        print("✅ Android project directory found")
    
    # Check for relevant files
    relevant_files = []
    for file_path in android_project.rglob("*"):
        if file_path.is_file():
            if file_path.suffix.lower() in ['.kt', '.xml', '.json', '.txt', '.md']:
                relevant_files.append(file_path)
    
    if not relevant_files:
        print("❌ No relevant files found in Android project")
        return False
    else:
        print(f"✅ Found {len(relevant_files)} relevant files to process")
    
    return True

def test_imports():
    """Test that all required modules can be imported."""
    print("\n📦 Testing imports...")
    
    try:
        import chromadb
        print("✅ chromadb imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import chromadb: {e}")
        return False
    
    try:
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        print("✅ langchain.text_splitter imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain.text_splitter: {e}")
        return False
    
    try:
        from langchain_openai import OpenAIEmbeddings
        print("✅ langchain_openai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain_openai: {e}")
        return False
    
    try:
        from langchain_community.vectorstores import Chroma
        print("✅ langchain_community.vectorstores imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain_community.vectorstores: {e}")
        return False
    
    try:
        from langchain.schema import Document
        print("✅ langchain.schema imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import langchain.schema: {e}")
        return False
    
    try:
        import tqdm
        print("✅ tqdm imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import tqdm: {e}")
        return False
    
    return True

def test_rag_processor():
    """Test the RAG processor initialization."""
    print("\n🤖 Testing RAG processor...")
    
    try:
        from android_rag_processor import AndroidProjectRAGProcessor
        
        # Initialize processor
        processor = AndroidProjectRAGProcessor()
        print("✅ RAG processor initialized successfully")
        
        # Test file discovery
        relevant_files = processor.get_relevant_files()
        if relevant_files:
            print(f"✅ Found {len(relevant_files)} relevant files")
            
            # Show some example files
            print("   Example files:")
            for i, file_path in enumerate(relevant_files[:5]):
                print(f"   {i+1}. {file_path}")
            if len(relevant_files) > 5:
                print(f"   ... and {len(relevant_files) - 5} more")
        else:
            print("❌ No relevant files found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing RAG processor: {e}")
        return False

def test_query_interface():
    """Test the query interface initialization."""
    print("\n🔍 Testing query interface...")
    
    try:
        from query_interface import AndroidProjectQueryInterface
        
        # Initialize query interface
        query_interface = AndroidProjectQueryInterface()
        print("✅ Query interface initialized successfully")
        
        # Test project summary
        summary = query_interface.get_project_summary()
        if "error" in summary:
            print("⚠️  No vector database found (this is expected if you haven't run the processor yet)")
        else:
            print("✅ Vector database found and accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing query interface: {e}")
        return False

def test_vector_db_manager():
    """Test the vector database manager."""
    print("\n🗄️  Testing vector database manager...")
    
    try:
        from vector_db_manager import VectorDBManager
        
        # Initialize manager
        manager = VectorDBManager()
        print("✅ Vector database manager initialized successfully")
        
        # Test getting stats
        stats = manager.get_database_stats()
        if "error" in stats:
            print("⚠️  No vector database found (this is expected if you haven't run the processor yet)")
        else:
            print("✅ Vector database statistics accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing vector database manager: {e}")
        return False

def run_all_tests():
    """Run all tests and provide a summary."""
    print("🧪 Running Android Project RAG System Tests")
    print("=" * 50)
    
    tests = [
        ("Environment Setup", test_environment),
        ("Module Imports", test_imports),
        ("RAG Processor", test_rag_processor),
        ("Query Interface", test_query_interface),
        ("Vector DB Manager", test_vector_db_manager)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n📊 Test Results Summary")
    print("=" * 30)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your RAG system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python android_rag_processor.py")
        print("2. Run: python query_interface.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon solutions:")
        print("1. Install missing dependencies: pip install -r requirements.txt")
        print("2. Set your OpenAI API key in the .env file")
        print("3. Ensure the ANDROID_APP directory exists")

def main():
    """Main function."""
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Android Project RAG System Test Script")
        print("Usage: python test_rag_system.py")
        print("This script tests all components of the RAG system.")
        return
    
    run_all_tests()

if __name__ == "__main__":
    main() 