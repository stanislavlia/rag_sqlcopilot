from langchain_community.vectorstores import Chroma
from copilot_base import OPENAI_API_KEY
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
import chromadb

CHROMA_DB_HOST="localhost"
CHROMA_DB_PORT=8000
OPENAI_EMBEDDING_FUNC = OpenAIEmbeddingFunction(model_name="text-embedding-ada-002",
                                                api_key=OPENAI_API_KEY)




