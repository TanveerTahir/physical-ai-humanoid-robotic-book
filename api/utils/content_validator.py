"""
Content validation utilities for the Physical AI & Humanoid Robotics textbook platform.
This module provides utilities for validating textbook content quality and consistency.
"""
import re
from typing import List, Dict, Any, Optional
from urllib.parse import urlparse
import requests
from ..models.chapter import Chapter


class ContentValidator:
    """
    Utility class for validating textbook content quality and consistency.
    """

    @staticmethod
    def validate_chapter_structure(chapter: Chapter) -> Dict[str, Any]:
        """
        Validate the basic structure of a chapter.
        """
        errors = []
        warnings = []

        # Validate required fields
        if not chapter.title or len(chapter.title.strip()) == 0:
            errors.append("Chapter title is required")

        if not chapter.slug or len(chapter.slug.strip()) == 0:
            errors.append("Chapter slug is required")

        if not chapter.content or len(chapter.content.strip()) == 0:
            errors.append("Chapter content is required")

        # Validate slug format (should be URL-friendly)
        if chapter.slug:
            if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', chapter.slug):
                warnings.append("Slug should be URL-friendly (lowercase, hyphens only)")

        # Validate content length (should have minimum content)
        if chapter.content and len(chapter.content.strip()) < 100:
            warnings.append("Chapter content seems very short (< 100 characters)")

        # Check for common content elements
        content_lower = chapter.content.lower() if chapter.content else ""

        # Check if learning objectives are present
        if not chapter.learning_objectives or len(chapter.learning_objectives) == 0:
            warnings.append("No learning objectives specified")

        # Check if prerequisites are mentioned
        if not chapter.prerequisites or len(chapter.prerequisites) == 0:
            warnings.append("No prerequisites specified")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    @staticmethod
    def validate_gpu_jetson_notes(chapter: Chapter) -> Dict[str, Any]:
        """
        Validate GPU/Jetson compatibility notes are present and appropriate.
        """
        errors = []
        warnings = []

        # According to constitution, each chapter should have GPU/Jetson notes
        if not chapter.gpu_notes and not chapter.jetson_notes:
            warnings.append("No GPU or Jetson compatibility notes provided")

        # If both are provided, check they're different and appropriate
        if chapter.gpu_notes and chapter.jetson_notes:
            if chapter.gpu_notes.strip() == chapter.jetson_notes.strip():
                warnings.append("GPU and Jetson notes are identical - consider if both are needed")

        # Check if notes indicate no hardware requirements
        if chapter.gpu_notes and "not required" in chapter.gpu_notes.lower():
            warnings.append("GPU not required - confirm this is intentional for a robotics textbook")

        if chapter.jetson_notes and "not required" in chapter.jetson_notes.lower():
            warnings.append("Jetson not required - confirm this is intentional for a robotics textbook")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    @staticmethod
    def validate_links_in_content(content: str) -> Dict[str, Any]:
        """
        Validate links in chapter content.
        """
        errors = []
        warnings = []

        # Find all links in content (both markdown and HTML style)
        markdown_links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
        html_links = re.findall(r'<a\s+href=["\']([^"\']+)["\'][^>]*>', content)
        all_links = markdown_links + [(None, link) for link in html_links]

        # Validate each link
        for link_text, url in all_links:
            try:
                parsed = urlparse(url)
                if parsed.scheme in ['http', 'https']:
                    # For external links, just validate format
                    if not parsed.netloc:
                        errors.append(f"Invalid URL format: {url}")
                elif parsed.scheme in ['', 'file']:
                    # For relative links, check format
                    if not url.startswith('/') and not url.startswith('./') and not url.startswith('../'):
                        warnings.append(f"Relative link might be malformed: {url}")
                else:
                    errors.append(f"Unsupported URL scheme: {url}")
            except Exception as e:
                errors.append(f"Error parsing URL {url}: {str(e)}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "total_links_found": len(all_links)
        }

    @staticmethod
    def validate_code_examples(content: str) -> Dict[str, Any]:
        """
        Validate code examples in chapter content.
        """
        errors = []
        warnings = []

        # Find all code blocks
        code_blocks = re.findall(r'```(\w*)\n(.*?)```', content, re.DOTALL)

        # Check for language specification
        for lang, code in code_blocks:
            if not lang or lang.strip() == '':
                warnings.append("Code block missing language specification")

        # Check for common robotics/ROS patterns that should be present in appropriate chapters
        content_lower = content.lower()

        # If chapter mentions ROS, check for common ROS patterns
        if 'ros' in content_lower:
            if not re.search(r'#?include\s+.*rclcpp', content) and not re.search(r'import.*rclpy', content):
                warnings.append("ROS chapter should include rclcpp/rclpy imports")

        # If chapter mentions Python, check for common Python patterns
        if 'python' in content_lower:
            if not re.search(r'def\s+\w+\s*\(', content):
                warnings.append("Python chapter should include function definitions")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "code_blocks_found": len(code_blocks)
        }

    @staticmethod
    def validate_terminology_consistency(content: str, terminology_dict: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Validate terminology consistency in chapter content.
        """
        errors = []
        warnings = []

        # Default robotics terminology to check
        default_terminology = {
            "robotics": ["robotics", "robotic"],
            "ai": ["ai", "artificial intelligence", "artificial-intelligence", "A.I."],
            "ros": ["ros", "ros2", "ros 2"],
            "urdf": ["urdf", "unified robot description format"],
            "gazebo": ["gazebo"],
            "isaac": ["isaac", "isaac sim", "isaac-sim"],
            "jetson": ["jetson", "nvidia jetson"],
            "gpu": ["gpu", "graphics processing unit"]
        }

        # Use provided terminology or default
        check_terminology = terminology_dict if terminology_dict else default_terminology

        content_lower = content.lower()

        # Check for consistent terminology usage
        for term, variations in check_terminology.items():
            found_variations = []
            for variation in variations:
                if variation.lower() in content_lower:
                    found_variations.append(variation)

            # If multiple variations of the same term are found, it's inconsistent
            if len(found_variations) > 1:
                warnings.append(f"Multiple variations of '{term}' found: {', '.join(found_variations)}. Consider standardizing.")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "terminology_issues": len(warnings)
        }

    @staticmethod
    def full_content_validation(chapter: Chapter, terminology_dict: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Perform full content validation on a chapter.
        """
        structure_validation = ContentValidator.validate_chapter_structure(chapter)
        gpu_validation = ContentValidator.validate_gpu_jetson_notes(chapter)
        links_validation = ContentValidator.validate_links_in_content(chapter.content or "")
        code_validation = ContentValidator.validate_code_examples(chapter.content or "")
        terminology_validation = ContentValidator.validate_terminology_consistency(
            chapter.content or "", terminology_dict
        )

        all_errors = (
            structure_validation["errors"] +
            gpu_validation["errors"] +
            links_validation["errors"] +
            code_validation["errors"]
        )

        all_warnings = (
            structure_validation["warnings"] +
            gpu_validation["warnings"] +
            links_validation["warnings"] +
            code_validation["warnings"] +
            terminology_validation["warnings"]
        )

        return {
            "valid": len(all_errors) == 0,
            "overall_score": 100 - (len(all_errors) * 10) - (len(all_warnings) * 2),  # Score from 0-100
            "structure_validation": structure_validation,
            "gpu_validation": gpu_validation,
            "links_validation": links_validation,
            "code_validation": code_validation,
            "terminology_validation": terminology_validation,
            "total_errors": len(all_errors),
            "total_warnings": len(all_warnings),
            "all_errors": all_errors,
            "all_warnings": all_warnings
        }


# Create a global content validator instance
content_validator = ContentValidator()