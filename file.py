import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="E-commerce Chatbot",
    page_icon="🛍️",
    layout="wide"
)

# Initialize Groq client
def setup_groq():
    try:
        # Get API key
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            st.error("Groq API key not found in .env file")
            return None
            
        # Create a simple HTTP client without proxy settings
        import httpx
        
        # Initialize Groq client with custom HTTP client
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

# Initialize Groq client
groq_client = setup_groq()

# Initialize session state for chat messages
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm your e-commerce assistant. How can I help you today?"
        }
    ]

# Display chat messages
st.title("E-commerce Assistant")
st.write("Ask me anything about our products, orders, or services!")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        if not groq_client:
            full_response = "Error: Groq client not initialized. Please check your API key."
        else:
            try:
                # Show a loading spinner while waiting for the response
                with st.spinner("Thinking..."):
                    # Call Groq API with a supported model
                    response = groq_client.chat.completions.create(
                        model="llama3-8b-8192",  # Using a supported model
                        messages=[
                            {
                                "role": "system",
                                "content": """You are a helpful e-commerce assistant. Provide concise and helpful responses to 
                                customer queries about products, orders, and general e-commerce questions.
                                Be friendly and professional in your responses."""
                            }
                        ] + [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.messages
                        ],
                        temperature=0.7,
                        max_tokens=1000,
                        stream=True
                    )
                    
                    # Stream the response
                    for chunk in response:
                        if chunk.choices[0].delta.content is not None:
                            content = chunk.choices[0].delta.content
                            full_response += content
                            message_placeholder.markdown(full_response + "▌")
                    
                    # Update the placeholder with the final response
                    message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"Sorry, I encountered an error: {str(e)}"
                message_placeholder.error(full_response)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Add a sidebar with some information
with st.sidebar:
    st.header("About")
    st.markdown("""
    This is an AI-powered e-commerce assistant. You can ask me about:
    - Product information
    - Order status
    - Return policies
    - And any other e-commerce related questions!
    """)
    
    if st.button("Clear Chat"):
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hello! I'm your e-commerce assistant. How can I help you today?"
            }
        ]
        st.rerun()

# Add some custom CSS for better appearance
st.markdown("""
    <style>
        .stChatFloatingInputContainer {
            bottom: 20px;
        }
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 1rem;
        }
        .stChatMessage p {
            margin: 0;
        }
    </style>
""", unsafe_allow_html=True)
