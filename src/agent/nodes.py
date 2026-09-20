from langgraph.graph import StateGraph, MessagesState, END
from langchain_core.messages import SystemMessage, RemoveMessage,HumanMessage
#--------------

from agent import AgentState
from controllers import get_working_chat
# from helper import get_settings

#--------------
# settings = get_settings()
# MAX_MESSAGES = settings.MAX_MESSAGES   # الحد اللي بعده نلخّص
# KEEP_RECENT = settings.KEEP_RECENT    # عدد الرسائل الحديثة اللي هتفضل كاملة

#--------------

def summarize_if_needed(state: AgentState, settings) -> AgentState:
    messages = state["messages"]

    if len(messages) <= settings.MAX_MESSAGES:
        return {}

    # افصل الـ System Message الأصلية (لو موجودة) عن باقي الرسايل قبل التلخيص
    system_messages = [m for m in messages if m.type == "system"]
    conversational_messages = [m for m in messages if m.type != "system"]

    if len(conversational_messages) <= settings.KEEP_RECENT:
        return {}   # لسه مفيش كفاية رسايل تستاهل تلخيص

    old_messages = conversational_messages[:-settings.KEEP_RECENT]
    recent_messages = conversational_messages[-settings.KEEP_RECENT:]

    conversation_text = "\n".join(f"{m.type}: {m.content}" for m in old_messages)
    summary_prompt = [
    HumanMessage(content=f"""
            Summarize this conversation in a short paragraph, keeping the most important information. 
            Write the summary in the same language the conversation was mostly conducted in:
            {conversation_text}
            """)] 
    summary_response = get_working_chat(settings, summary_prompt,tools=None,stage="summarization")
    summary_message = SystemMessage(content=f"Summary of the previous conversation: {summary_response.content}")

    delete_messages = [RemoveMessage(id=m.id) for m in old_messages]

    # System Message الأصلية (معلومات المستخدم) فضلت زي ما هي، متتلخصش أبدًا
    return {"messages": delete_messages + [summary_message]}

def call_model(state: AgentState, settings,tools,stage="Call Model") -> AgentState:
    messages = state["messages"]
    response = get_working_chat(settings, messages,tools,stage=stage)
    return {"messages": [response]}