from typing_extensions import TypedDict, List, Optional, Required
from langchain_core.runnables.base import RunnableSequence
from langgraph.graph import END, StateGraph
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import logging
import psycopg2



class PostgresExecutor():
    """Langraph workflow that executes provided SQL query on PostgreSQL"""

    def __init__(self,
                 pg_database : str,
                 pg_user : str,
                 pg_password : str,
                 pg_host : str,
                 pg_port : str,
                 pg_schema : str,
                 ):
        
        self.pg_database = pg_database
        self.pg_user = pg_user
        self.pg_password = pg_password
        self.pg_host = pg_host
        self.pg_port = pg_port
        self.pg_schema = pg_schema


        self.db_connection, self.db_cursor = self.__connect_to_db()
        
    def __connect_to_db(self):
        try:
            connection = psycopg2.connect(
                database=self.pg_database,
                user=self.pg_user,
                password=self.pg_password,
                host=self.pg_host,
                port=self.pg_port
            )
            cursor = connection.cursor()
            cursor.execute(f"SET search_path TO {self.pg_schema};")
            connection.commit()
            logging.info(f"[PostgresExecutor] Sucessfully connected")
            return connection, cursor
        except psycopg2.OperationalError as e:
            logging.error(f"[PostgresExecutor] OperationalError: {e}")
            return None, None
        except psycopg2.Error as e:
            logging.error(f"[PostgresExecutor] Error: {e}")
            return None, None
    
        


