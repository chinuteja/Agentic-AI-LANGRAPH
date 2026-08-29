# Notebook 4 — Blog Writer with Research + Image Generator

## 📌 What is this project?

This project is an **Agentic AI Blog Writer** built using **LangGraph**.

You give the application a topic, for example:

```text
What are the recent developments in Indian Stock Market?
```

The application then decides:

1. Does this topic need web research?
2. If yes, what should we search for?
3. What should the blog structure look like?
4. What should each section contain?
5. Should the final blog contain images?
6. If images are needed, what images should be generated?
7. How should everything be combined into the final Markdown file?

The final result is a Markdown blog with generated images where applicable.

---

# 🧠 Project Architecture

The complete workflow looks like this:

```text
                         USER TOPIC
                              |
                              v
                         +---------+
                         | ROUTER  |
                         +----+----+
                              |
                    Does it need research?
                       /              \
                     YES              NO
                      |                |
                      v                |
                 +---------+           |
                 |RESEARCH |           |
                 +----+----+           |
                      |                |
                      +-------+--------+
                              |
                              v
                       +-------------+
                       | ORCHESTRATOR|
                       +------+------+
                              |
                         Creates Plan
                              |
                              v
                           FANOUT
                              |
                +-------------+-------------+
                |             |             |
                v             v             v
             Worker        Worker        Worker
                |             |             |
                +-------------+-------------+
                              |
                              v
                    +------------------+
                    | REDUCER SUBGRAPH |
                    +--------+---------+
                             |
                    +--------v---------+
                    |  Merge Content   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    |  Decide Images   |
                    +--------+---------+
                             |
                             v
                    +------------------+
                    | Generate Images  |
                    |     Gemini       |
                    +--------+---------+
                             |
                             v
                       FINAL BLOG
```

---

# 🛠️ Technologies Used

This notebook uses:

- Python
- LangGraph
- LangChain
- Groq
- Tavily
- Pydantic
- Google GenAI
- Gemini image generation
- LangSmith
- Markdown
- `.env` environment variables

---

# 📦 Installation

Create a virtual environment first.

## Windows

```bash
python -m venv .venv
```

Activate it:

```bash
.venv\Scripts\activate
```

Install the required packages:

```bash
pip install langgraph
pip install langchain
pip install langchain-groq
pip install langchain-community
pip install langchain-openai
pip install python-dotenv
pip install tavily-python
pip install google-genai
pip install pydantic
```

You can also install them together:

```bash
pip install langgraph langchain langchain-groq langchain-community langchain-openai python-dotenv tavily-python google-genai pydantic
```

---

# 🔑 API Keys

Create a `.env` file in the same project directory.

Example:

```env
GROQ_API_KEY=your_groq_api_key
TAVILY_API_KEY=your_tavily_api_key
GOOGLE_API_KEY=your_google_api_key
```

Do **not** upload `.env` to GitHub.

Add this to `.gitignore`:

```text
.env
.venv/
__pycache__/
```

---

# 🔭 LangSmith

The notebook sets:

```python
os.environ["LANGCHAIN_PROJECT"] = "blog writer with research agent with images"
```

This gives the project a LangSmith project name for tracing/observability.

If you want LangSmith tracing, configure the appropriate LangSmith environment variables as well.

---

# 🤖 LLM Configuration

The main writing LLM is:

```python
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3
)
```

This model is used for the major reasoning and writing tasks.

The image-planning LLM is intentionally separated:

```python
image_planner_llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)
```

### Why are there two LLMs?

Because image planning is a relatively small task.

There is no need to use the larger model for every operation.

The project therefore follows this idea:

```text
Important writing/reasoning
        ↓
   GPT-OSS 120B

Image planning
        ↓
   GPT-OSS 20B
```

This also helps reduce token usage.

---

# 🧱 Pydantic Models

The project uses Pydantic models to make the LLM return structured information.

This is important because an LLM normally returns text.

For example:

```text
Write a blog about cricket...
```

But we want something structured like:

```text
Plan
 ├── blog_title
 ├── audience
 └── tasks
       ├── Task 1
       ├── Task 2
       └── Task 3
```

---

# 📝 Task Model

```python
class Task(BaseModel):

    id: int

    title: str

    brief: str
```

A `Task` represents one section of the blog.

Example:

```python
Task(
    id=1,
    title="Introduction to Cricket",
    brief="Explain the basics and history of cricket."
)
```

---

# 📋 Plan Model

```python
class Plan(BaseModel):

    blog_title: str

    audience: str

    tasks: List[Task]
```

The `Plan` represents the complete blog structure.

Example:

```text
Plan
│
├── Blog Title
├── Audience
│
└── Tasks
     ├── Introduction
     ├── History
     └── Modern Cricket
```

---

# 🔎 EvidenceItem

When research is required, the project collects information from the web.

Each source is represented by:

```python
class EvidenceItem(BaseModel):

    title: str

    url: str

    published_at: Optional[str]

    snippet: Optional[str]

    source: Optional[str]
```

This allows the application to keep track of where information came from.

---

# 🚦 Router

The router is the first node.

Its job is simple:

> "Does this blog topic need current web information?"

For example:

### Topic 1

```text
Explain what RAG is.
```

This is mostly an evergreen topic.

The router can choose:

```text
closed_book
```

### Topic 2

```text
What are the latest developments in the Indian stock market?
```

This changes frequently.

The router can choose:

```text
open_book
```

The router returns:

```python
{
    "needs_research": True,
    "mode": "open_book",
    "queries": [...]
}
```

---

# 🔀 Conditional Routing

The router is connected to:

```python
g.add_conditional_edges(
    "router",
    route_next,
    {
        "research": "research",
        "orchestrator": "orchestrator"
    }
)
```

This means:

```text
Router
  |
  +---- Research required ----> Research
  |
  +---- No research ----------> Orchestrator
```

This is one of the important LangGraph concepts demonstrated by this project.

---

# 🌐 Research Node

If research is required, the workflow reaches:

```python
research_node()
```

The research node:

1. Gets the queries generated by the router.
2. Searches Tavily.
3. Normalizes the results.
4. Sends the results to the LLM.
5. Converts them into `EvidenceItem` objects.
6. Removes duplicate URLs.

The flow is:

```text
Router
   |
   v
Search Queries
   |
   v
Tavily
   |
   v
Raw Search Results
   |
   v
LLM Evidence Extraction
   |
   v
EvidenceItem[]
```

---

# 🔍 Tavily Search

The notebook uses:

```python
TavilySearchResults(max_results=max_results)
```

The search result is normalized into:

```python
{
    "title": ...,
    "url": ...,
    "snippet": ...,
    "published_at": ...,
    "source": ...
}
```

This makes the search result easier to use later.

---

# 🎯 Orchestrator

The orchestrator creates the blog plan.

It uses structured output:

```python
llm.with_structured_output(Plan)
```

The LLM receives:

```text
Topic
Mode
Evidence
```

and creates:

```text
Plan
 |
 +-- Blog title
 +-- Audience
 |
 +-- Task 1
 +-- Task 2
 +-- ...
```

The notebook currently asks the orchestrator for:

```text
1-2 sections
```

This is useful during development because fewer sections means fewer LLM calls.

---

# 📤 Fanout

After the orchestrator creates the plan, the project uses LangGraph's `Send`.

The purpose of fanout is:

> Create one worker execution for every task in the plan.

Suppose the plan contains:

```text
Task 1 → Introduction
Task 2 → Market Trends
Task 3 → Future Outlook
```

Fanout creates:

```text
             FANOUT
                |
       +--------+--------+
       |        |        |
       v        v        v
    Worker   Worker   Worker
      1        2        3
```

This is called a **fan-out pattern**.

---

# 👷 Worker Node

Each worker writes **one section**.

The worker receives:

```text
Task
Topic
Mode
Plan
Evidence
```

Then the LLM generates the Markdown for that section.

For example:

```text
Task:
Introduction to Cricket

↓

Worker

↓

## Introduction to Cricket

Cricket is one of the world's...
```

The worker returns:

```python
{
    "sections": [
        (task.id, section_md)
    ]
}
```

---

# ❓ Why does the worker return `task.id`?

Because workers may finish in a different order.

For example:

```text
Task 1
Task 2
Task 3
```

could finish as:

```text
Task 2
Task 1
Task 3
```

If we simply joined the results, the blog could become incorrectly ordered.

By returning:

```python
(task.id, section_md)
```

the reducer can sort them:

```text
1 → Introduction
2 → Market Trends
3 → Future
```

So the final blog follows the original plan.

---

# 🔗 Merge Content

The first node inside the reducer subgraph is:

```python
merge_content()
```

Its job is to combine all worker outputs.

It:

1. Sorts sections by task ID.
2. Extracts the Markdown.
3. Joins the sections.
4. Adds the blog title.

The result looks like:

```markdown
# Blog Title

## Introduction

...

## Main Topic

...

## Conclusion

...
```

This is stored in:

```python
state["merged_md"]
```

---

# 🖼️ Image Planning

After the blog has been created, the project decides whether images would improve it.

This is handled by:

```python
decide_images()
```

The project uses a separate LLM:

```python
image_planner_llm
```

The LLM returns `ImageSpec` objects.

---

# 🖼️ ImageSpec

An `ImageSpec` describes one image:

```python
class ImageSpec(BaseModel):

    placeholder: str

    filename: str

    alt: str

    caption: str

    prompt: str

    size: Literal[
        "1024x1024",
        "1024x1536",
        "1536x1024"
    ]

    quality: Literal[
        "low",
        "medium",
        "high"
    ]
```

For example:

```text
ImageSpec
│
├── placeholder
│     [[IMAGE_1]]
│
├── filename
│     market_trend.png
│
├── alt
│     Indian stock market trend
│
├── caption
│     Market performance
│
└── prompt
      Create a professional chart...
```

---

# 💡 ImagePlan

The notebook contains:

```python
class ImagePlan(BaseModel):

    images: List[ImageSpec]
```

The purpose is simple.

The image-planning LLM only needs to answer:

> "Which images should be generated?"

It does not need to rewrite the entire blog.

So:

```text
Blog
 ↓
Image Planner
 ↓
ImagePlan
 ↓
ImageSpec[]
```

---

# 📍 Image Placeholders

The project uses placeholders such as:

```text
[[IMAGE_1]]
```

Instead of asking the LLM to rewrite the complete Markdown, Python inserts the placeholders using:

```python
insert_image_placeholders()
```

This is a good example of separating responsibilities:

```text
LLM
 ↓
Decides what image is needed

Python
 ↓
Inserts placeholder
```

The LLM handles reasoning.

Python handles deterministic operations.

---

# 🎨 Image Generation

The notebook uses Google GenAI for image generation.

The image model configured in the notebook is:

```python
gemini-2.5-flash-image
```

The workflow is:

```text
ImageSpec
    |
    v
Image Prompt
    |
    v
Gemini
    |
    v
Image Bytes
    |
    v
PNG file
```

Images are saved inside:

```text
images/
```

---

# 🔄 Image Replacement

Initially the Markdown contains:

```markdown
[[IMAGE_1]]
```

After the image is generated, it becomes something like:

```markdown
![Indian stock market trend](images/market_trend.png)

*Market performance*
```

The code performs this replacement automatically.

---

# 🧩 Reducer Subgraph

An important part of this project is that the reducer is itself a small LangGraph.

It looks like:

```text
START
  |
  v
merge_content
  |
  v
decide_images
  |
  v
generate_and_place_images
  |
  v
END
```

This demonstrates that a LangGraph node can itself be a compiled graph.

---

# 🌳 Main Graph

The main graph is:

```python
g = StateGraph(State)
```

Nodes:

```text
router
research
orchestrator
worker
reducer
```

Edges:

```text
START
  ↓
router
  ↓
research OR orchestrator
  ↓
orchestrator
  ↓
worker
  ↓
reducer
  ↓
END
```

The reducer is actually the reducer subgraph.

---

# 🧠 Complete Execution

For a topic such as:

```text
What are the recent developments in Indian Stock Market?
```

the execution is:

```text
1. User provides topic

        ↓

2. Router

   Detects that recent information is needed

        ↓

3. Research

   Tavily searches the web

        ↓

4. Evidence extraction

   Search results become EvidenceItem objects

        ↓

5. Orchestrator

   Creates Plan

        ↓

6. Fanout

   Creates one worker for each Task

        ↓

7. Workers

   Generate individual sections

        ↓

8. Merge Content

   Combines sections in the correct order

        ↓

9. Decide Images

   Decides whether images are useful

        ↓

10. Gemini

    Generates requested images

        ↓

11. Placeholder replacement

    [[IMAGE_1]] → actual image Markdown

        ↓

12. Final Markdown

    Blog is ready
```

---

# 📊 State

The workflow shares information using:

```python
class State(TypedDict):
```

The important fields are:

```text
topic
mode
needs_research
queries
evidence
plan
sections
final
merged_md
md_with_placeholders
image_specs
```

Think of `State` as a **shared backpack**.

Each node takes something out of the backpack, does some work, and puts new information back into it.

For example:

```text
Router
  ↓
State gets:
needs_research
mode
queries
```

Then:

```text
Research
  ↓
State gets:
evidence
```

Then:

```text
Orchestrator
  ↓
State gets:
plan
```

And so on.

---

# 🧪 Running the Workflow

The notebook currently uses:

```python
question = "What are the recent developments in Indian Stock Market?"
```

Then:

```python
output = app.invoke({
    "topic": question
})
```

The final blog is available through:

```python
output["final"]
```

---

# 💾 Saving the Blog

The notebook creates:

```text
blogs_generated_new/
```

Then generates a filename from the LLM-created title.

For example:

```text
blogs_generated_new/
    recent_developments_in_indian_stock_market_blog.md
```

The blog is saved using:

```python
output_path.write_text(
    output["final"],
    encoding="utf-8"
)
```

---

# 📁 Generated Files

After running the notebook, you can have:

```text
project/
│
├── notebook.ipynb
├── .env
│
├── images/
│   ├── market_trend.png
│   └── trading_process.png
│
└── blogs_generated_new/
    └── indian_stock_market_blog.md
```

---

# ⚠️ Important: API Rate Limits

This project can make multiple LLM requests.

For example:

```text
Router             → LLM
Research           → LLM
Orchestrator       → LLM
Worker 1           → LLM
Worker 2           → LLM
Image Planner      → LLM
```

Therefore, free API tiers can hit rate limits quickly.

You may see errors such as:

```text
429 RateLimitError
```

or:

```text
RESOURCE_EXHAUSTED
```

### Ways to reduce usage

- Keep the number of sections small.
- Use a smaller model for lightweight tasks.
- Limit the number of Tavily results.
- Don't send unnecessary context to workers.
- Avoid repeatedly generating the same image.
- Save generated images and reuse them when possible.

---

# 🚨 Important: Image Generation Quota

Gemini image generation has its own quota.

The notebook uses:

```python
model="gemini-2.5-flash-image"
```

If the Google API free quota is exhausted, image generation can fail even though your Groq API is working.

The blog-generation workflow should therefore be able to continue without an image when image generation fails.

The notebook implements a fallback message when image generation raises an exception.

---

# 🔐 Security

Never commit:

```text
.env
```

to GitHub.

Never write API keys directly in Python:

```python
GROQ_API_KEY = "abc123..."
```

Instead use:

```env
GROQ_API_KEY=...
```

and:

```python
load_dotenv()
```

---

# 🚀 Why this is an Agentic AI Project

This is more than a simple:

```text
Prompt → LLM → Answer
```

application.

The system makes decisions and performs multiple steps:

```text
Decide
  ↓
Research
  ↓
Plan
  ↓
Delegate
  ↓
Generate
  ↓
Evaluate image needs
  ↓
Generate images
  ↓
Assemble
```

The workflow dynamically chooses its path based on the user's request.

That is why LangGraph is useful here.

---

# 🎓 LangGraph Concepts You Learn

This notebook demonstrates:

### 1. StateGraph

```python
StateGraph(State)
```

Used to create the workflow.

### 2. State

Shared data between nodes.

### 3. Nodes

Functions such as:

```text
router_node
research_node
orchestrator
worker_node
merge_content
decide_images
generate_and_place_images
```

### 4. Conditional Edges

Used to decide:

```text
Research?
YES → research
NO  → orchestrator
```

### 5. Send

Used for fan-out:

```python
Send("worker", ...)
```

### 6. Structured Output

Used with Pydantic:

```python
llm.with_structured_output(Plan)
```

### 7. Subgraphs

The reducer itself is a graph.

### 8. Parallel Work

Multiple workers can generate sections independently.

### 9. Aggregation

The reducer combines the worker results.

---

# 🔧 Suggested Improvements

The current notebook is a strong learning project, but I would improve it in the following order.

## 1. Reduce unnecessary LLM calls

The current research node uses an LLM to convert Tavily results into `EvidencePack`.

That can potentially be replaced with deterministic Python normalization.

```text
Tavily
  ↓
Python normalization
  ↓
EvidenceItem
```

This saves one LLM call.

---

## 2. Use a smaller model for routing

Routing is a simple classification task.

A smaller model can handle:

```text
Research required?
```

while the larger model handles actual blog generation.

---

## 3. Limit evidence

Don't send 20 sources to every worker.

For example:

```python
evidence[:5]
```

is often enough for a small blog.

Also include the actual snippets, not just:

```text
title | URL | date
```

The snippet gives the worker useful factual context.

---

## 4. Use Python for exact charts

If the LLM requests:

```text
Nifty = 2.2%
Sensex = 2.1%
```

don't rely on an image-generation model to draw an accurate financial chart.

Use:

```text
LLM
 ↓
ImageSpec
 ↓
Chart?
 ↓
YES
 ↓
Matplotlib
```

This guarantees accurate numbers.

Use image-generation models for conceptual diagrams instead.

---

## 5. Add validation

A future architecture could be:

```text
Workers
   ↓
Reducer
   ↓
Validator
   |
   +---- PASS → END
   |
   +---- FAIL
           ↓
        Revision
           ↓
        Workers
```

The validator could check:

- Missing sections
- Citation problems
- Poor formatting
- Unsupported claims
- Missing images
- Broken Markdown

---

# 🏁 Final Summary

This project is an end-to-end **agentic blog generation pipeline**.

The most important idea is:

```text
                    User
                     |
                     v
                  Router
                     |
              Research needed?
                /          \
              Yes           No
               |             |
               v             |
            Tavily           |
               |             |
               +------+------+
                      |
                      v
                Orchestrator
                      |
                      v
                    Fanout
                      |
          +-----------+-----------+
          |           |           |
        Worker      Worker      Worker
          |           |           |
          +-----------+-----------+
                      |
                      v
                Merge Content
                      |
                      v
                Decide Images
                      |
                      v
              Generate Images
                      |
                      v
                  Final Blog
```

The project demonstrates how multiple specialized AI steps can be connected into a single workflow instead of asking one LLM to do everything in one prompt.

---

# 👨‍💻 Author

**Chinu Teja**

Data Scientist / AI Engineer

Focus areas:

- Generative AI
- Agentic AI
- LangGraph
- RAG
- LLM Applications
- MLOps
- Data Science
- Azure

