from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
import chromadb

CHROMA_DB_HOST="localhost"
CHROMA_DB_PORT=8000




