import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid


# **************************************** Utility Functions ******************************

def generate_thread_id():
    return str(uuid.uuid4())


def generate_thread_title(message, max_length=35):
    """Generate a sidebar title from the first user message."""
    message = message.strip()

    if len(message) <= max_length:
        return message

    return message[:max_length].strip() + "..."


def reset_chat():
    thread_id = generate_thread_id()

    st.session_state["thread_id"] = thread_id
    st.session_state["message_history"] = []

    add_thread(thread_id)

    # Give new chats a temporary title
    st.session_state["thread_titles"][thread_id] = "New Chat"


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def load_conversation(thread_id):
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
    st.session_state["chat_threads"] = []


# Store thread_id -> conversation title
if "thread_titles" not in st.session_state:
    st.session_state["thread_titles"] = {}


add_thread(st.session_state["thread_id"])


# **************************************** Sidebar UI *********************************

st.sidebar.title("LangGraph Chatbot")


if st.sidebar.button("New Chat"):
    reset_chat()
    st.rerun()


st.sidebar.header("My Conversations")


for thread_id in st.session_state["chat_threads"][::-1]:

    title = st.session_state["thread_titles"].get(
        thread_id,
        "New Chat"
    )

    if st.sidebar.button(
        title,
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

# Display conversation history

for message in st.session_state["message_history"]:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input

user_input = st.chat_input("Type here")


if user_input:

    # ------------------------------------------------
    # Set conversation title from FIRST user message
    # ------------------------------------------------

    thread_id = st.session_state["thread_id"]

    if (
        thread_id not in st.session_state["thread_titles"]
        or st.session_state["thread_titles"][thread_id] == "New Chat"
    ):

        st.session_state["thread_titles"][thread_id] = (
            generate_thread_title(user_input)
        )


    # ------------------------------------------------
    # Add user message to history
    # ------------------------------------------------

    st.session_state["message_history"].append(
        {
            "role": "user",
            "content": user_input
        }
    )


    with st.chat_message("user"):
        st.markdown(user_input)


    # ------------------------------------------------
    # LangGraph configuration
    # ------------------------------------------------

    CONFIG = {
        "configurable": {
            "thread_id": thread_id
        }
    }


    # ------------------------------------------------
    # Stream AI response
    # ------------------------------------------------

    with st.chat_message("assistant"):

        def ai_only_stream():

            for message_chunk, metadata in chatbot.stream(

                {
                    "messages": [
                        HumanMessage(content=user_input)
                    ]
                },

                config=CONFIG,

                stream_mode="messages"
            ):

                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content


        ai_message = st.write_stream(
            ai_only_stream()
        )


    # ------------------------------------------------
    # Save AI response
    # ------------------------------------------------

    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": ai_message
        }
    )