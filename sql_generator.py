from typing_extensions import TypedDict, List, Optional, Required
from langchain_core.runnables.base import RunnableSequence
from langgraph.graph import END, StateGraph
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from copilot_base import OPENAI_API_KEY, MODEL_NAME
import logging


SQL_GENERATOR_PROMT = PromptTemplate("""
    Current timestamp is {timestamp}.
    
    You are an expert analyst that transforms bussines questions into
    SQL queries and answer thee questions using data-driven approach.
    Our company is based on logistics and transportation. Your goal is to generate SQL query (postgres)
    to answer user's question.
                                     
    Answer this question using provided information: {question}
    
    relevant DDL stamenets that describe tables you might find useful: 
                                     {ddl_schemas}

    Here's SQL queries that answer similar questions, take a look at them:
                                     {sql_examples}
    
    You should also pay attention to additional tips and domain knowledge we provide:
                                     {docs}

    Make sure to generate READ-ONLY queries and your response is only valid SQL query without any 
    additional comments.             

""")

##=======SQL GENERATOR GRAPH STATE===============
class SQLGeneratorState(TypedDict):
    question : Required[str]
    session_id : Required[int] #need for memory
    generated_sql : str
    retrieval_response : dict
    postgres_executor_response : dict
    n_retries : int
    syntax_correct : bool




class SQLGenerator():
    """Agent responsible for generating SQL for provided question.
       Takes Retrieval Manager to dynamically build promt for LLM.
       Takes Postgres Executor to interact with DB."""

    def __init__(self,
            retrieval_agent : RunnableSequence,
            postgres_executor : RunnableSequence,
            llm : ChatOpenAI,
            retry_if_error=True,
            retry_if_syntax=True,
            max_retries=2
            ):
        
        self.llm = llm
        self.retrieval_agent = retrieval_agent
        self.postgres_executor = postgres_executor

        self.retry_if_error = retry_if_error
        self.retry_if_syntax = retry_if_syntax

    
    #================Nodes implementation=================
    def _retrieve_context(self, state : SQLGeneratorState):

        question = state["question"]

        retrieval_response = self.retrieval_agent.invoke({"question" : question})

        new_state = state
        new_state["retrieval_response"] = retrieval_response

        return new_state
    
    def _build_promt(self, state : SQLGeneratorState):




        


