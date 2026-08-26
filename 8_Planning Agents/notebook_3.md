# Agentic AI Blog Writer with LangGraph

A beginner-friendly LangGraph project that generates complete blog posts using an agentic workflow with conditional routing, optional web research, structured planning, parallel section generation, and final reduction.

## What this project does

Given a topic, the workflow decides whether research is required, optionally gathers web evidence, creates a structured blog plan, generates individual sections through worker nodes, and combines them into a final Markdown blog.

## Architecture

```text
                         User Topic
                             |
                             v
                         +-------+
                         | Router|
                         +---+---+
                             |
                +------------+------------+
                |                         |
          No research                 Research
                |                         |
                |                    +----v-----+
                |                    | Research |
                |                    +----+-----+
                |                         |
                +------------+------------+
                             |
                             v
                       Orchestrator
                             |
                        Structured Plan
                             |
                             v
                           Fanout
                             |
              +--------------+--------------+
              |              |              |
              v              v              v
           Worker         Worker         Worker
              |              |              |
              +--------------+--------------+
                             |
                             v
                          Reducer
                             |
                             v
                       Final Markdown
```

## Main concepts demonstrated

- `StateGraph` and shared state
- `TypedDict` state definitions
- Pydantic structured models
- Conditional routing
- Structured LLM output
- Optional web research
- LangGraph `Send` for fan-out
- Parallel worker execution
- Reducer/fan-in
- Markdown file generation

The uploaded notebook defines a dedicated shared `State` for the workflow. fileciteturn12file0L10-L15

## Workflow nodes

### 1. Router

The router decides whether the topic needs research and produces the routing information used by the graph. fileciteturn12file1L25-L30

### 2. Research

When research is required, this stage gathers external evidence that can be passed to later stages.

### 3. Orchestrator

The orchestrator creates a structured blog plan containing the title, audience, and ordered writing tasks.

### 4. Fanout

The fanout function creates a worker execution for each task in the generated plan using LangGraph's `Send` mechanism. fileciteturn12file2L40-L45

Conceptually:

```text
Plan
 |
 +-- Task 1 -> Worker 1
 +-- Task 2 -> Worker 2
 +-- Task 3 -> Worker 3
```

### 5. Worker

Each worker writes one section instead of generating the entire blog. The worker receives the assigned task, plan, topic, mode, and available evidence. fileciteturn12file3L55-L58

Workers return the task ID with the generated section so the reducer can restore the original plan order.

### 6. Reducer

The reducer sorts the generated sections, combines them into one Markdown document, and produces the final blog. The notebook's reducer is responsible for assembling the generated sections into a Markdown blog. fileciteturn12file4L67-L73

## Fan-out / fan-in

Suppose the plan contains three sections:

```text
             Fanout
        /      |      \
       v       v       v
    Worker   Worker   Worker
      1        2        3
       \       |       /
        \      |      /
          Reducer
```

The workers can finish in a different order. Returning `(task.id, section)` allows the reducer to sort the sections back into the order defined by the plan.

## State

The workflow state contains information such as:

```python
topic
mode
needs_research
queries
evidence
plan
sections
final
```

A suitable `sections` definition for the current worker/reducer design is:

```python
sections: Annotated[
    List[tuple[int, str]],
    operator.add
]
```

`operator.add` allows results from multiple workers to be accumulated instead of overwritten.

## Installation

Create a virtual environment:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Install the packages required by the notebook. A typical setup is:

```bash
pip install langgraph langchain langchain-core langchain-groq python-dotenv
```

If using Tavily research:

```bash
pip install tavily-python langchain-community
```

## Environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
```

Never commit `.env` or API keys to GitHub.

Load environment variables with:

```python
from dotenv import load_dotenv
load_dotenv()
```

## Running the notebook

Open the project in VS Code or Jupyter and run the notebook cells from top to bottom.

A typical graph invocation is conceptually:

```python
output = app.invoke(initial_state)
```

The exact `initial_state` should match the `State` definition in the notebook.

The final blog is available through:

```python
output["final"]
```

## Saving the generated blog

A safe filename can be generated from the blog title:

```python
from pathlib import Path
import re

output_dir = Path("blogs_generated_new")
output_dir.mkdir(parents=True, exist_ok=True)

title = output["plan"].blog_title

safe_title = re.sub(
    r"[^a-zA-Z0-9]+",
    "_",
    title
).strip("_").lower()

output_path = output_dir / f"{safe_title}_blog.md"

output_path.write_text(
    output["final"],
    encoding="utf-8"
)

print(f"Saved to: {output_path.resolve()}")
```

## Debugging the graph

To see what each node updates:

```python
for event in app.stream(
    {"topic": "Write a blog about cricket"},
    stream_mode="updates"
):
    print(event)
```

To inspect the complete accumulated state:

```python
for state in app.stream(
    {"topic": "Write a blog about cricket"},
    stream_mode="values"
):
    print(state)
```

## Groq rate limits

The workflow can make multiple LLM calls: router, orchestrator, and one call per worker. With a free API tier, several parallel workers can consume the tokens-per-minute allowance quickly.

For development, keep the generated plan small, for example 2–3 sections, and keep worker prompts concise. Once the workflow is stable, increase the number of sections or move to a plan with higher API limits.

## Research and grounding

For research-heavy topics, pass useful evidence to workers. Useful evidence includes:

- Source title
- URL
- Published date
- Search snippet or source content

Passing only URLs gives the worker less information with which to ground factual claims.

Workers should also be instructed not to invent URLs and to cite only sources actually provided by the research stage.

## Recommended improvements

The current workflow is a strong learning implementation. Good next improvements are:

1. Add stronger citation instructions.
2. Pass evidence snippets/content to workers.
3. Deduplicate research results.
4. Add retry/backoff for API rate limits.
5. Reduce unnecessary LLM calls.
6. Add a validation node after the reducer.
7. Add a revision loop when validation fails.
8. Verify citations and URLs.
9. Add LangSmith tracing and evaluation.
10. Build a Streamlit UI.

A future version could use:

```text
Router
  |
Research
  |
Orchestrator
  |
Fanout
  |
Workers
  |
Reducer
  |
Validator
 / \
Pass Fail
 |    |
END  Revision
       |
     Reducer
```

## Learning outcomes

After completing this project, you should understand how to combine:

- LangGraph state management
- Conditional edges
- Structured output
- External research
- Pydantic models
- `Send` and fan-out
- Parallel workers
- Fan-in/reducer patterns
- Research-grounded generation
- Markdown file generation

## Source notebook

This README is based on the uploaded notebook `3_basic_blog_writer_with_research.ipynb`. fileciteturn11file0L1-L8

The notebook contains the router, fanout, worker, and reducer implementation described above. fileciteturn12file1L25-L30 fileciteturn12file2L40-L45 fileciteturn12file3L55-L58 fileciteturn12file4L67-L73

## Disclaimer

This is a learning/portfolio project rather than a production-ready content platform. For production use, add robust error handling, observability, validation, citation verification, secret management, and API rate-limit handling.
