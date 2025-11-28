"""
Check current Twilio configuration
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")

client = Client(account_sid, auth_token)

print("="*60)
print("TWILIO PHONE NUMBER CONFIGURATION")
print("="*60)

# Get all phone numbers
numbers = client.incoming_phone_numbers.list()

for number in numbers:
    print(f"\nPhone Number: {number.phone_number}")
    print(f"Friendly Name: {number.friendly_name}")
    print(f"Voice URL: {number.voice_url}")
    print(f"Voice Method: {number.voice_method}")
    print(f"Voice Fallback URL: {number.voice_fallback_url}")
    print(f"Status Callback: {number.status_callback}")
    print("-"*60)

print("\n✓ If you see ngrok URL above, it needs to be changed!")
print("Run: python update_twilio_webhook.py")
