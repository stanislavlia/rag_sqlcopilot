from langchain_community.vectorstores import Chroma
from pprint import pprint
import os
import chromadb
from langchain.evaluation import EmbeddingDistance
from langchain.evaluation import load_evaluator
from copilot_base import ddl_vecstore, sqlexamples_vecstore, doc_vecstore
import logging
from retrieval_api import check_if_duplicate






    
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
CONTEXT_DOCS = [read_file_content(path) for path in DOCS_FILES]

TRAIN_SQL_EXAMPLES = [{"question" : example["question"],
                       "sql" : read_file_content(example["path"])} for example in TRAIN_SQL_FILES]

TRAIN_SQL_EXAMPLES = [add_comment_doc(doc["question"], doc["sql"]) for doc in TRAIN_SQL_EXAMPLES]


if __name__ == "__main__":

    
    
    
    

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

    