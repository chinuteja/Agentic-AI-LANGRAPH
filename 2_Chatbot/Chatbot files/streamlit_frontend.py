import streamlit as st
from langchain_core.messages import HumanMessage
from langgraph_backend import chatbot

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 LangGraph Chatbot")

# -----------------------------
# LangGraph Configuration
# -----------------------------
CONFIG = {
    "configurable": {
        "thread_id": "thread-1"
    }
}

# -----------------------------
# Session State
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -----------------------------
# Display Chat History
# -----------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -----------------------------
# User Input
# -----------------------------
user_input = st.chat_input("Ask me anything...")

if user_input:

    # Display user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)

    # Display assistant response
    with st.chat_message("assistant"):

        response = st.write_stream(
            chunk.content
            for chunk, metadata in chatbot.stream(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },
                config=CONFIG,
                stream_mode="messages"
            )
        )

    # Save assistant response
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response
        }
    )