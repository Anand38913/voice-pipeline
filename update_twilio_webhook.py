"""
Update Twilio webhook to point to Render URL
"""

import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
phone_number = "+19522543946"

# Get Render URL from user
render_url = input("Enter your Render URL (e.g., https://voice-pipeline-xxxx.onrender.com): ").strip()

if not render_url.startswith("http"):
    render_url = "https://" + render_url

webhook_url = f"{render_url}/voice/incoming"

print("\n" + "="*60)
print("UPDATING TWILIO WEBHOOK")
print("="*60)
print(f"Phone Number: {phone_number}")
print(f"New Webhook URL: {webhook_url}")
print("="*60)

# Initialize Twilio client
client = Client(account_sid, auth_token)

try:
    # Get the phone number
    incoming_phone_numbers = client.incoming_phone_numbers.list(phone_number=phone_number)
    
    if incoming_phone_numbers:
        number = incoming_phone_numbers[0]
        
        print(f"\nCurrent webhook: {number.voice_url}")
        
        # Update webhook
        number.update(
            voice_url=webhook_url,
            voice_method='POST'
        )
        
        print(f"\n✓ Webhook updated successfully!")
        print(f"New webhook: {webhook_url}")
        print("\nYou can now call (952) 254-3946 to test!")
        
    else:
        print("\n✗ Phone number not found!")
        
except Exception as e:
    print(f"\n✗ Error: {e}")
