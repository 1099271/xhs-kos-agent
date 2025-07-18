import os
import json
from langgraph.types import interrupt
import pandas as pd
import pymysql
import matplotlib.pyplot as plt
import seaborn as sns

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek
from typing import Annotated
from typing_extensions import TypedDict

from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import tool
from langchain_tavily import TavilySearch

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent

from pydantic import BaseModel, Field
from app.config.settings import settings
from app.utils.logger import app_logger as logger

load_dotenv(override=True)

search_tool = TavilySearch(max_results=10, topic="general")


@tool
def human_assistance(query: str) -> str:
    """
    Request assistance from a human.
    """
    human_response = interrupt({"query": query})
    return human_response["data"]


graph = create_react_agent()
