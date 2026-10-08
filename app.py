import streamlit as st
from src.api.routes import engine

st.set_page_config(page_title="M2Rag Chatbot", page_icon="🥗", layout="centered")

st.title("🥗 Dietary Guidance Chatbot")
st.markdown("Ask me questions about dietary guidelines, safe food handling, and nutrition!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is your question?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("Thinking..."):
            try:
                response = engine.ask(prompt)
                message_placeholder.markdown(response)
            except Exception as e:
                response = f"An error occurred: {str(e)}"
                message_placeholder.error(response)
        
    st.session_state.messages.append({"role": "assistant", "content": response})
