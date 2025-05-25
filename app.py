import streamlit as st
from urllib.parse import urlencode
import requests

# Load secrets from .streamlit/secrets.toml
API_URL = st.secrets["API_URL"]
CLIENT_ID = st.secrets["CLIENT_ID"]
COGNITO_DOMAIN = st.secrets["COGNITO_DOMAIN"]
REDIRECT_URI = st.secrets["REDIRECT_URI"]

st.set_page_config(page_title="OWASP Top 10 Assistant", layout="centered")
st.title("🔐 OWASP Top 10 Secure Coding Assistant")

# Construct OAuth2 authorization URL
auth_url = (
    f"https://{COGNITO_DOMAIN}/oauth2/authorize?" +
    urlencode({
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": "openid email"
    })
)

# Step 1: Prompt user to log in
if "access_token" not in st.session_state:
    st.markdown(f"[🔐 Login with Cognito]({auth_url})")

    # If redirected back with code, exchange for tokens
    query_params = st.experimental_get_query_params()
    if "code" in query_params:
        code = query_params["code"][0]
        token_url = f"https://{COGNITO_DOMAIN}/oauth2/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = {
            "grant_type": "authorization_code",
            "client_id": CLIENT_ID,
            "code": code,
            "redirect_uri": REDIRECT_URI
        }

        response = requests.post(token_url, headers=headers, data=data)
        if response.status_code == 200:
            tokens = response.json()
            st.session_state["access_token"] = tokens["id_token"]
            st.experimental_rerun()
        else:
            st.error("Login failed.")
else:
    st.success("✅ Logged in successfully")
    st.markdown("Ask me anything about the **OWASP Top 10** vulnerabilities!")

    # Step 2: Ask question
    question = st.text_input("📝 Your question")

    if st.button("Submit") and question:
        headers = {
            "Authorization": f"Bearer {st.session_state['access_token']}",
            "Content-Type": "application/json"
        }
        payload = {"input": question}

        res = requests.post(API_URL, json=payload, headers=headers)

        if res.status_code == 200:
            result = res.json().get("output", "No output received.")
            st.markdown("### 🧠 Response:")
            st.markdown(f"> {result}")
        else:
            st.error("Failed to get a response from the backend.")
            st.text(res.text)

    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.experimental_rerun()
