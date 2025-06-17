from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_openai import ChatOpenAI
import os
import loguru

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState

from langgraph.checkpoint.memory import InMemorySaver

from pydantic import BaseModel


class WeatherResponse(BaseModel):
    conditions: str


# def supermarket(state):
#     return {"ret": "{} has buy".format(state["ingredients"])}


# if __name__ == "__main__":

#     sg = StateGraph(dict)
#     sg.add_node("supermarket", supermarket)
#     sg.add_edge(START, "supermarket")
#     sg.add_edge("supermarket", END)


#     graph = sg.compile()
#     result = graph.invoke({"ingredients": "milk"})
#     print(result)
def prompt(state: AgentState, config: RunnableConfig) -> list[AnyMessage]:
    user_name = config["configurable"].get("user_name", "User")
    system_msg = SystemMessage(
        content=f"""You are a helpful assistant. Address the user as {user_name}.
    
    IMPORTANT: When a user asks about weather, you MUST use the get_weather tool to provide accurate information.
    Always use the available tools to answer weather-related questions. Do not make up weather information.
    """
    )
    return [system_msg] + state["messages"]


def get_weather(city: str) -> str:
    """Get the weather of a city"""
    return f"The weather of {city} is sunny"


os.environ["HTTP_PROXY"] = "http://127.0.0.1:7897"
os.environ["HTTPS_PROXY"] = "http://127.0.0.1:7897"

model = ChatOpenAI(
    model="anthropic/claude-3.7-sonnet",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_KEY"),
)

checkpointer = InMemorySaver()

agent = create_react_agent(
    model=model,
    tools=[get_weather],
    prompt=prompt,
    checkpointer=checkpointer,
    # response_format=WeatherResponse,  # 注释掉这行
    # prompt="""You are a helpful assistant that can get the weather of a city.
    # IMPORTANT: When a user asks about weather, you MUST use the get_weather tool to provide accurate information.
    # Always use the available tools to answer weather-related questions. Do not make up weather information.
    # If a user asks "What is the weather in [city]?", immediately use the get_weather tool with that city name.""",
)

# 修正配置格式
config = {"configurable": {"user_name": "Ryan Wang", "thread_id": "1"}}

bj_result = agent.invoke(
    {"messages": [{"role": "user", "content": "What is the weather in Beijing?"}]},
    config=config,
)

# sh_result = agent.invoke(
#     {"messages": [{"role": "user", "content": "What is the weather in Shanghai?"}]},
#     config=config,
# )

loguru.logger.info(bj_result)
# loguru.logger.info(sh_result)
