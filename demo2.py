
import os
import json
import urllib.request
import urllib.parse
import http.server
import socketserver
from urllib.parse import urlparse, parse_qs

# --------- Knowledge Base ---------
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

def get_ai_response(question, model="gpt-4o-mini", temperature=0.7):
    """Get AI response using OpenRouter API with urllib"""
    api_key = "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"
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": f"You are a helpful assistant for Amrita College, Coimbatore. Use this knowledge: {knowledge_base}"},
            {"role": "user", "content": question}
        ],
        "temperature": temperature
    }
    
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error: {str(e)}"

def simple_chatbot():
    """Simple command-line chatbot"""
    print("🎓 Amrita College, Coimbatore - AI Chatbot")
    print("Ask anything about Amrita College! (Type 'quit' to exit)")
    print("-" * 50)
    
    while True:
        question = input("\nYou: ").strip()
        
        if question.lower() in ['quit', 'exit', 'bye']:
            print("Goodbye!")
            break
        
        if not question:
            continue
        
        print("Bot: Thinking...")
        response = get_ai_response(question)
        print(f"Bot: {response}")

if __name__ == "__main__":
    simple_chatbot()
