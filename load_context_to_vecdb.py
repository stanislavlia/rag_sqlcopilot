from langchain_community.vectorstores import Chroma
from pprint import pprint
import os
import chromadb
from retrieval_api import CHROMA_DB_HOST, CHROMA_DB_PORT, OPENAI_EMBEDDING_FUNC
from langchain.evaluation import EmbeddingDistance
from langchain.evaluation import load_evaluator
import logging

DUP_TRESHOLD=0.99


def check_if_duplicate(collection, doc_content):

    most_similar_doc = collection.similarity_search_with_relevance_scores(query=doc_content, k=1)[0]
    similarity_score = most_similar_doc[1]

    if (similarity_score >= DUP_TRESHOLD):
        logging.warning(f"Collection {collection._collection.name.upper()};  Duplicate check for doc '{doc_content[:30]}...'; similarity score = {similarity_score}; DUPLICATE")
        return True
    
    logging.info(f"Duplicate check; similarity score = {similarity_score}; NEW DOCUMENT")
    return False

    
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

TRAIN_SQL_EXAMPLES = [add_comment_doc(doc["question"], doc["sql"]) for doc in TRAIN_SQL_EXAMPLES]


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

    print("All done sucessfuly")
    print(filtered_ddl)


    # question = "Who are the most efficient couriers according to KPI?"

    # relevant_ddl = ddl_vecstore.similarity_search_with_relevance_scores(query=question, k=4)

    # pprint(relevant_ddl)

    # relevant_examples = sqlexamples_vecstore.max_marginal_relevance_search(query=question, k=3)
    # relevant_doc = doc_vecstore.max_marginal_relevance_search(query=question, k=1)


    # #compose it to single promt
    # ddl_text = "\n\n".join([doc.page_content for doc in relevant_ddl])
    # sql_text = "\n\n".join([doc.page_content for doc in relevant_examples])
    # doc_text = "\n\n".join([doc.page_content for doc in relevant_doc])


    # promt = f"""

    #     User question about data: {question}

    #     Relevant DDL statements about tables you need:

    #     {ddl_text}

    #     Relevant SQL examples that work with similar questions:

    #     {sql_text}

    #     Domain knowldedge and hints you might find useful:

    #     {doc_text}


    #     Using all the above, generate SQL to answer the question.

    #     """ 
    
    # with open("promt.txt", "w") as f:
    #     f.write(promt)
    # print("DONE")

    