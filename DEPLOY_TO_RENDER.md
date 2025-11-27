# Deploy to Render - Step by Step

## Prerequisites
- GitHub account
- Render account (free - no credit card needed)
- Sarvam AI API key
- Twilio account with phone number

## Step 1: Push Code to GitHub

```bash
# Configure git (first time only)
git config --global user.email "your@email.com"
git config --global user.name "Your Name"

# Initialize and commit
git init
git add .
git commit -m "Voice AI pipeline deployment"

# Create repo on GitHub (https://github.com/new)
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/voice-pipeline.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy to Render

### 2.1 Sign Up
1. Go to https://render.com
2. Click "Get Started"
3. Sign up with GitHub (recommended)

### 2.2 Create Web Service
1. Click **New +** button
2. Select **Web Service**
3. Click **Connect GitHub**
4. Select your `voice-pipeline` repository
5. Click **Connect**

### 2.3 Configure Service
Render will auto-detect from `render.yaml`:
- **Name**: voice-pipeline
- **Environment**: Python 3
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python twilio_integration.py`
- **Instance Type**: Free

### 2.4 Add Environment Variables
Click **Advanced** → **Add Environment Variable**

Add these 4 variables (get values from your .env file):

| Key | Value |
|-----|-------|
| `SARVAM_API_KEY` | Your Sarvam API key |
| `TWILIO_ACCOUNT_SID` | Your Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Your Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number |

### 2.5 Deploy
1. Click **Create Web Service**
2. Wait 2-3 minutes for deployment
3. You'll see: "Your service is live 🎉"
4. Copy your URL: `https://voice-pipeline-xxxx.onrender.com`

## Step 3: Configure Twilio

### 3.1 Update Webhook
1. Go to https://console.twilio.com/us1/develop/phone-numbers/manage/incoming
2. Click your phone number
3. Under **Voice Configuration**:
   - **A CALL COMES IN**: Webhook
   - **URL**: `https://voice-pipeline-xxxx.onrender.com/voice/incoming`
   - **HTTP**: POST
4. Click **Save**

## Step 4: Test

### Option 1: Call the Number
Simply call your Twilio number from any phone!

### Option 2: Use Test Script
```bash
python call_me.py
```

## Expected Behavior

1. ☎️ Call connects
2. 🗣️ Hindi welcome message plays
3. 🎤 Beep - you can speak (30 seconds max)
4. 🤖 AI processes your speech
5. 🔊 AI responds in your language
6. ⌨️ Press 1 to continue, 2 to end

## Troubleshooting

### Deployment fails
- Check environment variables are set correctly
- Verify `requirements.txt` has all dependencies
- Check Render logs for errors

### Call connects but no response
- Verify Twilio webhook URL is correct
- Check Render logs for incoming requests
- Ensure service is not sleeping (free tier sleeps after 15 min)

### First call slow
- Free tier sleeps after inactivity
- First call wakes service (30 seconds)
- Subsequent calls are instant

### Audio quality issues
- Twilio uses 8kHz audio (lower quality)
- This is normal for phone calls
- Test with clear speech

## Monitoring

### View Logs
1. Go to Render dashboard
2. Click your service
3. Click **Logs** tab
4. See real-time request logs

### Check Status
- Green dot = Service running
- Yellow = Deploying
- Red = Error (check logs)

## Updating Code

```bash
# Make changes to your code
git add .
git commit -m "Update message"
git push

# Render auto-deploys on push!
```

## Cost

- **Render Free Tier**: $0/month
  - 750 hours/month
  - Sleeps after 15 min inactivity
  - Perfect for testing

- **Sarvam AI**: Pay per use
  - STT, LLM, TTS charges apply
  - Check Sarvam pricing

- **Twilio**: Pay per use
  - Incoming calls: ~$0.0085/min
  - Outgoing calls: varies by country

## Next Steps

- ✅ Test with different languages
- ✅ Monitor usage and costs
- ✅ Customize welcome message
- ✅ Add more languages
- ✅ Improve system prompts

## Support

Issues? Check:
1. Render logs
2. Twilio debugger
3. GitHub issues
