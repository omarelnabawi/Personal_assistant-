# Personal Assistant AI Agent 🤖

**Version: v0.2**

---

## 📝 Changelog — `V_0.2` vs `V_0.1`

`V_0.1` delivered a stateful, memory-enabled conversational agent with no ability to act on the world beyond replying in text. `V_0.2` adds a tool-calling layer (search + sandboxed device control) and structured logging. Nothing in `V_0.1` was removed; everything below is new or extended.

| Area | `V_0.1` (before) | `V_0.2` (now) |
|---|---|---|
| **Tools** | None — the model could only produce text | New `tools/` package: `tavily_search` (moved out of `graph.py` into its own module) plus a brand-new **device control** tool (`open_application`, `read_data_file`) |
| **Tool security model** | N/A | Strict **whitelist-first** design: allowed apps enforced via a Pydantic `Literal` type (rejected before the function body ever runs), file reads restricted to `data/`, extension-limited, `resolve()`-checked against symlink escapes, and size-capped |
| **Observability** | `print()` statements scattered across `model_router.py` | Centralized `logging` setup (`helper/logger.py`) with configurable levels (`DEBUG`/`INFO`/`WARNING`/`ERROR`), plus a `stage` label threaded through every model call (`call_model`, `summarize`) so log lines can be traced back to the exact node that triggered them |
| **Reasoning visibility** | Reasoning effort tuned blindly | Reasoning-token ratio (`reasoning / output_tokens`) computed and logged per call, to catch reasoning-token exhaustion (the `V_0.1`-documented empty-reply bug) before it silently recurs |
| **Model router** | Fixed `print()`-based fallback logging | Same Groq → Gemini fallback logic, now `stage`-aware and logging-based; Gemini call cleaned of unsupported `reasoning_effort`/`reasoning_format` kwargs that were causing silent request corruption |

---

## 🌟 Key Features (cumulative, including `V_0.1`)

- **Multi-Tier Model Routing (`controllers/model_router.py`)** — Groq fallback chain → Gemini as external fallback, both now instrumented with `stage`-labeled logging instead of prints.

- **Conversational Agent (`agent/`)** — unchanged `LangGraph` state machine (`summarize_if_needed` → `call_model`), now also wiring in the tools list on graph construction.

- **Tool Calling (`tools/`)** — **new in V_0.2**:
  - `search_tools.py` — `get_search_tools(settings)`, returning the Tavily search tool (logic unchanged, just relocated out of `graph.py`).
  - `device_control.py` — sandboxed local device control:
    - `open_application`: opens one of a fixed set of local apps (`vscode`, `browser`, `terminal`, `file_explorer`) via `subprocess.Popen` with list-form arguments (no shell interpolation, no injection surface).
    - `read_data_file`: reads text files (`.txt`/`.md`/`.json`/`.csv`) from `data/` only, with path-traversal and symlink protections, and a size cap.
    - No write, delete, or rename capability exists anywhere in this module — by design, not by omission.

- **Structured Logging (`helper/logger.py`)** — **new in V_0.2**: one centralized logger instance, level configurable in one place (`DEBUG` for development, `WARNING` for deployment), used everywhere `print()` used to be.

- **Long-Term Memory (`memory/`)**, **Structured Personal Info Schema**, **Dynamic System Prompting**, and **Configuration Management** — unchanged from `V_0.1`.

---

## 📂 Project Architecture

```text
Personal_assistant-/
│
├── src/
│   ├── agent/
│   │   ├── state.py            # AgentState (LangGraph MessagesState)
│   │   ├── nodes.py             # summarize_if_needed, call_model (now stage-aware)
│   │   └── graph.py             # START → summarize → call_model → (tools) → END
│   │
│   ├── controllers/
│   │   └── model_router.py      # Groq/Gemini fallback + structured output + stage logging
│   │
│   ├── tools/                    # ⭐ new in V_0.2
│   │   ├── __init__.py
│   │   ├── search_tools.py       # get_search_tools() — Tavily
│   │   └── device_control.py     # open_application, read_data_file (whitelist-sandboxed)
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
│   │   ├── logger.py             # ⭐ new in V_0.2 — centralized logging setup
│   │   └── __init__.py
│   │
│   ├── data/
│   │   ├── local_user.json      # this installation's user_id
│   │   └── users/
│   │       └── <user_id>.json   # per-user profile + personal_info
│   │
│   ├── .env
│   ├── .env.example
│   ├── app.py
│   └── requirements.txt
│
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔧 Tool Security Model (`tools/device_control.py`)

Device control is deliberately the most restricted part of the codebase, following defense-in-depth:

1. **`Literal` type on `app_name`** — the allowed app names are baked into the Pydantic schema itself, so an out-of-list value is rejected before `open_application`'s body ever executes.
2. **`field_validator` on `filename`** — rejects any `/`, `\`, or `..`, and restricts extensions to a fixed allow-list, before any filesystem access is attempted.
3. **Post-`resolve()` path check** — guards against symlink tricks that could point a legitimately-named file outside `data/`.
4. **Size cap** on reads, to avoid flooding the model's context with an oversized file.
5. **List-form `subprocess.Popen`** (never a shell string) — arguments are passed literally to the target program, eliminating shell-injection surface entirely.

Read-only, whitelist-only, no write/delete capability anywhere in this module.

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
conda create -n ai_agent python=3.13 -y
conda activate ai_agent
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
GROQ_API_KEY="api_key_here"
GROQ_FALLBACK_MODELS=openai/gpt-oss-120b,qwen3-32b,openai/gpt-oss-20b

GOOGLE_API_KEY="api_key_here"
GEMINI_FALLBACK_MODEL=

Model_TEMPERATURE=0.4
Model_MAX_TOKENS=3000
Model_TOP_P=1.0
Model_FREQUENCY_PENALTY=0.0
Model_PRESENCE_PENALTY=0.0

MAX_MESSAGES=5      # threshold after which older messages get summarized
KEEP_RECENT=3       # number of recent messages kept verbatim, never summarized

local_user="local"

TAVILY_API_KEY="api_key_here"
```

> `GEMINI_FALLBACK_MODEL` should be checked against Google's currently-supported free-tier models before deployment — model names and availability change over time, and previously-working values can 404 without notice.
> `GROQ_FALLBACK_MODELS` model names should likewise be verified against Groq's currently-hosted models — deprecated names fail with a 404 at request time, not at startup.

---

## 🚀 Usage Example
```bash
python src/app.py
```
First run will generate a local user ID and ask for your name once; every session after that recalls your stored profile automatically, and updates it when the session ends. The model may now also call tools mid-conversation (search, opening a whitelisted local app, or reading a file from `data/`) as part of producing its reply.

---

## 📄 License
This project is licensed under the terms of the LICENSE file included in the repository.