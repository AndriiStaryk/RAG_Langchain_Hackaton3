import os
import shutil
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from dotenv import load_dotenv
from android_rag_processor import AndroidProjectRAGProcessor

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VectorDBManager:
    """
    Manager for the vector database operations.
    """
    
    def __init__(self):
        load_dotenv()
        self.vector_db_path = os.getenv("VECTOR_DB_PATH", "./vector_db")
        self.rag_processor = AndroidProjectRAGProcessor()
    
    def get_database_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database.
        """
        try:
            vector_store = self.rag_processor.load_vector_store()
            if not vector_store:
                return {"error": "No vector database found"}
            
            collection = vector_store._collection
            count = collection.count()
            
            # Get metadata statistics
            metadata_stats = self._get_metadata_stats(collection)
            
            stats = {
                "total_documents": count,
                "vector_db_path": self.vector_db_path,
                "database_exists": os.path.exists(self.vector_db_path),
                "database_size": self._get_directory_size(self.vector_db_path),
                "metadata_stats": metadata_stats
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}
    
    def _get_metadata_stats(self, collection) -> Dict[str, Any]:
        """
        Get statistics about document metadata.
        """
        try:
            # Get all documents to analyze metadata
            results = collection.get()
            
            if not results or not results['metadatas']:
                return {"error": "No metadata available"}
            
            metadatas = results['metadatas']
            
            # Count file types
            file_types = {}
            languages = {}
            directories = {}
            
            for metadata in metadatas:
                if metadata:
                    # File types
                    file_ext = metadata.get('file_extension', 'Unknown')
                    file_types[file_ext] = file_types.get(file_ext, 0) + 1
                    
                    # Languages
                    lang = metadata.get('language', 'Unknown')
                    languages[lang] = languages.get(lang, 0) + 1
                    
                    # Directories
                    directory = metadata.get('directory', 'Unknown')
                    directories[directory] = directories.get(directory, 0) + 1
            
            return {
                "file_types": file_types,
                "languages": languages,
                "top_directories": dict(sorted(directories.items(), key=lambda x: x[1], reverse=True)[:10])
            }
            
        except Exception as e:
            logger.error(f"Error getting metadata stats: {e}")
            return {"error": str(e)}
    
    def _get_directory_size(self, path: str) -> str:
        """
        Get directory size in human-readable format.
        """
        try:
            if not os.path.exists(path):
                return "0 B"
            
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            
            # Convert to human-readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if total_size < 1024.0:
                    return f"{total_size:.1f} {unit}"
                total_size /= 1024.0
            
            return f"{total_size:.1f} TB"
            
        except Exception as e:
            logger.error(f"Error calculating directory size: {e}")
            return "Unknown"
    
    def clear_database(self) -> Dict[str, Any]:
        """
        Clear the entire vector database.
        """
        try:
            if os.path.exists(self.vector_db_path):
                shutil.rmtree(self.vector_db_path)
                logger.info(f"Cleared vector database at {self.vector_db_path}")
                return {"success": True, "message": "Vector database cleared successfully"}
            else:
                return {"success": True, "message": "Vector database does not exist"}
                
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
            return {"error": str(e)}
    
    def backup_database(self, backup_path: str = None) -> Dict[str, Any]:
        """
        Create a backup of the vector database.
        """
        try:
            if not os.path.exists(self.vector_db_path):
                return {"error": "Vector database does not exist"}
            
            if not backup_path:
                backup_path = f"{self.vector_db_path}_backup_{int(os.time.time())}"
            
            shutil.copytree(self.vector_db_path, backup_path)
            logger.info(f"Backup created at {backup_path}")
            
            return {
                "success": True,
                "backup_path": backup_path,
                "original_path": self.vector_db_path
            }
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return {"error": str(e)}
    
    def restore_database(self, backup_path: str) -> Dict[str, Any]:
        """
        Restore the vector database from a backup.
        """
        try:
            if not os.path.exists(backup_path):
                return {"error": f"Backup path {backup_path} does not exist"}
            
            # Clear existing database
            if os.path.exists(self.vector_db_path):
                shutil.rmtree(self.vector_db_path)
            
            # Restore from backup
            shutil.copytree(backup_path, self.vector_db_path)
            logger.info(f"Database restored from {backup_path}")
            
            return {
                "success": True,
                "restored_from": backup_path,
                "restored_to": self.vector_db_path
            }
            
        except Exception as e:
            logger.error(f"Error restoring database: {e}")
            return {"error": str(e)}
    
    def list_backups(self, backup_dir: str = ".") -> List[Dict[str, Any]]:
        """
        List available backups.
        """
        try:
            backups = []
            backup_dir_path = Path(backup_dir)
            
            for item in backup_dir_path.iterdir():
                if item.is_dir() and "vector_db_backup" in item.name:
                    backup_info = {
                        "name": item.name,
                        "path": str(item),
                        "size": self._get_directory_size(str(item)),
                        "created": item.stat().st_ctime if item.exists() else None
                    }
                    backups.append(backup_info)
            
            # Sort by creation time (newest first)
            backups.sort(key=lambda x: x["created"] or 0, reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"Error listing backups: {e}")
            return []
    
    def export_database_info(self, export_path: str = "vector_db_info.json") -> Dict[str, Any]:
        """
        Export database information to a JSON file.
        """
        try:
            stats = self.get_database_stats()
            
            with open(export_path, 'w') as f:
                json.dump(stats, f, indent=2, default=str)
            
            logger.info(f"Database info exported to {export_path}")
            
            return {
                "success": True,
                "export_path": export_path,
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"Error exporting database info: {e}")
            return {"error": str(e)}

def main():
    """
    Main function to run the vector database manager.
    """
    manager = VectorDBManager()
    
    print("🗄️  Vector Database Manager")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Get database statistics")
        print("2. Clear database")
        print("3. Create backup")
        print("4. Restore from backup")
        print("5. List backups")
        print("6. Export database info")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == "1":
            stats = manager.get_database_stats()
            print("\n📊 Database Statistics:")
            print(json.dumps(stats, indent=2, default=str))
            
        elif choice == "2":
            confirm = input("⚠️  Are you sure you want to clear the database? (yes/no): ").strip().lower()
            if confirm == "yes":
                result = manager.clear_database()
                print(f"\n🗑️  {result.get('message', result.get('error', 'Unknown error'))}")
            else:
                print("❌ Operation cancelled")
                
        elif choice == "3":
            backup_path = input("Enter backup path (or press Enter for default): ").strip()
            if not backup_path:
                backup_path = None
            result = manager.backup_database(backup_path)
            if "success" in result:
                print(f"✅ Backup created at: {result['backup_path']}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        elif choice == "4":
            backup_path = input("Enter backup path to restore from: ").strip()
            result = manager.restore_database(backup_path)
            if "success" in result:
                print(f"✅ Database restored from: {result['restored_from']}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        elif choice == "5":
            backups = manager.list_backups()
            if backups:
                print("\n📦 Available Backups:")
                for i, backup in enumerate(backups, 1):
                    print(f"{i}. {backup['name']}")
                    print(f"   Path: {backup['path']}")
                    print(f"   Size: {backup['size']}")
                    print()
            else:
                print("📭 No backups found")
                
        elif choice == "6":
            export_path = input("Enter export path (or press Enter for default): ").strip()
            if not export_path:
                export_path = "vector_db_info.json"
            result = manager.export_database_info(export_path)
            if "success" in result:
                print(f"✅ Database info exported to: {result['export_path']}")
            else:
                print(f"❌ Error: {result.get('error', 'Unknown error')}")
                
        elif choice == "7":
            print("👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 