from flask import Flask, request, jsonify, send_from_directory
import google.generativeai as genai
import os
from gtts import gTTS
import uuid  # For unique file names

app = Flask(__name__, static_folder='static')

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-pro-exp-03-25')  # Adjust as needed

# Directory for audio files
AUDIO_DIR = os.path.join(app.static_folder, 'audio')
os.makedirs(AUDIO_DIR, exist_ok=True)

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'No message provided'}), 400

        # Generate response using Gemini
        response = model.generate_content(message)
        
        if response and hasattr(response, 'text') and response.text:
            response_text = response.text.strip()
            
            # Generate audio from the response text
            audio_filename = f"{uuid.uuid4()}.mp3"
            audio_path = os.path.join(AUDIO_DIR, audio_filename)
            tts = gTTS(text=response_text, lang='en')
            tts.save(audio_path)
            
            # Return both text and audio URL
            audio_url = f"/static/audio/{audio_filename}"
            return jsonify({
                'response': response_text,
                'audio_url': audio_url
            })
        else:
            return jsonify({'error': 'No valid response from AI'}), 500
            
    except genai.GenerationError as ge:
        return jsonify({'error': f'Generation error: {str(ge)}'}), 500
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/static/audio/<filename>')
def serve_audio(filename):
    return send_from_directory(AUDIO_DIR, filename)

if __name__ == '__main__':
    app.run(debug=False, port=5000)
