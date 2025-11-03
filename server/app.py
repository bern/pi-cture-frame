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
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        # Handle response with candidates and parts containing inlineData
        if 'candidates' in result and len(result['candidates']) > 0:
            content = result['candidates'][0].get('content', {})
            parts = content.get('parts', [])
            
            if parts and len(parts) > 0:
                # Check if parts contain inlineData (image)
                if 'inlineData' in parts[0]:
                    inline_data = parts[0]['inlineData']
                    # Save the inlineData (contains mimeType and data)
                    global stored_image
                    stored_image = {
                        'mimeType': inline_data.get('mimeType'),
                        'data': inline_data.get('data')  # Base64 encoded image
                    }
                    # Print the stored image
                    print("Stored image:")
                    print(f"  mimeType: {stored_image['mimeType']}")
                    print(f"  data length: {len(stored_image['data']) if stored_image['data'] else 0} characters")
                    print(f"  data preview: {stored_image['data'][:100] if stored_image['data'] else 'None'}...")

                    inky = auto(ask_user=True, verbose=True)
                    image_data = base64.b64decode(stored_image['data'])
                    # Step 2: Wrap the bytes in a BytesIO buffer
                    image_buffer = BytesIO(image_data)
                    # Step 3: Open the image with PIL
                    img = Image.open(image_buffer)

                    inky.set_image(img)
                    inky.show()

                    return jsonify({
                        'success': True,
                        'message': 'Image received and stored successfully',
                        'image_info': {
                            'mimeType': stored_image['mimeType']
                        }
                    }), 200
                # Otherwise, extract text if available
                elif 'text' in parts[0]:
                    generated_text = parts[0]['text']
                    return jsonify({
                        'success': True,
                        'response': generated_text
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
            stored_image = {
                'name': data.get('name'),
                'type': data.get('type'),
                'size': data.get('size'),
                'data': data.get('data')  # Base64 encoded image
            }
            
            # Render image to inky display
            inky = auto(ask_user=True, verbose=True)
            image_data = base64.b64decode(stored_image['data'])
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

