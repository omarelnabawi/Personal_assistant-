# memory/identity.py
import uuid
import json
from pathlib import Path

#-------------------------------

from memory import get_user_info, save_user_info
#from helper import get_settings
from memory.store import get_user_info, save_user_info
#settings = get_settings()
BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "data" / "local_user.json"

#------------------------------

def get_or_create_user_id() -> str:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "user_id" in data:
            #print("user_id: ",data["user_id"])
            return data["user_id"]

    new_id = str(uuid.uuid4())
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"user_id": new_id}, f)
    return new_id

def get_or_ask_name(user_id: str) -> str:
    record = get_user_info(user_id)

    if record.get("name"):
        return record["name"]

    name = input("Hello , what is your full name  ")
    record["name"] = name
    save_user_info(user_id, record)
    return name