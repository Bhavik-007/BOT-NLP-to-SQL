from langchain_ollama import OllamaLLM
from app.engine.db_manager import DatabaseManager
from app.engine.vector_search import SchemaRetriever
from app.core.config import config
from app.core.security import SQLSecurity

class SQLBotService:
    def __init__(self, model_name=None):
        ollama_settings = config.settings.get("ollama", {})
        self.llm = OllamaLLM(
            base_url=ollama_settings.get("base_url", "http://localhost:11434"),
            model=model_name or ollama_settings.get("model", "llama3"),
            temperature=ollama_settings.get("temperature", 0)
        )
        self.db = DatabaseManager()
        self.retriever = SchemaRetriever()

    def ask(self, question: str):
        if not question or not question.strip():
            return "Please enter a business question.", ""

        # 1. Retrieve relevant metadata
        schema_context = self.retriever.get_relevant_schema(question)
        
        # 2. SQL Generation
        gen_prompt = self._build_sql_prompt(question, schema_context)
        generated_sql = self._clean_sql(self.llm.invoke(gen_prompt))

        is_safe, reason = SQLSecurity.validate(generated_sql, config.tables)
        if not is_safe:
            return f"I could not generate a safe query for that question. {reason}", generated_sql
        
        # 3. Execution
        df, error = self.db.execute_query(generated_sql)
        if error:
            return error, generated_sql
        if df is None or df.empty:
            return "No data found", generated_sql
            
        # 4. Summarization
        ans_prompt = (
            "You are a business data analyst. Answer the user's question using only "
            "the provided query result. Do not mention or expose SQL.\n\n"
            f"Question: {question}\n"
            f"Data JSON: {df.head(50).to_json(orient='records')}\n\n"
            "Return a concise business answer."
        )
        return self.llm.invoke(ans_prompt), generated_sql

    @staticmethod
    def _build_sql_prompt(question: str, schema_context: str) -> str:
        return (
            "You generate safe Microsoft SQL Server T-SQL for a read-only analytics assistant.\n"
            "Rules:\n"
            "- Return only one SELECT statement.\n"
            "- Do not include markdown fences, comments, explanations, or semicolons.\n"
            "- Use only the provided tables and columns.\n"
            "- Use the exact SQL table name from the schema, including square brackets and schema name when provided.\n"
            "- Never use INSERT, UPDATE, DELETE, DROP, ALTER, EXEC, TRUNCATE, SELECT INTO, temp tables, or stored procedures.\n"
            "- Add TOP 100 unless the user clearly asks for an aggregate result.\n\n"
            f"Allowed schema:\n{schema_context}\n\n"
            f"User question: {question}\n"
            "T-SQL:"
        )

    @staticmethod
    def _clean_sql(raw_sql: str) -> str:
        sql = (raw_sql or "").strip()
        if sql.startswith("```"):
            sql = sql.strip("`").replace("sql", "", 1).replace("SQL", "", 1).strip()
        return sql.rstrip(";").strip()
