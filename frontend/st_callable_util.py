from typing import Callable, TypeVar, Any, Dict, Optional
import inspect

from streamlit.runtime.scriptrunner import add_script_run_ctx, get_script_run_ctx
from streamlit.delta_generator import DeltaGenerator

from langchain_core.callbacks.base import BaseCallbackHandler
import streamlit as st

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

def transform_message_to_dict(messages):
    result = [
        {"role": "system", "content": msg.content} if isinstance(msg, SystemMessage) else
        {"role": "user", "content": msg.content} if isinstance(msg, HumanMessage) else
        {"role": "assistant", "content": msg.content}
        for msg in messages
    ]
    return result


async def invoke_our_graph(graph_runnable, inputs, config, st_placeholder):
    """
    Asynchronously processes a stream of events from the graph_runnable and updates the Streamlit interface.

    Args:
        st_messages (list): List of messages to be sent to the graph_runnable.
        st_placeholder (st.beta_container): Streamlit placeholder used to display updates and statuses.

    Returns:
        AIMessage: An AIMessage object containing the final aggregated text content from the events.
    """
    # Set up placeholders for displaying updates in the Streamlit app
    container = st_placeholder  # This container will hold the dynamic Streamlit UI components
    thoughts_placeholder = container.container()  # Container for displaying status messages
    token_placeholder = container.empty()  # Placeholder for displaying progressive token updates
    final_text = ""  # Will store the accumulated text from the model's response

    # Stream events from the graph_runnable asynchronously
    async for event in graph_runnable.astream_events(inputs, config, version="v2"):
        kind = event["event"]  # Determine the type of event received

        # if kind == "on_chat_model_stream":
        #     # The event corresponding to a stream of new content (tokens or chunks of text)
        #     addition = event["data"]["chunk"].content  # Extract the new content chunk
        #     final_text += addition  # Append the new content to the accumulated text
        #     if addition:
        #         token_placeholder.write(final_text)  # Update the st placeholder with the progressive response

        if kind == "on_chain_start":
           
            if event['name'] == "_check_choice_router":

                with thoughts_placeholder:
                    status_placeholder = st.empty()  # Placeholder to show the tool's status
                    with status_placeholder.status("Choosing Router...", expanded=True) as s:
                        # st.write("Called ", event['name'])  # Show which tool is being called
                        # st.write("Tool input: ")
                        # st.code(event['data'].get('input'))  # Display the input data sent to the tool
                        st.write("Next Action: ")
                        output_placeholder = st.empty()  # Placeholder for tool output that will be updated later below
                        s.update(label="Completed Calling Router!", expanded=False)  # Update the status once done

        elif kind == "on_chain_end":

            if event['name'] == "_check_choice_router":

                # The event signals the completion of a tool's execution
                with thoughts_placeholder:
                    # We assume that `on_tool_end` comes after `on_tool_start`, meaning output_placeholder exists
                    if 'output_placeholder' in locals():
                        output_placeholder.code(event['data'].get('output'))  # Display the tool's output

            elif event['name'] == "LangGraph":
                response =  {
                    "final_response" : event['data']["output"].get('final_response'),
                    "search_trial": event['data']["output"].get('search_trial'),
                    "full_information": event['data']["output"].get('full_information'),
                    "technical_reranker_output": event['data']["output"].get('technical_reranker_output'),
                }

    # Return the final aggregated message after all events have been processed
    return response