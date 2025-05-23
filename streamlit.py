import streamlit as st
import requests
import openai
from datetime import datetime

# Config
API_URL = "https://3m9yprbn71.execute-api.ap-south-1.amazonaws.com/production/process"
OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", "")  # Store in Streamlit secrets

st.set_page_config(page_title="PM Assist", layout="centered")

# CSS Styling
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stTextInput>div>div>input,
    .stTextArea>div>textarea {
        background-color: #f9f9f9;
        border-radius: 12px;
        padding: 0.75rem;
    }
    .stButton>button {
        background-color: #000000;
        color: white;
        border-radius: 12px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    .natural-response {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 PM Assist")

# OpenAI API Key Input (if not in secrets)
if not OPENAI_API_KEY:
    OPENAI_API_KEY = st.text_input("Enter OpenAI API Key:", type="password")

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_id" not in st.session_state:
    st.session_state.user_id = ""

# User ID Input
if not st.session_state.user_id:
    st.session_state.user_id = st.text_input("Enter your User ID to begin:")

# Chat Input
user_input = st.text_area("💬 Type your message:", height=150, placeholder="E.g. what the recent update on pm-assist")
send_btn = st.button("Send")

def format_with_openai(api_response, user_query):
    """Convert API response to natural language using OpenAI"""
    if not OPENAI_API_KEY:
        return "⚠️ OpenAI API key required for natural language formatting"
    
    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
        
        # Extract matches from the response
        matches = api_response.get("matches", [])
        if not matches:
            return "No relevant information found in the memory system."
        
        # Prepare context for OpenAI
        context = []
        for match in matches:
            text = match.get("text", "")
            timestamp = match.get("timestamp", "")
            score = match.get("score", 0)
            
            # Format timestamp if available
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%B %d, %Y at %I:%M %p")
                except:
                    formatted_time = timestamp
            else:
                formatted_time = "Unknown time"
            
            context.append(f"Content: {text}\nTimestamp: {formatted_time}\nRelevance Score: {score:.2f}")
        
        context_text = "\n\n".join(context)
        
        prompt = f"""
        The user asked: "{user_query}"
        
        Here are the search results from the memory system:
        
        {context_text}
        
        Please explain this information in natural language, keeping the context intact. 
        Make it conversational and easy to understand. Include the timing information naturally.
        If there are multiple results, present them in a coherent way.
        """
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that converts search results into natural, conversational language. Be concise but informative."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error processing with OpenAI: {str(e)}"

# On Send
if send_btn:
    if not st.session_state.user_id:
        st.warning("Please enter your User ID.")
    elif not user_input.strip():
        st.warning("Message cannot be empty.")
    else:
        # Store user input
        st.session_state.chat_history.append(("You", user_input))
        
        try:
            response = requests.post(API_URL, json={
                "user_id": st.session_state.user_id,
                "text": user_input
            })
            result = response.json()
            
            message = result.get("message", "")
            result_text = result.get("result", "")
            status = result.get("status", "error")
            action = result.get("action", "")
            
            if status == "success":
                if action == "query":
                    # Show raw response (optional, for debugging)
                    with st.expander("🔍 Raw API Response (Debug)"):
                        st.json(result)
                    
                    # Process with OpenAI for natural language
                    natural_response = format_with_openai(result, user_input)
                    reply = f"""
                    <div class="natural-response">
                    <h4>🤖 Natural Language Response:</h4>
                    {natural_response}
                    </div>
                    """
                else:
                    reply = f"✅ {message}"
            else:
                reply = f"❌ {message or 'Unknown error.'}"
                
        except Exception as e:
            reply = f"❌ Error: {str(e)}"
        
        st.session_state.chat_history.append(("PM Assist", reply))

# Display Chat
st.divider()
st.subheader("🗂️ Conversation History")
for sender, msg in reversed(st.session_state.chat_history):
    with st.chat_message(name=sender):
        st.markdown(msg, unsafe_allow_html=True)

# Instructions
with st.sidebar:
    st.header("📖 Instructions")
    st.write("""
    1. Enter your User ID
    2. Add OpenAI API key (in secrets or input field)
    3. Ask questions about PM Assist
    4. Get natural language responses powered by OpenAI
    """)
    
    st.header("🔧 Features")
    st.write("""
    - Memory search and retrieval
    - Natural language processing
    - Conversation history
    - Debug information available
    """)