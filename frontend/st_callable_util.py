import streamlit as st
from app.graphdb.flex import *
from app.graphdb.fixed import *
from app.preprocessing.extract_pdf import process_single_pdf

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)

from dotenv import load_dotenv
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

def transform_message_to_dict(messages):
    result = [
        {"role": "system", "content": msg.content} if isinstance(msg, SystemMessage) else
        {"role": "user", "content": msg.content} if isinstance(msg, HumanMessage) else
        {"role": "assistant", "content": msg.content}
        for msg in messages
    ]
    return result

async def invoke_our_graph(graph_runnable, inputs, config, st_placeholder):

    # Set up placeholders for displaying updates in the Streamlit app
    container = st_placeholder  # This container will hold the dynamic Streamlit UI components
    thoughts_placeholder = container.container()  # Container for displaying status messages

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
                        st.markdown("**:red[Next Action:]**")
                        choice_router = st.empty()  # Placeholder for tool output that will be updated later below
                        st.markdown("**:red[Extract Entity:]**")
                        entities = st.empty()
                        st.markdown("**:red[Filter Ranking:]**")
                        filter_results = st.empty()
                        st.markdown("**:red[Embedding Ranking:]**")
                        embedding_results = st.empty()
                        s.update(label="Completed Calling Router!", expanded=False)  # Update the status once done

        elif kind == "on_chain_end":

            if event['name'] == "_check_choice_router":
                # The event signals the completion of a tool's execution
                with thoughts_placeholder:
                    choice_router.code(event['data'].get('output'))  # Display the tool's output

            elif event['name'] == "query_analysis_node":
                with thoughts_placeholder:
                    entities.code(event['data'].get('output')['analyze_criteria'])  # Display the tool's output

            elif event['name'] == "search_fixed_filter":
                with thoughts_placeholder:
                    filter_results.code(event['data'].get('output')['filter_results'])  # Display the tool's output  

            elif event['name'] == "search_embedding":
                with thoughts_placeholder:
                    embedding_results.code(event['data'].get('output')['embedding_results'])  # Display the tool's output           

            elif event['name'] == "LangGraph":
                response =  {
                    "final_response" : event['data']["output"].get('final_response'),
                    "search_trial": event['data']["output"].get('search_trial'),
                    "full_information": event['data']["output"].get('full_information'),
                    "technical_reranker_output": event['data']["output"].get('technical_reranker_output'),
                }

    # Return the final aggregated message after all events have been processed
    return response

async def clear_upload_path(upload_path):
    try:
        if os.path.exists(upload_path):
            for file in os.listdir(upload_path):
                file_path = os.path.join(upload_path, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        logger.error(f"Error clearing upload path: {e}")

async def clear_json(json_path):
    try:
        if os.path.exists(json_path):
            with open(json_path, "w") as json_file:
                json.dump([], json_file)  

    except Exception as e:
        logger.error(f"Error resetting JSON file: {e}")
        
async def extract_from_pdf(pdf_paths):
    # Run tasks concurrently for each PDF
    tasks = [process_single_pdf(path, json_list_path="upload.json") for path in pdf_paths]
    await asyncio.gather(*tasks)
    await clear_upload_path(upload_path="uploads")

async def upload_to_database(json_path):

    with open(json_path, "r") as file:
        candidate_data = json.load(file)
    try:
        driver = await connect_to_neo4j(NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD)
        await create_flex_constraints(driver)
        await create_flex_nodes(driver, candidate_data)
        logger.info(f"{g}Successfully added person nodes and relationships")
        async with driver.session() as session:
            await create_fixed_constraints(session)
            nodes = prepare_nodes()
            node_types = ["Degree", "Position", "Skill", "Certification", "Publication"]
            for node_list, node_type in zip(nodes, node_types):
                await add_nodes_to_db(session, node_list, node_type)
    except Exception as e:
        logger.error(f"Error running main function:{e}")
    finally:
        await driver.close()
        logger.info(f"Disconnected from Neo4j")