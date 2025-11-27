"""
Make a test call to your number
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

# Your number
YOUR_NUMBER = "+917995465001"

# Your Render URL (update this after deployment)
RENDER_URL = input("Enter your Render URL (e.g., https://voice-pipeline-xxxx.onrender.com): ")

print("\n" + "="*60)
print("MAKING TEST CALL")
print("="*60)
print(f"From: {twilio_number}")
print(f"To: {YOUR_NUMBER}")
print(f"Webhook: {RENDER_URL}/voice/incoming")
print("="*60)

# Initialize Twilio client
client = Client(account_sid, auth_token)

try:
    # Make the call
    call = client.calls.create(
        to=YOUR_NUMBER,
        from_=twilio_number,
        url=f"{RENDER_URL}/voice/incoming",
        method="POST"
    )
    
    print(f"\n✓ Call initiated successfully!")
    print(f"Call SID: {call.sid}")
    print(f"Status: {call.status}")
    print(f"\nYou should receive a call at {YOUR_NUMBER} shortly!")
    print("\nWhen you answer:")
    print("1. Press 1 for Hindi, 2 for English, 3 for Telugu")
    print("2. Speak your electricity complaint after the beep")
    print("3. AI will respond in your selected language")
    print("4. Press 1 to continue or 2 to end")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nPossible reasons:")
    print("1. Trial account - verify +917995465001 at:")
    print("   https://console.twilio.com/us1/develop/phone-numbers/manage/verified")
    print("2. Insufficient credits")
    print("3. Render URL not deployed yet")
