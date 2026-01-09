"""
Rule-based Symptom Triage Engine with Risk Assessment
Uses multi-step questioning and risk scoring, NOT keyword-based diagnosis
"""

# High-risk symptom triggers (require follow-up, NOT immediate emergency)
HIGH_RISK_TRIGGERS = {
    'chest_pain': {
        'keywords': ['chest pain', 'chest pressure', 'chest tightness', 'chest discomfort'],
        'initial_message': 'Chest pain can have different causes. I need to ask a few quick questions to ensure your safety.',
        'questions': [
            "Are you feeling breathless or having difficulty breathing right now?",
            "Is the pain severe or crushing (like pressure on your chest)?",
            "Is the pain spreading to your left arm, jaw, neck, or back?",
            "Are you sweating, dizzy, or feeling nauseous?",
            "Has this pain lasted more than 20 minutes?"
        ],
        'risk_weights': {
            'base': 3,  # Base score for chest pain
            'breathless': 3,
            'severe_crushing': 3,
            'radiating': 3,
            'sweating_dizzy': 2,
            'duration_long': 2
        }
    },
    'breathing_difficulty': {
        'keywords': ['shortness of breath', 'short of breath', 'cant breathe', "can't breathe", 
                     'difficulty breathing', 'hard to breathe', 'gasping'],
        'initial_message': 'Breathing difficulty needs careful assessment. Let me ask a few important questions.',
        'questions': [
            "Is your breathing getting worse rapidly?",
            "Are your lips or fingernails turning blue?",
            "Are you unable to speak in full sentences?",
            "Do you have chest pain along with the breathing difficulty?",
            "Do you have a history of asthma or heart problems?"
        ],
        'risk_weights': {
            'base': 3,
            'worsening': 3,
            'blue_lips': 4,
            'cant_speak': 3,
            'chest_pain': 3,
            'history': 1
        }
    },
    'severe_bleeding': {
        'keywords': ['severe bleeding', 'heavy bleeding', 'uncontrolled bleeding', 'blood loss', 'bleeding heavily'],
        'initial_message': 'Bleeding needs immediate assessment. Please answer these questions.',
        'questions': [
            "Is the bleeding continuous and not stopping with pressure?",
            "Are you feeling dizzy or lightheaded?",
            "Is the blood spurting or pulsing out?",
            "Have you lost a significant amount of blood?",
            "Is the wound deep or large?"
        ],
        'risk_weights': {
            'base': 4,
            'continuous': 3,
            'dizzy': 2,
            'spurting': 4,
            'significant_loss': 3,
            'deep_wound': 2
        }
    }
}

# Routine symptoms (lower risk)
ROUTINE_SYMPTOMS = {
    'keywords': ['rash', 'skin rash', 'itching', 'itchy', 'itch', 'mild fever', 'low fever',
                 'headache', 'cough', 'cold', 'sore throat', 'runny nose', 'congestion'],
    'care_level': 'CLINIC',
    'urgency': 'medium'
}

# Risk scoring thresholds
RISK_THRESHOLDS = {
    'emergency': 6,  # Score >= 6 → Emergency
    'urgent': 3      # Score 3-5 → Urgent clinic, Score < 3 → Routine
}

DISCLAIMER = "This is not a medical diagnosis. This is a safety assessment tool. If you feel your condition is worsening or life-threatening, call 108 or 112 immediately."

# Clinic recommendations based on symptoms
CLINIC_RECOMMENDATIONS = {
    'fever': {
        'keywords': ['fever', 'high temperature', 'temperature', 'hot', 'burning up'],
        'recommended_clinics': [6, 7],  # Both clinics have General Medicine
        'reason': 'General Medicine specialists who can diagnose and treat fever-related conditions',
        'specialty': 'General Medicine'
    },
    'heart': {
        'keywords': ['chest pain', 'heart', 'cardiac', 'palpitation', 'irregular heartbeat'],
        'recommended_clinics': [6, 7],  # Both have Cardiology
        'reason': 'Cardiology specialists for heart-related concerns',
        'specialty': 'Cardiology'
    },
    'child': {
        'keywords': ['child', 'baby', 'infant', 'kid', 'toddler', 'pediatric'],
        'recommended_clinics': [6],  # Apollo has Pediatrics
        'reason': 'Pediatric specialists for children\'s healthcare',
        'specialty': 'Pediatrics'
    },
    'emergency': {
        'keywords': ['emergency', 'urgent', 'severe', 'critical'],
        'recommended_clinics': [7],  # Fortis has 24/7 Emergency
        'reason': '24/7 Emergency Care available',
        'specialty': 'Emergency Care'
    },
    'orthopedic': {
        'keywords': ['bone', 'fracture', 'joint pain', 'back pain', 'neck pain', 'sprain'],
        'recommended_clinics': [7],  # Fortis has Orthopedics
        'reason': 'Orthopedic specialists for bone and joint issues',
        'specialty': 'Orthopedics'
    },
    'general': {
        'keywords': ['general', 'checkup', 'consultation', 'routine'],
        'recommended_clinics': [6, 7],  # Both have General Medicine
        'reason': 'General physicians for routine checkups and consultations',
        'specialty': 'General Medicine'
    }
}


def get_clinic_recommendation(symptoms_text):
    """
    Recommend clinics based on symptoms
    Returns: dict with recommended_clinics, reason, specialty
    """
    symptoms_lower = symptoms_text.lower()
    
    # Check each recommendation category
    for category, data in CLINIC_RECOMMENDATIONS.items():
        for keyword in data['keywords']:
            if keyword in symptoms_lower:
                return {
                    'recommended_clinics': data['recommended_clinics'],
                    'reason': data['reason'],
                    'specialty': data['specialty'],
                    'category': category
                }
    
    # Default: recommend all clinics for general consultation
    return {
        'recommended_clinics': [6, 7],
        'reason': 'General consultation and healthcare services',
        'specialty': 'General Medicine',
        'category': 'general'
    }


def detect_high_risk_trigger(symptoms_text):
    """
    Detect if symptoms contain high-risk triggers that need follow-up
    Returns: (trigger_key, trigger_data) or (None, None)
    """
    symptoms_lower = symptoms_text.lower()
    
    for trigger_key, trigger_data in HIGH_RISK_TRIGGERS.items():
        for keyword in trigger_data['keywords']:
            if keyword in symptoms_lower:
                return trigger_key, trigger_data
    
    return None, None


def detect_routine_symptoms(symptoms_text):
    """
    Check if symptoms are routine/non-urgent
    """
    symptoms_lower = symptoms_text.lower()
    
    for keyword in ROUTINE_SYMPTOMS['keywords']:
        if keyword in symptoms_lower:
            return True
    
    return False


def calculate_risk_score(trigger_key, responses):
    """
    Calculate risk score based on follow-up responses
    
    Args:
        trigger_key: The high-risk trigger (e.g., 'chest_pain')
        responses: List of user responses to follow-up questions
    
    Returns:
        int: Risk score
    """
    if trigger_key not in HIGH_RISK_TRIGGERS:
        return 0
    
    weights = HIGH_RISK_TRIGGERS[trigger_key]['risk_weights']
    score = weights['base']  # Start with base score
    
    # Analyze responses for risk indicators
    all_responses = ' '.join(responses).lower()
    
    # Positive indicators (increase risk)
    positive_indicators = {
        'yes': 2,
        'yeah': 2,
        'yep': 2,
        'severe': 2,
        'intense': 2,
        'very': 1,
        'getting worse': 2,
        'worsening': 2,
        'spreading': 2,
        'unbearable': 3,
        'crushing': 3,
        'cant': 2,
        "can't": 2,
        'unable': 2,
        'more than': 1
    }
    
    for indicator, weight in positive_indicators.items():
        if indicator in all_responses:
            score += weight
    
    # Negative indicators (decrease risk)
    negative_indicators = {
        'no': -1,
        'nope': -1,
        'not': -1,
        'mild': -1,
        'slight': -1,
        'better': -2,
        'improving': -2
    }
    
    for indicator, weight in negative_indicators.items():
        if indicator in all_responses:
            score += weight
    
    # Ensure score doesn't go below base
    return max(score, weights['base'])


def should_ask_followup(session_state):
    """
    Determine if we should ask follow-up questions
    
    Args:
        session_state: Dict containing:
            - trigger_detected: str or None
            - followup_count: int
            - responses: list
    
    Returns:
        bool, str: (should_ask, question_text or None)
    """
    trigger = session_state.get('trigger_detected')
    count = session_state.get('followup_count', 0)
    
    if not trigger or trigger not in HIGH_RISK_TRIGGERS:
        return False, None
    
    questions = HIGH_RISK_TRIGGERS[trigger]['questions']
    
    if count < len(questions):
        return True, questions[count]
    
    return False, None


def run_triage(symptoms_collected, session_state=None):
    """
    Main triage function with risk assessment
    
    Args:
        symptoms_collected: List of symptom descriptions
        session_state: Dict with trigger_detected, followup_count, responses
    
    Returns: {
        'care_level': 'EMERGENCY' or 'CLINIC',
        'reason': str,
        'disclaimer': str,
        'next_step': str,
        'urgency_level': 'high' | 'medium' | 'low',
        'risk_score': int,
        'triage_result': str
    }
    """
    if not session_state:
        session_state = {
            'trigger_detected': None,
            'followup_count': 0,
            'responses': []
        }
    
    all_symptoms = ' '.join(symptoms_collected)
    
    # Check if high-risk trigger detected
    trigger_key, trigger_data = detect_high_risk_trigger(all_symptoms)
    
    if trigger_key:
        # Calculate risk score from follow-up responses
        risk_score = calculate_risk_score(trigger_key, session_state.get('responses', []))
        
        # Emergency decision based on risk score
        if risk_score >= RISK_THRESHOLDS['emergency']:
            return {
                'care_level': 'EMERGENCY',
                'reason': 'Based on your symptoms and responses, you may be experiencing a medical emergency',
                'disclaimer': DISCLAIMER,
                'next_step': 'Call 108 (Medical Emergency) or 112 (Unified Emergency) immediately, or go to the nearest emergency room',
                'urgency_level': 'high',
                'risk_score': risk_score,
                'triage_result': 'emergency',
                'emergency_numbers': ['108', '102', '112']
            }
        
        # Urgent clinic visit
        elif risk_score >= RISK_THRESHOLDS['urgent']:
            return {
                'care_level': 'CLINIC',
                'reason': 'Your symptoms require prompt medical evaluation',
                'disclaimer': DISCLAIMER,
                'next_step': 'Schedule an appointment with a healthcare provider within 24 hours. If symptoms worsen, call 108.',
                'urgency_level': 'high',
                'risk_score': risk_score,
                'triage_result': 'clinic'
            }
        
        # Lower risk, routine clinic
        else:
            return {
                'care_level': 'CLINIC',
                'reason': 'Your symptoms should be evaluated by a healthcare professional',
                'disclaimer': DISCLAIMER,
                'next_step': 'Schedule an appointment with a healthcare provider within the next few days',
                'urgency_level': 'medium',
                'risk_score': risk_score,
                'triage_result': 'clinic'
            }
    
    # Routine symptoms
    elif detect_routine_symptoms(all_symptoms):
        return {
            'care_level': 'CLINIC',
            'reason': 'Your symptoms suggest a condition that can be evaluated at a clinic',
            'disclaimer': DISCLAIMER,
            'next_step': 'Schedule an appointment with a healthcare provider',
            'urgency_level': 'low',
            'risk_score': 0,
            'triage_result': 'clinic'
        }
    
    # Unknown symptoms - default to clinic
    else:
        return {
            'care_level': 'CLINIC',
            'reason': 'Your symptoms require professional evaluation',
            'disclaimer': DISCLAIMER,
            'next_step': 'Schedule an appointment with a healthcare provider to discuss your symptoms',
            'urgency_level': 'medium',
            'risk_score': 0,
            'triage_result': 'clinic'
        }


def get_triage_summary(triage_result):
    """
    Generate a human-readable summary of the triage decision
    """
    care_level = triage_result['care_level']
    
    if care_level == 'EMERGENCY':
        emoji = '🚨'
        header = 'EMERGENCY - IMMEDIATE ATTENTION REQUIRED'
    else:
        urgency_emojis = {'high': '⚠️', 'medium': '📋', 'low': '✅'}
        emoji = urgency_emojis.get(triage_result['urgency_level'], '📋')
        header = f"CLINIC VISIT RECOMMENDED ({triage_result['urgency_level'].upper()} PRIORITY)"
    
    summary = f"{emoji} {header}\n\n"
    summary += f"Assessment: {triage_result['reason']}\n\n"
    summary += f"Recommended Action: {triage_result['next_step']}\n\n"
    
    if 'risk_score' in triage_result and triage_result['risk_score'] > 0:
        summary += f"Risk Assessment Score: {triage_result['risk_score']}\n\n"
    
    summary += f"⚠️ {triage_result['disclaimer']}"
    
    return summary


def get_initial_trigger_message(trigger_key):
    """
    Get the initial message when a high-risk trigger is detected
    """
    if trigger_key in HIGH_RISK_TRIGGERS:
        return HIGH_RISK_TRIGGERS[trigger_key]['initial_message']
    return None
