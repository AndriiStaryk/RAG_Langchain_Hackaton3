#!/usr/bin/env python3
"""
Swift File Cleaner
Cleans up existing Swift files by removing markdown formatting and extracting only Swift code.
"""

import os
import re
import logging
from pathlib import Path
from typing import List

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def extract_swift_code(content: str) -> str:
    """
    Extract only Swift code from content, removing all markdown formatting.
    
    Args:
        content: The file content that may contain markdown and Swift code
        
    Returns:
        Clean Swift code without markdown formatting
    """
    # First, try to extract code blocks marked as swift
    swift_blocks = re.findall(r"```swift(.*?)```", content, re.DOTALL)
    if swift_blocks:
        # Join all swift code blocks
        cleaned = "\n".join(block.strip() for block in swift_blocks)
    else:
        # If no swift code blocks, remove markdown formatting
        lines = content.splitlines()
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

def clean_swift_file(file_path: Path) -> bool:
    """
    Clean a single Swift file by removing markdown formatting.
    
    Args:
        file_path: Path to the Swift file to clean
        
    Returns:
        True if file was cleaned successfully, False otherwise
    """
    try:
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract Swift code
        cleaned_content = extract_swift_code(content)
        
        # Write back the cleaned content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(cleaned_content)
        
        logger.info(f"Cleaned: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error cleaning {file_path}: {e}")
        return False

def clean_swift_directory(directory_path: str = "./swift_output") -> None:
    """
    Clean all Swift files in a directory recursively.
    
    Args:
        directory_path: Path to the directory containing Swift files
    """
    directory = Path(directory_path)
    
    if not directory.exists():
        logger.error(f"Directory not found: {directory_path}")
        return
    
    # Find all Swift files
    swift_files = list(directory.rglob("*.swift"))
    
    if not swift_files:
        logger.warning(f"No Swift files found in {directory_path}")
        return
    
    logger.info(f"Found {len(swift_files)} Swift files to clean")
    
    # Clean each file
    cleaned_count = 0
    for swift_file in swift_files:
        if clean_swift_file(swift_file):
            cleaned_count += 1
    
    logger.info(f"Successfully cleaned {cleaned_count}/{len(swift_files)} files")

def main():
    """Main function to run the Swift file cleaner."""
    import sys
    
    # Get directory from command line argument or use default
    directory = sys.argv[1] if len(sys.argv) > 1 else "./swift_output"
    
    print("🧹 Swift File Cleaner")
    print("=" * 30)
    print(f"Cleaning Swift files in: {directory}")
    
    clean_swift_directory(directory)
    
    print("✅ Cleaning complete!")

if __name__ == "__main__":
    main() 