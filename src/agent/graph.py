from langgraph.graph import StateGraph, START, END
from functools import partial

#-----------------

from agent import AgentState,call_model, summarize_if_needed

#----------------

def build_graph(settings):
    workflow = StateGraph(AgentState)

    workflow.add_node("summarize", partial(summarize_if_needed, settings=settings))
    workflow.add_node("call_model", partial(call_model, settings=settings))

    workflow.add_edge(START, "summarize")
    workflow.add_edge("summarize", "call_model")
    workflow.add_edge("call_model", END)

    return workflow.compile()