from typing_extensions import TypedDict, List, Optional, Required
from langchain_core.runnables.base import RunnableSequence
from langgraph.graph import END, StateGraph
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import logging
import pandas as pd
import psycopg2


##=======QUERY EXECUTOR GRAPH STATE===============
class SQLExecutorGraphState(TypedDict):
    sql_query : Required[str]
    sql_result : List
    sql_result_markdown : str
    is_query_safe : bool
    any_errors : bool
    error_trace : str


class PostgresExecutor():
    """Langraph workflow that executes provided SQL query on PostgreSQL"""

    def __init__(self,
                 pg_database : str,
                 pg_user : str,
                 pg_password : str,
                 pg_host : str,
                 pg_port : str,
                 pg_schema : str,
                 limit_rows=30
                 ):
        
        self.pg_database = pg_database
        self.pg_user = pg_user
        self.pg_password = pg_password
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_schema = pg_schema
        self.limit_rows = limit_rows

        self.db_connection = self.__connect_to_db()

        self.graph_workflow = self.__build_graph()
        
    def __connect_to_db(self):
        try:
            connection = psycopg2.connect(
                database=self.pg_database,
                user=self.pg_user,
                password=self.pg_password,
                host=self.pg_host,
                port=self.pg_port
            )
            
            logging.info(f"[PostgresExecutor] Sucessfully connected")
            return connection
        except psycopg2.OperationalError as e:
            logging.error(f"[PostgresExecutor] OperationalError: {e}")
            return None
        except psycopg2.Error as e:
            logging.error(f"[PostgresExecutor] Error: {e}")
            return None
    
    def sql_result_to_markdown(self, sql_result, column_names):

        df = pd.DataFrame(sql_result)
        df.columns = column_names

        return df.to_markdown()


    def _sanitize_query(self, state: SQLExecutorGraphState):
        unsafe_keywords = ['DROP', 'DELETE', 'ALTER', 'CREATE', 'INSERT', 'UPDATE']
        sql_query = state["sql_query"].upper()

        new_state = state

        if any(keyword in sql_query for keyword in unsafe_keywords):
            new_state["is_query_safe"] = False
            new_state["any_errors"] = True
            new_state["error_trace"] = "The query is unsafe and tries to ALTER database. READ-ONLY mode is only acceptable"
            logging.warn(f"[PostgresExecutor] Detected UNSAFE query")

            return state
        else:
            new_state["is_query_safe"] = True
            new_state["any_errors"] = False
            logging.info(f"[PostgresExecutor] query is SAFE")
            
            return state

    def _decide_to_execute_query(self, state : SQLExecutorGraphState):
        if state["is_query_safe"]:
            return "execute_query"
        return "END"
        

    def _execute_query(self, state : SQLExecutorGraphState):

        sql_query = state["sql_query"]
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute(sql_query)
            self.db_connection.commit()

            sql_result = cursor.fetchmany(size=self.limit_rows)
            column_names = [desc[0] for desc in cursor.description]
            sql_result_markdown = self.sql_result_to_markdown(sql_result, column_names)

            new_state = state
            new_state["any_errors"] = False
            new_state["sql_result"] = sql_result
            new_state["sql_result_markdown"] = sql_result_markdown
            logging.info(f"[PostgresExecutor] Sucessfully executed query")

            return new_state
        
        except psycopg2.Error as e:
            logging.error(f"[PostgresExecutor] Error executing query: {e}")
            new_state = state
            new_state["any_errors"] = True
            new_state["error_trace"] = str(e)
            new_state["sql_result"] = None
            new_state["sql_result_markdown"] = None

            return new_state
        
        finally:
            if cursor:
                cursor.close()


    def __build_graph(self):

        workflow = StateGraph(SQLExecutorGraphState)

        workflow.add_node("sanitize_query", self._sanitize_query)
        workflow.add_node("execute_query", self._execute_query)

        workflow.set_entry_point("sanitize_query")
        workflow.add_conditional_edges("sanitize_query",
                                       self._decide_to_execute_query,
                                       path_map={"execute_query" : "execute_query",
                                                 "END" : END})
        
        workflow.add_edge("execute_query", END)

        graph = workflow.compile().with_config({"run_name": "PostgreSQL Executor"})
        logging.info(f"[PostgresExecutor] graph compiled successfully")
        return graph

    def get_runnable(self) -> RunnableSequence:

        return self.graph_workflow

    
    
    

