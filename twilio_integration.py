"""
Twilio integration for voice pipeline
Handles incoming calls and processes them through the voice pipeline
"""

import asyncio
import os
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
import aiohttp
from dotenv import load_dotenv
from voice_pipeline import process_audio

load_dotenv()

app = Flask(__name__)

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

# Initialize Twilio client
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


async def process_audio_with_pipeline(audio_url, language="auto"):
    """Process audio through voice pipeline"""
    
    # Download audio from Twilio
    async with aiohttp.ClientSession() as session:
        async with session.get(audio_url, auth=aiohttp.BasicAuth(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)) as response:
            if response.status != 200:
                return None, "Error downloading audio"
            
            audio_data = await response.read()
    
    # Process through unified pipeline
    response_text, audio_output, detected_lang = await process_audio(audio_data, language=language)
    
    if audio_output:
        return audio_output, response_text
    
    return None, "Processing error"


@app.route("/voice/incoming", methods=['GET', 'POST'])
def incoming_call():
    """Handle incoming call"""
    print(f"Incoming call received! Method: {request.method}")
    print(f"Headers: {dict(request.headers)}")
    
    response = VoiceResponse()
    
    # Language selection
    gather = response.gather(
        action='/voice/language',
        method='POST',
        num_digits=1,
        timeout=5
    )
    
    # Multi-language welcome
    gather.say("Welcome to electricity department.", voice='Polly.Joanna', language='en-IN')
    gather.say("Press 1 for Hindi.", voice='Polly.Joanna', language='en-IN')
    gather.say("हिंदी के लिए 1 दबाएं।", voice='Polly.Aditi', language='hi-IN')
    gather.say("Press 2 for English.", voice='Polly.Joanna', language='en-IN')
    gather.say("अंग्रेजी के लिए 2 दबाएं।", voice='Polly.Aditi', language='hi-IN')
    gather.say("Press 3 for Telugu.", voice='Polly.Joanna', language='en-IN')
    gather.say("తెలుగు కోసం 3 నొక్కండి.", voice='alice', language='te-IN')
    
    # Default to Hindi if no input
    response.redirect('/voice/start?lang=hi-IN')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/voice/language", methods=['POST'])
def select_language():
    """Handle language selection"""
    digit = request.form.get('Digits')
    
    # Map digit to language
    lang_map = {
        '1': 'hi-IN',
        '2': 'en-IN',
        '3': 'te-IN'
    }
    
    selected_lang = lang_map.get(digit, 'hi-IN')
    
    response = VoiceResponse()
    response.redirect(f'/voice/start?lang={selected_lang}')
    
    return Response(str(response), mimetype='text/xml')


@app.route("/voice/start", methods=['GET', 'POST'])
def start_recording():
    """Start recording after language selection"""
    lang = request.args.get('lang', 'hi-IN')
    
    response = VoiceResponse()
    
    # Welcome message in selected language
    messages = {
        'hi-IN': "नमस्ते, बिजली विभाग में आपका स्वागत है। कृपया अपनी समस्या बताएं।",
        'en-IN': "Hello, welcome to electricity department. Please tell us your issue.",
        'te-IN': "నమస్కారం, విద్యుత్ విభాగానికి స్వాగతం. దయచేసి మీ సమస్యను చెప్పండి."
    }
    
    voice_map = {
        'hi-IN': 'Polly.Aditi',
        'en-IN': 'Polly.Joanna',
        'te-IN': 'alice'
    }
    
    response.say(
        messages.get(lang, messages['hi-IN']),
        voice=voice_map.get(lang, 'Polly.Aditi'),
        language=lang
    )
    
    # Record user input with language parameter
    response.record(
        action=f'/voice/process?lang={lang}',
        method='POST',
        max_length=30,
        play_beep=True,
        transcribe=False
    )
    
    return Response(str(response), mimetype='text/xml')


@app.route("/voice/process", methods=['POST'])
def process_recording():
    """Process recorded audio"""
    recording_url = request.form.get('RecordingUrl')
    lang = request.args.get('lang', 'hi-IN')
    
    if not recording_url:
        response = VoiceResponse()
        error_msg = {
            'hi-IN': "माफ़ कीजिए, कोई समस्या हुई। कृपया दोबारा कॉल करें।",
            'en-IN': "Sorry, there was an issue. Please call again.",
            'te-IN': "క్షమించండి, సమస్య వచ్చింది. దయచేసి మళ్లీ కాల్ చేయండి."
        }
        voice_map = {'hi-IN': 'Polly.Aditi', 'en-IN': 'Polly.Joanna', 'te-IN': 'alice'}
        response.say(error_msg.get(lang, error_msg['hi-IN']), voice=voice_map.get(lang), language=lang)
        return Response(str(response), mimetype='text/xml')
    
    # Process audio through pipeline with selected language
    audio_output, response_text = asyncio.run(process_audio_with_pipeline(recording_url + '.wav', language=lang))
    
    response = VoiceResponse()
    voice_map = {'hi-IN': 'Polly.Aditi', 'en-IN': 'Polly.Joanna', 'te-IN': 'te-IN-Chirp3-HD-Charon'}
    
    if audio_output:
        # Use Twilio's Say with the text response
        response.say(response_text, voice=voice_map.get(lang), language=lang)
        
        # Ask if they need more help
        continue_msg = {
            'hi-IN': "क्या आपको और मदद चाहिए? हाँ के लिए 1 दबाएं, नहीं के लिए 2 दबाएं।",
            'en-IN': "Do you need more help? Press 1 for yes, 2 for no.",
            'te-IN': "మీకు మరింత సహాయం కావాలా? అవును కోసం 1, కాదు కోసం 2 నొక్కండి."
        }
        gather = response.gather(
            action=f'/voice/continue?lang={lang}',
            method='POST',
            num_digits=1,
            timeout=5
        )
        gather.say(continue_msg.get(lang), voice=voice_map.get(lang), language=lang)
    else:
        error_msg = {
            'hi-IN': "माफ़ कीजिए, कोई समस्या हुई। कृपया दोबारा कॉल करें।",
            'en-IN': "Sorry, there was an issue. Please call again.",
            'te-IN': "క్షమించండి, సమస్య వచ్చింది. దయచేసి మళ్లీ కాల్ చేయండి."
        }
        response.say(error_msg.get(lang), voice=voice_map.get(lang), language=lang)
    
    return Response(str(response), mimetype='text/xml')


@app.route("/voice/continue", methods=['POST'])
def continue_call():
    """Handle continue/end call"""
    digits = request.form.get('Digits')
    lang = request.args.get('lang', 'hi-IN')
    
    response = VoiceResponse()
    
    voice_map = {
        'hi-IN': 'Polly.Aditi',
        'en-IN': 'Polly.Joanna',
        'te-IN': 'alice'
    }
    
    continue_msg = {
        'hi-IN': "कृपया अपनी समस्या बताएं।",
        'en-IN': "Please tell us your issue.",
        'te-IN': "దయచేసి మీ సమస్యను చెప్పండి."
    }
    
    goodbye_msg = {
        'hi-IN': "धन्यवाद। आपका दिन शुभ हो।",
        'en-IN': "Thank you. Have a good day.",
        'te-IN': "ధన్యవాదాలు. మంచి రోజు కలగాలి."
    }
    
    if digits == '1':
        # Continue - record again
        response.say(continue_msg.get(lang), voice=voice_map.get(lang), language=lang)
        response.record(
            action=f'/voice/process?lang={lang}',
            method='POST',
            max_length=30,
            play_beep=True,
            transcribe=False
        )
    else:
        # End call
        response.say(goodbye_msg.get(lang), voice=voice_map.get(lang), language=lang)
        response.hangup()
    
    return Response(str(response), mimetype='text/xml')


@app.route("/voice/status", methods=['POST'])
def call_status():
    """Handle call status updates"""
    call_status = request.form.get('CallStatus')
    print(f"Call status: {call_status}")
    return '', 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print("="*60)
    print("TWILIO VOICE INTEGRATION")
    print("="*60)
    print(f"\nStarting Flask server on port {port}...")
    print("="*60)
    
    app.run(host='0.0.0.0', port=port, debug=False)
