#!/usr/bin/env python3
import os
import google.generativeai as genai

api_key = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=api_key)

print("Testing available models...")
try:
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  ✅ {model.name}")
except Exception as e:
    print(f"❌ Error: {e}")
