#!/usr/bin/env python3
"""
Automated validation script for Section B content quality.
This script validates that all chapters in Section B meet the educational quality standards.
"""
import os
import sys
import re
import yaml
from pathlib import Path
from typing import List, Dict, Tuple

def validate_frontmatter(file_path: str) -> Tuple[bool, List[str]]:
    """Validate the frontmatter of a markdown file."""
    errors = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if file starts with frontmatter
    if not content.startswith('---'):
        errors.append("File does not start with frontmatter (---)")
        return False, errors

    # Extract frontmatter
    parts = content.split('---', 2)
    if len(parts) < 3:
        errors.append("Could not extract frontmatter")
        return False, errors

    frontmatter_str = parts[1]

    try:
        frontmatter = yaml.safe_load(frontmatter_str)
    except yaml.YAMLError as e:
        errors.append(f"Invalid YAML in frontmatter: {e}")
        return False, errors

    # Check required fields
    required_fields = ['title', 'sidebar_position', 'description']
    for field in required_fields:
        if field not in frontmatter:
            errors.append(f"Missing required field: {field}")

    # Check for GPU/Jetson notes
    if 'gpu_notes' not in frontmatter:
        errors.append("Missing gpu_notes in frontmatter")
    if 'jetson_notes' not in frontmatter:
        errors.append("Missing jetson_notes in frontmatter")

    return len(errors) == 0, errors

def validate_content_structure(file_path: str) -> Tuple[bool, List[str]]:
    """Validate the structure of the content."""
    errors = []
    warnings = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for required sections
    required_sections = ['Prerequisites', 'Learning Objectives', 'Introduction', 'Summary']

    for section in required_sections:
        if f'## {section}' not in content and f'# {section}' not in content:
            errors.append(f"Missing required section: {section}")

    # Check for evaluation checkpoints
    if 'Evaluation Checkpoints' not in content and 'evaluation' not in content.lower():
        warnings.append("No evaluation checkpoints found")

    # Check for hands-on lab
    if 'Hands-on Lab' not in content and 'hands-on' not in content.lower():
        warnings.append("No hands-on lab found")

    # Check content length (should be substantial)
    if len(content) < 1000:  # At least 1000 characters
        errors.append("Content appears too short (<1000 characters)")

    return len(errors) == 0, errors, warnings

def validate_ros2_content(file_path: str) -> Tuple[bool, List[str]]:
    """Validate that ROS2-specific content exists."""
    errors = []
    warnings = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for ROS2 code examples
    code_blocks = re.findall(r'```python.*?```', content, re.DOTALL)
    ros2_indicators = ['rclpy', 'Node', 'create_publisher', 'create_subscription', 'Twist', 'JointState']

    has_ros2_code = any(indicator in content for indicator in ros2_indicators)
    if not has_ros2_code and len(code_blocks) > 0:
        warnings.append("No obvious ROS2 code indicators found in code examples")

    # Check for ROS2 concepts
    ros2_concepts = ['topics', 'services', 'actions', 'nodes', 'ROS2', 'publisher', 'subscriber']
    has_ros2_concepts = any(concept in content.lower() for concept in ros2_concepts)
    if not has_ros2_concepts:
        warnings.append("No ROS2 concepts mentioned in content")

    return len(errors) == 0, errors, warnings

def validate_chapter_completion(chapter_path: str) -> Tuple[bool, List[str], List[str]]:
    """Validate a single chapter."""
    all_errors = []
    all_warnings = []

    # Validate frontmatter
    valid, errors = validate_frontmatter(chapter_path)
    all_errors.extend(errors)

    # Validate content structure
    valid, errors, warnings = validate_content_structure(chapter_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    # Validate ROS2 content
    valid, errors, warnings = validate_ros2_content(chapter_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    return len(all_errors) == 0, all_errors, all_warnings

def validate_section_b() -> Tuple[bool, Dict[str, List[str]], Dict[str, List[str]]]:
    """Validate all chapters in Section B."""
    section_b_path = Path("book/docs/ros-nervous-system/")

    if not section_b_path.exists():
        return False, {"error": ["Section B directory not found"]}, {}

    chapter_files = list(section_b_path.glob("*.md"))

    if not chapter_files:
        return False, {"error": ["No chapter files found in Section B"]}, {}

    all_results = {}
    all_warnings = {}

    for chapter_file in chapter_files:
        print(f"Validating {chapter_file.name}...")
        valid, errors, warnings = validate_chapter_completion(str(chapter_file))

        if errors:
            all_results[str(chapter_file)] = errors
        if warnings:
            all_warnings[str(chapter_file)] = warnings

        status = "✓" if not errors else "✗"
        print(f"  {status} {chapter_file.name} ({len(errors)} errors, {len(warnings)} warnings)")

    overall_valid = len(all_results) == 0

    return overall_valid, all_results, all_warnings

def main():
    """Main function to run the validation."""
    print("Validating Section B content quality...")
    print("=" * 50)

    valid, errors, warnings = validate_section_b()

    print("\n" + "=" * 50)
    print("VALIDATION RESULTS:")
    print("=" * 50)

    if errors:
        print(f"\n❌ ERRORS FOUND ({len(errors)} files with errors):")
        for file_path, file_errors in errors.items():
            print(f"  {file_path}:")
            for error in file_errors:
                print(f"    - {error}")
    else:
        print("\n✅ NO ERRORS FOUND")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)} files with warnings):")
        for file_path, file_warnings in warnings.items():
            print(f"  {file_path}:")
            for warning in file_warnings:
                print(f"    - {warning}")
    else:
        print("\n✅ NO WARNINGS FOUND")

    print(f"\nOverall validation: {'✅ PASSED' if not errors else '❌ FAILED'}")

    # Return appropriate exit code
    sys.exit(0 if not errors else 1)

if __name__ == "__main__":
    main()