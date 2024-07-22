from typing_extensions import TypedDict, List, Optional, Required
from langchain_core.runnables.base import RunnableSequence
from langgraph.graph import END, StateGraph
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import logging


#==============OLD SCHEMA======================
class OldSchemaState(TypedDict, total=False):
    '''Represents the state of the workflow'''
    question: Required[str]
    session_id : Required[str]
    visualization_need : Optional[str] #'yes'/'no'
    history: Optional[dict]
    is_relevant: Optional[str]
    need_for_sql: Optional[str]
    answer: Optional[str]
    empty_result: Optional[str]
    sql_query: Optional[str]
    sql_result: Optional[str]
    visualization_config : Optional[dict]


class CopilotAPIWrapper():
    """API wrapper for compatability with old front"""

    def __init__(self, sql_generator : RunnableSequence):

        self.sql_generator = sql_generator

        self.graph_workflow = self.__build_graph()


    def _invoke_sql_generator(self, state : OldSchemaState):
        
        question = state["question"]
        session_id = state["session_id"]

        response = self.sql_generator.invoke({"question" : question,
                                              "session_id" : session_id})

        #parse response to old schema

        new_state = state

        new_state["answer"] = response["final_answer"]
        new_state["sql_query"] = response["generated_sql"]
        new_state["visualization_need"] = 'no'

        return new_state
    


    def __build_graph(self):
        
        workflow = StateGraph(OldSchemaState)
        workflow.add_node("invoke_agent", self._invoke_sql_generator)

        workflow.set_entry_point("invoke_agent")
        workflow.add_edge("invoke_agent", END)

        graph = workflow.compile().with_config({"run_name": "CopilotAPI"})
        return graph
    
    def get_runnable(self) -> RunnableSequence:

        return self.graph_workflow