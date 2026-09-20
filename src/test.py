from langchain_tavily import TavilySearch
from helper import get_settings

settings = get_settings()

tool = TavilySearch(
    tavily_api_key=settings.tavily_api_key.get_secret_value(),   # أو .get_secret_value() لو SecretStr
    max_results=3
)

result = tool.invoke({"query": "test"})
print(result)