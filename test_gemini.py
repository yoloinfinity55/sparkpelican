#!/usr/bin/env python3
import os
import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY not set")
    exit(1)

print(f"✅ API key found")
genai.configure(api_key=api_key)

# Test simple text generation
print("Testing Gemini API with text...")
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say hello in 5 words")
    print(f"✅ Gemini text API works: {response.text[:50]}")
except Exception as e:
    print(f"❌ Gemini text API error: {e}")

# Test file upload
print("\nTesting Gemini file upload...")
try:
    # Create a tiny test file
    with open('test_audio.txt', 'w') as f:
        f.write("test")
    
    uploaded = genai.upload_file(path='test_audio.txt', display_name='test')
    print(f"✅ File upload works: {uploaded.name}")
    
    # Clean up
    genai.delete_file(uploaded.name)
    import os
    os.remove('test_audio.txt')
    print("✅ File cleanup works")
except Exception as e:
    print(f"❌ File upload error: {e}")
    import traceback
    traceback.print_exc()
