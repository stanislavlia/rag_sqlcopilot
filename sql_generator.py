from typing_extensions import TypedDict, List, Optional, Required
from langchain_core.runnables.base import RunnableSequence
from langgraph.graph import END, StateGraph
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from copilot_base import OPENAI_API_KEY, MODEL_NAME
import logging


##=======SQL GENERATOR GRAPH STATE===============

class SQLGeneratorState(TypedDict):
    question : Required[str]
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

        


