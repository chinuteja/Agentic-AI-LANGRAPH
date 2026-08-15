import streamlit as st
from langgraph_backend_database import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid


# **************************************** Utility Functions *************************

def generate_thread_id():
    """Generate a unique thread ID."""
    return str(uuid.uuid4())


def reset_chat():
    """Create a new chat thread and reset message history."""
    thread_id = generate_thread_id()

    st.session_state["thread_id"] = thread_id
    add_thread(thread_id)
    st.session_state["message_history"] = []


def add_thread(thread_id):
    """Add thread ID to session state if it doesn't already exist."""
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
    """Load messages from a saved LangGraph conversation."""
    state = chatbot.get_state(
        config={
            "configurable": {
                "thread_id": thread_id
            }
        }
    )

    return state.values.get("messages", [])


# **************************************** Session Setup ******************************

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

add_thread(st.session_state["thread_id"])


# **************************************** Sidebar UI *********************************

st.sidebar.title("LangGraph Chatbot")


if st.sidebar.button("New Chat"):
    reset_chat()
    st.rerun()


st.sidebar.header("My Conversations")


# Display conversations in reverse order
for thread_id in st.session_state["chat_threads"][::-1]:

    if st.sidebar.button(
        str(thread_id),
        key=f"thread_{thread_id}"
    ):

        st.session_state["thread_id"] = thread_id

        messages = load_conversation(thread_id)

        temp_messages = []

        for msg in messages:

            if isinstance(msg, HumanMessage):
                role = "user"
            else:
                role = "assistant"

            temp_messages.append(
                {
                    "role": role,
                    "content": msg.content
                }
            )

        st.session_state["message_history"] = temp_messages

        st.rerun()


# **************************************** Main UI ************************************

st.title("LangGraph Chatbot")


# Load conversation history
for message in st.session_state["message_history"]:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input
user_input = st.chat_input("Type here")


if user_input:

    # Add user message to history
    st.session_state["message_history"].append(
        {
            "role": "user",
            "content": user_input
        }
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)


    # LangGraph configuration
    CONFIG = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        },
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn",
    }


    # Generate assistant response
    with st.chat_message("assistant"):

        ai_message = st.write_stream(
            message_chunk.content
            for message_chunk, metadata in chatbot.stream(
                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },
                config=CONFIG,
                stream_mode="messages"
            )
        )


    # Save assistant response in session history
    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": ai_message
        }
    )