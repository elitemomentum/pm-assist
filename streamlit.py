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
    st.session_state.user_id = st.text_input("🆔 Enter your User ID to begin:")
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# Chat input
user_input = st.text_area("💬 Type your message (authentication, update, or query):", height=150)
send_btn = st.button("📤 Send")

# Send message
if send_btn and user_input and st.session_state.user_id:
    st.session_state.chat_history.append(("You", user_input))

    response = requests.post(API_URL, json={
        "user_id": st.session_state.user_id,
        "text": user_input
    })

    try:
        result = response.json()
    except Exception as e:
        result = {"status": "error", "message": str(e)}

    # Update authenticated status if present
    if "authenticated" in result:
        st.session_state.authenticated = result["authenticated"]

    # Build reply
    status = result.get("status", "")
    message = result.get("message", "")
    action = result.get("action", "")
    matches = result.get("matches", [])
    result_text = result.get("result", "")

    if status == "success":
        if action == "query" and matches:
            reply = "📄 **Memory Result:**\n\n"
            for m in matches:
                reply += f"- {m['text']} *(score: {round(m['score'], 2)})*\n"
        elif action == "query":
            reply = f"📄 **Memory Result:**\n\n{result_text or message}"
        else:
            reply = f"✅ {message}"
    else:
        reply = f"❌ {message or 'Something went wrong.'}"

    st.session_state.chat_history.append(("PM Assist", reply))

# Show chat history
for sender, msg in reversed(st.session_state.chat_history):
    st.markdown(f"**{sender}:** {msg}", unsafe_allow_html=True)
