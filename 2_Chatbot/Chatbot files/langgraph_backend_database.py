from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages

from dotenv import load_dotenv
import sqlite3

load_dotenv()


# **************************************** LLM ***************************************

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)


# **************************************** State **************************************

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# **************************************** Chat Node *********************************

def chat_node(state: ChatState):

    response = llm.invoke(state["messages"])

    return {
        "messages": [response]
    }


# **************************************** SQLite *************************************

conn = sqlite3.connect(
    "chatbot.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn)


# **************************************** Graph **************************************

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)


chatbot = graph.compile(
    checkpointer=checkpointer
)


# **************************************** Threads ************************************

def retrieve_all_threads():

    all_threads = set()

    for checkpoint in checkpointer.list(None):

        thread_id = checkpoint.config["configurable"]["thread_id"]

        all_threads.add(thread_id)

    return list(all_threads)