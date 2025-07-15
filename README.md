# Android Project RAG System

A comprehensive RAG (Retrieval-Augmented Generation) system designed to process Android projects and create a vector knowledge base for LLM context. This system allows you to query your Android project using natural language and get intelligent responses based on the actual codebase.

## Features

- 🔍 **Intelligent File Processing**: Automatically processes Kotlin, Java, XML, JSON, and other relevant Android project files
- 🧠 **Vector Knowledge Base**: Creates embeddings using OpenAI and stores them in a Chroma vector database
- 🤖 **Natural Language Queries**: Query your Android project using natural language
- 📊 **Comprehensive Metadata**: Tracks file types, languages, directories, and relationships
- 🔄 **Smart Chunking**: Intelligent text splitting with configurable chunk sizes and overlap
- 💾 **Database Management**: Backup, restore, and manage your vector database
- 📈 **Statistics & Analytics**: Get detailed insights about your processed project

## Project Structure

```
Hackaton3/
├── ANDROID_APP/                    # Your Android project
├── android_rag_processor.py        # Main RAG processing script
├── query_interface.py              # Interactive query interface
├── vector_db_manager.py            # Vector database management
├── requirements.txt                # Python dependencies
├── env_template.txt                # Environment variables template
└── README.md                      # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the environment template and add your OpenAI API key:

```bash
cp env_template.txt .env
```

Edit the `.env` file and add your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
VECTOR_DB_PATH=./vector_db
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MAX_TOKENS=4000
INCLUDE_EXTENSIONS=.kt,.xml,.json,.txt,.md
EXCLUDE_PATTERNS=__pycache__,*.pyc,.git,node_modules
```

### 3. Process Your Android Project

Run the main RAG processor to create the vector knowledge base:

```bash
python android_rag_processor.py
```

This will:
- Scan all relevant files in your `ANDROID_APP` directory
- Process and chunk the content
- Create embeddings using OpenAI
- Store everything in a Chroma vector database

### 4. Query Your Project

Use the interactive query interface:

```bash
python query_interface.py
```

Or use the programmatic interface:

```python
from query_interface import AndroidProjectQueryInterface

# Initialize the query interface
query_interface = AndroidProjectQueryInterface()

# Query your project
result = query_interface.query_project("How does the quiz functionality work?")
print(result["llm_response"])
```

## Usage Examples

### Example Queries

1. **Code Structure Questions**:
   - "What activities are in the app?"
   - "Show me the data models"
   - "How is the UI structured?"

2. **Functionality Questions**:
   - "How does the quiz functionality work?"
   - "What sports are supported?"
   - "How is user data stored?"

3. **File-Specific Questions**:
   - "What's in the MainActivity?"
   - "Show me the layout files"
   - "What's in the data models?"

### Database Management

Manage your vector database using the manager:

```bash
python vector_db_manager.py
```

Options include:
- Get database statistics
- Clear the database
- Create/restore backups
- Export database information

## Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Required | Your OpenAI API key |
| `VECTOR_DB_PATH` | `./vector_db` | Path to store the vector database |
| `CHUNK_SIZE` | `1000` | Size of text chunks |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `MAX_TOKENS` | `4000` | Maximum tokens for LLM responses |
| `INCLUDE_EXTENSIONS` | `.kt,.xml,.json,.txt,.md` | File extensions to process |
| `EXCLUDE_PATTERNS` | `__pycache__,*.pyc,.git,node_modules` | Patterns to exclude |

### File Processing

The system automatically processes:
- **Kotlin files** (`.kt`) - Main Android code
- **XML files** (`.xml`) - Layouts and configurations
- **JSON files** (`.json`) - Data and configurations
- **Text files** (`.txt`) - Documentation and data
- **Markdown files** (`.md`) - Documentation

## API Reference

### AndroidProjectRAGProcessor

Main class for processing Android projects.

```python
from android_rag_processor import AndroidProjectRAGProcessor

# Initialize processor
processor = AndroidProjectRAGProcessor(project_path="ANDROID_APP")

# Process the entire project
vector_store = processor.run_full_processing()

# Query the knowledge base
results = processor.query_knowledge_base("How does the quiz work?", k=5)
```

### AndroidProjectQueryInterface

Interface for querying the knowledge base.

```python
from query_interface import AndroidProjectQueryInterface

# Initialize query interface
query_interface = AndroidProjectQueryInterface()

# Query with LLM response
result = query_interface.query_project("What activities are in the app?")

# Search by file type
kotlin_files = query_interface.search_by_file_type(".kt", "activity")

# Search by directory
ui_files = query_interface.search_by_directory("ui", "layout")
```

### VectorDBManager

Manage the vector database.

```python
from vector_db_manager import VectorDBManager

# Initialize manager
manager = VectorDBManager()

# Get statistics
stats = manager.get_database_stats()

# Create backup
backup_result = manager.backup_database()

# Clear database
clear_result = manager.clear_database()
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**:
   ```
   Error: OPENAI_API_KEY not found in environment variables!
   ```
   Solution: Make sure your `.env` file contains a valid OpenAI API key.

2. **Project Path Not Found**:
   ```
   Error: Project path ANDROID_APP does not exist!
   ```
   Solution: Ensure your Android project is in the `ANDROID_APP` directory or update the path in the processor.

3. **Vector Database Errors**:
   ```
   Error: No vector store available
   ```
   Solution: Run the RAG processor first to create the vector database.

4. **Memory Issues**:
   If you encounter memory issues with large projects, try:
   - Reducing `CHUNK_SIZE` in your `.env` file
   - Processing files in smaller batches
   - Using a machine with more RAM

### Performance Tips

1. **For Large Projects**:
   - Increase `CHUNK_SIZE` to reduce the number of embeddings
   - Use `EXCLUDE_PATTERNS` to skip unnecessary files
   - Process during off-peak hours to avoid API rate limits

2. **For Better Results**:
   - Use specific, detailed queries
   - Include file names or paths in your queries
   - Ask about specific functionality rather than general questions

3. **For Development**:
   - Use the interactive query interface for exploration
   - Export database info for analysis
   - Create regular backups of your vector database

## Advanced Usage

### Custom File Processing

You can customize which files are processed by modifying the `INCLUDE_EXTENSIONS` and `EXCLUDE_PATTERNS` in your `.env` file.

### Custom Embeddings

To use different embedding models, modify the `AndroidProjectRAGProcessor` class:

```python
# Use a different embedding model
self.embeddings = OpenAIEmbeddings(
    openai_api_key=os.getenv("OPENAI_API_KEY"),
    model="text-embedding-3-large"  # or other models
)
```

### Custom Chunking

Adjust chunking parameters for better results:

```python
# More aggressive chunking for code files
self.text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,  # Smaller chunks for code
    chunk_overlap=100,
    separators=["\n\n", "\n", " ", ""]
)
```

## Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

If you encounter any issues or have questions:

1. Check the troubleshooting section above
2. Review the logs for detailed error messages
3. Ensure your OpenAI API key is valid and has sufficient credits
4. Verify your Android project structure is correct

---

**Happy coding! 🚀** 