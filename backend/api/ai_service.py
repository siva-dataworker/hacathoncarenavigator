"""
AI Service using OpenRouter API
Supports English and Tanglish (casual Tamil-English mix)
Acts as an intelligent agent, not a chatbot
"""

import openai
import re

# OpenRouter configuration
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# Clinic FAQ Knowledge Base
CLINIC_FAQ = {
    "doctor_timing": "Our doctors are available Monday to Saturday, 9 AM to 8 PM. Sunday appointments are available on request.",
    "trust": "We are a certified clinic with experienced doctors. All our doctors are licensed and have 10+ years of experience. We follow strict hygiene protocols.",
    "emergency": "For emergencies, please call 108 immediately. We handle non-emergency consultations and routine care.",
    "payment": "We accept cash, cards, UPI, and all major insurance plans. Consultation fees start from ₹300.",
    "location": "We are located in the city center with easy parking. You can find our exact location on Google Maps.",
    "services": "We provide general consultation, diagnostics, minor procedures, and health checkups. Specialized treatments are referred to partner hospitals."
}

SYSTEM_PROMPT = """You are an intelligent AI agent for a medical clinic. You help patients book appointments.

BOOKING FLOW:
1. User describes symptoms → Ask ONE follow-up question (e.g., "How long have you had this?")
2. User answers → Ask ONE more follow-up if needed (e.g., "Any other symptoms?")
3. After 2 follow-ups → Ask: "When would you like to come in?"
4. User gives timing → Ask: "What's your name and phone number?"
5. User gives name/phone → STOP (system confirms booking)

HANDLING QUESTIONS:
- Basic greetings (how are you, etc.) → Answer briefly and redirect to health concerns
- Clinic FAQs (timing, services, payment) → Answer directly
- Off-topic questions → Answer briefly once, then redirect if repeated

RULES:
- Keep responses to 1-2 sentences maximum
- Be professional, friendly, and helpful
- Accept Tanglish (Tamil-English mix)
- You are an AGENT, not an assistant or chatbot
- Ask questions one at a time, never multiple questions together

EXAMPLES:
User: "how r u"
You: "I'm doing well, thank you! Do you have any health concerns I can help with?"

User: "when is doctor available"
You: "Our doctors are available Monday to Saturday, 9 AM to 8 PM."

User: "I have fever"
You: "How long have you had the fever?"
"""


def chat_with_ai(conversation_history, user_message, clinic_context=None):
    """
    Send message to OpenRouter AI and get response
    
    Args:
        conversation_history: List of previous messages
        user_message: Current user message
        clinic_context: Optional clinic information
    
    Returns:
        AI response text
    """
    try:
        # Check if message is FAQ-related first (pass history to avoid repeating)
        faq_response = check_faq(user_message, conversation_history)
        if faq_response:
            return faq_response
        
        # Check for off-topic questions
        off_topic_count = count_off_topic_questions(conversation_history, user_message)
        if off_topic_count >= 2:
            return "I'm here to help with appointments and clinic-related queries. Do you have any health concerns I can assist with?"
        
        # Build system prompt
        system_prompt = SYSTEM_PROMPT
        if clinic_context:
            system_prompt += f"\n\nClinic: {clinic_context.get('name', 'Our Clinic')}"
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (convert 'agent' role to 'assistant' for API)
        for msg in conversation_history:
            role = msg["role"]
            if role == "agent":
                role = "assistant"
            messages.append({
                "role": role,
                "content": msg["content"]
            })
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        print(f"Sending to AI: {len(messages)} messages")  # Debug
        
        # Call OpenRouter API (old style)
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=messages,
            temperature=0.7,
            max_tokens=80
        )
        
        ai_response = response.choices[0].message.content.strip()
        print(f"AI Response: {ai_response}")  # Debug
        
        return ai_response
    
    except Exception as e:
        print(f"AI Service Error: {e}")
        import traceback
        traceback.print_exc()
        # Return a more helpful fallback
        return "Could you tell me more about what you're experiencing?"


def count_off_topic_questions(conversation_history, current_message):
    """
    Count how many off-topic (non-medical, non-clinic) questions user has asked
    
    Args:
        conversation_history: List of previous messages
        current_message: Current user message
    
    Returns:
        Number of off-topic questions
    """
    off_topic_keywords = [
        'how are you', 'how r u', 'what is your name', 'who are you',
        'tell me about yourself', 'where are you from', 'what do you do',
        'are you real', 'are you human', 'weather', 'news', 'politics',
        'sports', 'movie', 'food', 'recipe', 'joke', 'story'
    ]
    
    # Medical/clinic related keywords
    medical_keywords = [
        'symptom', 'pain', 'fever', 'cough', 'cold', 'sick', 'hurt',
        'doctor', 'appointment', 'clinic', 'hospital', 'medicine',
        'treatment', 'health', 'medical', 'disease', 'injury'
    ]
    
    count = 0
    
    # Check conversation history
    for msg in conversation_history:
        if msg['role'] == 'user':
            msg_lower = msg['content'].lower()
            # Check if it's off-topic
            is_off_topic = any(keyword in msg_lower for keyword in off_topic_keywords)
            is_medical = any(keyword in msg_lower for keyword in medical_keywords)
            
            if is_off_topic and not is_medical:
                count += 1
    
    # Check current message
    current_lower = current_message.lower()
    is_off_topic = any(keyword in current_lower for keyword in off_topic_keywords)
    is_medical = any(keyword in current_lower for keyword in medical_keywords)
    
    if is_off_topic and not is_medical:
        count += 1
    
    return count


def check_faq(message, conversation_history=None):
    """
    Check if message is asking a FAQ question and return answer
    Only return FAQ if it hasn't been answered recently
    
    Args:
        message: User message
        conversation_history: List of previous messages (optional)
    
    Returns:
        FAQ answer or None
    """
    message_lower = message.lower()
    
    # Check if this FAQ was already answered in last 3 messages
    if conversation_history:
        recent_messages = conversation_history[-3:] if len(conversation_history) > 3 else conversation_history
        for msg in recent_messages:
            if msg.get('role') == 'agent' or msg.get('role') == 'assistant':
                # Check if any FAQ answer was already given
                for faq_answer in CLINIC_FAQ.values():
                    if faq_answer in msg.get('content', ''):
                        # FAQ already answered recently, don't repeat
                        return None
    
    # Doctor timing questions - be more specific
    timing_keywords = ['when', 'what time', 'timing', 'hours', 'schedule', 'open', 'close']
    doctor_keywords = ['doctor', 'physician', 'clinic']
    if any(tk in message_lower for tk in timing_keywords) and any(dk in message_lower for dk in doctor_keywords):
        return CLINIC_FAQ['doctor_timing']
    
    # Trust/credibility questions
    if any(word in message_lower for word in ['trust', 'certified', 'qualified', 'experience', 'licensed', 'why should']):
        return CLINIC_FAQ['trust']
    
    # Emergency questions
    if any(word in message_lower for word in ['emergency', 'urgent', 'critical', '108', '112']):
        return CLINIC_FAQ['emergency']
    
    # Payment questions
    if any(word in message_lower for word in ['payment', 'cost', 'fee', 'price', 'insurance', 'accept', 'charge']):
        return CLINIC_FAQ['payment']
    
    # Location questions
    if any(word in message_lower for word in ['location', 'address', 'where', 'parking', 'map', 'directions']):
        return CLINIC_FAQ['location']
    
    # Services questions
    if any(word in message_lower for word in ['service', 'treatment', 'provide', 'offer', 'do you have', 'what do you']):
        return CLINIC_FAQ['services']
    
    return None


def count_followup_questions(messages):
    """
    Count how many follow-up questions the agent has asked about symptoms
    
    Args:
        messages: List of conversation messages
    
    Returns:
        Number of follow-up questions asked
    """
    count = 0
    user_mentioned_symptoms = False
    
    for msg in messages:
        if msg['role'] == 'user' and not user_mentioned_symptoms:
            # First user message with symptoms
            user_mentioned_symptoms = True
        elif msg['role'] == 'assistant' and user_mentioned_symptoms:
            # Count questions after symptoms mentioned
            if '?' in msg['content'] and not any(word in msg['content'].lower() for word in ['when would you', 'name and phone', 'what\'s your name']):
                count += 1
    
    return count


def extract_symptoms_from_conversation(messages):
    """
    Use AI to extract key symptoms from conversation
    
    Args:
        messages: List of conversation messages
    
    Returns:
        List of extracted symptoms
    """
    try:
        # Build conversation text
        conversation_text = "\n".join([
            f"{msg['role']}: {msg['content']}" 
            for msg in messages if msg['role'] == 'user'
        ])
        
        # Ask AI to extract symptoms
        extraction_prompt = f"""Extract ONLY the medical symptoms from this conversation. 
List them as simple keywords (e.g., "chest pain", "fever", "rash").

Conversation:
{conversation_text}

Symptoms (comma-separated):"""
        
        response = openai.ChatCompletion.create(
            model="openai/gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You extract medical symptoms from text."},
                {"role": "user", "content": extraction_prompt}
            ],
            temperature=0.3,
            max_tokens=100
        )
        
        symptoms_text = response.choices[0].message.content.strip()
        symptoms = [s.strip() for s in symptoms_text.split(',') if s.strip()]
        
        return symptoms
    
    except Exception as e:
        print(f"Symptom Extraction Error: {e}")
        # Fallback: extract from user messages
        return [msg['content'] for msg in messages if msg['role'] == 'user']


def should_run_triage(message_count):
    """
    Decide if we should run triage based on message count
    """
    return message_count >= 5  # Increased from 3 to 5 to allow booking flow


def extract_booking_info(message):
    """
    Extract name and phone from user message
    Returns: (name, phone) or (None, None)
    """
    import re
    
    # Look for phone number (10 digits, may have spaces or dashes)
    phone_match = re.search(r'\b\d[\d\s-]{8,}\d\b', message)
    
    if phone_match:
        # Clean phone number (remove spaces and dashes)
        phone = re.sub(r'[\s-]', '', phone_match.group())
        
        # Only accept if it's exactly 10 digits
        if len(phone) == 10:
            # Extract name (words before or after phone, excluding common filler words)
            text_without_phone = message.replace(phone_match.group(), '').strip()
            words = text_without_phone.split()
            
            # Filter out common words
            stop_words = ['and', 'is', 'my', 'name', 'phone', 'number', 'the', 'a', 'an', 'i', 'am']
            name_words = [w for w in words if w.lower() not in stop_words and not w.isdigit()]
            
            # Take first 1-2 words as name
            if name_words:
                name = ' '.join(name_words[:2])
                return (name.strip().title(), phone)
    
    return (None, None)
