import requests
import json
import streamlit as st
from dotenv import load_dotenv
import os
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

# Load environment variables
load_dotenv()

# Retrieve environment variables
APPLICATION_TOKEN = os.getenv("ASTRA_DB_APPLICATION_TOKEN")
API_ENDPOINT = os.getenv("ASTRA_DB_API_ENDPOINT")
KEYSPACE = os.getenv("ASTRA_DB_KEYSPACE")
SECURE_BUNDLE_PATH = os.getenv("ASTRA_DB_SECURE_BUNDLE_PATH")

# Function to run the flow
def run_flow(message: str) -> dict:
    api_url = f"{API_ENDPOINT}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}"
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }
    headers = {"Authorization": "Bearer " + APPLICATION_TOKEN, "Content-Type": "application/json"}
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# Function to connect to Astra DB
def connect_to_astra():
    auth_provider = PlainTextAuthProvider('token', APPLICATION_TOKEN)
    cloud_config = {
        'secure_connect_bundle': SECURE_BUNDLE_PATH
    }
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    session.set_keyspace(KEYSPACE)
    return session

# Main function
def main():
    st.title("Social Media Performance Analysis")

    # Initialize session state for chat history
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Input field for the user
    message = st.text_area("", placeholder="How can we assist you today?")

    # Button to send the query
    if st.button("Generate Insights"):
        if not message.strip():
            st.error("Please enter a message")
            return

        try:
            with st.spinner("Running flow..."):
                response = run_flow(message)
                response_text = response["outputs"][0]["outputs"][0]["results"]["message"]["text"]

            # Append user message and response to chat history
            st.session_state["messages"].append({"user": message, "bot": response_text})

        except Exception as e:
            st.error(str(e))

    # Display chat history
    st.subheader("Chat History")
    for chat in st.session_state["messages"]:
        st.markdown(f"**You:** {chat['user']}")
        st.markdown(f"**Bot:** {chat['bot']}")
        st.divider()  # Adds a divider for better readability

if __name__ == "__main__":
    main()
