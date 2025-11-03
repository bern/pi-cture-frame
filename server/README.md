# Server Setup

This is a Flask server for Bernie's Desk Frame application.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set your Google Gemini API key as an environment variable:
```bash
export GOOGLE_GEMINI_API_KEY='your-api-key-here'
```

Or create a `.env` file (not tracked in git) with:
```
GOOGLE_GEMINI_API_KEY=your-api-key-here
```

3. Run the server:
```bash
python app.py
```

The server will run on `http://localhost:3000`.

## API Endpoints

- `GET /` - Returns 200 OK
- `GET /prompt?prompt=<your-prompt>` - Sends prompt to Google Gemini API
- `POST /image` - Receives and stores base64 encoded image in the request body

## Note on Gemini Image Generation

The Gemini API primarily focuses on text generation. For image generation capabilities, you may need to:
- Use a different Gemini model variant if available
- Use a different image generation service
- Adjust the model name in `app.py` based on your API access

