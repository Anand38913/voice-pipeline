"""
Voice Pipeline - Unified STT → LLM → TTS processing
Supports Hindi, Telugu, and auto-detection
"""

import asyncio
import os
import base64
import aiohttp
from dotenv import load_dotenv

load_dotenv()


async def process_audio(audio_data, language="auto"):
    """
    Process audio through complete pipeline
    
    Args:
        audio_data: Audio bytes (WAV format)
        language: "hi-IN" (Hindi), "te-IN" (Telugu), or "auto" (detect)
    
    Returns:
        tuple: (response_text, response_audio_bytes, detected_language)
    """
    
    api_key = os.getenv("SARVAM_API_KEY")
    
    # Step 1: Speech-to-Text
    if language == "auto":
        # Try multiple languages and pick best
        transcript, detected_lang = await auto_detect_language(audio_data, api_key)
    else:
        transcript = await speech_to_text(audio_data, language, api_key)
        detected_lang = language
    
    if not transcript:
        return None, None, None
    
    # Apply corrections
    transcript = apply_corrections(transcript, detected_lang)
    
    # Step 2: Language Model
    response_text = await generate_response(transcript, detected_lang, api_key)
    
    if not response_text:
        return None, None, None
    
    # Apply TTS corrections
    tts_text = apply_tts_corrections(response_text, detected_lang)
    
    # Truncate if too long
    if len(tts_text) > 500:
        tts_text = tts_text[:497] + "..."
    
    # Step 3: Text-to-Speech
    response_audio = await text_to_speech(tts_text, detected_lang, api_key)
    
    return response_text, response_audio, detected_lang


async def speech_to_text(audio_data, language, api_key):
    """Convert speech to text"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {"api-subscription-key": api_key}
            data = aiohttp.FormData()
            data.add_field('file', audio_data, filename='audio.wav', content_type='audio/wav')
            data.add_field('language_code', language)
            
            async with session.post(
                "https://api.sarvam.ai/speech-to-text",
                headers=headers,
                data=data
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('transcript', '')
    except Exception as e:
        print(f"STT Error: {e}")
    return None


async def auto_detect_language(audio_data, api_key):
    """Auto-detect language from audio"""
    transcripts = {}
    
    for lang_code in ["hi-IN", "te-IN"]:
        text = await speech_to_text(audio_data, lang_code, api_key)
        if text:
            transcripts[lang_code] = text
    
    if not transcripts:
        return None, None
    
    # Count native script characters
    best_lang = None
    best_score = 0
    
    for lang_code, text in transcripts.items():
        if lang_code == "hi-IN":
            score = sum(1 for char in text if '\u0900' <= char <= '\u097F') * 10
        elif lang_code == "te-IN":
            score = sum(1 for char in text if '\u0C00' <= char <= '\u0C7F') * 10
        else:
            score = 0
        
        if score > best_score:
            best_score = score
            best_lang = lang_code
    
    # Default to Hindi if no clear winner
    if not best_lang or best_score == 0:
        best_lang = "hi-IN"
    
    return transcripts.get(best_lang), best_lang


async def generate_response(transcript, language, api_key):
    """Generate AI response"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "api-subscription-key": api_key,
                "Content-Type": "application/json"
            }
            
            # Language-specific system prompts
            if language == "te-IN":
                system_prompt = """మీరు హైదరాబాద్‌లో విద్యుత్ విభాగం కస్టమర్ సర్వీస్.
సంక్షిప్తంగా సమాధానం ఇవ్వండి (400 అక్షరాలు గరిష్టం).
సంఖ్యలను తెలుగు పదాలలో రాయండి (రెండు, మూడు).
యూజర్ చెప్పిన ప్రాంతం పేరు మీ సమాధానంలో తప్పకుండా చెప్పండి."""
            else:  # Hindi
                system_prompt = """आप हैदराबाद में बिजली विभाग की कस्टमर सर्विस हैं।
संक्षिप्त जवाब दें (400 अक्षर अधिकतम).
संख्याओं को हिंदी शब्दों में लिखें (दो, तीन).
यूजर ने जो इलाका बताया उसे अपने जवाब में ज़रूर दोहराएं."""
            
            payload = {
                "model": "sarvam-m",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": transcript}
                ],
                "stream": False
            }
            
            async with session.post(
                "https://api.sarvam.ai/v1/chat/completions",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    return result.get('choices', [{}])[0].get('message', {}).get('content', '')
    except Exception as e:
        print(f"LLM Error: {e}")
    return None


async def text_to_speech(text, language, api_key):
    """Convert text to speech"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "api-subscription-key": api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "inputs": [text],
                "target_language_code": language,
                "speaker": "anushka",
                "pitch": 0,
                "pace": 1.0,
                "loudness": 1.5,
                "speech_sample_rate": 8000,  # Twilio uses 8kHz
                "enable_preprocessing": True,
                "model": "bulbul:v2"
            }
            
            async with session.post(
                "https://api.sarvam.ai/text-to-speech",
                headers=headers,
                json=payload
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    audio_base64 = result.get('audios', [''])[0]
                    if audio_base64:
                        return base64.b64decode(audio_base64)
    except Exception as e:
        print(f"TTS Error: {e}")
    return None


def apply_corrections(text, language):
    """Apply language-specific corrections"""
    corrections = {
        "jivpatamgudi": "మెహెందిపట్నం" if language == "te-IN" else "मेहंदीपटनम",
        "jivpatam gudi": "మెహెందిపట్నం" if language == "te-IN" else "मेहंदीपटनम",
        "लाइट": "लाइट (बिजली)",
        "light": "లైట్ (విద్యుత్)" if language == "te-IN" else "लाइट (बिजली)",
        "करंट": "करंट (बिजली)",
        "current": "కరెంట్ (విద్యుత్)" if language == "te-IN" else "करंट (बिजली)",
    }
    
    for wrong, right in corrections.items():
        text = text.replace(wrong, right)
    
    return text


def apply_tts_corrections(text, language):
    """Apply pronunciation corrections for TTS"""
    if language == "te-IN":
        text = text.replace("మెహెందిపట్నం", "మెహెంది పట్నం")
    else:  # Hindi
        text = text.replace("मेहंदीपटनम", "मेहंदी पटनम")
    
    return text
