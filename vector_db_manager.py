# import os
# import shutil
# import json
# import logging
# from pathlib import Path
# from typing import Dict, Any, List
# from dotenv import load_dotenv
# from android_rag_processor import AndroidProjectRAGProcessor
# from langchain_community.vectorstores import Chroma
# from langchain_core.documents import Document
# from langchain_openai import OpenAIEmbeddings

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# class VectorDBManager:
#     """
#     Manager for the vector database operations.
#     """
    
#     def __init__(self):
#         load_dotenv()
#         self.vector_db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
#         self.rag_processor = AndroidProjectRAGProcessor()
    
#     def get_database_stats(self) -> Dict[str, Any]:
#         """
#         Get statistics about the vector database.
#         """
#         try:
#             vector_store = self.rag_processor.load_vector_store()
#             if not vector_store:
#                 return {"error": "No vector database found"}
            
#             collection = vector_store._collection
#             count = collection.count()
            
#             # Get metadata statistics
#             metadata_stats = self._get_metadata_stats(collection)
            
#             stats = {
#                 "total_documents": count,
#                 "vector_db_path": self.vector_db_path,
#                 "database_exists": os.path.exists(self.vector_db_path),
#                 "database_size": self._get_directory_size(self.vector_db_path),
#                 "metadata_stats": metadata_stats
#             }
            
#             return stats
            
#         except Exception as e:
#             logger.error(f"Error getting database stats: {e}")
#             return {"error": str(e)}
    
#     def _get_metadata_stats(self, collection) -> Dict[str, Any]:
#         """
#         Get statistics about document metadata.
#         """
#         try:
#             # Get all documents to analyze metadata
#             results = collection.get()
            
#             if not results or not results['metadatas']:
#                 return {"error": "No metadata available"}
            
#             metadatas = results['metadatas']
            
#             # Count file types
#             file_types = {}
#             languages = {}
#             directories = {}
            
#             for metadata in metadatas:
#                 if metadata:
#                     # File types
#                     file_ext = metadata.get('file_extension', 'Unknown')
#                     file_types[file_ext] = file_types.get(file_ext, 0) + 1
                    
#                     # Languages
#                     lang = metadata.get('language', 'Unknown')
#                     languages[lang] = languages.get(lang, 0) + 1
                    
#                     # Directories
#                     directory = metadata.get('directory', 'Unknown')
#                     directories[directory] = directories.get(directory, 0) + 1
            
#             return {
#                 "file_types": file_types,
#                 "languages": languages,
#                 "top_directories": dict(sorted(directories.items(), key=lambda x: x[1], reverse=True)[:10])
#             }
            
#         except Exception as e:
#             logger.error(f"Error getting metadata stats: {e}")
#             return {"error": str(e)}
    
#     def _get_directory_size(self, path: str) -> str:
#         """
#         Get directory size in human-readable format.
#         """
#         try:
#             if not os.path.exists(path):
#                 return "0 B"
            
#             total_size = 0
#             for dirpath, dirnames, filenames in os.walk(path):
#                 for filename in filenames:
#                     filepath = os.path.join(dirpath, filename)
#                     if os.path.exists(filepath):
#                         total_size += os.path.getsize(filepath)
            
#             # Convert to human-readable format
#             for unit in ['B', 'KB', 'MB', 'GB']:
#                 if total_size < 1024.0:
#                     return f"{total_size:.1f} {unit}"
#                 total_size /= 1024.0
            
#             return f"{total_size:.1f} TB"
            
#         except Exception as e:
#             logger.error(f"Error calculating directory size: {e}")
#             return "Unknown"
    
#     def clear_database(self) -> Dict[str, Any]:
#         """
#         Clear the entire vector database.
#         """
#         try:
#             if os.path.exists(self.vector_db_path):
#                 shutil.rmtree(self.vector_db_path)
#                 logger.info(f"Cleared vector database at {self.vector_db_path}")
#                 return {"success": True, "message": "Vector database cleared successfully"}
#             else:
#                 return {"success": True, "message": "Vector database does not exist"}
                
#         except Exception as e:
#             logger.error(f"Error clearing database: {e}")
#             return {"error": str(e)}
    
#     def backup_database(self, backup_path: str = None) -> Dict[str, Any]:
#         """
#         Create a backup of the vector database.
#         """
#         try:
#             if not os.path.exists(self.vector_db_path):
#                 return {"error": "Vector database does not exist"}
            
#             if not backup_path:
#                 backup_path = f"{self.vector_db_path}_backup_{int(os.time.time())}"
            
#             shutil.copytree(self.vector_db_path, backup_path)
#             logger.info(f"Backup created at {backup_path}")
            
#             return {
#                 "success": True,
#                 "backup_path": backup_path,
#                 "original_path": self.vector_db_path
#             }
            
#         except Exception as e:
#             logger.error(f"Error creating backup: {e}")
#             return {"error": str(e)}
    
#     def restore_database(self, backup_path: str) -> Dict[str, Any]:
#         """
#         Restore the vector database from a backup.
#         """
#         try:
#             if not os.path.exists(backup_path):
#                 return {"error": f"Backup path {backup_path} does not exist"}
            
#             # Clear existing database
#             if os.path.exists(self.vector_db_path):
#                 shutil.rmtree(self.vector_db_path)
            
#             # Restore from backup
#             shutil.copytree(backup_path, self.vector_db_path)
#             logger.info(f"Database restored from {backup_path}")
            
#             return {
#                 "success": True,
#                 "restored_from": backup_path,
#                 "restored_to": self.vector_db_path
#             }
            
#         except Exception as e:
#             logger.error(f"Error restoring database: {e}")
#             return {"error": str(e)}
    
#     def list_backups(self, backup_dir: str = ".") -> List[Dict[str, Any]]:
#         """
#         List available backups.
#         """
#         try:
#             backups = []
#             backup_dir_path = Path(backup_dir)
            
#             for item in backup_dir_path.iterdir():
#                 if item.is_dir() and "vector_db_backup" in item.name:
#                     backup_info = {
#                         "name": item.name,
#                         "path": str(item),
#                         "size": self._get_directory_size(str(item)),
#                         "created": item.stat().st_ctime if item.exists() else None
#                     }
#                     backups.append(backup_info)
            
#             # Sort by creation time (newest first)
#             backups.sort(key=lambda x: x["created"] or 0, reverse=True)
            
#             return backups
            
#         except Exception as e:
#             logger.error(f"Error listing backups: {e}")
#             return []
    
#     def export_database_info(self, export_path: str = "vector_db_info.json") -> Dict[str, Any]:
#         """
#         Export database information to a JSON file.
#         """
#         try:
#             stats = self.get_database_stats()
            
#             with open(export_path, 'w') as f:
#                 json.dump(stats, f, indent=2, default=str)
            
#             logger.info(f"Database info exported to {export_path}")
            
#             return {
#                 "success": True,
#                 "export_path": export_path,
#                 "stats": stats
#             }
            
#         except Exception as e:
#             logger.error(f"Error exporting database info: {e}")
#             return {"error": str(e)}

# def detect_language(content: str, filename: str) -> str:
#     if filename.endswith(".kt"):
#         return "Kotlin"
#     if filename.endswith(".swift"):
#         return "Swift"
#     if filename.endswith(".dart"):
#         return "Dart"
#     if filename.endswith(".ts"):
#         return "TypeScript"
#     if "data class" in content or "fun " in content:
#         return "Kotlin"
#     if "struct " in content or "SwiftUI" in content:
#         return "Swift"
#     if "override Widget" in content:
#         return "Dart"
#     return "Unknown"

# def detect_component_type(content: str, filename: str) -> str:
#     if "ViewModel" in filename or "ViewModel" in content:
#         return "ViewModel"
#     if "View" in filename or "Widget" in content:
#         return "View"
#     if "Repository" in filename:
#         return "Repository"
#     if "data class" in content or "struct " in content:
#         return "Model"
#     return "Unknown"

# def extract_component_name(filename: str) -> str:
#     return Path(filename).stem

# def reindex_components_to_vectorstore(
#     input_vector_db: str = "./vector_db",
#     output_vector_db: str = "./component_vector_db"
# ):
#     print("📥 Загрузка исходной Chroma-векторки...")
    
#     # Check if input vectorstore exists and has data
#     if not os.path.exists(input_vector_db):
#         print(f"❌ Input vectorstore not found at: {input_vector_db}")
#         return
    
#     try:
#         input_store = Chroma(
#             persist_directory=input_vector_db,
#             embedding_function=OpenAIEmbeddings()
#         )
        
#         print("📤 Извлечение документов...")
#         raw_docs = input_store.get()
#         documents = raw_docs["documents"]
#         metadatas = raw_docs["metadatas"]
        
#         print(f"📊 Found {len(documents)} documents in input vectorstore")
        
#         if len(documents) == 0:
#             print("❌ No documents found in input vectorstore!")
#             return
        
#         # Print sample metadata to debug
#         print("🔍 Sample metadata:")
#         for i, meta in enumerate(metadatas[:3]):
#             print(f"  Doc {i}: {meta}")
        
#         new_docs = []

#         for doc_text, meta in zip(documents, metadatas):
#             filename = meta.get("source") or meta.get("file_name") or meta.get("file_path") or "Unknown"
#             content = doc_text.strip()
#             language = detect_language(content, filename)
#             component_type = detect_component_type(content, filename)
#             name = extract_component_name(filename)

#             print(f"🧠 Обработка: {filename} → {component_type} [{language}]")

#             doc = Document(
#                 page_content=content,
#                 metadata={
#                     "filename": filename,
#                     "component_type": component_type,
#                     "language": language,
#                     "name": name
#                 }
#             )
#             new_docs.append(doc)

#         print(f"💾 Сохранение {len(new_docs)} документов в новую векторную базу...")
        
#         # Create output directory if it doesn't exist
#         os.makedirs(output_vector_db, exist_ok=True)
        
#         output_store = Chroma.from_documents(
#             documents=new_docs,
#             embedding=OpenAIEmbeddings(),
#             persist_directory=output_vector_db
#         )
        
#         # Explicitly persist
#         output_store.persist()
        
#         # Verify the output store has documents
#         output_docs = output_store.get()
#         print(f"✅ Компоненты успешно сохранены в Chroma-векторку. Output store has {len(output_docs['documents'])} documents.")
        
#     except Exception as e:
#         print(f"❌ Error during reindexing: {e}")
#         import traceback
#         traceback.print_exc()

# if __name__ == "__main__":
#     # You can change these paths as needed
#     reindex_components_to_vectorstore() 

import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings

# === Logging config ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

load_dotenv()

# === Detection logic ===
def detect_language(content: str, filename: str) -> str:
    if filename.endswith(".kt"):
        return "Kotlin"
    if filename.endswith(".swift"):
        return "Swift"
    if filename.endswith(".dart"):
        return "Dart"
    if filename.endswith(".ts"):
        return "TypeScript"
    if "data class" in content or "fun " in content:
        return "Kotlin"
    if "struct " in content or "SwiftUI" in content:
        return "Swift"
    if "override Widget" in content:
        return "Dart"
    return "Unknown"

def detect_component_type(content: str, filename: str) -> str:
    if "ViewModel" in filename or "ViewModel" in content:
        return "ViewModel"
    if "View" in filename or "Widget" in content:
        return "View"
    if "Repository" in filename or "Repository" in content:
        return "Repository"
    if "data class" in content or "struct " in content:
        return "Model"
    return "Unknown"

def extract_component_name(filename: str) -> str:
    return Path(filename).stem

# === Main reindexing function ===
def reindex_components_to_vectorstore(
    input_vector_db: str = "./vector_db",
    output_vector_db: str = "./component_vector_db"
):
    logger.info("📥 Loading input vectorstore...")

    if not os.path.exists(input_vector_db):
        logger.error(f"❌ Input vectorstore not found: {input_vector_db}")
        return

    try:
        input_store = Chroma(
            persist_directory=input_vector_db,
            embedding_function=OpenAIEmbeddings()
        )

        raw_docs = input_store.get()
        documents = raw_docs.get("documents", [])
        metadatas = raw_docs.get("metadatas", [])

        if not documents:
            logger.warning("No documents found in the input vectorstore.")
            return

        logger.info(f"📊 Total documents loaded: {len(documents)}")

        new_docs = []
        known, unknown = 0, 0

        for doc_text, meta in zip(documents, metadatas):
            filename = meta.get("source") or meta.get("file_name") or meta.get("file_path") or "Unknown"
            content = doc_text.strip()
            language = detect_language(content, filename)
            component_type = detect_component_type(content, filename)
            name = extract_component_name(filename)

            if component_type == "Unknown" or language == "Unknown":
                unknown += 1
                continue

            known += 1
            logger.info(f"{filename} → {component_type} ({language})")

            new_docs.append(Document(
                page_content=content,
                metadata={
                    "filename": filename,
                    "component_type": component_type,
                    "language": language,
                    "name": name
                }
            ))

        if not new_docs:
            logger.warning("No valid components to save.")
            return

        os.makedirs(output_vector_db, exist_ok=True)

        logger.info(f"💾 Saving {len(new_docs)} classified components to: {output_vector_db}")
        output_store = Chroma.from_documents(
            documents=new_docs,
            embedding=OpenAIEmbeddings(),
            persist_directory=output_vector_db
        )
        output_store.persist()

        logger.info(f"✅ Reindex complete: {known} saved, {unknown} skipped as 'Unknown'.")

    except Exception as e:
        logger.exception(f"❌ Error during reindexing: {e}")

# === Entry point ===
if __name__ == "__main__":
    reindex_components_to_vectorstore()
