import os
import base64
import requests
from flask import Flask, request, Response
from dotenv import load_dotenv
from twilio.twiml.voice_response import VoiceResponse, Start, Stream

load_dotenv()
app = Flask(__name__)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

# -------------------------------
# 1. INBOUND CALL HANDLER
# -------------------------------
@app.post("/voice/incoming")
def incoming_call():
    """
    This answers the call and starts streaming audio in 16k L16
    (Telugu requires clarity)
    """

    response = VoiceResponse()

    start = Start()
    start.stream(
        url=f"wss://{request.host}/media",  # WebSocket
        track="inbound_audio",
        codec="audio/l16;rate=16000"        # CRITICAL for Telugu
    )
    response.append(start)

    response.say("Welcome. Telugu, Hindi or English lo matladandi.", language="en-IN")

    return Response(str(response), mimetype="text/xml")


# -------------------------------
# 2. WEBSOCKET AUDIO STREAM (MEDIA STREAM)
# -------------------------------
from flask_sock import Sock
sock = Sock(app)

@sock.route('/media')
def media_stream(ws):
    """
    Receives Twilio audio (base64 PCM), sends to Sarvam STT,
    gets auto-language detection, and returns TTS audio.
    """

    print("🔵 Media Stream Connected")

    while True:
        message = ws.receive()
        if not message:
            break

        # Twilio sends JSON messages, speech frames come in "media"
        import json
        msg = json.loads(message)

        if msg.get("event") == "media":
            audio_b64 = msg["media"]["payload"]

            # -------------------------------
            # SEND AUDIO TO SARVAM STT
            # -------------------------------
            stt_payload = {
                "config": {
                    "language": "auto",       # Hindi + English + Telugu detection
                    "task": "transcribe"
                },
                "audio": audio_b64
            }

            stt_resp = requests.post(
                "https://api.sarvam.ai/speech-to-text",
                json=stt_payload,
                headers={"Authorization": f"Bearer {SARVAM_API_KEY}"}
            ).json()

            text = stt_resp.get("text", "").strip()
            if text:
                print(f"👂 Heard → {text}")

                # -------------------------------
                # Detect language
                # -------------------------------
                detected_lang = stt_resp.get("language", "en")

                print(f"🌐 Detected language → {detected_lang}")

                # -------------------------------
                # Select the correct TTS voice
                # -------------------------------
                if detected_lang == "te":
                    voice = "te-IN-Charlie"
                elif detected_lang == "hi":
                    voice = "hi-IN-Meera"
                else:
                    voice = "en-IN-Rhea"

                # -------------------------------
                # SEND TO SARVAM TTS
                # -------------------------------
                tts_payload = {
                    "voice": voice,
                    "input": f"Meeru cheppindi: {text}",
                    "format": "wav"
                }

                tts_resp = requests.post(
                    "https://api.sarvam.ai/text-to-speech",
                    json=tts_payload,
                    headers={"Authorization": f"Bearer {SARVAM_API_KEY}"}
                ).json()

                audio_reply = tts_resp["audio"]

                # -------------------------------
                # RETURN AUDIO TO TWILIO STREAM
                # -------------------------------
                ws.send(json.dumps({
                    "event": "media",
                    "media": {"payload": audio_reply}
                }))

    print("🔴 Media stream closed")


@app.get("/")
def home():
    return "Sarvam + Twilio Voice Bot Running!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
