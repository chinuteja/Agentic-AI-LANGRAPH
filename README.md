# Agentic AI with LangGraph

A hands-on learning repository for building **Agentic AI applications with LangGraph, LangChain, Groq, RAG, MCP, tool calling, persistence, and human-in-the-loop workflows**.

The repository is organized as a progressive tutorial: start with basic LangGraph workflows, then move into stateful chatbots, observability with LangSmith, MCP, and agentic RAG.

## Repository Overview

```text
Agentic-AI-LANGRAPH/
│
├── 1_Workflows/
│   └── Sequential, parallel, routing and workflow examples
│
├── 2_Chatbot/
│   ├── Basic chatbot
│   ├── Persistence
│   └── Chatbot application files
│
├── 3_LangSmith/
│   └── LangSmith tracing and observability examples
│
├── 4_MCP/
│   ├── MCP server
│   ├── MCP clients
│   └── Synchronous/asynchronous MCP examples
│
├── 5_Agentic RAG/
│   └── Agentic RAG experiments and document retrieval workflows
│
├── requirments.txt
└── .gitignore
```

The repository currently contains dedicated sections for workflows, chatbots, LangSmith, MCP, and Agentic RAG. citeturn8file0turn9file0turn10file0

## What You'll Learn

### 1. LangGraph Workflows

Build graph-based workflows using:

- `StateGraph`
- Nodes and edges
- Sequential workflows
- Parallel execution
- Conditional routing
- State management
- Reducers and `Annotated`
- Graph compilation and invocation

### 2. Stateful Chatbots

Learn how to build conversational applications with:

- LangGraph message state
- `add_messages`
- Conversation persistence
- Thread IDs
- SQLite-based checkpoints
- Streamlit chat interfaces
- Conversation history management

The chatbot section includes basic chatbot and persistence examples. citeturn9file0

### 3. LangSmith

Explore how to trace and inspect LangChain/LangGraph applications using LangSmith for debugging, observability, and evaluation.

### 4. Model Context Protocol (MCP)

The MCP section demonstrates how to separate tools from the agent application using an MCP server/client architecture.

Examples include:

- MCP server implementation
- MCP client integration
- Tool discovery
- Tool calling from LangGraph
- Synchronous and asynchronous execution

The repository currently contains `mcp_server.py`, `chatbot.py`, `chatbot_async.py`, and `chatbot-mcp.py` under `4_MCP`. citeturn10file0

### 5. Agentic RAG

Explore an agentic approach to Retrieval-Augmented Generation where the LLM can decide when retrieval is required and use retrieval tools before generating a grounded answer.

Typical flow:

```text
User Question
     ↓
  Chat Node
     ↓
Need Retrieval?
   ↙      ↘
 No        Yes
 ↓          ↓
END      RAG Tool
            ↓
         Retriever
            ↓
      Retrieved Context
            ↓
        Chat Node
            ↓
           END
```

## Technology Stack

- Python
- LangGraph
- LangChain
- Groq
- LangSmith
- MCP
- FAISS / vector retrieval
- Streamlit
- SQLite
- Jupyter Notebook

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/chinuteja/Agentic-AI-LANGRAPH.git
cd Agentic-AI-LANGRAPH
```

### 2. Create a virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirments.txt
```

> The repository currently uses the filename `requirments.txt` rather than `requirements.txt`. citeturn8file0

### 4. Configure environment variables

Create a `.env` file in the project root and add the API keys required by the example you are running.

Example:

```env
GROQ_API_KEY=your_groq_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

Never commit `.env` or API keys to GitHub.

## Running the Examples

Most examples are Jupyter notebooks. Open the repository in VS Code and run the notebooks from their respective folders.

For Python applications, run the relevant file from the project directory, for example:

```bash
python 4_MCP/mcp_server.py
```

or:

```bash
python 4_MCP/chatbot_async.py
```

## Learning Path

A suggested progression through this repository is:

```text
1_Workflows
     ↓
2_Chatbot
     ↓
3_LangSmith
     ↓
4_MCP
     ↓
5_Agentic RAG
```

Start by understanding graph state and control flow, then move into persistence and observability. After that, learn how MCP externalizes tools, and finally combine retrieval with agentic decision-making.

## Key Concepts Covered

| Concept | Purpose |
|---|---|
| StateGraph | Defines the agent workflow as a graph |
| Nodes | Execute individual pieces of logic |
| Edges | Control execution flow |
| Conditional Edges | Route execution based on state/model output |
| Annotated Reducers | Safely merge concurrent state updates |
| Checkpointers | Persist graph state |
| Thread IDs | Maintain independent conversations |
| ToolNode | Execute tool calls from the graph |
| MCP | Standardize tool/server integration |
| RAG | Ground LLM responses in retrieved documents |
| Agentic RAG | Let the agent decide when retrieval is needed |
| LangSmith | Trace and debug LLM workflows |

## Security Notes

Keep secrets out of source code. Use environment variables for API keys and credentials. The repository already contains a `.gitignore` and should be used with a local `.env` file for secrets. citeturn8file0

## Project Goal

The goal of this repository is to provide a practical progression from **basic LangGraph workflows to production-oriented Agentic AI patterns**. The examples are intentionally hands-on so that each concept can be implemented, debugged, and extended into larger AI applications.

## Author

**Chinuteja**

GitHub: https://github.com/chinuteja

Repository: https://github.com/chinuteja/Agentic-AI-LANGRAPH
