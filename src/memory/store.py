import json
from pathlib import Path
from datetime import datetime, timezone

#--------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "users"

#--------------------------------

def get_user_info(user_id: str) -> dict:
    file_path = DATA_DIR / f"{user_id}.json"
    if not file_path.exists():
        return {
            "user_id": user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_updated": None,
            "conversation_count": 0,
            "personal_info": {},
        }
    with open(file_path, "r", encoding="utf-8") as f:
        #print(json.load(f))
        return json.load(f)
    

def save_user_info(user_id: str, full_record: dict):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    full_record["user_id"] = user_id
    full_record["last_updated"] = datetime.now(timezone.utc).isoformat()
    file_path = DATA_DIR / f"{user_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(full_record, f, ensure_ascii=False, indent=2)