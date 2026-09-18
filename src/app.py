from langchain_core.messages import HumanMessage,SystemMessage
import json

#-------------------------------------

from helper import get_settings
from agent import build_graph
from prompt import SystemPrompt
from memory import get_user_info,extract_and_merge ,get_or_create_user_id,get_or_ask_name

#------------------------------------
settings = get_settings()
graph = build_graph(settings)
sys_prompt = SystemPrompt()

state = {
    "messages": [sys_prompt.get_system_message()]
}

#------------------------------------

USER_ID = get_or_create_user_id()   # بدل الـ "omar_test" الثابتة
#USER_ID = settings.local_user
USER_NAME=get_or_ask_name(USER_ID)

#------------------------------------

record = get_user_info(USER_ID)
personal_info = record.get("personal_info", {})

if personal_info:
    context_message = SystemMessage(content=f"""
Known information about the user from previous conversations (use this to answer accurately, don't say you're unsure if the info is here):
{json.dumps(personal_info, ensure_ascii=False, indent=2)}
""")
    state["messages"].append(context_message)
    #print("personal info :\n", personal_info)
else:
    print("thier is no personal_info")

#-------------------------------------


def ask(question: str):
    global state
    state["messages"].append(HumanMessage(content=question))
    state = graph.invoke(state, config={"recursion_limit": 10})
    return state["messages"][-1].content


Q = input(f"Enter is your question  : ")
while Q != "exit":
    answer = ask(Q)
    print("Answer:", answer)
    Q = input("Enter your question: ")

#print("جاري حفظ معلوماتك...")
updated_info = extract_and_merge(USER_ID, state["messages"], settings)
#print("تم الحفظ:", updated_info)