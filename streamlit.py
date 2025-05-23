import streamlit as st
import requests

# Config
API_URL = "https://3m9yprbn71.execute-api.ap-south-1.amazonaws.com/production/process"
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
        padding: 1.2rem;
        border-radius: 12px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
        font-size: 1.05em;
        line-height: 1.6;
    }
    .openai-badge {
        background-color: #10a37f;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: 600;
        margin-bottom: 0.5rem;
        display: inline-block;
    }
    .raw-response {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        font-family: monospace;
        font-size: 0.85em;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧠 PM Assist")

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_id" not in st.session_state:
    st.session_state.user_id = ""

# User ID Input
if not st.session_state.user_id:
    st.session_state.user_id = st.text_input("Enter your User ID to begin:")

# Chat Input
user_input = st.text_area("💬 Type your message:", height=150, placeholder="E.g. Authenticate as alice with passcode 1234\nOr: what the recent update on pm-assist")
send_btn = st.button("Send")

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
            natural_response = result.get("natural_response", "")
            openai_processed = result.get("openai_processed", False)
            
            if status == "success":
                if action == "query":
                    # Show natural language response if available
                    if natural_response:
                        badge_html = '<div class="openai-badge">🤖 AI Enhanced</div>' if openai_processed else '<div class="openai-badge" style="background-color: #6c757d;">🔄 Fallback</div>'
                        
                        reply = f"""
                        {badge_html}
                        <div class="natural-response">
                        {natural_response}
                        </div>
                        """
                        
                        # Add raw response in expander for debugging
                        raw_response_html = f"""
                        <details>
                        <summary style="cursor: pointer; font-weight: 600; color: #6c757d; margin-top: 1rem;">🔍 View Raw Data</summary>
                        <div class="raw-response" style="margin-top: 0.5rem;">
                        <strong>Matches Found:</strong> {len(result.get("matches", []))}<br>
                        <strong>Status:</strong> {status}<br>
                        <strong>OpenAI Processed:</strong> {openai_processed}<br><br>
                        <strong>Raw Response:</strong><br>
                        {str(result)}
                        </div>
                        </details>
                        """
                        reply += raw_response_html
                    else:
                        # Fallback to original format if no natural response
                        reply = f"📄 **Memory Result:**\n\n{result_text or message}"
                elif action == "authenticate":
                    if result.get("authenticated"):
                        reply = f"🔐 **Authentication Successful**\n\n✅ {message}"
                    else:
                        reply = f"🔐 **Authentication Failed**\n\n❌ {message}"
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

if st.session_state.chat_history:
    for sender, msg in reversed(st.session_state.chat_history):
        with st.chat_message(name=sender):
            st.markdown(msg, unsafe_allow_html=True)
else:
    st.info("💡 Start by authenticating with your credentials, then ask questions!")

# Sidebar with instructions and status
with st.sidebar:
    st.header("📖 Instructions")
    st.write("""
    **Getting Started:**
    1. Enter your User ID
    2. Authenticate: `Authenticate as [username] with passcode [code]`
    3. Ask questions or store information
    
    **Example Commands:**
    - `Authenticate as alice with passcode 1234`
    - `what the recent update on pm-assist`
    - `store: PM project milestone completed`
    """)
    
    st.header("🔧 Features")
    st.write("""
    - 🤖 **AI-Enhanced Responses** (OpenAI powered)
    - 🔍 **Smart Memory Search**
    - 🔐 **Secure Authentication**
    - 📊 **Raw Data Available**
    - 💬 **Conversation History**
    """)
    
    # Status indicators
    st.header("📊 Status")
    if st.session_state.user_id:
        st.success(f"🆔 User ID: {st.session_state.user_id}")
    else:
        st.warning("⚠️ No User ID entered")
    
    if st.session_state.chat_history:
        auth_messages = [msg for sender, msg in st.session_state.chat_history if "Authentication Successful" in msg]
        if auth_messages:
            st.success("🔐 Authenticated")
        else:
            st.warning("🔐 Not authenticated")
    else:
        st.info("🔐 Authentication pending")

# Footer
st.markdown("---")
st.markdown("*PM Assist - Your intelligent project management companion*")