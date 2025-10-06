import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Coding Assistant",
    page_icon="💻",
    layout="wide"
)

# Initialize Groq client
def setup_groq():
    try:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.error("Groq API key not found in .env file")
            return None

        import httpx
        client = Groq(
            api_key=api_key,
            http_client=httpx.Client(
                timeout=30.0,
                follow_redirects=True,
                verify=True
            )
        )
        return client
    except Exception as e:
        st.error(f"Failed to initialize Groq client: {str(e)}")
        return None

groq_client_instance = setup_groq()

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "👋 Hello! I'm your coding assistant. What programming challenge can I help you solve today?"
        }
    ]

# Sidebar with instructions and settings
with st.sidebar:
    st.title("💻 Coding Assistant")
    st.markdown("""
    ### How to use:
    1. Type your coding question in the chat box below
    2. Press Enter or click Send
    3. I can help you with:
       - Debugging code
       - Writing scripts
       - Understanding programming concepts
       - Exploring frameworks and libraries
    """)
    
    if st.button("🔄 Clear Chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hello! I'm your coding assistant. What programming challenge can I help you solve today?"
            }
        ]
        st.rerun()

# Main chat interface
def main():
    st.title("💬 Coding Assistant")
    
    groq_client = groq_client_instance
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    if prompt := st.chat_input("Type your coding question here..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            if not groq_client:
                full_response = "Error: Could not connect to the AI service. Please check your API key."
            else:
                try:
                    response = groq_client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[
                            {
                                "role": "system",
                                "content": """You are a knowledgeable and friendly coding assistant. 
                                Help users with programming questions, debugging, code generation, and 
                                explanations of technical concepts. Be clear, concise, and supportive.
                                """
                            },
                            *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                        ],
                        temperature=0.7,
                        max_tokens=1024,
                        stream=True
                    )
                    
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
                except Exception as e:
                    full_response = f"⚠️ Sorry, I encountered an error: {str(e)}"
                    message_placeholder.error(full_response)
        
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()

# Custom CSS
st.markdown("""
    <style>
        .stChatFloatingInputContainer {
            bottom: 20px;
        }
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.8rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .stChatMessage p {
            margin: 0;
            line-height: 1.6;
        }
        .stButton>button {
            width: 100%;
            margin-top: 0.5rem;
            background-color: #2196F3;
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
        }
        .stButton>button:hover {
            background-color: #1976D2;
        }
    </style>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
