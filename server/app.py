from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from PIL import Image
from inky.auto import auto
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)  # Enable CORS for the client to communicate with the server

# Google Gemini API Key
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY', 'your-api-key-here')

# Gemini API base URL
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent'

# Variable to store the received image
stored_image = None

@app.route('/', methods=['GET'])
def root():
    """Root route that returns 200 OK"""
    return 'OK', 200

@app.route('/prompt', methods=['GET'])
def handle_prompt():
    """Handle prompt query parameter and send it to Google Gemini Flash 2.5 for image generation"""
    prompt = request.args.get('prompt')
    
    if not prompt:
        return jsonify({'error': 'Prompt query parameter is required'}), 400
    
    try:
        # Call Gemini API using REST API directly
        # Adjust model name as needed for "flash 2.5 nano banana"
        api_url = f"{GEMINI_API_URL}?key={GOOGLE_GEMINI_API_KEY}"
        
        # Concatenate resolution requirement to the prompt
        enhanced_prompt = f"{prompt} resolution is fixed at 800x480 pixels"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": enhanced_prompt
                }]
            }]
        }
        
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract image data from Gemini response following the bash script pattern
        # Look for "data" field in inlineData structure: candidates[0].content.parts[].inlineData.data
        image_data_base64 = None
        mime_type = None
        
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0].get('content', {})
            parts = content.get('parts', [])
            
            for part in parts:
                # Check for both 'inlineData' and 'inline_data' formats
                inline_data = part.get('inlineData') or part.get('inline_data')
                if inline_data:
                    image_data_base64 = inline_data.get('data')
                    mime_type = inline_data.get('mimeType') or inline_data.get('mime_type')
                    if image_data_base64:
                        break
        
        if image_data_base64:
            # Ensure proper padding for base64 decoding
            # Base64 strings must be multiples of 4 characters
            padding_needed = len(image_data_base64) % 4
            if padding_needed:
                image_data_base64 += '=' * (4 - padding_needed)
            
            # Decode base64 data (like the bash script: base64 --decode)
            image_data = base64.b64decode(image_data_base64)
            
            # Open image and resize for inky display
            inky = auto(ask_user=True, verbose=True)
            img = Image.open(BytesIO(image_data))
            resized_image = img.resize(inky.resolution)
            inky.set_image(resized_image)
            inky.show()
            
            # Store image info
            global stored_image
            stored_image = {
                'mimeType': mime_type,
                'data': image_data_base64
            }

            return jsonify({
                'success': True,
                'message': 'Image received and stored successfully',
                'image_info': {
                    'mimeType': stored_image['mimeType']
                }
            }), 200
            
        # Fallback if no valid structure found
        return jsonify({
            'success': True,
            'response': str(result)
        }), 200
        
    except requests.exceptions.RequestException as e:
        return jsonify({
            'error': 'Failed to generate content',
            'details': str(e)
        }), 500
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate content',
            'details': str(e)
        }), 500

@app.route('/image', methods=['POST'])
def handle_image():
    """Receive base64 encoded image from POST request body and store it"""
    global stored_image
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Extract image data from the request body
        # The client sends: {name, type, size, data} where data is base64
        if 'data' in data:
            base64_data = data.get('data')
            
            # Strip data URL prefix if present (e.g., "data:image/png;base64,")
            if base64_data and ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Ensure proper padding for base64 decoding
            # Base64 strings must be multiples of 4 characters
            padding_needed = len(base64_data) % 4
            if padding_needed:
                base64_data += '=' * (4 - padding_needed)
            
            stored_image = {
                'name': data.get('name'),
                'type': data.get('type'),
                'size': data.get('size'),
                'data': base64_data  # Base64 encoded image
            }
            
            # Render image to inky display
            inky = auto(ask_user=True, verbose=True)
            image_data = base64.b64decode(base64_data)
            # Wrap the bytes in a BytesIO buffer
            image_buffer = BytesIO(image_data)
            # Open the image with PIL
            img = Image.open(image_buffer)

            inky.set_image(img)
            inky.show()
            
            return jsonify({
                'success': True,
                'message': 'Image received and stored successfully',
                'image_info': {
                    'name': stored_image['name'],
                    'type': stored_image['type'],
                    'size': stored_image['size']
                }
            }), 200
        else:
            return jsonify({'error': 'Image data is required in the request body'}), 400
            
    except Exception as e:
        return jsonify({
            'error': 'Failed to process image',
            'details': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)

