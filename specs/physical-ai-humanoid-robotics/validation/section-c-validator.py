#!/usr/bin/env python3
"""
Automated validation script for Section C content quality.
This script validates that all chapters in Section C meet the educational quality standards.
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

def validate_content_structure(file_path: str) -> Tuple[bool, List[str], List[str]]:
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

def validate_simulation_content(file_path: str) -> Tuple[bool, List[str], List[str]]:
    """Validate that simulation content exists."""
    errors = []
    warnings = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check for simulation concepts
    simulation_indicators = [
        'simulation', 'gazebo', 'physics', 'sensor', 'world', 'model', 'robot',
        'urdf', 'sdf', 'ros2', 'rclpy', 'isaac', 'unity', 'rendering', 'environment'
    ]

    has_simulation_content = any(indicator in content.lower() for indicator in simulation_indicators)
    if not has_simulation_content:
        warnings.append("No obvious simulation content indicators found")

    # Check for code examples
    code_blocks = re.findall(r'```.*?\n.*?\n```', content, re.DOTALL)
    if len(code_blocks) < 2:
        warnings.append(f"Few code examples found ({len(code_blocks)}, recommend at least 2)")

    # Check for diagrams/figures mentions
    diagram_keywords = ['diagram', 'figure', 'image', 'graph', 'chart', 'architecture', 'visualization']
    diagram_count = sum(1 for keyword in diagram_keywords if keyword.lower() in content.lower())

    if diagram_count < 1:
        warnings.append("No diagrams/figures mentioned in content")

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

    # Validate simulation content
    valid, errors, warnings = validate_simulation_content(chapter_path)
    all_errors.extend(errors)
    all_warnings.extend(warnings)

    return len(all_errors) == 0, all_errors, all_warnings

def validate_section_c() -> Tuple[bool, Dict[str, List[str]], Dict[str, List[str]]]:
    """Validate all chapters in Section C."""
    section_c_path = Path("book/docs/digital-twin/")

    if not section_c_path.exists():
        return False, {"error": ["Section C directory not found"]}, {}

    chapter_files = list(section_c_path.glob("*.md"))

    if not chapter_files:
        return False, {"error": ["No chapter files found in Section C"]}, {}

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
    print("Validating Section C content quality...")
    print("=" * 50)

    valid, errors, warnings = validate_section_c()

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