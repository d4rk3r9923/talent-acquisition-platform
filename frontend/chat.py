import os
import json
from dotenv import load_dotenv
import asyncio
import uuid
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from app.agents import AgentGraph
from app.references.client import chatOpenai_client, embedding_OpenAI
from st_callable_util import (
    invoke_our_graph, 
    transform_message_to_dict, 
    extract_from_pdf, 
    upload_to_database,
    clear_json,
    clear_upload_path
)  


def create_upload_tab(tab):
    with tab:
        st.write("#### Upload your PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file is not None:
            save_uploaded_file(uploaded_file)


def save_uploaded_file(uploaded_file):
    # Save the uploaded PDF to the 'uploads' folder
    save_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Define JSON output file path
    
    try:
        with st.spinner("Extracting..."):
            json_output_path = "upload.json"
            # Run PDF extraction and upload process
            asyncio.run(extract_from_pdf([save_path], json_path=json_output_path))
            asyncio.run(upload_to_database(json_path=json_output_path))
        
        st.success("PDF was processed successfully and added to Graph Database.")

        # Load and display the JSON content
        if os.path.exists(json_output_path):
            with open(json_output_path, "r") as json_file:
                json_content = json.load(json_file)
            person_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, json_content[-1]["person"]["path_pdf"]))
            st.success(f"Extracted ID successfully: **{person_id}**")
        clear_upload_path("uploads")
        clear_json(json_path=json_output_path)

    except Exception as e:
        st.error(f"An error occurred: {e}")


def create_chat_tab(tab, prompt, main_agent):
    with tab:

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

            # Use spinner while processing the response
            with st.spinner("Thinking..."):
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


st.set_page_config(
    page_title="Talent Acquisition Platform",  # Sets the tab name
    page_icon="📌"  # Optional: Sets the tab icon 
)
st.title("📌 Talent Acquisition Platform")

main_agent = AgentGraph(llm=chatOpenai_client, model_embedding=embedding_OpenAI)


# Initialize chat messages in session state
if "messages" not in st.session_state:
    st.session_state["messages"] = [AIMessage(content="How can I help you?")]
    st.session_state["search_trial"] = 0
    st.session_state["full_information"] = ""
    st.session_state["technical_reranker_output"] = ""

# st write magic
with st.expander(label="Introduction", expanded=False):
    """
    [The AI-Powered Talent Acquisition Platform](http://localhost:8501/) transforms recruitment by leveraging advanced AI to streamline processes, enhance candidate experiences, and deliver data-driven insights. 

    This thesis presents the development of an AI-powered talent
    acquisition platform enhanced the hiring process by enabling `natural language queries` for improved candidate search and `automating document parsing` to convert unstructured resumes into structured data for dynamic relationship modeling. 
    """
    # Show image inside the expander
    st.image("images/system.png", caption="AI-Powered Talent Acquisition System Architecture")

# Capture user input from chat input
prompt = st.chat_input("Type your message here...")

tab1, tab2 = st.tabs(["Chat with HR Agents", "Upload PDF to Database"])
create_chat_tab(tab1, prompt, main_agent)
create_upload_tab(tab2)