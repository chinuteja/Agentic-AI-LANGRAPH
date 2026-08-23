import asyncio

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage, HumanMessage
from langchain_groq import ChatGroq

from langchain_mcp_adapters.client import MultiServerMCPClient
from dotenv import load_dotenv


load_dotenv()


# ============================================================
# State
# ============================================================

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ============================================================
# MCP Client
# ============================================================

client = MultiServerMCPClient(
    {
        "calculator_server": {
            "transport": "stdio",
            "command": "python",
            "args": ["mcp_server.py"],
        }
    }
)


# ============================================================
# Build Graph
# ============================================================

async def build_graph():

    # Get tools from MCP server
    tools = await client.get_tools()

    print("MCP tools available:")

    for tool in tools:
        print("-", tool.name)

    # --------------------------------------------------------
    # LLM
    # --------------------------------------------------------

    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.3
    )

    llm_with_tools = llm.bind_tools(tools)

    # --------------------------------------------------------
    # Chat Node
    # --------------------------------------------------------

    async def chat_node(state: ChatState):

        response = await llm_with_tools.ainvoke(
            state["messages"]
        )

        return {
            "messages": [response]
        }

    # --------------------------------------------------------
    # Tool Node
    # --------------------------------------------------------

    tool_node = ToolNode(tools)

    # --------------------------------------------------------
    # Graph
    # --------------------------------------------------------

    graph = StateGraph(ChatState)

    graph.add_node(
        "chat_node",
        chat_node
    )

    graph.add_node(
        "tools",
        tool_node
    )

    graph.add_edge(
        START,
        "chat_node"
    )

    graph.add_conditional_edges(
        "chat_node",
        tools_condition
    )

    graph.add_edge(
        "tools",
        "chat_node"
    )

    graph.add_edge(
        "chat_node",
        END
    )

    chatbot = graph.compile()

    return chatbot


# ============================================================
# Main
# ============================================================

async def main():

    chatbot = await build_graph()

    result = await chatbot.ainvoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "Find the modulus of 132354 and 23 "
                        "and give the answer like a cricket commentator."
                    )
                )
            ]
        }
    )

    print("\nFinal Answer:")
    print(result["messages"][-1].content)


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    asyncio.run(main())