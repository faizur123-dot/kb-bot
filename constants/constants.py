PINECONE_INDEX = "regie-ai-interview"
FILE_FORMAT_PARQUET = "PARQUET"
FILE_FORMAT_CSV = "CSV"
FILE_FORMAT_JSON = "JSON"
LOCAL_ENVIRONMENT = "local"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 20
EMBEDDED_TEXT = "embedded_text"
SRC_CREATION_TIME = "src_creation_time"
SRC_TEXT = "source_text"
TENANT_ID = "tenant_id"
SRC = "source"
SRC_ID = "source_id"
PARENT_SOURCE_ID = 'parent_source_id'
SRC_TEXT_CHECKSUM = 'src_text_checksum'
POSTGRES_PORT = 5432
POSTGRES_USER = "postgres"
FILE_PERSIST_LOCATION = "/tmp/"
CATEGORIES = ["Bug", "Feature Request", "General Question", "Other"]
CATEGORISE_BUG_TEMPLATE = """
You are a helpful assistant that categorizes user text into one of the following categories: {categories}.
Based on the text provided, please provide the most suitable category. Dont tell anything outside category. if anything outside category, put it in General Question
Text: {text}
Category:
"""
KB_QUERY_TEMPLATE = "You are a highly knowledgeable assistant. "
"Answer the following question using only the information provided in the vector database. "
"If the answer cannot be found in the database, respond with 'I don't know.'\n\n"
"Question: {question}"

JIRA_EMAIL = "furahman41@gmail.com"
RETRIES_FOR_ASSIGNING_TICKET = 3
PROJECT_KEY = "SCRUM"
KNOWLEDGE_BASE_QUERY_RESPONSE_MESSAGE = (
    "Your knowledge base response is ready! View message."
)
