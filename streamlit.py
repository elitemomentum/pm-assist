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
user_input = st.text_area("💬 Type your message:", height=150, placeholder="Type your message here...")
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
                        reply = f"""
                        <div class="natural-response">
                        {natural_response}
                        </div>
                        """
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