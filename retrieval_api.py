from langchain_community.vectorstores import Chroma
from copilot_base import OPENAI_API_KEY
from langchain_openai import OpenAIEmbeddings

import chromadb

CHROMA_DB_HOST="localhost"
CHROMA_DB_PORT=8000
OPENAI_EMBEDDING_FUNC = OpenAIEmbeddings(model="text-embedding-ada-002",
                                        api_key=OPENAI_API_KEY)




