"""这个智能体包含如下几个功能
1.和客户进行交互，咨询客户的产品是什么
2.根据客户的产品，生成产品定义和客户做二次确认
3.询问客户的消费者洞察和产品卖点，方便 ICP
"""

from dataclasses import dataclass
from typing import Annotated
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from langchain_openai import ChatOpenAI

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)


@dataclass
class ProductDefineState(TypedDict):
    """Input State for Product Define Agent"""

    messages: Annotated[list, add_messages]


# Create the graph
pd_graph = StateGraph(ProductDefineState)
llm = ChatOpenAI(
    base_url="https://api.moonshot.cn/v1",
    model="kimi-k2-0711-preview",
    api_key="sk-rwyEzBJZpvbwFxicBOX3ajSlcd34ehVzd99ohHENAklLLLLQ",
)


def chatbot(state: ProductDefineState):
    return {"messages": [llm.invoke(state["messages"])]}


pd_graph.add_node("chatbot", chatbot)
pd_graph.add_edge(START, "chatbot")
pd_graph.add_edge("chatbot", END)


graph = pd_graph.compile()

result = graph.invoke(
    {
        "messages": [
            SystemMessage(
                content="你是一个产品经理，请根据客户的需求，生成产品定义和客户做二次确认"
            )
        ],
        "messages": [
            HumanMessage(
                content="你好，我是小明，我正在开发一个产品，请帮我定义一下产品"
            )
        ],
    }
)
print(result)
