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
    </style>
""", unsafe_allow_html=True)

st.title("🧠 PM Assist – Project Memory Chat")

# Session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_id" not in st.session_state:
    st.session_state.user_id = st.text_input("Enter your User ID to begin:")

# Chatbox input
user_input = st.text_area("Type your message (authentication, update, or query):", height=150)
send_btn = st.button("💬 Send")

# Process input
if send_btn and user_input and st.session_state.user_id:
    response = requests.post(API_URL, json={
        "user_id": st.session_state.user_id,
        "text": user_input
    })
    result = response.json()
    st.session_state.chat_history.append(("You", user_input))
    
    message = result.get("message", "")
    action = result.get("action", "")
    result_text = result.get("result", "")

    if result.get("status") == "success":
        if action == "query":
            reply = f"📄 **Result:**\n\n{result_text}"
        else:
            reply = f"✅ {message}"
    else:
        reply = f"❌ {message}"
    
    st.session_state.chat_history.append(("PM Assist", reply))

# Display chat history
for sender, msg in reversed(st.session_state.chat_history):
    st.markdown(f"**{sender}:** {msg}", unsafe_allow_html=True)
