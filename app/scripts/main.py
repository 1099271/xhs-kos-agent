from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from app.config.settings import settings

from app.utils.logger import app_logger as logger


def get_weather(query: str):
    """Call to surf the web

    Args:
        query (str): _description_
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy"
    return "It's 90 degrees and sunny"


# model = ChatOpenAI(
#     model="gpt-4o-mini",
#     temperature=0,
#     max_tokens=1024,
#     api_key=os.getenv("OPENAI_KEY"),
# )
# model = init_chat_model(
#     model="claude-3.7-sonnet",
#     temperature=0,
#     max_tokens=1024,
#     base_url="https://openrouter.ai/api/v1",
#     api_key=os.getenv("OPENROUTER_KEY"),
# )

model = ChatOpenAI(
    model_name="anthropic/claude-3.7-sonnet",  # 请确认这是 OpenRouter 上正确的模型标识符
    temperature=0,
    max_tokens=1024,
    openai_api_base="https://openrouter.ai/api/v1",
    openai_api_key=settings.OPENROUTER_KEY,
    default_headers={  # （可选）OpenRouter 推荐的请求头
        "HTTP-Referer": "http://localhost",  # 如果适用，替换为您的站点 URL
        "X-Title": "LangGraph XHS KOS Agent",  # 替换为您的应用名称
    },
)

agent = create_react_agent(
    model=model, tools=[get_weather], prompt="You are a helpful assistant"
)
# Run the agent
result = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]}
)
print(result)
