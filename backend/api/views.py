from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Clinic, ChatSession, Appointment
from .serializers import ClinicSerializer, ChatSessionSerializer, AppointmentSerializer
from .triage import (
    detect_high_risk_trigger, 
    should_ask_followup, 
    run_triage, 
    get_triage_summary,
    get_initial_trigger_message,
    get_clinic_recommendation
)
from .ai_service import chat_with_ai, extract_symptoms_from_conversation, should_run_triage, extract_booking_info


@api_view(['POST'])
def triage_start(request):
    """
    POST /api/triage/start
    Start a new triage session
    
    Request: {}
    Response: {
        "session_id": 1,
        "message": "Hi! I'm here to help...",
        "status": "active"
    }
    """
    session = ChatSession.objects.create()
    
    welcome_message = "Hi! I'm here to help assess your symptoms. Please describe what you're experiencing. (You can use English or Tanglish - I understand both!)"
    
    session.messages.append({'role': 'assistant', 'content': welcome_message})
    session.save()
    
    return Response({
        'session_id': session.id,
        'message': welcome_message,
        'status': 'active'
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def triage_continue(request):
    """
    POST /api/triage/continue
    Continue triage conversation with proper risk assessment
    
    Request: {
        "session_id": 1,
        "message": "I have chest pain"
    }
    
    Response: {
        "session_id": 1,
        "message": "AI response or triage result",
        "triage_complete": false,
        "triage_result": null or {...},
        "needs_followup": bool,
        "followup_question": str or null
    }
    """
    session_id = request.data.get('session_id')
    user_message = request.data.get('message', '').strip()
    
    if not session_id or not user_message:
        return Response(
            {'error': 'session_id and message are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        session = ChatSession.objects.get(id=session_id)
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Add user message
    session.messages.append({'role': 'user', 'content': user_message})
    session.symptoms_collected.append(user_message)
    
    # Initialize session state if not exists
    if not hasattr(session, 'triage_state') or not session.triage_state:
        session.triage_state = {
            'trigger_detected': None,
            'followup_count': 0,
            'responses': []
        }
    
    # Check for high-risk trigger
    trigger_key, trigger_data = detect_high_risk_trigger(user_message)
    
    if trigger_key and not session.triage_state.get('trigger_detected'):
        # First detection of high-risk symptom
        session.triage_state['trigger_detected'] = trigger_key
        session.triage_state['followup_count'] = 0
        session.triage_state['responses'] = []
        
        # Send initial warning message (NOT emergency yet)
        initial_message = get_initial_trigger_message(trigger_key)
        
        session.messages.append({'role': 'assistant', 'content': initial_message})
        session.save()
        
        # Ask first follow-up question
        should_ask, question = should_ask_followup(session.triage_state)
        
        if should_ask:
            session.messages.append({'role': 'assistant', 'content': question})
            session.triage_state['followup_count'] += 1
            session.save()
            
            return Response({
                'session_id': session.id,
                'message': question,
                'triage_complete': False,
                'triage_result': None,
                'needs_followup': True,
                'trigger_warning': initial_message
            })
    
    # If we're in follow-up mode
    elif session.triage_state.get('trigger_detected'):
        # Store the response
        session.triage_state['responses'].append(user_message)
        
        # Check if we need more follow-ups
        should_ask, question = should_ask_followup(session.triage_state)
        
        if should_ask:
            # Ask next follow-up question
            session.messages.append({'role': 'assistant', 'content': question})
            session.triage_state['followup_count'] += 1
            session.save()
            
            return Response({
                'session_id': session.id,
                'message': question,
                'triage_complete': False,
                'triage_result': None,
                'needs_followup': True
            })
        else:
            # All follow-ups complete, run triage with risk assessment
            triage_result = run_triage(session.symptoms_collected, session.triage_state)
            session.triage_result = triage_result['triage_result']
            
            response_message = get_triage_summary(triage_result)
            
            if triage_result['care_level'] == 'CLINIC':
                response_message += "\n\nWould you like to book an appointment with a nearby clinic?"
            
            session.messages.append({'role': 'assistant', 'content': response_message})
            session.save()
            
            return Response({
                'session_id': session.id,
                'message': response_message,
                'triage_complete': True,
                'triage_result': triage_result,
                'needs_followup': False
            })
    
    # Count user messages
    message_count = len([m for m in session.messages if m['role'] == 'user'])
    
    # Check if we should run triage (for non-high-risk symptoms)
    if should_run_triage(message_count):
        # Run triage
        triage_result = run_triage(session.symptoms_collected, session.triage_state)
        session.triage_result = triage_result['triage_result']
        
        response_message = get_triage_summary(triage_result)
        
        if triage_result['care_level'] == 'CLINIC':
            response_message += "\n\nWould you like to book an appointment with a nearby clinic?"
        
        session.messages.append({'role': 'assistant', 'content': response_message})
        session.save()
        
        return Response({
            'session_id': session.id,
            'message': response_message,
            'triage_complete': True,
            'triage_result': triage_result,
            'needs_followup': False
        })
    
    else:
        # Continue conversation with AI
        ai_response = chat_with_ai(session.messages[:-1], user_message)
        
        session.messages.append({'role': 'assistant', 'content': ai_response})
        session.save()
        
        return Response({
            'session_id': session.id,
            'message': ai_response,
            'triage_complete': False,
            'triage_result': None,
            'needs_followup': False
        })


@api_view(['GET'])
def list_clinics(request):
    """
    GET /api/clinics
    Get list of available clinics
    
    Response: [
        {
            "id": 1,
            "name": "Downtown Health Clinic",
            "address": "123 Main St",
            "unique_code": "downtown"
        }
    ]
    """
    clinics = Clinic.objects.all()
    serializer = ClinicSerializer(clinics, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_clinic_by_id(request, clinic_id):
    """
    GET /api/clinics/{clinic_id}
    Get a specific clinic by ID
    
    Response: {
        "id": 1,
        "name": "Downtown Health Clinic",
        "address": "123 Main St",
        "phone": "555-1234",
        "unique_code": "downtown"
    }
    """
    try:
        clinic = Clinic.objects.get(id=clinic_id)
        serializer = ClinicSerializer(clinic)
        return Response(serializer.data)
    except Clinic.DoesNotExist:
        return Response(
            {'error': 'Clinic not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
def book_appointment(request):
    """
    POST /api/book-appointment
    Create a new appointment
    
    Request: {
        "clinic_id": 1,
        "patient_name": "John Doe",
        "patient_phone": "555-0123",
        "symptoms_summary": "Chest pain and fever",
        "urgency_level": "high",
        "preferred_time": "2026-01-10T14:00:00"
    }
    
    Response: {
        "id": 1,
        "clinic": 1,
        "clinic_name": "Downtown Health Clinic",
        "patient_name": "John Doe",
        "patient_phone": "555-0123",
        "symptoms_summary": "Chest pain and fever",
        "urgency_level": "high",
        "preferred_time": "2026-01-10T14:00:00",
        "status": "pending",
        "created_at": "2026-01-08T16:00:00"
    }
    """
    serializer = AppointmentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_clinic_bookings(request, clinic_id):
    """
    GET /api/clinic/{clinic_id}/bookings
    Get all bookings for a specific clinic
    
    Response: [
        {
            "id": 1,
            "patient_name": "John Doe",
            "patient_phone": "555-0123",
            "symptoms_summary": "Chest pain and fever",
            "urgency_level": "high",
            "preferred_time": "2026-01-10T14:00:00",
            "status": "pending",
            "created_at": "2026-01-08T16:00:00"
        }
    ]
    """
    try:
        clinic = Clinic.objects.get(id=clinic_id)
        appointments = clinic.appointments.all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    except Clinic.DoesNotExist:
        return Response(
            {'error': 'Clinic not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )


# Legacy endpoints for backward compatibility
@api_view(['POST'])
def start_chat(request):
    """Legacy endpoint - same as triage_start"""
    session = ChatSession.objects.create()
    
    welcome_message = "Hi! I'm your AI agent. I'm here to help assess your symptoms and book appointments. What brings you here today?"
    
    session.messages.append({'role': 'agent', 'content': welcome_message})
    session.save()
    
    serializer = ChatSessionSerializer(session)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
def send_message(request):
    """Legacy endpoint - updated to use new triage logic"""
    session_id = request.data.get('session_id')
    user_message = request.data.get('message', '').strip()
    
    if not session_id or not user_message:
        return Response(
            {'error': 'session_id and message are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        session = ChatSession.objects.get(id=session_id)
    except ChatSession.DoesNotExist:
        return Response(
            {'error': 'Session not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Add user message
    session.messages.append({'role': 'user', 'content': user_message})
    session.symptoms_collected.append(user_message)
    
    # Initialize session state if not exists
    if not session.triage_state:
        session.triage_state = {
            'trigger_detected': None,
            'followup_count': 0,
            'responses': []
        }
    
    # Check for high-risk trigger
    trigger_key, trigger_data = detect_high_risk_trigger(user_message)
    
    if trigger_key and not session.triage_state.get('trigger_detected'):
        # First detection of high-risk symptom
        session.triage_state['trigger_detected'] = trigger_key
        session.triage_state['followup_count'] = 0
        session.triage_state['responses'] = []
        
        # Send initial warning message (NOT emergency yet)
        initial_message = get_initial_trigger_message(trigger_key)
        
        session.messages.append({'role': 'assistant', 'content': initial_message})
        session.save()
        
        # Ask first follow-up question
        should_ask, question = should_ask_followup(session.triage_state)
        
        if should_ask:
            session.messages.append({'role': 'assistant', 'content': question})
            session.triage_state['followup_count'] += 1
            session.save()
            
            return Response({
                'message': question,
                'triage_result': None,
                'urgency_level': None,
                'should_triage': False,
                'needs_followup': True,
                'trigger_warning': initial_message,
                'session': ChatSessionSerializer(session).data
            })
    
    # If we're in follow-up mode
    elif session.triage_state.get('trigger_detected'):
        # Store the response
        session.triage_state['responses'].append(user_message)
        
        # Check if we need more follow-ups
        should_ask, question = should_ask_followup(session.triage_state)
        
        if should_ask:
            # Ask next follow-up question
            session.messages.append({'role': 'assistant', 'content': question})
            session.triage_state['followup_count'] += 1
            session.save()
            
            return Response({
                'message': question,
                'triage_result': None,
                'urgency_level': None,
                'should_triage': False,
                'needs_followup': True,
                'session': ChatSessionSerializer(session).data
            })
        else:
            # All follow-ups complete, run triage with risk assessment
            triage_result = run_triage(session.symptoms_collected, session.triage_state)
            session.triage_result = triage_result['triage_result']
            
            response_message = get_triage_summary(triage_result)
            
            # Get clinic recommendation based on symptoms
            all_symptoms = ' '.join(session.symptoms_collected)
            clinic_rec = get_clinic_recommendation(all_symptoms)
            
            if triage_result['care_level'] == 'CLINIC':
                response_message += "\n\nWould you like to book an appointment with a nearby clinic?"
            
            session.messages.append({'role': 'assistant', 'content': response_message})
            session.save()
            
            return Response({
                'message': response_message,
                'triage_result': triage_result['triage_result'],
                'triage_data': triage_result,
                'urgency_level': triage_result['urgency_level'],
                'should_triage': True,
                'clinic_recommendation': clinic_rec,
                'session': ChatSessionSerializer(session).data
            })
    
    # Count user messages
    message_count = len([m for m in session.messages if m['role'] == 'user'])
    
    # Check if user provided name and phone (booking completion) - CHECK THIS FIRST
    name, phone = extract_booking_info(user_message)
    
    if name and phone:
        # Booking info complete! Create appointment in session (not database for demo)
        import random
        booking_id = random.randint(1000, 9999)
        
        # Store in Django session (temporary)
        if not request.session.get('demo_bookings'):
            request.session['demo_bookings'] = []
        
        booking_data = {
            'id': booking_id,
            'patient_name': name,
            'patient_phone': phone,
            'symptoms': ' '.join(session.symptoms_collected),
            'date': 'Tomorrow',  # Simplified for demo
            'time': '10:00 AM',  # Simplified for demo
            'clinic_id': session_id  # Use session ID as placeholder
        }
        
        request.session['demo_bookings'].append(booking_data)
        request.session.modified = True
        
        # Send confirmation message
        confirmation_msg = f"✅ Appointment booked successfully!\n\nBooking ID: #{booking_id}\nPatient: {name}\nPhone: {phone}\nDate: Tomorrow\nTime: 10:00 AM\n\nThe clinic will call you to confirm. Thank you!"
        
        session.messages.append({'role': 'agent', 'content': confirmation_msg})
        session.save()
        
        return Response({
            'message': confirmation_msg,
            'triage_result': None,
            'urgency_level': None,
            'should_triage': False,
            'booking_confirmed': True,
            'booking_id': booking_id,
            'session': ChatSessionSerializer(session).data
        })
    
    # Check if we should run triage (for non-high-risk symptoms)
    if should_run_triage(message_count):
        # Run triage
        triage_result = run_triage(session.symptoms_collected, session.triage_state)
        session.triage_result = triage_result['triage_result']
        
        response_message = get_triage_summary(triage_result)
        
        if triage_result['care_level'] == 'CLINIC':
            # Instead of stopping, ask AI to continue with booking questions
            session.messages.append({'role': 'assistant', 'content': response_message})
            session.save()
            
            # Ask AI to transition to booking
            booking_prompt = "Now ask the patient when they would like to come in for an appointment. Ask about their preferred date and time."
            ai_response = chat_with_ai(session.messages, booking_prompt)
            
            session.messages.append({'role': 'assistant', 'content': ai_response})
            session.save()
            
            return Response({
                'message': ai_response,
                'triage_result': triage_result['triage_result'],
                'triage_data': triage_result,
                'urgency_level': triage_result['urgency_level'],
                'should_triage': True,
                'session': ChatSessionSerializer(session).data
            })
        else:
            # Emergency case
            session.messages.append({'role': 'assistant', 'content': response_message})
            session.save()
            
            return Response({
                'message': response_message,
                'triage_result': triage_result['triage_result'],
                'triage_data': triage_result,
                'urgency_level': triage_result['urgency_level'],
                'should_triage': True,
                'session': ChatSessionSerializer(session).data
            })
    
    else:
        # Continue conversation with AI
        try:
            # Get clinic context if available
            clinic_context = None
            if hasattr(session, 'clinic_id'):
                try:
                    clinic = Clinic.objects.get(id=session.clinic_id)
                    clinic_context = {'name': clinic.name}
                except:
                    pass
            
            ai_response = chat_with_ai(session.messages[:-1], user_message, clinic_context)
        except Exception as e:
            print(f"AI chat failed: {e}")
            ai_response = "I understand. Can you tell me more?"
        
        session.messages.append({'role': 'agent', 'content': ai_response})
        session.save()
        
        return Response({
            'message': ai_response,
            'triage_result': None,
            'urgency_level': None,
            'should_triage': False,
            'session': ChatSessionSerializer(session).data
        })


@api_view(['GET'])
def get_clinic_by_code(request, unique_code):
    """Get clinic by unique code"""
    try:
        clinic = Clinic.objects.get(unique_code=unique_code)
        serializer = ClinicSerializer(clinic)
        return Response(serializer.data)
    except Clinic.DoesNotExist:
        return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def get_clinic_appointments(request, unique_code):
    """Get all appointments for a clinic by unique code"""
    try:
        clinic = Clinic.objects.get(unique_code=unique_code)
        appointments = clinic.appointments.all()
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)
    except Clinic.DoesNotExist:
        return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)
