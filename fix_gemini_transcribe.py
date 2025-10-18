#!/usr/bin/env python3
from pathlib import Path

file_path = Path('myapp/youtube_transcript.py')
content = file_path.read_text()

# Find and replace the entire function
old_function = '''def _transcribe_with_gemini_sync(audio_file_path: str) -> str:
    """Transcribe audio file using Gemini API."""
    # Configure Gemini API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise TranscriptError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    
    try:
        # Upload audio file to Gemini
        print("📤 Uploading audio to Gemini...")
        audio_file = genai.upload_file(audio_file_path)
        print(f"✅ Audio uploaded: {audio_file.name}")
        
        # Generate transcript using Gemini
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        prompt = """Please transcribe this audio completely and accurately. 
        Include ALL spoken content without summarization.
        Maintain natural sentence structure and punctuation.
        Return ONLY the transcript text, no commentary or formatting."""
        
        response = model.generate_content([prompt, audio_file])
        transcript = response.text
        
        # Clean up uploaded file from Gemini
        try:
            genai.delete_file(audio_file.name)
            print("��️  Cleaned up Gemini file")
        except Exception as e:
            logger.warning(f"Failed to delete Gemini file: {e}")
        
        return transcript.strip()
        
    except Exception as e:
        raise TranscriptError(f"Gemini transcription failed: {str(e)}")'''

new_function = '''def _transcribe_with_gemini_sync(audio_file_path: str) -> str:
    """Transcribe audio file using Gemini API."""
    import time
    
    # Configure Gemini API
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise TranscriptError("GEMINI_API_KEY environment variable not set")
    
    genai.configure(api_key=api_key)
    
    uploaded_file = None
    try:
        # Upload audio file to Gemini
        print("📤 Uploading audio to Gemini...")
        uploaded_file = genai.upload_file(audio_file_path)
        print(f"✅ Audio uploaded: {uploaded_file.name}")
        
        # Wait for file to be processed
        max_wait = 120
        wait_time = 0
        while uploaded_file.state.name == "PROCESSING":
            if wait_time >= max_wait:
                raise TranscriptError("Timeout waiting for audio processing")
            print(f"⏳ Processing audio file... ({wait_time}s)")
            time.sleep(5)
            wait_time += 5
            uploaded_file = genai.get_file(uploaded_file.name)
        
        if uploaded_file.state.name == "FAILED":
            raise TranscriptError("Gemini failed to process audio file")
        
        print(f"✅ Audio file ready: {uploaded_file.state.name}")
        
        # Generate transcript using Gemini
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        
        prompt = """Transcribe this audio file completely and accurately. 
Include all spoken words. Return only the transcript text."""
        
        response = model.generate_content([uploaded_file, prompt])
        
        if not response or not response.text:
            raise TranscriptError("Empty response from Gemini")
        
        transcript = response.text
        print(f"✅ Transcription complete ({len(transcript)} characters)")
        
        return transcript.strip()
        
    except Exception as e:
        raise TranscriptError(f"Gemini transcription failed: {str(e)}")
    
    finally:
        if uploaded_file:
            try:
                genai.delete_file(uploaded_file.name)
                print("🗑️  Cleaned up Gemini file")
            except Exception as e:
                logger.warning(f"Failed to delete Gemini file: {e}")'''

if old_function in content:
    content = content.replace(old_function, new_function)
    file_path.write_text(content)
    print("✅ Updated _transcribe_with_gemini_sync function")
else:
    print("❌ Could not find the old function. Manual update needed.")
