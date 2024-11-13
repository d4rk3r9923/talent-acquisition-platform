import streamlit as st
import os
import time
import subprocess

def create_chat_tab(tab):
    """Create the Chat tab content."""
    with tab:
        st.header("Chat with AI")
        user_input = st.text_input("You:", "")
        if st.button("Send"):
            response = f"AI: You said '{user_input}'"
            st.text(response)

def create_upload_tab(tab):
    """Create the Upload PDF tab content."""
    with tab:
        st.header("Upload your PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file is not None:
            save_uploaded_file(uploaded_file)
            display_success_message()

def save_uploaded_file(uploaded_file):
    """Save the uploaded file to a local directory."""
    save_path = os.path.join("uploads", uploaded_file.name)
    os.makedirs("uploads", exist_ok=True)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

def display_success_message():
    """Display a temporary success message."""
    success_message = st.empty()
    success_message.success("Upload successful!")
    time.sleep(5)
    success_message.empty()

def setup_app():
    st.title("Talent Acquisition Platform")
    tab1, tab2 = st.tabs(["Chat", "Upload PDF"])
    create_chat_tab(tab1)
    create_upload_tab(tab2)


setup_app()
