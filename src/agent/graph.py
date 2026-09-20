from langgraph.graph import StateGraph, START, END
#from langchain_tavily  import TavilySearch
from tools import get_search_tools, DEVICE_CONTROL_TOOLS
from langgraph.prebuilt import ToolNode,tools_condition
from functools import partial

#-----------------

from agent import AgentState,call_model, summarize_if_needed
from helper import get_settings
settings=get_settings()

#----------------

def build_graph(settings):
    tools = get_search_tools(settings) + DEVICE_CONTROL_TOOLS
    #tavily_search=TavilySearch(
    #     tavily_api_key=settings.tavily_api_key.get_secret_value(),
    #     max_results=3,
    #     search_depth="basic",
    #     include_answer=True
    # )
    # tools=[tavily_search]

    workflow = StateGraph(AgentState)


    workflow.add_node("summarize", partial(summarize_if_needed, settings=settings))
    workflow.add_node("call_model", partial(call_model, settings=settings, tools=tools))
    workflow.add_node("tools",ToolNode(tools))

    workflow.add_edge(START, "summarize")
    workflow.add_edge("summarize", "call_model")
    workflow.add_conditional_edges(
        "call_model",
        tools_condition,
        {
            "tools":"tools",
            END:END,
        },
    )
    workflow.add_edge("tools", "call_model")

    return workflow.compile()