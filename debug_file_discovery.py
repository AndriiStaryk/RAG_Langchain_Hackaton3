#!/usr/bin/env python3
"""
Debug script to understand file discovery differences.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def debug_file_discovery():
    """Debug the file discovery process."""
    print("🔍 Debugging File Discovery")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    android_project = Path("ANDROID_APP")
    
    # Test script logic
    print("\n📋 Test Script Logic (35 files):")
    print("-" * 30)
    test_files = []
    for file_path in android_project.rglob("*"):
        if file_path.is_file():
            if file_path.suffix.lower() in ['.kt', '.xml', '.json', '.txt', '.md']:
                test_files.append(file_path)
    
    print(f"Found {len(test_files)} files with test script logic")
    for i, file_path in enumerate(test_files[:10]):
        print(f"  {i+1}. {file_path}")
    if len(test_files) > 10:
        print(f"  ... and {len(test_files) - 10} more")
    
    # RAG processor logic
    print("\n🤖 RAG Processor Logic:")
    print("-" * 30)
    
    # Get environment variables
    include_extensions = os.getenv("INCLUDE_EXTENSIONS", ".kt,.xml,.json,.txt,.md").split(",")
    exclude_patterns = os.getenv("EXCLUDE_PATTERNS", "__pycache__,*.pyc,.git,node_modules").split(",")
    
    print(f"Include extensions: {include_extensions}")
    print(f"Exclude patterns: {exclude_patterns}")
    
    rag_files = []
    excluded_files = []
    
    for file_path in android_project.rglob("*"):
        if file_path.is_file():
            # Check if file extension is in include list
            extension_match = any(file_path.suffix.lower() in ext.lower() for ext in include_extensions)
            
            if extension_match:
                # Check if file should be excluded
                should_exclude = any(pattern in str(file_path) for pattern in exclude_patterns)
                
                if should_exclude:
                    excluded_files.append(file_path)
                else:
                    rag_files.append(file_path)
    
    print(f"\nFound {len(rag_files)} files with RAG processor logic")
    print(f"Excluded {len(excluded_files)} files due to patterns")
    
    print("\n📁 RAG Processor Files:")
    for i, file_path in enumerate(rag_files[:10]):
        print(f"  {i+1}. {file_path}")
    if len(rag_files) > 10:
        print(f"  ... and {len(rag_files) - 10} more")
    
    print("\n🚫 Excluded Files:")
    for i, file_path in enumerate(excluded_files[:10]):
        print(f"  {i+1}. {file_path}")
    if len(excluded_files) > 10:
        print(f"  ... and {len(excluded_files) - 10} more")
    
    # Show differences
    test_set = set(test_files)
    rag_set = set(rag_files)
    
    only_in_test = test_set - rag_set
    only_in_rag = rag_set - test_set
    
    print(f"\n🔍 Analysis:")
    print(f"Files only in test script: {len(only_in_test)}")
    print(f"Files only in RAG processor: {len(only_in_rag)}")
    print(f"Files in both: {len(test_set & rag_set)}")
    
    if only_in_test:
        print("\nFiles only in test script:")
        for file_path in list(only_in_test)[:5]:
            print(f"  - {file_path}")
        if len(only_in_test) > 5:
            print(f"  ... and {len(only_in_test) - 5} more")
    
    if only_in_rag:
        print("\nFiles only in RAG processor:")
        for file_path in list(only_in_rag)[:5]:
            print(f"  - {file_path}")
        if len(only_in_rag) > 5:
            print(f"  ... and {len(only_in_rag) - 5} more")

def show_file_types():
    """Show all file types in the project."""
    print("\n📊 File Type Analysis")
    print("=" * 30)
    
    android_project = Path("ANDROID_APP")
    file_types = {}
    
    for file_path in android_project.rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            file_types[ext] = file_types.get(ext, 0) + 1
    
    print("All file types found:")
    for ext, count in sorted(file_types.items()):
        print(f"  {ext}: {count} files")

def main():
    """Main function."""
    debug_file_discovery()
    show_file_types()

if __name__ == "__main__":
    main() 