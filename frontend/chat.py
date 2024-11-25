import os
from dotenv import load_dotenv
import asyncio
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from graph import invoke_our_graph
from app.agents import AgentGraph
from app.references.client import chatOpenai_client, embedding_OpenAI

from st_callable_util import invoke_our_graph, transform_message_to_dict  # Utility function to get a Streamlit callback handler with context

load_dotenv()

# Set the tab name and icon
st.set_page_config(
    page_title="Talent Acquisition Platform",  # Sets the tab name
    page_icon="📌"  # Optional: Sets the tab icon 
)
st.title("📌 Talent Acquisition Platform")

main_agent = AgentGraph(llm=chatOpenai_client, model_embedding=embedding_OpenAI)

# Initialize the expander state
if "expander_open" not in st.session_state:
    st.session_state.expander_open = True
# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [AIMessage(content="How can I help you?")]
    st.session_state["search_trial"] = 0
    st.session_state["full_information"] = ""
    st.session_state["technical_reranker_output"] = ""

# Capture user input from chat input
prompt = st.chat_input()

# Toggle expander state based on user input
if prompt is not None:
    st.session_state.expander_open = False  # Close the expander when the user starts typing

# st write magic
with st.expander(label="Introduction", expanded=st.session_state.expander_open):
    """
    [The AI-Powered Talent Acquisition Platform](http://localhost:8501/) transforms recruitment by leveraging advanced AI to streamline processes, enhance candidate experiences, and deliver data-driven insights. 

    This thesis presents the development of an AI-powered talent
    acquisition platform aimed at revolutionizing the recruitment process by leveraging advanced technologies, including `Natural Language Processing (NLP)` and `Large Language
    Models (LLMs)`. 
    """

# Loop through all messages in the session state and render them as a chat on every st.refresh mech
for msg in st.session_state.messages:
    # https://docs.streamlit.io/develop/api-reference/chat/st.chat_message
    # we store them as AIMessage and HumanMessage as its easier to send to LangGraph
    if isinstance(msg, AIMessage):
        st.chat_message("assistant").write(msg.content)
    elif isinstance(msg, HumanMessage):
        st.chat_message("user").write(msg.content)

# Handle user input if provided
if prompt:
    # create a placeholder container for streaming and any other events to visually render here
    placeholder = st.container()
    st.session_state.messages.append(HumanMessage(content=prompt))
    st.chat_message("user").write(prompt)

    # Transform message to dict
    conservation_history = transform_message_to_dict(st.session_state.messages)

    response = asyncio.run(invoke_our_graph(
            graph_runnable=main_agent.compiled_graph,
            inputs={
                "conversation_history": conservation_history, 
                "search_trial": st.session_state["search_trial"],
                "full_information": st.session_state["full_information"],
                "technical_reranker_output": st.session_state["technical_reranker_output"],
            },
            config={},
            st_placeholder=placeholder,
        )
    )
    # Append the final AI response to the session state
    final_response = response["final_response"]
    st.session_state["messages"].append(AIMessage(content=response["final_response"]))
    st.session_state["search_trial"] = response["search_trial"]
    st.session_state["full_information"] = response["full_information"]
    st.session_state["technical_reranker_output"] = response["technical_reranker_output"]

    # Display the final AI response
    st.chat_message("assistant").write(final_response)


