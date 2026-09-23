from langchain_groq import ChatGroq
from groq import BadRequestError, RateLimitError, APIError
from langchain_google_genai import ChatGoogleGenerativeAI
#---------------------------------
from helper import logger
#---------------------------------
#settings = get_settings()
#FALLBACK_MODELS = settings.fallback_models_list

def _try_groq(settings, formatted_prompt,tools=None,stage="unknown"):
    last_error = None
    formatted_prompt = sanitize_messages(formatted_prompt)
    for model_name in settings.fallback_models_list:
        try:
            chat = ChatGroq(
                model=model_name,
                temperature=settings.Model_TEMPERATURE,
                max_tokens=settings.Model_MAX_TOKENS,
                api_key=settings.GROQ_API_KEY.get_secret_value()
            )

            if tools:
                chat = chat.bind_tools(tools)

            response = chat.invoke(formatted_prompt)
            logger.info(f"[{stage}] Model Run successfuly : {model_name} (Groq) ✅")
            if response.usage_metadata:
                logger.info(f"Ratio of resoning from the output tokens:\n{response.usage_metadata['output_token_details']['reasoning']/response.usage_metadata['output_tokens']*100}%"  )
            #logger.debug(f"response:\n**{response}**")
            return response
        except (BadRequestError, RateLimitError, APIError) as e:
            logger.warning(f"[{stage}] فشل {model_name}: {e}")
            last_error = e
            continue
    raise RuntimeError(f"[{stage}] problem in Gtoq ❌: {last_error}")

def _try_gemini(settings, formatted_prompt,tools=None,stage="unknown"):
    formatted_prompt = sanitize_messages(formatted_prompt)
    chat = ChatGoogleGenerativeAI(
        model=settings.GEMINI_FALLBACK_MODEL,
        temperature=settings.Model_TEMPERATURE,
        google_api_key=settings.GOOGLE_API_KEY.get_secret_value()
    )
    if tools:
        chat = chat.bind_tools(tools)
    
    response = chat.invoke(formatted_prompt)
    logger.info(f"[{stage}] Model Run successfuly : {settings.GEMINI_FALLBACK_MODEL} ✅")
    return response

def get_working_chat(settings, formatted_prompt,tools=None,stage="unknown"):
    try:
        return _try_groq(settings, formatted_prompt,tools,stage)
    except RuntimeError as groq_error:
        logger.warning(f"[{stage}] Groq فشلت بالكامل، بنحوّل لـ Gemini... ({groq_error})")
        return _try_gemini(settings, formatted_prompt,stage)

def extract_answer(response) -> str:
    content = response.content
    if isinstance(content, str):
        return content
    return str(content)   # fallback نادر جدًا هيحصل


def get_working_chat_structured(settings, formatted_prompt, schema,stage="extract New Data"):  
    last_error = None
    formatted_prompt = sanitize_messages(formatted_prompt)
    for model_name in settings.fallback_models_list:
        try:
            chat = ChatGroq(
                model=model_name,
                temperature=settings.Model_TEMPERATURE,
                max_tokens=settings.Model_MAX_TOKENS,
                api_key=settings.GROQ_API_KEY.get_secret_value(),
                reasoning_effort="low",
                reasoning_format="hidden"
            )
            structured_chat = chat.with_structured_output(schema,method="json_schema")
            response = structured_chat.invoke(formatted_prompt)
            logger.info(f"[{stage}] Model Extraction success : {model_name} (Groq) ✅")
            return response
        except (BadRequestError, RateLimitError, APIError) as e:
            logger.warning(f"[{stage}] فشل {model_name}: {e}")
            last_error = e
            continue
    raise RuntimeError(f"[{stage}] كل موديلات Groq فشلت في الاستخراج المنظم. آخر خطأ: {last_error}")

def clean_text(text):
    if isinstance(text, str):
        return text.encode("utf-8", errors="ignore").decode("utf-8")
    return text

def sanitize_messages(messages):
    if isinstance(messages, list):
        for m in messages:
            if hasattr(m, "content") and isinstance(m.content, str):
                m.content = clean_text(m.content)
    return messages