#!/usr/bin/env python3
"""
Complete Workflow Script
Runs the entire pipeline: RAG processing -> Component extraction -> Translation -> Cleaning
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command: str, description: str) -> bool:
    """
    Run a command and return success status.
    
    Args:
        command: The command to run
        description: Description of what the command does
        
    Returns:
        True if command succeeded, False otherwise
    """
    print(f"\n🔄 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ Success!")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        if e.stdout:
            print("Stdout:")
            print(e.stdout)
        if e.stderr:
            print("Stderr:")
            print(e.stderr)
        return False

def check_requirements():
    """Check if all required files and dependencies are available."""
    print("🔍 Checking Requirements")
    print("=" * 30)
    
    # Check if required scripts exist
    required_files = [
        "android_rag_processor.py",
        "component_extractor.py", 
        "kotlin_to_swift_translator.py",
        "clean_swift_files.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        return False
    
    # Check if Android project exists
    if not os.path.exists("ANDROID_APP"):
        print("❌ ANDROID_APP directory not found!")
        return False
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment variables!")
        return False
    
    print("✅ All requirements met!")
    return True

def main():
    """Run the complete workflow."""
    print("🚀 Complete Android to Swift Translation Workflow")
    print("=" * 60)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements not met. Please fix the issues above.")
        return
    
    # Step 1: Run RAG processor
    print("\n📦 Step 1: Processing Android project with RAG")
    if not run_command("python3 android_rag_processor.py", "Running RAG processor"):
        print("❌ RAG processing failed!")
        return
    
    # Step 2: Extract components
    print("\n🔍 Step 2: Extracting Android components")
    if not run_command("python3 component_extractor.py", "Running component extractor"):
        print("❌ Component extraction failed!")
        return
    
    # Step 3: Translate to Swift
    print("\n🔄 Step 3: Translating to Swift")
    if not run_command("python3 kotlin_to_swift_translator.py", "Running Kotlin to Swift translator"):
        print("❌ Translation failed!")
        return
    
    # Step 4: Clean Swift files
    print("\n🧹 Step 4: Cleaning Swift files")
    if not run_command("python3 clean_swift_files.py", "Cleaning Swift files"):
        print("❌ Swift file cleaning failed!")
        return
    
    # Final summary
    print("\n🎉 Workflow Complete!")
    print("=" * 30)
    
    # Check results
    swift_output_dir = "./swift_output"
    if os.path.exists(swift_output_dir):
        swift_files = list(Path(swift_output_dir).rglob("*.swift"))
        print(f"📁 Generated {len(swift_files)} Swift files in {swift_output_dir}")
        
        if swift_files:
            print("\n📄 Generated files:")
            for file in swift_files:
                print(f"  - {file.name}")
    else:
        print("❌ No Swift output directory found!")
    
    print("\n✅ All steps completed successfully!")

if __name__ == "__main__":
    main() 