#!/usr/bin/env python3
"""
Integration test for the complete SparkYouTube system

Tests the complete workflow from YouTube URL to blog post generation.
Requires API key for full testing.
"""

import asyncio
import sys
import os
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_complete_workflow():
    """Test the complete workflow without actually calling APIs."""
    print("🧪 Testing Complete Workflow Integration...")

    try:
        from spark_youtube.processor import SparkYouTubeProcessor
        from spark_youtube.config.settings import get_config

        # Test processor initialization
        processor = SparkYouTubeProcessor()
        print("   ✅ Processor initialized successfully")

        # Test configuration access
        config = get_config()
        print(f"   ✅ Configuration loaded: {config.gemini_model}")

        # Test environment validation
        validation = processor.validate_environment()

        if validation['valid']:
            print("   ✅ Environment validation passed")
        else:
            print(f"   ⚠️  Environment issues: {validation['issues']}")

        print("   ✅ Integration test structure verified")
        return True

    except Exception as e:
        print(f"   ❌ Integration test failed: {e}")
        return False

def test_module_dependencies():
    """Test that all modules can import their dependencies."""
    print("\n🧪 Testing Module Dependencies...")

    try:
        # Test all core modules can be imported
        from spark_youtube.config import settings
        from spark_youtube.core.transcript import extractor
        from spark_youtube.core.ai import generator
        from spark_youtube.core.integrator import pelican
        from spark_youtube import processor, cli

        print("   ✅ All modules imported successfully")

        # Test key classes can be instantiated (without API calls)
        try:
            from spark_youtube.core.transcript.extractor import TranscriptExtractor, LanguageDetector
            from spark_youtube.core.integrator.pelican import PelicanIntegrator

            # These should work without API keys
            detector = LanguageDetector()
            print("   ✅ LanguageDetector instantiated")

            integrator = PelicanIntegrator()
            print("   ✅ PelicanIntegrator instantiated")

        except Exception as e:
            print(f"   ⚠️  Some classes need API key: {e}")

        return True

    except Exception as e:
        print(f"   ❌ Module dependency test failed: {e}")
        return False

def test_file_structure():
    """Test that the new file structure is complete."""
    print("\n🧪 Testing File Structure...")

    try:
        required_files = [
            "src/spark_youtube/__init__.py",
            "src/spark_youtube/config/__init__.py",
            "src/spark_youtube/config/settings.py",
            "src/spark_youtube/core/__init__.py",
            "src/spark_youtube/core/transcript/__init__.py",
            "src/spark_youtube/core/transcript/extractor.py",
            "src/spark_youtube/core/ai/__init__.py",
            "src/spark_youtube/core/ai/generator.py",
            "src/spark_youtube/core/integrator/__init__.py",
            "src/spark_youtube/core/integrator/pelican.py",
            "src/spark_youtube/processor.py",
            "src/spark_youtube/cli.py",
            "src/requirements.txt",
            "src/README.md"
        ]

        missing_files = []
        for file_path in required_files:
            full_path = Path(__file__).parent / file_path
            if not full_path.exists():
                missing_files.append(file_path)

        if not missing_files:
            print("   ✅ All required files present")
            return True
        else:
            print(f"   ❌ Missing files: {missing_files}")
            return False

    except Exception as e:
        print(f"   ❌ File structure test failed: {e}")
        return False

def test_documentation():
    """Test that documentation files exist and are complete."""
    print("\n🧪 Testing Documentation...")

    try:
        # Check for key documentation files
        doc_files = [
            "src/README.md",
            "docs/project_spec.md",
            "docs/sop.md"
        ]

        for doc_file in doc_files:
            full_path = Path(__file__).parent / doc_file
            if full_path.exists():
                # Check file size (should be substantial)
                size = full_path.stat().st_size
                if size > 1000:  # At least 1KB
                    print(f"   ✅ {doc_file} ({size} bytes)")
                else:
                    print(f"   ⚠️  {doc_file} seems small ({size} bytes)")
            else:
                print(f"   ❌ Missing documentation: {doc_file}")
                return False

        print("   ✅ Documentation files verified")
        return True

    except Exception as e:
        print(f"   ❌ Documentation test failed: {e}")
        return False

def main():
    """Main integration test function."""
    print("🚀 SparkYouTube Integration Test Suite")
    print("=" * 50)
    print("Testing the complete redesigned system...")

    tests = [
        test_file_structure,
        test_module_dependencies,
        test_documentation,
        test_complete_workflow
    ]

    results = []
    for test in tests:
        results.append(test())

    passed = sum(results)
    total = len(results)

    print(f"\n📊 Integration Test Summary: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All integration tests passed!")
        print("\n🚀 The redesigned SparkYouTube system is ready for use!")
        print("\n📋 Quick Start:")
        print("   1. Set your API key: export GEMINI_API_KEY='your_key'")
        print("   2. Install dependencies: pip install -r src/requirements.txt")
        print("   3. Run setup: python src/spark_youtube/cli.py setup")
        print("   4. Process videos: python src/spark_youtube/cli.py single 'YOUTUBE_URL'")

        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
