from langchain_core.messages import HumanMessage
import json
import re

#-------------------------------

from controllers import get_working_chat_structured,deep_merge_personal_info
from memory import get_user_info, save_user_info
from models import PersonalInfo

#------------------------------

def extract_and_merge(user_id: str, messages: list, settings):

    record = get_user_info(user_id)
    existing_personal_info = record.get("personal_info", {})

    conversation_text = "\n".join(
        f"{m.type}: {m.content}" for m in messages if m.type in ("human", "ai")
    )

    prompt = [
        HumanMessage(content=f"""
Currently stored user information (JSON):
{json.dumps(existing_personal_info, ensure_ascii=False)}

New conversation:
{conversation_text}

Update the information: Add any new details about the user (name, job, education, interests, or any permanent personal details),
modify anything that has changed, and retain any existing information that remains valid.
Return the output as JSON only, without any additional explanation.
""")
    ]

    
    extracted: PersonalInfo = get_working_chat_structured(settings, prompt, PersonalInfo)
    extracted_dict = extracted.model_dump(exclude_none=True)   # ✅ استبعد أي حقل فاضي من الأساس

    merged_info = deep_merge_personal_info(existing_personal_info, extracted_dict)

    record["personal_info"] = merged_info
    record["conversation_count"] = record.get("conversation_count", 0) + 1
    save_user_info(user_id, record)
    return record