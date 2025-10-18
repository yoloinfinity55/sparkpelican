"""
AI Content Generation Module

Uses Google Gemini AI to generate high-quality blog posts from YouTube transcripts.
Supports multiple languages and provides structured, SEO-optimized content.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from spark_youtube.config.settings import get_config

logger = logging.getLogger(__name__)
config = get_config()

class AIGenerationError(Exception):
    """Custom exception for AI generation errors."""
    pass

class ContentGenerator:
    """AI-powered content generator using Google Gemini."""

    def __init__(self):
        """Initialize the AI generator."""
        if not GEMINI_AVAILABLE:
            raise AIGenerationError("google-generativeai not installed")

        if not config.gemini_api_key:
            raise AIGenerationError("GEMINI_API_KEY not configured")

        # Configure Gemini
        genai.configure(api_key=config.gemini_api_key)
        self.model = genai.GenerativeModel(config.gemini_model)

        # Generation config optimized for blog content
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.8,
            top_k=40,
            max_output_tokens=4096,
        )

    def _get_language_instructions(self, language: str) -> str:
        """Get language-specific instructions for content generation."""
        language_map = {
            'en': """LANGUAGE REQUIREMENTS:
- Write the entire blog post in English
- Use professional, clear English suitable for international readers
- Maintain formal tone appropriate for blog content
- Use proper English grammar and punctuation""",

            'zh-cn': """LANGUAGE REQUIREMENTS:
- Write the entire blog post in Chinese (Simplified Chinese)
- Use professional, clear Chinese suitable for readers
- Maintain formal tone appropriate for blog content
- Use proper Chinese grammar and punctuation""",

            'zh-tw': """LANGUAGE REQUIREMENTS:
- Write the entire blog post in Traditional Chinese
- Use professional, clear Traditional Chinese suitable for readers
- Maintain formal tone appropriate for blog content
- Use proper Traditional Chinese grammar and punctuation""",

            'ko': """LANGUAGE REQUIREMENTS:
- Write the entire blog post in Korean
- Use professional, clear Korean suitable for readers
- Maintain formal tone appropriate for blog content
- Use proper Korean grammar and punctuation""",

            'ja': """LANGUAGE REQUIREMENTS:
- Write the entire blog post in Japanese
- Use professional, clear Japanese suitable for readers
- Maintain formal tone appropriate for blog content
- Use proper Japanese grammar and punctuation""",

            'es': """LANGUAGE REQUIREMENTS:
- Write the entire blog post in Spanish
- Use professional, clear Spanish suitable for readers
- Maintain formal tone appropriate for blog content
- Use proper Spanish grammar and punctuation""",

            'fr': """LANGUAGE REQUIREMENTS:
- Write the entire blog post in French
- Use professional, clear French suitable for readers
- Maintain formal tone appropriate for blog content
- Use proper French grammar and punctuation""",

            'de': """LANGUAGE REQUIREMENTS:
- Write the entire blog post in German
- Use professional, clear German suitable for readers
- Maintain formal tone appropriate for blog content
- Use proper German grammar and punctuation"""
        }

        return language_map.get(language, language_map['en'])

    def _generate_title(self, transcript: str, language: str, custom_title: Optional[str] = None) -> str:
        """Generate SEO-optimized title from transcript."""
        if custom_title:
            return self._clean_title(custom_title)

        # Extract key topics for better context
        key_topics = self._extract_key_topics(transcript[:2000])

        prompt = f"""Generate a compelling blog post title based on this video transcript.

REQUIREMENTS:
- Length: 50-60 characters (strict limit)
- Format: Choose the most appropriate format:
  * "How to [Action] [Benefit]"
  * "[Number] Ways to [Achieve Result]"
  * "Complete Guide to [Topic]"
  * "Why [Topic] Matters for [Audience]"
  * "[Action]: A [Adjective] Guide"
- Include power words: Complete, Essential, Proven, Ultimate, Simple, Effective
- Focus on value proposition and benefits
- Remove video-specific words: "Watch", "Episode", "Part", "#"
- Must be clear, specific, and actionable
- Do NOT use quotes around the title

Key Topics Identified: {key_topics}

Transcript excerpt:
{transcript[:1500]}

Generate 3 title options:

Option 1:
Option 2:
Option 3:

Now select the BEST title and write it below with NO prefix, NO label, JUST the title text:

BEST TITLE:"""

        try:
            response = self._call_gemini_sync(prompt)
            title = self._extract_best_title(response)
            title = self._clean_title(title)
            title = self._optimize_title_length(title)

            logger.info(f"Generated title: {title} ({len(title)} chars)")
            return title

        except Exception as e:
            logger.warning(f"Title generation failed, using fallback: {str(e)}")
            return self._generate_fallback_title(transcript, key_topics)

    def _extract_key_topics(self, transcript_excerpt: str) -> str:
        """Extract 2-3 main topics from transcript for better title generation."""
        prompt = f"""Extract the 2-3 main topics from this transcript in 5 words or less.

Transcript:
{transcript_excerpt}

Main topics (comma-separated, 5 words max):"""

        try:
            response = self._call_gemini_sync(prompt)
            return response.strip()[:100]
        except:
            words = transcript_excerpt.split()[:50]
            return ' '.join(words[:10])

    def _clean_title(self, title: str) -> str:
        """Remove quotes, extra spaces, prefixes, and video-specific language."""
        if not title:
            return "Generated Blog Post"

        # Remove quotes
        title = title.strip().strip('"').strip("'").strip('`')

        # Remove "Title 1:", "Title 2:", etc. prefixes
        title = re.sub(r'^(Title|Option)\s*\d+:\s*', '', title, flags=re.IGNORECASE)

        # Remove "BEST TITLE:" prefix if present
        title = re.sub(r'^BEST\s*TITLE:\s*', '', title, flags=re.IGNORECASE)

        # Remove video-specific terms
        video_terms = ['watch this', 'in this video', 'episode', 'part', '#', '|']
        for term in video_terms:
            title = re.sub(term, '', title, flags=re.IGNORECASE)

        # Clean up extra spaces
        title = ' '.join(title.split())

        # Remove trailing ellipsis or "for..." artifacts
        title = re.sub(r'\s*\.\.\.$', '', title)
        title = re.sub(r'\s+for\.\.\.$', '', title)

        # Capitalize properly
        title = self._title_case(title)

        return title

    def _title_case(self, title: str) -> str:
        """Apply proper title case."""
        small_words = {'a', 'an', 'and', 'as', 'at', 'but', 'by', 'for', 'in', 'of', 'on', 'or', 'the', 'to', 'with'}
        words = title.split()

        if not words:
            return title

        # Always capitalize first and last word
        words[0] = words[0].capitalize()
        if len(words) > 1:
            words[-1] = words[-1].capitalize()

        # Handle middle words
        for i in range(1, len(words) - 1):
            if words[i].lower() not in small_words:
                words[i] = words[i].capitalize()
            else:
                words[i] = words[i].lower()

        return ' '.join(words)

    def _optimize_title_length(self, title: str) -> str:
        """Ensure title is 50-60 characters for SEO."""
        if len(title) <= 60:
            return title

        # Try to cut at word boundary
        if len(title) > 60:
            title = title[:57]
            last_space = title.rfind(' ')
            if last_space > 40:
                title = title[:last_space]
            # Don't add ellipsis - better to have clean cut

        return title

    def _extract_best_title(self, response: str) -> str:
        """Extract the best title from multi-option response."""
        lines = [l.strip() for l in response.split('\n') if l.strip()]

        # Look for "BEST TITLE" marker first
        for i, line in enumerate(lines):
            if 'BEST TITLE' in line.upper():
                # Get next non-empty line
                for j in range(i + 1, len(lines)):
                    candidate = lines[j].strip()
                    # Remove any prefix
                    candidate = re.sub(r'^(Title|Option)\s*\d+:\s*', '', candidate, flags=re.IGNORECASE)
                    candidate = re.sub(r'^BEST\s*TITLE:\s*', '', candidate, flags=re.IGNORECASE)
                    if candidate and len(candidate) > 10 and not candidate.startswith(('---', '*', 'Generate', 'Option')):
                        return candidate

        # Look for lines after "Option 1:", "Option 2:", etc.
        best_options = []
        for i, line in enumerate(lines):
            if re.match(r'^(Title|Option)\s*\d+:', line, re.IGNORECASE):
                # Extract the title part after the colon
                title_part = re.sub(r'^(Title|Option)\s*\d+:\s*', '', line, flags=re.IGNORECASE)
                if title_part and len(title_part) > 10:
                    best_options.append(title_part)
                # Check next line too
                elif i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if len(next_line) > 10 and not re.match(r'^(Title|Option)\s*\d+:', next_line, re.IGNORECASE):
                        best_options.append(next_line)

        # Return the last option (usually the refined one)
        if best_options:
            return best_options[-1]

        # Fallback: get last substantial non-empty line
        for line in reversed(lines):
            # Remove any prefix
            line = re.sub(r'^(Title|Option)\s*\d+:\s*', '', line, flags=re.IGNORECASE)
            line = re.sub(r'^BEST\s*TITLE:\s*', '', line, flags=re.IGNORECASE)
            if line and len(line) > 10 and not line.startswith(('---', '*', 'Generate', 'Create', 'Now select')):
                return line

        return "Generated Blog Post"

    def _generate_fallback_title(self, transcript: str, key_topics: str) -> str:
        """Generate a fallback title when AI fails."""
        sentences = transcript.split('.')[:5]
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 20 and len(sentence) < 100:
                title = sentence[:60]
                title = self._optimize_title_length(title)
                return self._clean_title(title)

        if key_topics:
            return f"Guide to {key_topics[:40]}"
        return "Essential Video Content Guide"

    def _generate_content(self, transcript: str, language: str) -> str:
        """Generate main blog content from transcript."""
        transcript_words = len(transcript.split())
        target_words = int(transcript_words * 0.5)  # Aim for 50% of original length

        language_instructions = self._get_language_instructions(language)

        prompt = f"""Transform this YouTube video transcript into a professional blog post.

{language_instructions}

CRITICAL REQUIREMENTS:
- Length: Approximately {target_words} words (50% of original)
- Remove ALL filler words: "um", "uh", "like", "you know", "basically", "actually"
- Remove repetitions and redundant explanations
- Focus ONLY on key insights and actionable information
- Write in clear, professional paragraphs (not spoken style)

STRUCTURE (must follow exactly):
## Introduction
[2-3 sentences: Hook reader + What they'll learn + Why it matters]

## Key Takeaways
[Bullet list: 3-5 main points - be specific and actionable]

## [Section 1 - Descriptive Heading]
[2-3 concise paragraphs covering first major topic]

## [Section 2 - Descriptive Heading]
[2-3 concise paragraphs covering second major topic]

## [Section 3 - Descriptive Heading]
[2-3 concise paragraphs covering third major topic]

## Practical Applications
[Bullet list: 3-4 specific action steps readers can take]

## Conclusion
[2-3 sentences: Summarize value + Call to action]

WRITING STYLE:
- Short paragraphs (2-4 sentences max)
- Active voice only
- Specific examples instead of vague statements
- One idea per paragraph
- Use subheadings for clarity
- Bold important terms sparingly

EXCLUDE:
- Any reference to "in this video", "the speaker says", timestamps
- Tangents and off-topic content
- Overly detailed explanations
- Marketing fluff

Transcript:
{transcript}

Blog Post (markdown format):"""

        try:
            response = self._call_gemini_sync(prompt)
            content = self._post_process_content(response)
            content_words = len(content.split())
            logger.info(f"Generated content: {content_words} words (target: {target_words}, ratio: {content_words/transcript_words:.1%})")

            return content

        except Exception as e:
            logger.error(f"Content generation failed: {str(e)}")
            return self._generate_fallback_content(transcript)

    def _post_process_content(self, content: str) -> str:
        """Clean up generated content."""
        filler_phrases = [
            r'\b(um|uh|like|you know|basically|actually)\b',
            r'\b(in this video|the speaker says|as mentioned)\b',
            r'\[.*?\]',
        ]

        for pattern in filler_phrases:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' +', ' ', content)

        return content.strip()

    def _generate_fallback_content(self, transcript: str) -> str:
        """Generate fallback content when AI fails."""
        words = transcript.split()
        content_length = min(len(words) // 2, 500)

        content = f"""## Introduction

This content is based on a YouTube video exploring important concepts and insights.

## Key Points

{' '.join(words[:content_length])}

## Conclusion

For the complete discussion, watch the original video."""

        return content

    def _generate_summary(self, transcript: str, language: str) -> str:
        """Generate concise, engaging summary."""
        language_instructions = self._get_language_instructions(language)

        prompt = f"""Create a compelling 2-3 sentence summary that makes someone want to read this blog post.

REQUIREMENTS:
- Length: 2-3 sentences (150 words max)
- First sentence: Hook with the main benefit or insight
- Second sentence: Key takeaway or learning
- Third sentence (optional): Who should read this or call to action
- Write in active voice, be specific
- Do NOT start with "This post/article/video discusses..."

{language_instructions}

Transcript excerpt:
{transcript[:2000]}

Summary:"""

        try:
            response = self._call_gemini_sync(prompt)
            summary = response.strip()

            if len(summary) > 20 and not any(word in summary.lower() for word in ['error', 'failed', 'unable']):
                return summary
        except Exception as e:
            logger.warning(f"Summary generation failed: {str(e)}")

        return self._generate_fallback_summary(transcript)

    def _generate_fallback_summary(self, transcript: str) -> str:
        """Generate fallback summary when AI fails."""
        try:
            sentences = [s.strip() for s in transcript.split('.') if len(s.strip()) > 30]
            meaningful = []

            for sentence in sentences[:15]:
                if not any(sentence.lower().startswith(word) for word in ['hey', 'hi', 'hello', 'so', 'okay', 'um', 'uh']):
                    meaningful.append(sentence)
                    if len(meaningful) >= 2:
                        break

            if meaningful:
                summary = '. '.join(meaningful[:2])
                if not summary.endswith('.'):
                    summary += '.'
                return summary

            words = transcript.split()[:40]
            return f"{' '.join(words)}..."

        except:
            return "Discover valuable insights and practical knowledge from this comprehensive video content."

    def _generate_tags(self, transcript: str, custom_tags: Optional[List[str]] = None) -> List[str]:
        """Generate relevant tags for the content."""
        if custom_tags:
            return [tag.lower().strip() for tag in custom_tags]

        prompt = f"""Generate 5-7 specific, relevant tags for this blog post.

REQUIREMENTS:
- Use lowercase, no spaces (use-hyphens-for-phrases)
- Be specific (not generic like "video" or "content")
- Include: topic keywords, technologies, concepts, target audience
- Avoid: overly broad terms, duplicates

Transcript:
{transcript[:1500]}

Tags (comma-separated):"""

        try:
            response = self._call_gemini_sync(prompt)
            tags = [tag.strip().lower() for tag in response.split(',') if tag.strip()]
            return tags[:7]
        except:
            return ["tutorial", "guide", "learning"]

    def _call_gemini_sync(self, prompt: str) -> str:
        """Synchronous Gemini API call."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            raise

    def generate_slug(self, title: str) -> str:
        """Generate URL-friendly slug from title."""
        if not title:
            return 'untitled'

        # Remove special characters and replace spaces with hyphens
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)  # Remove non-word chars except spaces and hyphens
        slug = re.sub(r'[\s_]+', '-', slug)   # Replace spaces/underscores with hyphens
        slug = slug.strip('-')
        return slug[:50]  # Limit length

    async def generate_post_data(
        self,
        transcript: str,
        video_id: str,
        language: str,
        custom_title: Optional[str] = None,
        category: str = None,
        tags: Optional[List[str]] = None,
        youtube_title: Optional[str] = None,
        youtube_thumbnail: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate complete post data from transcript."""
        try:
            # Generate content concurrently for better performance
            title_task = asyncio.get_event_loop().run_in_executor(
                None, self._generate_title, transcript, language, custom_title
            )
            content_task = asyncio.get_event_loop().run_in_executor(
                None, self._generate_content, transcript, language
            )
            summary_task = asyncio.get_event_loop().run_in_executor(
                None, self._generate_summary, transcript, language
            )
            tags_task = asyncio.get_event_loop().run_in_executor(
                None, self._generate_tags, transcript, tags
            )

            title, content, summary, generated_tags = await asyncio.gather(
                title_task, content_task, summary_task, tags_task
            )

            # Create post slug and filename
            post_slug = self.generate_slug(title)
            date_prefix = datetime.now().strftime("%Y-%m-%d")
            filename = f"{date_prefix}-{post_slug}.md"

            # Create front matter
            front_matter = self._create_front_matter(
                title=title,
                date=datetime.now().isoformat(),
                author=config.default_author,
                category=category or config.default_category,
                tags=generated_tags,
                slug=post_slug,
                youtube_id=video_id,
                summary=summary,
                youtube_thumbnail=youtube_thumbnail
            )

            # Combine into full markdown
            full_content = f"---\n{front_matter}---\n\n{summary}\n\n{content}"

            return {
                "title": title,
                "slug": post_slug,
                "content": full_content,
                "front_matter": front_matter,
                "youtube_id": video_id,
                "category": category or config.default_category,
                "tags": generated_tags,
                "summary": summary,
                "filename": filename,
                "language": language
            }

        except Exception as e:
            logger.error(f"Post generation failed: {str(e)}")
            raise AIGenerationError(f"Failed to generate post: {str(e)}")

    def _create_front_matter(
        self,
        title: str,
        date: str,
        author: str,
        category: str,
        tags: List[str],
        slug: str,
        youtube_id: str,
        summary: str,
        youtube_thumbnail: Optional[str] = None
    ) -> str:
        """Create Pelican front matter YAML."""
        front_matter_lines = [
            f"title: {title}",
            f"date: {date}",
            f"author: {author}",
            f"category: {category}",
            f"tags: {', '.join(tags)}",
            f"slug: {slug}",
            f"youtube_id: {youtube_id}",
            f"summary: {summary}"
        ]

        # Add image field if YouTube thumbnail is provided
        if youtube_thumbnail:
            # Convert absolute path to relative path for Pelican
            from pathlib import Path
            thumbnail_path = Path(youtube_thumbnail)
            try:
                # Get relative path from content directory
                relative_path = thumbnail_path.relative_to(self.content_dir.parent)
                front_matter_lines.append(f"image: {relative_path}")
            except ValueError:
                # Fallback to basename if path is not relative to content dir
                front_matter_lines.append(f"image: {thumbnail_path.name}")

        return '\n'.join(front_matter_lines)

# Convenience functions
async def generate_post_data(
    transcript: str,
    video_id: str,
    language: str,
    **kwargs
) -> Dict[str, Any]:
    """Generate post data using AI."""
    generator = ContentGenerator()
    return await generator.generate_post_data(transcript, video_id, language, **kwargs)
