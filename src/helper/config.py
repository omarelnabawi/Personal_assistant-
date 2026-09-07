from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    GROQ_API_KEY: str
    GOOGLE_API_KEY: str
    GROQ_FALLBACK_MODELS: str 
    GEMINI_FALLBACK_MODEL: str 
    Model_TEMPERATURE: float
    Model_MAX_TOKENS: int 
    Model_TOP_P: float 
    Model_FREQUENCY_PENALTY: float 
    Model_PRESENCE_PENALTY: float 

    model_config = SettingsConfigDict(env_file=".env",ignore_extra=True)

    @property
    def fallback_models_list(self) -> list[str]:
        return [m.strip() for m in self.GROQ_FALLBACK_MODELS.split(",")]

def get_settings():
    return Settings()