# Personal Assistant AI Agent 🤖

**Version: v0.1**

---

## 📝 Changelog — `V_0.1` vs `main`

`main` holds the original, simple version of the project: a single-turn Groq/Gemini chat call with a basic system prompt — no memory, no agent framework, no persistent identity. `V_0.1` builds a full stateful agent on top of it. Nothing in `main` was removed; everything below is new.

| Area | `main` (before) | `V_0.1` (now) |
|---|---|---|
| **Conversation** | Stateless — every call to the model is independent, no memory of previous questions | Stateful — built as a **LangGraph** graph (`agent/`) that carries full conversation history across turns |
| **Long conversations** | No handling — full history sent every time, cost grows without limit | **Automatic summarization** (`summarize_if_needed`) once `MAX_MESSAGES` is exceeded, keeping the last `KEEP_RECENT` messages verbatim and protecting system messages from being summarized away |
| **User memory** | None — the assistant knows nothing about the user between sessions | **Persistent long-term memory** (`memory/`): a structured `PersonalInfo` profile per user, extracted at the end of each session and **deep-merged** into their stored record, then re-injected at the start of the next session |
| **User identity** | None — no concept of "who is asking" | Local **UUID-based identity** (`identity.py`), generated once per installation and reused across runs; optional stored display name |
| **Model output** | Plain text only | Two modes: plain text (`get_working_chat`) for conversation, and **guaranteed-schema structured output** (`get_working_chat_structured`, via `method="json_schema"`) for memory extraction |
| **Reasoning control** | None — reasoning-heavy models could silently return an empty reply on complex questions | `reasoning_effort="low"` + `reasoning_format="hidden"` tuning to prevent reasoning-token exhaustion |
| **System prompt** | Static role/style template, requested JSON output with a `reasoning` field meant for on-screen debugging | Rewritten for a **voice-first assistant**: concise, no markdown/tables in replies, asks one clarifying question instead of guessing, strict language-matching regardless of the language of injected context |
| **Data schema** | None | Explicit `PersonalInfo` Pydantic schema (`models/schema/personal_info.py`) — one field per fact (e.g. a single `current_role` instead of drift-prone duplicate `occupation`/`company` fields) |
| **Storage** | None | Per-user JSON file (`data/users/<user_id>.json`), isolated behind a `store.py` layer so a future move to MongoDB only changes that one file |

A resilient, memory-enabled Python AI Agent built with **LangGraph**, **LangChain**, and **Pydantic**. Features a multi-tiered fallback Model Router across **Groq** and **Google Gemini**, short-term conversation summarization, long-term structured personal-memory extraction, and a persistent local user identity — all designed to scale toward a database-backed, multi-user system.

---

## 🌟 Key Features

- **Multi-Tier Model Routing (`controllers/model_router.py`)**
  - **Primary Provider (Groq)**: Iterates through a fallback sequence of models (`openai/gpt-oss-20b` → `qwen3-32b` → `openai/gpt-oss-120b`) on rate limits, API failures, or bad requests.
  - **Secondary External Provider (Gemini)**: Falls back to `gemini-2.5-flash` via Google's OpenAI-compatible endpoint if every Groq model fails.
  - **Reasoning Control**: Uses `reasoning_effort="low"` and `reasoning_format="hidden"` to keep responses concise and prevent reasoning-token exhaustion on complex queries.
  - **Two invocation modes**: `get_working_chat()` for plain conversational replies, and `get_working_chat_structured()` for guaranteed-schema JSON output (via `method="json_schema"`).

- **Conversational Agent (`agent/`)** — built as a **LangGraph** state machine:
  - `state.py` — `AgentState`, extending `MessagesState`, holds the full running conversation.
  - `nodes.py` — two nodes:
    - `summarize_if_needed`: once the conversation exceeds `MAX_MESSAGES`, older messages are condensed into a single summary while the last `KEEP_RECENT` messages are kept verbatim. System messages (language rules, injected personal context) are excluded from summarization so they never get lost.
    - `call_model`: sends the current state to the model router and appends the reply.
  - `graph.py` — wires the flow: `START → summarize → call_model → END`.

- **Long-Term Memory (`memory/`)**
  - `identity.py` — generates and persists a local **UUID** per installation (`get_or_create_user_id`), with an optional stored display name (`get_or_ask_name`). Designed to be swapped later for real auth (e.g. Google Sign-In) without touching the rest of the app.
  - `store.py` — reads/writes each user's record as `data/users/<user_id>.json`, containing `user_id`, `created_at`, `last_updated`, `conversation_count`, and `personal_info`. Isolated as the single storage layer — swapping to MongoDB later only changes this file.
  - `extractor.py` — at the end of a session, extracts a structured `PersonalInfo` object (via `get_working_chat_structured`) from the conversation and **deep-merges** it into the existing record field-by-field, so unrelated facts are never wiped by an incomplete extraction.

- **Structured Personal Info Schema (`models/schema/personal_info.py`)**
  - A `PersonalInfo` Pydantic model (name, `current_role`, education, languages, military service, `additional_notes`, …) — a single source of truth per fact, avoiding contradictory duplicate fields (e.g. a unified `current_role` instead of separate, driftable `occupation` / `company` fields).

- **Dynamic System Prompting (`models/system_prompt.py`)**
  - Voice-assistant-oriented: concise, no markdown/tables in spoken-style replies, asks one short clarifying question when needed instead of guessing.
  - Strict language-matching rule (reply in the language of the latest user message, regardless of the language of stored summaries/context).

- **Strict Configuration Management (`helper/config.py`)**
  - `pydantic-settings`-based, type-safe `.env` parsing, including the fallback model list, reasoning/memory tuning knobs (`MAX_MESSAGES`, `KEEP_RECENT`), and both provider API keys.

---

## 📂 Project Architecture

```text
Personal_assistant-/
│
├── src/
│   ├── agent/
│   │   ├── state.py            # AgentState (LangGraph MessagesState)
│   │   ├── nodes.py             # summarize_if_needed, call_model
│   │   └── graph.py             # START → summarize → call_model → END
│   │
│   ├── controllers/
│   │   └── model_router.py      # Groq/Gemini fallback + structured output
│   │
│   ├── memory/
│   │   ├── identity.py          # local UUID + display name
│   │   ├── store.py             # per-user JSON read/write
│   │   └── extractor.py         # extraction + deep-merge into personal_info
│   │
│   ├── models/
│   │   ├── schema/
│   │   │   └── personal_info.py # Pydantic schema for long-term memory
│   │   ├── system_prompt.py     # Configurable System Prompt builder
│   │   └── __init__.py
│   │
│   ├── helper/
│   │   ├── config.py            # Pydantic BaseSettings and env parser
│   │   └── __init__.py
│   │
│   ├── data/
│   │   ├── local_user.json      # this installation's user_id
│   │   └── users/
│   │       └── <user_id>.json   # per-user profile + personal_info
│   │
│   ├── .env                     # Environment keys (Git-ignored)
│   ├── .env.example             # Example configuration template
│   ├── app.py                   # Application execution entry point
│   └── requirements.txt         # Project dependencies
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔄 Request Flow

```text
                    [ User Input ]
                          │
                          ▼
              ┌─────────────────────┐
              │  LangGraph Agent    │
              │ summarize → call    │
              └──────────┬──────────┘
                          │
                          ▼
             ┌─────────────────────────┐
             │ Groq Model Failover Loop│
             └────────────┬────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌───────────────┐
│gpt-oss-20b   │──►│qwen3-32b     │──►│gpt-oss-120b   │
└──────┬───────┘   └──────┬───────┘   └──────┬────────┘
       │  (fail)          │  (fail)          │
    (success)          (success)          (success)
       └──────────────────┴─────────┬────────┘
                                    │
                       (All Groq Models Failed)
                                    ▼
                      ┌──────────────────────────┐
                      │ Gemini 2.5 Flash          │
                      │ (OpenAI-compatible fallback)
                      └─────────────┬────────────┘
                                    │
                                    ▼
                             [ Reply to User ]
                                    │
                          (session ends)
                                    ▼
                  ┌───────────────────────────────┐
                  │ extract_and_merge → PersonalInfo│
                  │  deep-merged into data/users/   │
                  └───────────────────────────────┘
```

---

## ⚙️ Prerequisites & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/omarelnabawi/Personal_assistant-.git
cd Personal_assistant-
```

### 2. Set Up Virtual Environment

**Linux / WSL (Conda — Recommended):**
```bash
conda create -n personal_assistant python=3.13 -y
conda activate personal_assistant
```

**Standard venv:**
```bash
python3.13 -m venv personal_assistant
source personal_assistant/bin/activate
```

**Windows (PowerShell / CMD):**
```dos
python -m venv personal_assistant
personal_assistant\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r src/requirements.txt
```

---

## 🔑 Environment Variables Setup

Create a `.env` file in `src/` based on `.env.example`:
```bash
cp src/.env.example src/.env
```

Key variables:
```env
GROQ_API_KEY=
GOOGLE_API_KEY=
GROQ_FALLBACK_MODELS=openai/gpt-oss-20b,qwen3-32b,openai/gpt-oss-120b
GEMINI_FALLBACK_MODEL=gemini-2.5-flash
GROQ_TEMPERATURE=0.4
GROQ_MAX_TOKENS=2500
MAX_MESSAGES=10
KEEP_RECENT=3
```

---

## 🚀 Usage Example
```bash
python src/app.py
```
First run will generate a local user ID and ask for your name once; every session after that recalls your stored profile automatically, and updates it when the session ends.

---

## 📄 License
This project is licensed under the terms of the LICENSE file included in the repository.