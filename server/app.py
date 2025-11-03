from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enable CORS for the client to communicate with the server

# Google Gemini API Key
GOOGLE_GEMINI_API_KEY = os.getenv('GOOGLE_GEMINI_API_KEY', 'your-api-key-here')

# Configure the Gemini API
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)

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
        # Initialize the Gemini model for image generation
        # Using gemini-2.0-flash-exp or gemini-pro-vision based on availability
        # Adjust model name as needed for "flash 2.5 nano banana"
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Generate image based on prompt
        # Note: Gemini API primarily generates text; for image generation, 
        # you may need to use a different approach or service
        response = model.generate_content(prompt)
        
        return jsonify({
            'success': True,
            'response': response.text if hasattr(response, 'text') else str(response)
        }), 200
        
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

