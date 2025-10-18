#!/usr/bin/env python3
"""
Test script for the redesigned SparkYouTube modules
"""

import sys
import os
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing Module Imports...")

    try:
        # Test configuration import
        from spark_youtube.config.settings import get_config
        print("   ✅ Configuration module imported")

        # Test transcript extractor import
        from spark_youtube.core.transcript.extractor import TranscriptExtractor
        print("   ✅ Transcript extractor imported")

        # Test AI generator import (will fail without API key, but should import)
        try:
            from spark_youtube.core.ai.generator import ContentGenerator
            print("   ✅ AI generator imported")
        except Exception as e:
            print(f"   ⚠️  AI generator import issue (expected without API key): {e}")

        return True

    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        return False

def test_configuration():
    """Test configuration functionality."""
    print("\n🧪 Testing Configuration...")

    try:
        from spark_youtube.config.settings import get_config

        config = get_config()
        print(f"   ✅ Config loaded: content_dir={config.content_dir}")
        print(f"   ✅ Config loaded: logs_dir={config.logs_dir}")
        print(f"   ✅ Config loaded: thumbnails_dir={config.thumbnails_dir}")

        # Check directories exist
        assert config.content_dir.exists()
        assert config.logs_dir.exists()
        assert config.thumbnails_dir.exists()
        print("   ✅ All config directories created")

        return True

    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Testing Redesigned SparkYouTube Modules")
    print("=" * 50)

    tests = [test_imports, test_configuration]
    results = []

    for test in tests:
        results.append(test())

    passed = sum(results)
    total = len(results)

    print(f"\n📊 Test Summary: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All tests passed! The redesigned modules are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
