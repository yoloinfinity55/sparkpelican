#!/usr/bin/env python3
from pathlib import Path
import re

file_path = Path('myapp/youtube_transcript.py')
content = file_path.read_text()

# Replace the transcription function with a working version
old_pattern = r'def _transcribe_with_gemini_sync\(audio_file_path: str\) -> str:.*?(?=\ndef [a-z_]|\Z)'

new_function = '''def _transcribe_with_gemini_sync(audio_file_path: str) -> str:
    """Transcribe audio file using Gemini API - alternative approach without file upload."""
    import base64
    
    # Configure Gemini API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise TranscriptError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    
    try:
        print("📤 Preparing audio for Gemini...")
        
        # Read audio file as bytes
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()
        
        # Use the simpler API with inline audio data
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create the audio part
        audio_part = {
            "inline_data": {
                "mime_type": "audio/mp3",
                "data": base64.b64encode(audio_bytes).decode('utf-8')
            }
        }
        
        prompt = "Transcribe this audio file completely and accurately. Include all spoken words. Return only the transcript text, nothing else."
        
        print("🤖 Transcribing with Gemini 2.0 Flash...")
        response = model.generate_content([prompt, audio_part])
        
        if not response or not response.text:
            raise TranscriptError("Empty response from Gemini")
        
        transcript = response.text
        print(f"✅ Transcription complete ({len(transcript)} characters)")
        
        return transcript.strip()
        
    except Exception as e:
        raise TranscriptError(f"Gemini transcription failed: {str(e)}")

'''

content = re.sub(old_pattern, new_function, content, flags=re.DOTALL)
file_path.write_text(content)
print("✅ Updated to use inline audio data (no file upload needed)")
