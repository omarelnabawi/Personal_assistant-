"""
search_tools.py
----------------
أدوات البحث الخارجي. حاليًا: Tavily فقط.
اتفصلت من graph.py عشان build_graph تفضل مسؤولة بس عن بناء الجراف،
مش عن تعريف الأدوات نفسها.
"""

from langchain_tavily import TavilySearch


def get_search_tools(settings) -> list:
    """يبني ويرجّع قائمة أدوات البحث الجاهزة للربط مع الموديل."""
    tavily_search = TavilySearch(
        tavily_api_key=settings.tavily_api_key.get_secret_value(),
        max_results=3,
        search_depth="basic",
        include_answer=True,
    )
    return [tavily_search]