from langchain_core.runnables import RunnablePassthrough, RunnableParallel
import logging
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from retrieval_graph import RetrievalManager
from postgres_executor_graph import PostgresExecutor
import chromadb
import os
from dotenv import load_dotenv
from pprint import pprint

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

#============SETTINGS==================
PG_DATABASE = os.getenv('PG_DATABASE')
PG_USER = os.getenv('PG_USER')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_SCHEMA = os.getenv('PG_SCHEMA')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PG_URI = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
MODEL_NAME="gpt-4o"
MEMORY_DIR=os.getenv("MEMORY_DIR", default="/memory_dir")
CHROMA_DB_HOST="localhost"
CHROMA_DB_PORT=8000
OPENAI_EMBEDDING_FUNC = OpenAIEmbeddings(model="text-embedding-ada-002",
                                        api_key=OPENAI_API_KEY)


#Connect to Chroma
chromadb_client = chromadb.HttpClient(host=CHROMA_DB_HOST,
                                          port=CHROMA_DB_PORT)

logging.info("Connected to Chroma sucessfully")

#Create collections
ddl_vecstore = Chroma(client=chromadb_client,
                          collection_name="ddl_statements",
                          embedding_function=OPENAI_EMBEDDING_FUNC,
                          persist_directory=None)
    
sqlexamples_vecstore = Chroma(client=chromadb_client,
                          collection_name="sql_examples",
                          embedding_function=OPENAI_EMBEDDING_FUNC,
                          persist_directory=None)
    
doc_vecstore = Chroma(client=chromadb_client,
                          collection_name="docs",
                          embedding_function=OPENAI_EMBEDDING_FUNC,
                          persist_directory=None)


retrieval_manager = RetrievalManager(ddl_collection=ddl_vecstore,
                                     sql_examples_collection=sqlexamples_vecstore,
                                     doc_collection=doc_vecstore).get_runnable()



postgres_executor = PostgresExecutor(pg_database=PG_DATABASE,
                                     pg_user=PG_USER,
                                     pg_password=PG_PASSWORD,
                                     pg_host=PG_HOST,
                                     pg_port=PG_PORT,
                                     pg_schema=PG_SCHEMA).get_runnable()





postgres_executor.invoke({"sql_query" : "DELETE _id, fullname FROM copilot2.couriers LIMIT 102"})



# pprint(retrieval_manager.invoke({"question" : "Who is the most efficient driver according to KPI?"}))


 