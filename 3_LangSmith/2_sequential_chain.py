from groq import Groq
from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

load_dotenv()
os.environ["LANGCHAIN_PROJECT"] = "SEQUENTIAL_CHAIN_DEMO"
prompt1 = PromptTemplate(
    template='Generate a detailed report on {topic} make sure it is within 200 words',
    input_variables=['topic']
)

prompt2 = PromptTemplate(
    template='Generate a 5 pointer summary from the following text \n {text}',
    input_variables=['text']
)

model = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3
)

parser = StrOutputParser()
config = {
    "tags": ["sequential_chain_demo","llm_chain","report generation","summary_generation"],
    "metadata": {
        "author": "LangSmith Demo",
        "description": "This is a demo of sequential chain using LangSmith",
        "model": "openai/gpt-oss-120b",
        "temperature": 0.3
    }
}

chain = prompt1 | model | parser | prompt2 | model | parser

result = chain.invoke({'topic': 'Unemployment in India'}, config=config)

print(result)