# Personal Assistant AI Agent 🤖

A resilient, production-ready Python AI Agent built with LangChain and Pydantic Settings. Features a multi-tiered fallback Model Router across **Groq** and **Google Gemini** to guarantee high availability, dynamic prompt formatting, and structured JSON outputs.

---

## 🌟 Key Features

- **Multi-Tier Model Routing (`model_router.py`)**:
  - **Primary Provider (Groq)**: Automatically iterates through a fallback sequence of Groq models (`openai/gpt-oss-20b`, `qwen3-32b`, `openai/gpt-oss-120b`) upon encountering rate limits, API failures, or bad requests.
  - **Secondary External Provider (Google Gemini)**: Instantly switches to `gemini-2.0-flash` if all primary Groq models fail.
- **Strict Configuration Management (`config.py`)**: Powered by `pydantic-settings` for type-safe environment variable validation and parsed lists.
- **Dynamic System Prompting (`system_prompt.py`)**: Configurable roles and response styles using `langchain_core`, enforcing language auto-detection (Arabic/English) and structured JSON outputs.
- **High Availability Architecture**: Built to handle API Downtimes (`RateLimitError`, `BadRequestError`, `APIError`) smoothly without breaking user flows.

---

## 📂 Project Architecture

```text
Personal_assistant-/
│
├── src/
│   ├── controllers/
│   │   └── model_router.py    # Implements Groq & Gemini fallback sequence
│   │
│   ├── helper/
│   │   ├── config.py          # Pydantic BaseSettings and env parser
│   │   └── __init__.py
│   │
│   ├── models/
│   │   ├── schema/            # Schema definitions
│   │   ├── system_prompt.py   # Configurable System Prompt builder
│   │   └── __init__.py
│   │
│   ├── .env                   # Environment keys (Git-ignored)
│   ├── .env.example           # Example configuration template
│   ├── app.py                 # Application execution entry point
│   └── requirements.txt       # Project dependencies
│
├── .gitignore
├── LICENSE
└── README.md
```
# 🔄 Model Routing & Fallback Logic
```text
                    [ User Input ]
                          │
                          ▼
             ┌─────────────────────────┐
             │ Groq Model Failover Loop│
             └────────────┬────────────┘
                          │
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
┌──────────────┐   ┌──────────────┐   ┌───────────────┐
│gpt-oss-20b   │► failure? ► │qwen3-32b     │► failure? ► │gpt-oss-120b   │
└──────┬───────┘   └──────┬───────┘   └──────┬────────┘
       │                  │                  │
    (Success)          (Success)          (Success)
       │                  │                  │
       └──────────────────┴─────────┬────────┘
                                    │
                       (All Groq Models Failed)
                                    │
                                    ▼
                      ┌──────────────────────────┐
                      │ Gemini 2.0 Flash         │
                      │ (External Fallback)      │
                      └─────────────┬────────────┘
                                    │
                                (Success)
                                    │
                                    ▼
                             [ JSON Response ]
```
# ⚙️ Prerequisites & Setup

## 1. Clone the Repository
```bash
git clone https://github.com/omarelnabawi/Personal_assistant-.git
cd Personal_assistant-
```
## 2. Set Up Virtual Environment

**Linux / macOS / Ubuntu (Conda - Recommended):**
```bash
conda create -n personal_assistant python=3.13 -y
conda activate personal_assistant
```
**Linux / macOS / Ubuntu (Standard venv):**

```Bash
python3.13 -m venv personal_assistant
source personal_assistant/bin/activate
```
**Windows (PowerShell / CMD):**

```DOS
python -m venv personal_assistant
personal_assistant\Scripts\activate
```

## 3. Install Dependencies

```Bash
pip install -r src/requirements.txt
```
# 🔑 Environment Variables Setup
- Create a ``.env`` file in the src/ directory based on ``.env.example``:

              cp src/.env.example src/.env
       
- Configure your API keys and hyper-parameters in ``src/.env``
# 🚀 Usage Example
Run the main application entry point:
```bash
python src/app.py
```
# 📄 License
This project is licensed under the terms of the LICENSE file included in the repository.

