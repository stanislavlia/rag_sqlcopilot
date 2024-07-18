from typing_extensions import TypedDict, List, Optional, Required
from langchain_core.runnables.base import RunnableSequence
from langgraph.graph import END, StateGraph
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from datetime import datetime
import pytz
import logging
import re

AMLATY_TZ = pytz.timezone('Asia/Almaty')

SQL_GENERATOR_PROMT = PromptTemplate(template="""
    Current timestamp is {timestamp}.
    
    You are an expert analyst that transforms bussines questions into
    SQL queries and answer thee questions using data-driven approach.
    Our company is based on logistics and transportation. Your goal is to generate SQL query (postgres)
    to answer user's question.
                                     
    Answer this question using provided information: {question}
    
    relevant DDL stamenets that describe tables you might find useful: 
                                     {ddls}

    Here's SQL queries that answer similar questions, take a look at them:
                                     {sql_examples}
    
    You should also pay attention to additional tips and domain knowledge we provide:
                                     {docs}

    Make sure to generate READ-ONLY queries and your response is only valid SQL query without any 
    additional comments.             

""", input_variables=["timestamp", "question", "ddls", "sql_examples", "docs"])

RESULT_INTERPRETER_PROMT = PromptTemplate.from_template("""
    Current timestamp is {timestamp}.
    
    You are an expert analyst that transforms bussines questions into
    SQL queries and answer thee questions using data-driven approach.
    Our company is based on logistics and transportation. Your goal is interpret generated 
    SQL query and response from Postgres DB in order to answer user question.

    User question was: {question}
    Generated SQL: {generated_sql}

    SQL result in markdown: {sql_result_md}
    
    And provided domain knowledge that you can utilize: {domain}
    
    Make sure to explain what steps were done on a high level without technincal details and
    NEVER include SQL query into your response.
    Translate your answer in Russian.
                                                    
""")


##=======SQL GENERATOR GRAPH STATE===============
class SQLGeneratorState(TypedDict):
    question : Required[str]
    session_id : Required[str] #need for memory
    generated_sql : str
    retrieval_response : dict
    postgres_executor_response : dict
    n_retries : int
    syntax_correct : bool
    final_answer : str


#TODO: include previous query when retrying




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
            max_retries=1,
            sql_promt=SQL_GENERATOR_PROMT,
            result_promt=RESULT_INTERPRETER_PROMT,
            ):
        
        self.llm = llm
        self.retrieval_agent = retrieval_agent
        self.postgres_executor = postgres_executor

        self.retry_if_error = retry_if_error
        self.retry_if_syntax = retry_if_syntax
        self.sql_promt = sql_promt
        self.result_promt = result_promt
        self.n_retries = max_retries


        self.generator_chain = (self.sql_promt | self.llm | StrOutputParser())
        self.interpret_chain = (self.result_promt | self.llm | StrOutputParser())
        self.graph_workflow = self.__build_graph()


    def join_docs(self, documents):

        return "\n----------------NEW DOCUMENT---------------\n".join([doc.page_content for doc in documents])
    
    def extract_sql(self, llm_response):
     
        # If the llm_response contains a CTE (with clause), extract the last sql between WITH and ;
        sqls = re.findall(r"\bWITH\b .*?;", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            return sql

        # If the llm_response is not markdown formatted, extract last sql by finding select and ; in the response
        sqls = re.findall(r"SELECT.*?;", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            return sql

        # If the llm_response contains a markdown code block, with or without the sql tag, extract the last sql from it
        sqls = re.findall(r"```sql\n(.*)```", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            return sql

        sqls = re.findall(r"```(.*)```", llm_response, re.DOTALL)
        if sqls:
            sql = sqls[-1]
            return sql

        return llm_response


    def format_question_retry(self, question, generated_sql, trace):

        updated_question = f"""Your goal was to answer this question using SQL: {question}
                        and you produced the following SQL: {generated_sql}
        Database returned the following traceback on error {trace}. Please, fix your SQL query"""

        return updated_question
    
    #================Nodes implementation=================
    def _retrieve_context(self, state : SQLGeneratorState):

        question = state["question"]

        retrieval_response = self.retrieval_agent.invoke({"question" : question})

        new_state = state
        new_state["retrieval_response"] = retrieval_response
        new_state["n_retries"] = 0

        return new_state
    
    def _generate_sql(self, state : SQLGeneratorState):

        question = state["question"]
        retrieval_response = state["retrieval_response"]

        current_time = datetime.now(AMLATY_TZ).strftime('%Y-%m-%d-%H-%M')

        ddls = self.join_docs(retrieval_response["relevant_ddl"])
        sql_examples = self.join_docs(retrieval_response["relevant_sql_examples"])
        docs = self.join_docs(retrieval_response["relevant_documentation"])

        #invoke llm
        logging.info("Calling LLM to generate SQL")
        llm_response = self.generator_chain.invoke({"question" : question,
                                                    "timestamp" : current_time,
                                                    "ddls" : ddls,
                                                    "sql_examples" : sql_examples,
                                                    "docs" : docs})
        

        #extract sql from response
        logging.info("Extracting SQL from llm response")
        llm_sql_generated = self.extract_sql(llm_response)

        new_state = state
        new_state["generated_sql"] = llm_sql_generated
        return new_state
        

    #to be added
    def _check_sql_syntax(self, state : SQLGeneratorState):
        pass

    def _run_sql(self, state : SQLGeneratorState):

        sql_query = state["generated_sql"]

        postgres_executor_response = self.postgres_executor.invoke({"sql_query" : sql_query})

        new_state = state
        new_state["postgres_executor_response"] = postgres_executor_response


        ##check for any errors
        if ((state["postgres_executor_response"]["is_query_safe"] == False)
             or (state["postgres_executor_response"]["any_errors"] == True)):
            
            error_trace = new_state["postgres_executor_response"]["error_trace"]
            new_state["n_retries"] += 1
            new_state["question"] = self.format_question_retry(state["question"],
                                                                state["generated_sql"],
                                                                error_trace)

            #new_state["question"] = new_state["question"] + f"\nPrevious time your query produced the following error: {error_trace}\n. Fix it please"
            logging.error(f"Detected error; Need to RETRY...")

        return new_state
        
        
    def _decide_to_retry(self, state : SQLGeneratorState):

        if ((state["postgres_executor_response"]["is_query_safe"] == False)
             or (state["postgres_executor_response"]["any_errors"] == True)):
            
            if state["n_retries"] <= self.n_retries:
                return "retry"
            else:
                return "finish"
        
        return "finish"
    

    def _interpret_results(self, state : SQLGeneratorState):

        if ((state["postgres_executor_response"]["is_query_safe"] == False)
             or (state["postgres_executor_response"]["any_errors"] == True)):
            new_state = state
            new_state["final_answer"] = "After several retries, some error still persists when trying to run SQL query.\n Sorry for inconvinience"

            #clean them for better readability (they saved anyway)
            new_state["postgres_executor_response"] = None
            new_state["retrieval_response"] = None
            return new_state
        
        new_state = state

        current_time = datetime.now(AMLATY_TZ).strftime('%Y-%m-%d-%H-%M')

        llm_answer = self.interpret_chain.invoke({"question" : state["question"],
                                                    "timestamp" : current_time,
                                                    "domain" : self.join_docs(state["retrieval_response"]["relevant_documentation"]),
                                                    "generated_sql" : state["generated_sql"],
                                                    "sql_result_md" : state["postgres_executor_response"]["sql_result_markdown"]})
        
        new_state["final_answer"] = llm_answer
        
        #clean them for better readability
        new_state["postgres_executor_response"] = None
        new_state["retrieval_response"] = None
        return new_state


    def __build_graph(self):

        workflow = StateGraph(SQLGeneratorState)

        workflow.add_node("retrieve_context", self._retrieve_context)
        workflow.add_node("generate_sql", self._generate_sql)
        workflow.add_node("run_sql", self._run_sql)
        workflow.add_node("interpret", self._interpret_results)

        workflow.set_entry_point("retrieve_context")
        workflow.add_edge("retrieve_context", "generate_sql")
        workflow.add_edge("generate_sql", "run_sql")
        workflow.add_conditional_edges("run_sql",
                                        self._decide_to_retry,
                                        path_map={"retry" : "generate_sql",
                                                  "finish" : "interpret"})
        workflow.add_edge("interpret", END)

        graph = workflow.compile().with_config({"run_name": "SQLCopilotAgent"})
        logging.info(f"[SQLCOPILOT] graph compiled successfully")
        return graph

    def get_runnable(self) -> RunnableSequence:

        return self.graph_workflow



        


