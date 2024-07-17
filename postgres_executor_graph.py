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

        df = pd.DataFrame(sql_result, column_names)
        return df.to_markdown()


    def _sanitize_query(self, state : SQLExecutorGraphState):
        pass

    def _execute_query(self, state : SQLExecutorGraphState):

        sql_query = state["sql_query"]
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute()
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






    
    
    

