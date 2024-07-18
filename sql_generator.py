from typing_extensions import TypedDict, List, Optional, Required
from langchain_core.runnables.base import RunnableSequence
from langgraph.graph import END, StateGraph
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from copilot_base import OPENAI_API_KEY, MODEL_NAME
import logging


llm = ChatOpenAI(model=MODEL_NAME,
             temperature=0,
             verbose=True,
             openai_api_key=OPENAI_API_KEY,
             max_tokens=3500
             )



class SQLGenerator():
    """Agent responsible for generating SQL for provided question.
       Takes Retrieval Manager to dynamically build promt for LLM."""

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

        


