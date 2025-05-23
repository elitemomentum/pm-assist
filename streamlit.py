import streamlit as st
import requests

st.set_page_config(page_title="PM Assist", layout="wide")

st.markdown("""
    <style>
    .main {
        background-color: #ffffff;
    }
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

st.title("🧠 PM Assist – Natural Language Project Memory")

with st.sidebar:
    st.header("🔐 Authentication")
    user_id = st.text_input("User ID", placeholder="Enter your ID")
    username = st.text_input("Username", placeholder="e.g. johndoe")
    passcode = st.text_input("Passcode", type="password")
    auth_button = st.button("Authenticate")

authenticated = False
if auth_button:
    response = requests.post("https://3m9yprbn71.execute-api.ap-south-1.amazonaws.com/production/process", json={
        "user_id": user_id,
        "text": f"authenticate as {username} with passcode {passcode}"
    })
    result = response.json()
    if result.get("authenticated"):
        st.success(result.get("message"))
        authenticated = True
    else:
        st.error(result.get("message"))

if authenticated or st.session_state.get("authenticated"):
    st.session_state["authenticated"] = True
    st.success("Authenticated ✔")

    mode = st.radio("Choose Action", ["Send Note", "Query Memory"], horizontal=True)
    user_input = st.text_area("Your Input", height=150, placeholder="e.g. I updated the roadmap for Q3 goals")
    go = st.button("Submit")

    if go and user_input:
        action = "send" if mode == "Send Note" else "query"
        response = requests.post("https://3m9yprbn71.execute-api.ap-south-1.amazonaws.com/production/process", json={
            "user_id": user_id,
            "text": user_input
        })
        result = response.json()
        if result.get("status") == "success":
            st.success(result.get("message"))
            if result.get("action") == "query":
                st.write("### 📄 Result")
                st.markdown(result.get("result", "No result returned."))
        else:
            st.error(result.get("message"))
else:
    st.info("Please authenticate to begin.")
