from langchain_community.vectorstores import Chroma
from pprint import pprint
import os
import chromadb
from retrieval_api import CHROMA_DB_HOST, CHROMA_DB_PORT, OPENAI_EMBEDDING_FUNC



def read_file_content(path):
    with open(path, "r") as file:
        content = file.read()
        return content
    
def add_comment_doc(doc_content, comment):
    return comment + "\n\n" + doc_content 


CONTEXT_DIR_PATH = "tables_info/"

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

DOCS_FILES = [
    "tables_info/logistics_domain_promt_no_sql.txt",
    "tables_info/logistics_domain_promt.txt"
]

TRAIN_SQL_FILES = [
    {"path" : "tables_info/avg_departure_time.sql",
     "question" : "What is the average departure time of our couriers/drivers?" },
    
    {"path" : "tables_info/kpi.sql",
     "question" : "Who are the most efficient drivers/couriers according to our KPI?"},
    
    {"path" : "tables_info/list_branches.sql",
     "question" : "What deparments do we have in our company?"},

    {"path" : "tables_info/metrics_summary.sql",
     "question" : "Give me the summary about All applications, Incoming applications, Finished applications and Canceled applications"}
]

DDL_TABLES_FILES = [os.path.join(CONTEXT_DIR_PATH, filename) for filename in DDL_TABLES_FILES]    
DDL_TABLES_SQL_QUERIES = [read_file_content(path) for path in DDL_TABLES_FILES]
CONTEXT_DOCS = [read_file_content(path) for path in DDL_TABLES_FILES]

TRAIN_SQL_EXAMPLES = [{"question" : example["question"],
                       "sql" : read_file_content(example["path"])} for example in TRAIN_SQL_FILES]



if __name__ == "__main__":

    #Connect to Chroma
    chromadb_client = chromadb.HttpClient(host=CHROMA_DB_HOST,
                                          port=CHROMA_DB_PORT)
    

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
    
    #load context to collections
