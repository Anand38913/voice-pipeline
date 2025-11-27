# Voice AI Pipeline with Twilio & Sarvam AI

Real-time voice conversation system supporting Hindi and Telugu languages for customer service.

## Features

- 🎤 **Speech-to-Text** - Sarvam AI STT (Hindi/Telugu)
- 🤖 **AI Processing** - Sarvam LLM with context awareness
- 🔊 **Text-to-Speech** - Sarvam TTS with natural pronunciation
- 📞 **Phone Integration** - Twilio voice calls
- 🌐 **Multi-language** - Auto-detects Hindi/Telugu/English
- 📍 **Location Aware** - Recognizes area names (Mehndipatnam, etc.)

## Project Structure

```
├── twilio_integration.py    # Main Flask app for Twilio webhooks
├── hindi_pipeline.py         # Hindi-only voice pipeline
├── telugu_pipeline.py        # Telugu-only voice pipeline
├── multilang_pipeline.py     # Auto-detect language pipeline
├── call_me.py               # Script to initiate test calls
├── requirements.txt         # Python dependencies
├── render.yaml             # Render deployment config
└── .env.example            # Environment variables template
```

## Quick Start (Local Testing)

### 1. Install Dependencies

```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```
SARVAM_API_KEY=your_sarvam_api_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=your_twilio_number
```

### 3. Test with Audio Files

```bash
# Hindi pipeline
python hindi_pipeline.py your_audio.wav

# Telugu pipeline
python telugu_pipeline.py your_audio.wav

# Auto-detect language
python multilang_pipeline.py your_audio.wav
```

## Deploy to Render (Production)

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "Voice AI pipeline"
git remote add origin https://github.com/YOUR_USERNAME/voice-pipeline.git
git push -u origin main
```

### 2. Deploy on Render

1. Go to [render.com](https://render.com) and sign up (free)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository
4. Render auto-detects settings from `render.yaml`
5. Add environment variables:
   - `SARVAM_API_KEY`
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_PHONE_NUMBER`
6. Click **Create Web Service**
7. Wait 2-3 minutes for deployment
8. Copy your URL: `https://voice-pipeline-xxxx.onrender.com`

### 3. Configure Twilio Webhook

1. Go to [Twilio Console](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
2. Click your phone number
3. Set **Voice URL** to: `https://your-render-url.onrender.com/voice/incoming`
4. Set **HTTP Method** to: **POST**
5. Click **Save**

### 4. Test Your Voice AI

Call your Twilio number or run:
```bash
python call_me.py
```

## How It Works

### Call Flow

1. **User calls** Twilio number
2. **Welcome message** plays in Hindi
3. **User speaks** (up to 30 seconds recorded)
4. **AI processes**:
   - Speech-to-Text (Sarvam STT)
   - Language Model (Sarvam LLM)
   - Text-to-Speech (Sarvam TTS)
5. **AI responds** in user's language
6. **Option to continue** or end call

### Pipeline Architecture

```
Audio Input → STT → Context Manager → LLM → TTS → Audio Output
```

## API Configuration

### Sarvam AI APIs Used

- **STT**: `https://api.sarvam.ai/speech-to-text`
- **LLM**: `https://api.sarvam.ai/v1/chat/completions` (sarvam-m model)
- **TTS**: `https://api.sarvam.ai/text-to-speech` (bulbul:v2 model)

### Features

- ✅ Natural Hindi/Telugu numbers (दो, तीन not 2, 3)
- ✅ Location name recognition and pronunciation
- ✅ Context-aware responses
- ✅ Automatic language detection
- ✅ 30-second audio limit handling
- ✅ Pronunciation corrections for TTS

## Environment Variables

| Variable | Description |
|----------|-------------|
| `SARVAM_API_KEY` | Your Sarvam AI API key |
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | Your Twilio phone number |
| `PORT` | Server port (auto-set by Render) |

## Troubleshooting

### Audio too long error
- Sarvam STT supports max 30 seconds
- Audio is auto-trimmed in pipelines

### TTS character limit
- Responses limited to 500 characters
- Auto-truncated if longer

### Render free tier
- Service sleeps after 15 min inactivity
- First call may take 30 seconds to wake up

## License

MIT

## Support

For issues or questions, please open a GitHub issue.
