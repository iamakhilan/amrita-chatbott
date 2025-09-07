
import streamlit as st
import requests
import os

# --------- Page Configuration ---------
st.set_page_config(
    page_title="Amrita College Chatbot",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 Amrita College, Coimbatore - AI Chatbot")
st.markdown(
    """
    Ask anything about **Amrita College**!  
    This chatbot uses **OpenRouter.ai** models to answer your questions.
    """
)

# --------- Sidebar Controls ---------
st.sidebar.header("⚙️ Settings")

# Model selector
model = st.sidebar.selectbox(
    "Choose a model:",
    ["gpt-4o-mini", "gpt-5-mini"]
)

# Temperature control
temperature = st.sidebar.slider("Creativity (temperature)", 0.0, 1.0, 0.7)

# Clear chat button
if st.sidebar.button("🗑️ Clear Chat"):
    st.session_state.chat_history = []

# --------- Preloaded Knowledge Base ---------
knowledge_base = """
Amrita Vishwa Vidyapeetham, Coimbatore campus, is a multidisciplinary university.
It offers programs in Engineering, Arts, Sciences, Business, and Medicine.
The university is accredited with A++ grade by NAAC.
Facilities include hostels, libraries, sports, research centers, and labs.
The Coimbatore campus is the main campus with over 800 acres.
Popular engineering programs: CSE, ECE, Mechanical, Civil, AI & Data Science.
Hostels are separate for boys and girls, with mess and Wi-Fi facilities.
Research focus areas: AI, Robotics, Biomedical, Renewable Energy.
Sports: Football, Basketball, Cricket, Frisbee, Tennis, Athletics.
Cultural activities: Music, Dance, Dramatics, Technical fests, Annual Day.
Contact: +91-422-2685000, coimbatore@amrita.edu
"""

# --------- Chat History State ---------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --------- Display Chat History (chat bubbles) ---------
for role, message in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(message)

# --------- User Input (modern chat input) ---------
user_input = st.chat_input("Ask a question about Amrita College:")

if user_input:
    # Save user message
    st.session_state.chat_history.append(("user", user_input))

    # Prepare full chat history for API
    messages = [{"role": "system", "content": "You are a helpful assistant for Amrita College, Coimbatore."}]
    for role, msg in st.session_state.chat_history:
        messages.append({"role": role, "content": msg})

    # --------- OpenRouter API Call ---------
    api_key = "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"  # Inserted user API key
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "temperature": temperature
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        answer = response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        answer = f"⚠️ Error: {e}"

    # Save bot response
    st.session_state.chat_history.append(("assistant", answer))

    # Display bot response as chat bubble
    with st.chat_message("assistant"):
        st.markdown(answer)
