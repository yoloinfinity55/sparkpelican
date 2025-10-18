#!/usr/bin/env python3
from pathlib import Path
import re

file_path = Path('myapp/youtube_transcript.py')
content = file_path.read_text()

# Find the function and replace it with a working version
pattern = r'def _transcribe_with_gemini_sync\(audio_file_path: str\) -> str:.*?(?=\ndef |\Z)'

new_function = '''def _transcribe_with_gemini_sync(audio_file_path: str) -> str:
    """Transcribe audio file using Gemini API."""
    import time
    
    # Configure Gemini API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise TranscriptError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    
    try:
        # Upload audio file to Gemini Files API
        print("📤 Uploading audio to Gemini...")
        with open(audio_file_path, 'rb') as f:
            audio_file = genai.upload_file(path=audio_file_path, display_name="audio_transcription")
        
        print(f"✅ Audio uploaded: {audio_file.name}")
        
        # Wait for file processing
        max_attempts = 30
        for attempt in range(max_attempts):
            file_info = genai.get_file(audio_file.name)
            if file_info.state.name == "ACTIVE":
                print(f"✅ Audio file ready")
                break
            elif file_info.state.name == "FAILED":
                raise TranscriptError("Audio file processing failed")
            print(f"⏳ Waiting for processing... ({attempt + 1}/{max_attempts})")
            time.sleep(2)
        else:
            raise TranscriptError("Timeout waiting for file processing")
        
        # Use Gemini to transcribe - simpler approach
        print("🤖 Generating transcript...")
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        result = model.generate_content([
            audio_file,
            "Listen to this audio and transcribe everything that is spoken. Provide only the transcript text, nothing else."
        ])
        
        transcript = result.text
        
        # Cleanup
        try:
            genai.delete_file(audio_file.name)
            print("🗑️  Cleaned up Gemini file")
        except:
            pass
        
        print(f"✅ Transcription complete ({len(transcript)} characters)")
        return transcript.strip()
        
    except Exception as e:
        raise TranscriptError(f"Gemini transcription failed: {str(e)}")

'''

# Use regex to replace the function
content = re.sub(pattern, new_function, content, flags=re.DOTALL)

file_path.write_text(content)
print("✅ Updated _transcribe_with_gemini_sync function with simpler API approach")
