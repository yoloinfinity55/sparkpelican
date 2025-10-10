"""
AI Blog Post Generation Module

Uses Google Gemini AI to generate blog posts from YouTube transcripts.
Handles content processing, summarization, and Markdown formatting.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, Optional, List
import logging

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

from slugify import slugify

logger = logging.getLogger(__name__)

class AIGenerationError(Exception):
    """Custom exception for AI generation errors."""
    pass

class AIGenerator:
    """AI-powered blog post generator using Google Gemini."""

    def __init__(self):
        """Initialize the AI generator with Gemini configuration."""
        if not GEMINI_AVAILABLE:
            raise AIGenerationError("google-generativeai not installed")

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            raise AIGenerationError("GEMINI_API_KEY environment variable not set")

        genai.configure(api_key=api_key)

        # Use Gemini 1.5 Flash for text generation (updated model name)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

        # Configure generation parameters
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.8,
            top_k=40,
            max_output_tokens=4096,
        )

    async def generate_post_async(
        self,
        transcript: str,
        video_id: str,
        custom_title: Optional[str] = None,
        category: str = "General",
        tags: List[str] = None
    ) -> Dict[str, str]:
        """
        Generate a complete blog post from YouTube transcript.

        Args:
            transcript: Video transcript text
            video_id: YouTube video ID
            custom_title: User-specified title (optional)
            category: Post category
            tags: List of tags

        Returns:
            Dict containing post data: title, content, slug, etc.
        """
        try:
            # Generate different parts concurrently
            title_task = self._generate_title(transcript, custom_title)
            content_task = self._generate_content(transcript, video_id)
            summary_task = self._generate_summary(transcript)
            tags_task = self._generate_tags(transcript, tags or [])

            # Wait for all tasks to complete
            title, content, summary, generated_tags = await asyncio.gather(
                title_task, content_task, summary_task, tags_task
            )

            # Create post slug
            post_slug = slugify(title)

            # Generate front matter
            front_matter = self._create_front_matter(
                title=title,
                date=datetime.now().isoformat(),
                author="AI Generated",
                category=category,
                tags=generated_tags,
                slug=post_slug,
                youtube_id=video_id,
                summary=summary
            )

            # Combine into full markdown
            full_content = f"---\n{front_matter}---\n\n{summary}\n\n{content}"

            return {
                "title": title,
                "slug": post_slug,
                "content": full_content,
                "front_matter": front_matter,
                "youtube_id": video_id,
                "category": category,
                "tags": generated_tags,
                "summary": summary
            }

        except Exception as e:
            logger.error(f"AI generation failed: {str(e)}")
            raise AIGenerationError(f"Failed to generate post: {str(e)}")

    async def _generate_title(self, transcript: str, custom_title: Optional[str]) -> str:
        """Generate an engaging title from the transcript."""
        if custom_title:
            return custom_title

        prompt = f"""
        Generate an engaging, SEO-friendly blog post title based on this YouTube video transcript.
        The title should be under 60 characters and capture the main topic.

        Transcript excerpt:
        {transcript[:1000]}...

        Title:
        """

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._call_gemini, prompt
            )
            return response.strip().strip('"').strip("'")
        except Exception as e:
            # Fallback title generation
            words = transcript.split()[:8]  # First 8 words
            if words:
                title = ' '.join(words)
                if len(title) > 50:
                    title = title[:47] + '...'
                return f"YouTube Video: {title}"
            return "YouTube Video Content"

    async def _generate_content(self, transcript: str, video_id: str) -> str:
        """Generate detailed blog post content from transcript."""
        prompt = f"""
        Create a comprehensive blog post based on this YouTube video transcript.
        Write in a conversational, engaging tone suitable for a technical blog.

        Requirements:
        - Start with an introduction that hooks the reader
        - Organize content with clear headings and subheadings
        - Include key takeaways and lessons learned
        - End with a conclusion
        - Use proper markdown formatting
        - Keep it informative and valuable

        Video ID: {video_id}

        Transcript:
        {transcript}

        Blog Post:
        """

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._call_gemini, prompt
            )
            return response.strip()
        except Exception as e:
            return f"Generated content from video {video_id}\n\n{transcript[:500]}..."

    async def _generate_summary(self, transcript: str) -> str:
        """Generate a concise summary of the video."""
        # First, try to generate summary with AI
        prompt = f"""
        Create a brief, engaging summary (2-3 sentences) of this YouTube video transcript.
        Capture the main topic and key insights.

        Transcript:
        {transcript[:2000]}...

        Summary:
        """

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._call_gemini, prompt
            )
            summary = response.strip()
            # Ensure we got a meaningful response
            if len(summary) > 20 and not summary.lower().startswith(('error', 'failed', 'unable')):
                return summary
        except Exception as e:
            logger.warning(f"AI summary generation failed: {str(e)}")

        # Fallback: Generate summary from transcript content
        return self._generate_fallback_summary(transcript)

    def _generate_fallback_summary(self, transcript: str) -> str:
        """Generate a fallback summary when AI fails."""
        try:
            # Extract first meaningful sentences from transcript
            sentences = transcript.split('.')
            meaningful_sentences = []

            for sentence in sentences[:10]:  # Check first 10 sentences
                sentence = sentence.strip()
                if len(sentence) > 20 and not sentence.startswith(('Hey', 'Hi', 'Hello', 'So', 'Okay', 'Alright')):
                    meaningful_sentences.append(sentence)
                    if len(meaningful_sentences) >= 2:
                        break

            if meaningful_sentences:
                # Create a summary from the first meaningful sentences
                summary = '. '.join(meaningful_sentences[:2])
                if not summary.endswith('.'):
                    summary += '.'

                # Clean up common filler words and make it more readable
                summary = summary.replace(' um ', ' ').replace(' uh ', ' ')
                return summary

            # If no meaningful sentences found, create a generic summary
            words = transcript.split()[:50]  # First 50 words
            if words:
                summary = ' '.join(words)
                if len(summary) > 100:
                    summary = summary[:97] + '...'
                return summary

            return "Video content summary generated from transcript."

        except Exception as e:
            logger.warning(f"Fallback summary generation failed: {str(e)}")
            return "Video content summary generated from transcript."

    async def _generate_tags(self, transcript: str, custom_tags: List[str]) -> List[str]:
        """Generate relevant tags for the post."""
        if custom_tags:
            return custom_tags

        prompt = f"""
        Generate 5-8 relevant tags for a blog post based on this YouTube transcript.
        Tags should be lowercase, comma-separated, and relevant to the content.

        Transcript:
        {transcript[:1500]}...

        Tags (comma-separated):
        """

        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._call_gemini, prompt
            )
            # Parse comma-separated tags
            tags = [tag.strip().lower() for tag in response.split(',') if tag.strip()]
            return tags[:8]  # Limit to 8 tags
        except Exception as e:
            return ["youtube", "video", "content"]

    def _call_gemini(self, prompt: str) -> str:
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

    def _create_front_matter(
        self,
        title: str,
        date: str,
        author: str,
        category: str,
        tags: List[str],
        slug: str,
        youtube_id: str,
        summary: str
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
        return '\n'.join(front_matter_lines)

# Global generator instance
_generator_instance = None

async def generate_post_async(**kwargs) -> Dict[str, str]:
    """
    Convenience function to generate a post.

    Sets up the generator instance if needed and calls the generation method.
    """
    global _generator_instance

    if _generator_instance is None:
        _generator_instance = AIGenerator()

    return await _generator_instance.generate_post_async(**kwargs)
