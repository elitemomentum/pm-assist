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

st.title("🧠 Assistant")

# Session State Initialization
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "user_id" not in st.session_state:
    st.session_state.user_id = ""

# User ID Input
if not st.session_state.user_id:
    st.session_state.user_id = st.text_input("Enter your User ID to begin:")

# Chat Input
user_input = st.text_area("💬 Type your message:", height=150, placeholder="E.g. Authenticate as alice with passcode 1234")
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

            try:
                if status == "success":
                    if action == "query":
                        if matches:
                            reply = "📄 **Memory Result:**\n\n"
                            for m in matches:
                                reply += f"- {m['text']} *(score: {round(m['score'], 2)})*\n"
                        elif result_text:
                            reply = f"📄 **Memory Result:**\n\n{result_text}"
                        else:
                            reply = "📄 **Memory Result:**\n\n_No relevant memory found._"
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
