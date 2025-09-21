import streamlit as st
import requests
import os
import time
from datetime import datetime
from typing import Dict, List, Tuple
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Load environment variables from .env file

# Page configuration
st.set_page_config(
    page_title="Amrita College AI Chatbot",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://amrita.edu/contact',
        'Report a bug': None,
        'About': "AI-powered chatbot for Amrita College, Coimbatore"
    }
)

# API Configuration
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
FIXED_MODEL = "openai/gpt-4o-mini"
FIXED_TEMPERATURE = 0.7

# Enhanced Knowledge Base
KNOWLEDGE_BASE = """
AMRITA VISHWA VIDYAPEETHAM - COIMBATORE CAMPUS

🏛️ UNIVERSITY OVERVIEW:
- Established: 2003, A++ NAAC accredited multidisciplinary university
- Campus Size: 400+ acres, main campus of Amrita Vishwa Vidyapeetham
- Location: Ettimadai, Coimbatore, Tamil Nadu, India
- University Type: Private, Deemed-to-be University status

🎓 ACADEMIC PROGRAMS:
Engineering: CSE, ECE, Mechanical, Civil, Aerospace, AI & Data Science, Cybersecurity
Sciences: Physics, Chemistry, Mathematics, Biotechnology, Microbiology
Business: MBA, BBA with various specializations
Arts & Humanities: English, Psychology, Social Work
Medicine: MBBS, Nursing, Physiotherapy, Allied Health Sciences

🏠 CAMPUS FACILITIES:
- Separate hostels for boys and girls with 24/7 security
- Central library with 2+ lakh books and digital resources
- State-of-the-art laboratories and research centers
- Sports complex: Cricket, Football, Basketball, Tennis, Swimming
- Medical center with qualified doctors and ambulance service
- Banking and ATM facilities on campus

🔬 RESEARCH & INNOVATION:
- Centers of Excellence in AI, Robotics, Cybersecurity
- Live-in-Labs® program for rural development
- International collaborations with top universities
- Patent filing and technology transfer support
- Student research opportunities from undergraduate level

🎭 STUDENT LIFE:
- Cultural festivals: Anokha (technical), Shristi (cultural)
- 100+ student clubs and organizations
- Sports teams competing at national level
- International exchange programs
- Placement assistance with 90%+ placement rate

📞 CONTACT INFORMATION:
- Phone: +91-422-2685000
- Email: coimbatore@amrita.edu
- Website: www.amrita.edu
- Address: Amrita Vishwa Vidyapeetham, Ettimadai, Coimbatore - 641112
"""

# =========================================================================
# UTILITY FUNCTIONS
# =========================================================================

def initialize_session_state() -> None:
    """Initialize all session state variables with default values."""
    default_states = {
        'chat_history': [],
        'conversation_id': f"conv_{int(time.time())}",
        'total_tokens_used': 0,
        'chat_started': False
    }
    
    for key, default_value in default_states.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def get_api_key() -> str:
    return st.secrets["API_KEY"]

def validate_api_key(api_key: str) -> bool:
    if not api_key:
        return False
    return api_key.startswith('sk-or-v1-') and len(api_key) > 20

def format_chat_message(role: str, content: str, timestamp: str = None) -> Dict:
    return {
        'role': role,
        'content': content,
        'timestamp': timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'conversation_id': st.session_state.conversation_id
    }

def make_api_request(messages: List[Dict], api_key: str) -> Tuple[str, bool]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Amrita College Chatbot"
    }
    
    payload = {
        "model": FIXED_MODEL,
        "messages": messages,
        "temperature": FIXED_TEMPERATURE,
        "max_tokens": 1000,
        "stream": False
    }
    
    try:
        with st.spinner("🤔 Thinking..."):
            response = requests.post(
                OPENROUTER_BASE_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            
            if 'choices' not in result or not result['choices']:
                return "❌ No response received from the AI model.", False
            
            content = result['choices'][0]['message']['content']
            
            # Update token usage if available
            if 'usage' in result:
                st.session_state.total_tokens_used += result['usage'].get('total_tokens', 0)
            
            return content, True
            
    except requests.exceptions.Timeout:
        return "⏰ Request timed out. Please try again.", False
    except requests.exceptions.ConnectionError:
        return "🌐 Connection error. Please check your internet connection.", False
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            return "🔑 Invalid API key. Please check your API key configuration.", False
        elif response.status_code == 429:
            return "⚠️ Rate limit exceeded. Please wait a moment and try again.", False
        else:
            return f"❌ HTTP Error {response.status_code}: {str(e)}", False
    except Exception as e:
        logger.error(f"API request failed: {str(e)}")
        return f"❌ Unexpected error: {str(e)}", False

def display_typing_animation():
    placeholder = st.empty()
    for i in range(3):
        placeholder.markdown("🤖 Assistant is typing" + "." * (i + 1))
        time.sleep(0.3)
    placeholder.empty()

# =========================================================================
# UI COMPONENTS
# =========================================================================

def render_header():
    """Render the application header with styling."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="color: #FF6B35; margin-bottom: 0;">🎓 Amrita College AI Chatbot</h1>
        <p style="color: #666; font-size: 1.1em; margin-top: 0.5rem;">
            Your intelligent assistant for Amrita Vishwa Vidyapeetham, Coimbatore
        </p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with simplified controls."""
    st.sidebar.markdown("## ⚙️ Chat Controls")
    
    # Clear chat button
    if st.sidebar.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.conversation_id = f"conv_{int(time.time())}"
        st.rerun()
    
    # New session button
    if st.sidebar.button("🔄 New Session", use_container_width=True):
        for key in ['chat_history', 'total_tokens_used', 'chat_started']:
            if key in st.session_state:
                if key == 'chat_history':
                    st.session_state[key] = []
                elif key == 'total_tokens_used':
                    st.session_state[key] = 0
                elif key == 'chat_started':
                    st.session_state[key] = False
        st.session_state.conversation_id = f"conv_{int(time.time())}"
        st.rerun()
    
    st.sidebar.markdown("---")
    
    # Statistics
    st.sidebar.markdown("### 📊 Session Stats")
    st.sidebar.metric("Messages Sent", len([m for m in st.session_state.chat_history if m['role'] == 'user']))
    st.sidebar.metric("AI Responses", len([m for m in st.session_state.chat_history if m['role'] == 'assistant']))
    if st.session_state.total_tokens_used > 0:
        st.sidebar.metric("Tokens Used", f"{st.session_state.total_tokens_used:,}")

def render_chat_interface():
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message['role']):
            st.markdown(message['content'])
            if 'timestamp' in message:
                st.caption(f"🕒 {message['timestamp']}")

def render_welcome_message():
    """Render welcome message for new users."""
    if not st.session_state.chat_started and not st.session_state.chat_history:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 10px; color: white; margin: 1rem 0;">
            <h3 style="margin-top: 0; color: white;">👋 Welcome to Amrita College AI Chatbot!</h3>
            <p style="margin-bottom: 0;">
                I'm here to help you with information about Amrita Vishwa Vidyapeetham, Coimbatore.
                Ask me anything about academics, campus life, facilities, admissions, or student services!
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Suggested questions
        st.markdown("**💡 Try asking me about:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎓 Academic Programs", use_container_width=True):
                st.session_state.suggested_question = "What academic programs are available at Amrita College?"
        
        with col2:
            if st.button("🏠 Campus Facilities", use_container_width=True):
                st.session_state.suggested_question = "Tell me about the campus facilities and hostels"
        
        with col3:
            if st.button("📞 Contact Information", use_container_width=True):
                st.session_state.suggested_question = "How can I contact Amrita College?"

# =========================================================================
# MAIN APPLICATION
# =========================================================================

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Get API key from environment
    
    api_key = get_api_key()
    st.sidebar.write(f"🔍 API key loaded: {api_key[:8]}...")

    # Check if API key is available and valid
    if not api_key or not validate_api_key(api_key):
        st.error("🔑 API key not found or invalid. Please ensure API_KEY is set in your environment variables.")
        st.info("Expected format: API_KEY=sk-or-v1-...")
        return
    
    # Render sidebar
    render_sidebar()
    
    # Render welcome message for new users
    render_welcome_message()
    
    # Render chat interface
    render_chat_interface()
    
    # Handle suggested questions
    user_input = None
    if hasattr(st.session_state, 'suggested_question'):
        user_input = st.session_state.suggested_question
        delattr(st.session_state, 'suggested_question')
    
    # Chat input
    if not user_input:
        user_input = st.chat_input("Ask me anything about Amrita College...")
    
    # Process user input
    if user_input:
        st.session_state.chat_started = True
        
        # Add user message to history
        user_message = format_chat_message('user', user_input)
        st.session_state.chat_history.append(user_message)
        
        # Display user message
        with st.chat_message('user'):
            st.markdown(user_input)
            st.caption(f"🕒 {user_message['timestamp']}")
        
        # Prepare messages for API
        system_message = {
            "role": "system",
            "content": f"""You are a helpful and knowledgeable assistant for Amrita Vishwa Vidyapeetham, Coimbatore campus. 
            
Use this knowledge base to answer questions accurately:
{KNOWLEDGE_BASE}

Guidelines:
- Be friendly, helpful, and informative
- Provide specific details when available
- If you don't know something specific, say so and suggest contacting the college directly
- Use emojis appropriately to make responses engaging
- Keep responses concise but comprehensive
- Always maintain a positive and welcoming tone"""
        }
        
        api_messages = [system_message]
        for msg in st.session_state.chat_history:
            api_messages.append({
                "role": msg['role'],
                "content": msg['content']
            })
        
        # Make API request
        response_content, success = make_api_request(api_messages, api_key)
        
        # Add assistant response to history
        assistant_message = format_chat_message('assistant', response_content)
        st.session_state.chat_history.append(assistant_message)
        
        # Display assistant response with typing effect
        if success:
            display_typing_animation()
        
        with st.chat_message('assistant'):
            st.markdown(response_content)
            st.caption(f"🕒 {assistant_message['timestamp']}")
        
        # Auto-rerun to update the interface
        st.rerun()

# =========================================================================
# APPLICATION ENTRY POINT
# =========================================================================

if __name__ == "__main__":

    main()


