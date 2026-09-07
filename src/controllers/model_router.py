from langchain_groq import ChatGroq
from groq import BadRequestError, RateLimitError, APIError
from langchain_google_genai import ChatGoogleGenerativeAI
#---------------------------------
from helper import get_settings
#---------------------------------
settings = get_settings()
FALLBACK_MODELS = settings.fallback_models_list


def _try_groq(settings, formatted_prompt):
    last_error = None
    for model_name in settings.fallback_models_list:
        try:
            chat = ChatGroq(
                model=model_name,
                temperature=settings.Model_TEMPERATURE,
                max_tokens=settings.Model_MAX_TOKENS,
                api_key=settings.GROQ_API_KEY,
            )
            response = chat.invoke(formatted_prompt)
            print(f"✅ اشتغل بالموديل: {model_name} (Groq)")
            return response
        except (BadRequestError, RateLimitError, APIError) as e:
            print(f"⚠️ فشل {model_name}: {e}")
            last_error = e
            continue
    raise RuntimeError(f"كل موديلات Groq فشلت. آخر خطأ: {last_error}")

def _try_gemini(settings, formatted_prompt):
    chat = ChatGoogleGenerativeAI(
        model=settings.GEMINI_FALLBACK_MODEL,
        temperature=settings.Model_TEMPERATURE,
        google_api_key=settings.GOOGLE_API_KEY,
    )
    response = chat.invoke(formatted_prompt)
    print(f"✅ اشتغل بموديل: {settings.GEMINI_FALLBACK_MODEL} (Gemini - fallback خارجي)")
    return response

def get_working_chat(settings, formatted_prompt):
    try:
        return _try_groq(settings, formatted_prompt)
    except RuntimeError as groq_error:
        print(f"🔄 Groq فشلت بالكامل، بنحوّل لـ Gemini... ({groq_error})")
        return _try_gemini(settings, formatted_prompt)