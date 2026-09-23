from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr

class Settings(BaseSettings):
    GROQ_API_KEY: SecretStr
    GOOGLE_API_KEY: SecretStr
    GROQ_FALLBACK_MODELS: str 
    GEMINI_FALLBACK_MODEL: str 
    Model_TEMPERATURE: float
    Model_MAX_TOKENS: int 
    Model_TOP_P: float 
    Model_FREQUENCY_PENALTY: float 
    Model_PRESENCE_PENALTY: float 
    MAX_MESSAGES: int
    KEEP_RECENT: int
    local_user: str 
    tavily_api_key: SecretStr
    GROQ_VOICE_MODEL:str

    model_config = SettingsConfigDict(env_file=".env",extra="ignore")

    @property
    def fallback_models_list(self) -> list[str]:
        return [m.strip() for m in self.GROQ_FALLBACK_MODELS.split(",")]

def get_settings():
    return Settings()