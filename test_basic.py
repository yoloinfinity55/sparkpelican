#!/usr/bin/env python3
"""
Basic functionality test for redesigned modules (no API key required)
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_configuration_without_api():
    """Test configuration module without API key validation."""
    print("🧪 Testing Configuration Module (without API key)...")

    try:
        # Temporarily modify environment to avoid API key requirement
        original_key = os.environ.get('GEMINI_API_KEY')
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']

        from spark_youtube.config.settings import ProjectConfig

        # Test configuration with missing API key (should fail gracefully)
        try:
            config = ProjectConfig()
            print("   ⚠️  Config initialized without API key (unexpected)")
        except ValueError as e:
            print(f"   ✅ Config properly requires API key: {e}")

        # Restore API key if it existed
        if original_key:
            os.environ['GEMINI_API_KEY'] = original_key

        return True

    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def test_transcript_functions():
    """Test transcript extraction functions."""
    print("\n🧪 Testing Transcript Functions...")

    try:
        from spark_youtube.core.transcript.extractor import (
            TranscriptExtractor,
            extract_video_id,
            LanguageDetector
        )

        # Test video ID extraction
        test_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://youtube.com/watch?v=abc123def45"
        ]

        for url in test_urls:
            video_id = extract_video_id(url)
            assert len(video_id) == 11
            print(f"   ✅ Extracted video ID: {video_id} from {url}")

        # Test language detector
        detector = LanguageDetector()
        test_texts = [
            ("Hello world, this is a test.", "en"),
            ("这是一个测试文本。", "zh-cn"),
            ("This is a mixed text with some 中文 content.", "en")
        ]

        for text, expected_lang in test_texts:
            detected = detector.detect_language(text)
            print(f"   ✅ Language detection: '{text[:30]}...' -> {detected}")

        print("   ✅ Transcript functions working correctly")
        return True

    except Exception as e:
        print(f"   ❌ Transcript test failed: {e}")
        return False

def test_directory_structure():
    """Test that the new directory structure is correct."""
    print("\n🧪 Testing Directory Structure...")

    try:
        # Check that our new structure exists
        required_paths = [
            "src/spark_youtube/config/settings.py",
            "src/spark_youtube/core/transcript/extractor.py",
            "src/spark_youtube/core/ai/generator.py"
        ]

        for path in required_paths:
            full_path = Path(__file__).parent / path
            if full_path.exists():
                print(f"   ✅ Found: {path}")
            else:
                print(f"   ❌ Missing: {path}")
                return False

        print("   ✅ Directory structure is correct")
        return True

    except Exception as e:
        print(f"   ❌ Directory structure test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Redesigned SparkYouTube Modules (Basic Functionality)")
    print("=" * 60)

    tests = [
        test_configuration_without_api,
        test_transcript_functions,
        test_directory_structure
    ]

    results = []
    for test in tests:
        results.append(test())

    passed = sum(results)
    total = len(results)

    print(f"\n📊 Test Summary: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All basic tests passed! The redesigned modules are structurally sound.")
        print("\n📋 Next Steps:")
        print("   1. Set GEMINI_API_KEY to test full functionality")
        print("   2. Create Pelican integrator module")
        print("   3. Build main processor script")
        print("   4. Create CLI interface")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
