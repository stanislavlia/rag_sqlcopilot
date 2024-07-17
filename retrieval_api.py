from typing_extensions import TypedDict, List, Optional, Required
from langchain_core.runnables.base import RunnableSequence
from langgraph.graph import END, StateGraph
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_community.vectorstores import VectorStore
from langchain_core.documents import Document
import logging

DUP_TRESHOLD=0.99

def check_if_duplicate(collection, doc_content):

    most_similar_doc = collection.similarity_search_with_relevance_scores(query=doc_content, k=1)

    if (len(most_similar_doc) == 0):
        logging.info(f"Collection {collection._collection.name.upper()} IS EMPTY;  NEW DOCUMENT")
        return False
        
    similarity_score = most_similar_doc[0][1]

    if (similarity_score >= DUP_TRESHOLD):
        logging.warning(f"Collection {collection._collection.name.upper()};  Duplicate check for doc '{doc_content[:30]}...'; similarity score = {similarity_score}; DUPLICATE")
        return True
    
    logging.info(f"Duplicate check; similarity score = {similarity_score}; NEW DOCUMENT")
    return False



##=======RETRIEVAL GRAPH STATE===============

class RetrievalGraphState(TypedDict):
    """Represents the state of Retrieval workflow"""
    question: Required[str]
    relevant_ddl : List[Document]
    relevant_sql_examples : List[Document]
    relevant_documentation : List[Document]




class RetrievalManager():
    """LangGraph workflow that manages retrieval from VectorDB"""

    def __init__(self, 
                 ddl_collection : VectorStore,
                 sql_examples_collection : VectorStore,
                 doc_collection : VectorStore,
                 k_ddl=4,
                 k_sql=3,
                 k_doc=1):
        
        
        self.ddl_collection = ddl_collection
        self.sql_examples_collection = sql_examples_collection
        self.doc_collection = doc_collection
        
        self.k_ddl = k_ddl
        self.k_sql = k_sql
        self.k_doc = k_doc

        self.graph_workflow = self.__build_graph()
    
    def __build_graph(self):
        pass

    
    def _retrieve_similar_ddl(self, state : RetrievalGraphState):
        
        question = state['question']

        retrieved_ddls = self.ddl_collection.similarity_search(query=question,
                                                               k=self.k_ddl)
        
        new_state = state
        new_state['relevant_ddl'] = retrieved_ddls

        logging.info(f"[RETRIEVAL] Question: {question}; Retrieved ddls sucessfully")

        return new_state
    
    def _retrieve_similar_sql(self, state : RetrievalGraphState):
        question = state['question']

        retrieved_sqls = self.sql_examples_collection.max_marginal_relevance_search(query=question,
                                                                                   k=self.k_sql)
        
        new_state = state
        new_state['relevant_sql_examples'] = retrieved_sqls
        logging.info(f"[RETRIEVAL] Question: {question}; Retrieved SQLs sucessfully")

        return new_state
    
    def _retrieve_similar_documentation(self, state : RetrievalGraphState):
        question = state["question"]

        retrieved_documentation = self.doc_collection.similarity_search(query=question,
                                                                        k=self.k_doc)
        
        new_state = state
        new_state['relevant_documentation'] = retrieved_documentation
        logging.info(f"[RETRIEVAL] Question: {question}; Retrieved Documentation sucessfully")

        return new_state
    
