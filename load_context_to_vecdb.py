from langchain_community.vectorstores import Chroma
from pprint import pprint
import os

from langchain.evaluation import EmbeddingDistance
from langchain.evaluation import load_evaluator
import logging
from retrieval_graph import check_if_duplicate
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings


load_dotenv()


    
def read_file_content(path):
    with open(path, "r") as file:
        content = file.read()
        return content
    
def add_comment_doc(doc_content, comment):
    return comment + "\n\n" + doc_content 





CHROMA_DIR = "./chroma"
CONTEXT_DIR_PATH = "tables_info/"
SQL_EXAMPLES_DIR = "sql_examples/"
DOMAIN_CONTEXT_DIR = "domain_context/"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


DDL_TABLES_FILES = [
    "applicationgoods.txt",
    "applications.txt",
    "apporders.txt",
    "clients.txt",
    "companies.txt",
    "couriers.txt",
    "routes.txt",
    "transports.txt"
]

DOCS_FILES = [os.path.join(DOMAIN_CONTEXT_DIR, file) for file in os.listdir(DOMAIN_CONTEXT_DIR)]

TRAIN_SQL_FILES = os.listdir(SQL_EXAMPLES_DIR)


DDL_TABLES_FILES = [os.path.join(CONTEXT_DIR_PATH, filename) for filename in DDL_TABLES_FILES]    
DDL_TABLES_SQL_QUERIES = [read_file_content(path) for path in DDL_TABLES_FILES]
CONTEXT_DOCS = [read_file_content(path) for path in DOCS_FILES]

TRAIN_SQL_EXAMPLES = [read_file_content(os.path.join(SQL_EXAMPLES_DIR, file))
                       for file in TRAIN_SQL_FILES]



if __name__ == "__main__":


    OPENAI_EMBEDDING_FUNC = OpenAIEmbeddings(model="text-embedding-ada-002",
                                        api_key=OPENAI_API_KEY)


    ddl_vecstore = Chroma(persist_directory=CHROMA_DIR  ,
                          collection_name="ddl_statements",
                          embedding_function=OPENAI_EMBEDDING_FUNC,
                        persist_directory=None)
    
    sqlexamples_vecstore = Chroma(persist_directory=CHROMA_DIR ,
                            collection_name="sql_examples",
                            embedding_function=OPENAI_EMBEDDING_FUNC,
                            )
        
    doc_vecstore = Chroma(persist_directory=CHROMA_DIR,
                            collection_name="docs",
                            embedding_function=OPENAI_EMBEDDING_FUNC,
                            )


    #load docs to collections

    filtered_ddl = [doc for doc in DDL_TABLES_SQL_QUERIES if not check_if_duplicate(ddl_vecstore, doc)]
    filtered_sql_exmpls = [doc for doc in TRAIN_SQL_EXAMPLES if not check_if_duplicate(sqlexamples_vecstore, doc)]
    filtered_documentation = [doc for doc in CONTEXT_DOCS if not check_if_duplicate(doc_vecstore, doc)]
    



    #load context to collections
    if (filtered_ddl):
        ddl_vecstore.add_texts(texts=filtered_ddl)
    if (filtered_sql_exmpls):
        sqlexamples_vecstore.add_texts(texts=filtered_sql_exmpls)
    if (filtered_documentation):
        doc_vecstore.add_texts(texts=filtered_documentation)

    logging.info(f"{len(filtered_ddl)} of new docs loaded to DDL collection")
    logging.info(f"{len(filtered_sql_exmpls)} of new docs loaded to sql examples collection")
    logging.info(f"{len(filtered_documentation)} of new docs loaded to documentation collection")

    