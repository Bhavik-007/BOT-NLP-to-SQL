# Enterprise NLP-to-SQL and Document RAG Bot

An enterprise-style Streamlit application that provides two assistant modes:

- **SQL Assistant**: Ask natural language business questions and receive answers from Microsoft SQL Server without exposing generated SQL in the UI.
- **Document Assistant**: Upload documents or images, create a vector index, and ask grounded questions against text content or image-derived analytical descriptions using Retrieval-Augmented Generation.

The application uses local LLM inference through Ollama, SQL Server connectivity through SQLAlchemy and pyodbc, vector search through Qdrant with an in-memory fallback, and optional MongoDB persistence for document metadata and chat history.

## Features

- Natural language to SQL Server answers
- Read-only SQL generation and validation
- Windows Authentication for SQL Server
- YAML-driven database and RAG configuration
- Streamlit enterprise-style UI
- Ollama local model integration
- Qdrant semantic retrieval for SQL schema, documents, and image-derived knowledge
- Document and image upload with manual index creation
- Supported document types: TXT, MD, CSV, PDF, DOCX
- Supported image types: PNG, JPG, JPEG, TIF, TIFF
- Visualization analysis for charts, dashboards, maps, heatmaps, diagrams, plots, and infographics
- Optional MongoDB metadata and chat history storage
- Audit logging to both `logs/app.log` and `logs/app.csv`
- SQL Server connection test utility
- Sample SQL Server tables and data script

## High-Level Architecture

```text
User
 |
 | Streamlit UI
 v
app/ui/main.py
 |
 +-----------------------+
 | Assistant Mode Switch |
 +-----------------------+
     |                         |
     v                         v
SQL Assistant              Document Assistant
     |                         |
     v                         v
SQLBotService              RAGService
     |                         |
     +--> SchemaRetriever      +--> DocumentLoader
     |       |                 +--> DocumentVectorStore
     |       v                 +--> MongoManager
     |     Qdrant              |
     |                         v
     +--> Ollama LLM         Qdrant or Memory Fallback
     |
     +--> SQLSecurity
     |
     +--> DatabaseManager
             |
             v
        SQL Server
```

## Project Structure

```text
app/
  core/
    config.py              # Loads YAML and .env configuration
    logging_config.py      # Rotating app log and CSV audit logging
    security.py            # SQL safety validation

  engine/
    db_manager.py          # SQLAlchemy + pyodbc database execution
    vector_search.py       # SQL schema vector retrieval
    document_loader.py     # Document text extraction and chunking
    image_analyzer.py      # Ollama vision-based image analysis
    document_vector_store.py # Document vector indexing/search
    mongo_manager.py       # Optional MongoDB persistence

  services/
    bot_service.py         # NLP-to-SQL orchestration
    rag_service.py         # Document and image RAG orchestration

  ui/
    main.py                # Streamlit application

config/
  settings.yaml            # SQL Server, Ollama, Qdrant settings
  tables_config.yaml       # Approved SQL tables, columns, relationships
  rag_settings.yaml        # Document RAG and MongoDB settings

sql/
  sample_business_tables.sql

test_sql_connection.py     # SQL Server connectivity tester
requirements.txt
```

## Technology Stack

- **Frontend**: Streamlit
- **LLM Runtime**: Ollama local models
- **SQL Database**: Microsoft SQL Server
- **SQL Authentication**: Windows Authentication
- **DB Layer**: SQLAlchemy + pyodbc
- **Vector Search**: Qdrant
- **Embeddings**: sentence-transformers
- **Document Metadata**: MongoDB, optional
- **Configuration**: YAML + `.env`
- **Logging**: Python logging with rotating logs and CSV audit file

## Setup

### 1. Create and activate virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

If `python` is not available, use your installed Python launcher/path.

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Install SQL Server ODBC Driver

Install Microsoft ODBC Driver 17 or 18 for SQL Server.

The current project configuration uses:

```yaml
driver: "ODBC Driver 17 for SQL Server"
```

### 4. Configure SQL Server

Edit:

[config/settings.yaml](config/settings.yaml)

Example:


### 5. Test SQL Server connection

```powershell
python test_sql_connection.py
```

The script tests common SQL Server connection values and prints the working server value.

### 6. Create sample tables

Run this script in SSMS against `Jarvis_dev`:

[sql/sample_business_tables.sql](sql/sample_business_tables.sql)

It creates:

- `[dbo].[Product_Master]`
- `[dbo].[Sales_Order]`

The existing expected customer table is:

- `[dbo].[Customer_Purchase]`

## Running the Application

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/ui/main.py
```

Then open the Streamlit URL shown in the terminal.

## SQL Assistant Flow

```text
User question
 -> Validate question intent
 -> Retrieve relevant table schema from Qdrant or YAML fallback
 -> Generate safe T-SQL using Ollama
 -> Validate generated SQL
 -> Execute read-only query against SQL Server
 -> Summarize result using Ollama
 -> Return business answer to UI
 -> Write audit row to logs/app.csv
```

The generated SQL is intentionally not displayed in the frontend.

## SQL Safety Controls

The SQL Assistant validates generated SQL before execution:

- Only `SELECT` statements are allowed
- Multiple statements are blocked
- SQL comments are blocked
- Destructive keywords are blocked
- Only configured tables are allowed
- Table metadata comes from `config/tables_config.yaml`

Blocked operations include:

```text
INSERT, UPDATE, DELETE, DROP, ALTER, EXEC, TRUNCATE, MERGE, CREATE
```

## Table Configuration

Approved SQL tables are configured in:

[config/tables_config.yaml](config/tables_config.yaml)

Example:

```yaml
tables:
  Customer_Purchase:
    schema: "dbo"
    full_name: "[dbo].[Customer_Purchase]"
    description: "Customer purchase table containing customer demographics, purchase amount, ad click flag, actual label, and predicted label."
    primary_key: "Customer_ID"
    allowed_columns: ["Customer_ID","Age","City","Purchase_Amount","Ad_Click","Actual","Predicted"]
```

To add another SQL table, add it to this file with:

- logical table name
- schema
- full SQL Server object name
- description
- primary key
- allowed columns
- optional relationships

Restart Streamlit after changing table config.

## Document And Image Assistant Flow

```text
Upload document or image
 -> Click Create Document Index
 -> Extract text or analyze visualization with Ollama vision
 -> Split into chunks
 -> Create embeddings
 -> Store chunks in Qdrant or memory fallback
 -> Ask document or image question
 -> Retrieve relevant chunks
 -> Generate grounded answer using Ollama
 -> Optionally save metadata/history to MongoDB
```

Supported document types:

```text
txt, md, csv, pdf, docx
```

Supported image types:

```text
png, jpg, jpeg, tif, tiff
```

Image analysis is designed for:

```text
business charts, data visualizations, graphs, dashboards, spatial maps, heatmaps,
engineering diagrams, scientific plots, and infographics
```

For images, the app generates a semantic description that captures visualization type, visible labels, trends, outliers, analytical insights, and limitations.

For scanned PDFs, text extraction may fail because OCR is not currently included. Convert scanned PDFs to searchable text PDFs or add an OCR pipeline.

## Document RAG Configuration

Edit:

[config/rag_settings.yaml](config/rag_settings.yaml)

```yaml
rag:
  collection_name: "document_chunks"
  chunk_size: 900
  chunk_overlap: 150
  top_k: 4
  supported_file_types: ["txt", "md", "csv", "pdf", "docx", "png", "jpg", "jpeg", "tif", "tiff"]

image_analysis:
  vision_model: "llava"
  timeout_seconds: 120

```

## Qdrant

Qdrant is used for:

- SQL schema semantic retrieval
- document and image-derived chunk vector search

Start Qdrant with Docker:

```powershell
docker run -p 6333:6333 qdrant/qdrant
```

If Qdrant is not running:

- SQL Assistant falls back to YAML schema context
- Document Assistant uses in-memory vector search for the current Streamlit session

## MongoDB

MongoDB is optional. It stores:

- uploaded document and image metadata
- document assistant chat history

Start MongoDB locally or update:


If MongoDB is unavailable, the app continues running and skips persistence.

## Ollama

The app expects Ollama at:

```yaml
ollama:
  base_url: "http://localhost:11434"
  model: "llama3"
```

Start Ollama and ensure your model is available:

```powershell
ollama pull llama3
ollama pull llava
ollama serve
```

`llama3` is used for text answering. `llava` is used for image and visualization analysis. You can change the vision model in `config/rag_settings.yaml`.

## Audit Logging

The application writes:

```text
logs/app.log
logs/app.csv
```

`app.csv` contains structured audit rows:

```csv
timestamp_utc,status,question,generated_sql,answer
```

For Document Assistant entries, `generated_sql` is blank.

## Environment Variables

## Example SQL Assistant Questions

```text
What is the average purchase amount by city?
Show total sales amount by region.
Which product category has the highest sales?
Show sales by customer city and product category.
What is the average order value by sales channel?
```

## Example Document Assistant Questions

After uploading and indexing a document:

```text
Summarize this document.
What is the candidate's education background?
List the key skills mentioned in the document.
What are the important dates in this document?
What experience is described in the document?
```

After uploading and indexing an image or visualization:

```text
What type of visualization is this?
What are the main trends in this chart?
Summarize the key insights from this dashboard.
Are there any outliers or anomalies?
What business conclusion can be drawn from this heatmap?
Explain this engineering diagram.
```

## Troubleshooting

### SQL Server error 53

Usually means SQL Server host or instance is wrong.

Run:

```powershell
python test_sql_connection.py
```

Use the working server value in `config/settings.yaml`.

### Invalid object name

The table name in generated SQL does not exist in SQL Server.

Fix:

- Confirm the real table name in SSMS
- Update `config/tables_config.yaml`
- Restart Streamlit

### Qdrant connection refused

Start Qdrant:

```powershell
docker run -p 6333:6333 qdrant/qdrant
```

Or continue with fallback mode.

### PDF uploaded but no document answer

If the PDF is scanned/image-based, `pypdf` cannot extract text.

Fix:

- Use a searchable PDF
- Convert PDF to text
- Add OCR support in a future enhancement

### Image analysis fails

Confirm Ollama is running and the configured vision model exists:

```powershell
ollama pull llava
ollama list
```

Then retry `Create Document Index` from the Streamlit sidebar.

### App imports fail with `No module named app`

Run from project root:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app/ui/main.py
```

## Roadmap

Recommended next enhancements:

- Add OCR for scanned PDFs and image text extraction
- Add user authentication
- Add role-based table access
- Add SQL query preview for admins only
- Add FastAPI backend service layer
- Add persistent Qdrant collections per user/session
- Add MongoDB chat history viewer
- Add exportable answer reports
- Add automated tests for SQL validation and document ingestion

## Current Status

The application currently supports:

- SQL Assistant against SQL Server
- Document Assistant with manual document and image indexing
- Image recognition and visualization analysis through Ollama vision models
- Local Ollama LLM
- Qdrant with fallback behavior
- Optional MongoDB persistence
- Structured CSV audit logging
