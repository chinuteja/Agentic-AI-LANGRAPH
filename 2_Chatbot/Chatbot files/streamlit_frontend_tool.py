import streamlit as st
from langgraph_tool_backend import (
    chatbot,
    retrieve_all_threads,
    delete_thread
)
from langchain_core.messages import AIMessage, HumanMessage
import uuid


# ============================================================
# Utility Functions
# ============================================================

def generate_thread_id():
    """Generate a unique thread ID."""
    return str(uuid.uuid4())


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


def get_thread_title(thread_id):
    """Get the first user question as the conversation title."""

    messages = load_conversation(thread_id)

    for message in messages:

        if isinstance(message, HumanMessage):

            title = message.content.strip()

            # Keep sidebar title short
            if len(title) > 35:
                title = title[:35] + "..."

            return title

    return "New Chat"


def add_thread(thread_id):
    """Add thread to session state if it doesn't exist."""

    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def reset_chat():
    """Create a new conversation."""

    thread_id = generate_thread_id()

    st.session_state["thread_id"] = thread_id
    st.session_state["message_history"] = []

    add_thread(thread_id)


def load_thread(thread_id):
    """Load selected conversation."""

    st.session_state["thread_id"] = thread_id

    messages = load_conversation(thread_id)

    temp_messages = []

    for msg in messages:

        if isinstance(msg, HumanMessage):
            role = "user"

        elif isinstance(msg, AIMessage):
            role = "assistant"

        else:
            continue

        temp_messages.append(
            {
                "role": role,
                "content": msg.content
            }
        )

    st.session_state["message_history"] = temp_messages


def delete_chat(thread_id):
    """Delete conversation from database and session state."""

    # Delete from LangGraph database
    delete_thread(thread_id)

    # Remove from session state
    if thread_id in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].remove(thread_id)

    # If currently active chat was deleted
    if st.session_state["thread_id"] == thread_id:

        new_thread_id = generate_thread_id()

        st.session_state["thread_id"] = new_thread_id
        st.session_state["message_history"] = []

        add_thread(new_thread_id)


# ============================================================
# Session State
# ============================================================

if "message_history" not in st.session_state:
    st.session_state["message_history"] = []


if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = generate_thread_id()


if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()


add_thread(st.session_state["thread_id"])


# ============================================================
# Sidebar
# ============================================================

st.sidebar.title("🤖 LangGraph Chatbot")


# New Chat
if st.sidebar.button(
    "➕ New Chat",
    use_container_width=True
):

    reset_chat()
    st.rerun()


st.sidebar.divider()

st.sidebar.subheader("💬 My Conversations")


# ============================================================
# Conversation List
# ============================================================

for thread_id in st.session_state["chat_threads"][::-1]:

    title = get_thread_title(thread_id)

    col1, col2 = st.sidebar.columns(
        [5, 1],
        gap="small"
    )

    # Conversation
    with col1:

        if st.button(
            title,
            key=f"thread_{thread_id}",
            use_container_width=True
        ):

            load_thread(thread_id)
            st.rerun()

    # Delete
    with col2:

        if st.button(
            "🗑️",
            key=f"delete_{thread_id}",
            help="Delete this conversation"
        ):

            delete_chat(thread_id)
            st.rerun()


# ============================================================
# Main UI
# ============================================================

st.title("💬 LangGraph Chatbot")


# ============================================================
# Display Conversation History
# ============================================================

for message in st.session_state["message_history"]:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# Chat Input
# ============================================================

user_input = st.chat_input("Type your message...")


if user_input:

    # --------------------------------------------------------
    # Add user message to UI
    # --------------------------------------------------------

    st.session_state["message_history"].append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):
        st.markdown(user_input)


    # --------------------------------------------------------
    # LangGraph Configuration
    # --------------------------------------------------------

    CONFIG = {
        "configurable": {
            "thread_id": st.session_state["thread_id"]
        },
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn"
    }


    # --------------------------------------------------------
    # Stream AI Response
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # Save Assistant Response
    # --------------------------------------------------------

    st.session_state["message_history"].append(
        {
            "role": "assistant",
            "content": ai_message
        }
    )