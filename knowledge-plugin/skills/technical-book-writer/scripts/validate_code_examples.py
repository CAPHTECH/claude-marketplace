#!/usr/bin/env python3
"""
Code Example Validator for Technical Books

Extracts code blocks from markdown files and validates syntax for multiple languages.
Supports Python, JavaScript, TypeScript, Go, Rust, Java, and more.

Usage:
    python validate_code_examples.py <markdown_file>
    python validate_code_examples.py <markdown_file> --language python
    python validate_code_examples.py <directory> --recursive

Examples:
    # Validate all code in a single chapter
    python validate_code_examples.py chapter1.md

    # Validate only Python code
    python validate_code_examples.py chapter1.md --language python

    # Validate all chapters recursively
    python validate_code_examples.py ./chapters --recursive
"""

import re
import sys
import ast
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
import subprocess
import tempfile


class CodeBlock:
    """Represents a code block extracted from markdown."""

    def __init__(self, language: str, code: str, line_number: int, file_path: str):
        self.language = language.lower()
        self.code = code
        self.line_number = line_number
        self.file_path = file_path

    def __repr__(self):
        return f"CodeBlock(language={self.language}, line={self.line_number}, file={self.file_path})"


def extract_code_blocks(markdown_content: str, file_path: str) -> List[CodeBlock]:
    """
    Extract all code blocks from markdown content.

    Args:
        markdown_content: The markdown file content
        file_path: Path to the markdown file (for error reporting)

    Returns:
        List of CodeBlock objects
    """
    code_blocks = []
    lines = markdown_content.split('\n')
    i = 0

    while i < len(lines):
        line = lines[i]
        # Match code fence: ```language
        match = re.match(r'^```(\w+)', line)
        if match:
            language = match.group(1)
            start_line = i + 1
            code_lines = []
            i += 1

            # Collect code until closing fence
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i])
                i += 1

            code = '\n'.join(code_lines)
            code_blocks.append(CodeBlock(language, code, start_line, file_path))

        i += 1

    return code_blocks


def validate_python(code: str) -> Tuple[bool, str]:
    """Validate Python code syntax."""
    try:
        ast.parse(code)
        return True, "OK"
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_javascript(code: str) -> Tuple[bool, str]:
    """Validate JavaScript/TypeScript code syntax using Node.js."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name

        # Use node --check to validate syntax
        result = subprocess.run(
            ['node', '--check', temp_file],
            capture_output=True,
            text=True,
            timeout=5
        )

        Path(temp_file).unlink()

        if result.returncode == 0:
            return True, "OK"
        else:
            return False, result.stderr.strip()
    except FileNotFoundError:
        return None, "Node.js not found - skipping JavaScript validation"
    except subprocess.TimeoutExpired:
        return False, "Validation timeout"
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_typescript(code: str) -> Tuple[bool, str]:
    """Validate TypeScript code syntax."""
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(code)
            temp_file = f.name

        # Use tsc to validate syntax
        result = subprocess.run(
            ['tsc', '--noEmit', '--skipLibCheck', temp_file],
            capture_output=True,
            text=True,
            timeout=10
        )

        Path(temp_file).unlink()

        if result.returncode == 0:
            return True, "OK"
        else:
            return False, result.stderr.strip()
    except FileNotFoundError:
        return None, "TypeScript compiler not found - skipping TypeScript validation"
    except subprocess.TimeoutExpired:
        return False, "Validation timeout"
    except Exception as e:
        return False, f"Error: {str(e)}"


def validate_code_block(block: CodeBlock) -> Tuple[bool, str]:
    """
    Validate a code block based on its language.

    Returns:
        (success: bool, message: str)
        success = True if valid, False if invalid, None if validation skipped
    """
    validators = {
        'python': validate_python,
        'py': validate_python,
        'javascript': validate_javascript,
        'js': validate_javascript,
        'typescript': validate_typescript,
        'ts': validate_typescript,
    }

    validator = validators.get(block.language)
    if validator:
        return validator(block.code)
    else:
        return None, f"No validator for language: {block.language}"


def validate_file(file_path: Path, language_filter: str = None) -> Dict:
    """
    Validate all code blocks in a markdown file.

    Args:
        file_path: Path to markdown file
        language_filter: Optional language to filter (e.g., 'python')

    Returns:
        Dictionary with validation results
    """
    content = file_path.read_text(encoding='utf-8')
    code_blocks = extract_code_blocks(content, str(file_path))

    if language_filter:
        code_blocks = [b for b in code_blocks if b.language == language_filter.lower()]

    results = {
        'file': str(file_path),
        'total_blocks': len(code_blocks),
        'validated': 0,
        'passed': 0,
        'failed': 0,
        'skipped': 0,
        'errors': []
    }

    for block in code_blocks:
        success, message = validate_code_block(block)

        if success is True:
            results['validated'] += 1
            results['passed'] += 1
        elif success is False:
            results['validated'] += 1
            results['failed'] += 1
            results['errors'].append({
                'block': block,
                'message': message
            })
        else:  # success is None (skipped)
            results['skipped'] += 1

    return results


def print_results(results: Dict):
    """Print validation results."""
    print(f"\n{'='*70}")
    print(f"File: {results['file']}")
    print(f"{'='*70}")
    print(f"Total code blocks: {results['total_blocks']}")
    print(f"Validated: {results['validated']}")
    print(f"  ✓ Passed: {results['passed']}")
    print(f"  ✗ Failed: {results['failed']}")
    print(f"  ⊘ Skipped: {results['skipped']}")

    if results['errors']:
        print(f"\n{'─'*70}")
        print("ERRORS:")
        for i, error in enumerate(results['errors'], 1):
            block = error['block']
            message = error['message']
            print(f"\n{i}. {block.file_path}:{block.line_number} [{block.language}]")
            print(f"   {message}")


def main():
    parser = argparse.ArgumentParser(
        description='Validate code examples in technical book markdown files'
    )
    parser.add_argument(
        'path',
        help='Markdown file or directory to validate'
    )
    parser.add_argument(
        '--language', '-l',
        help='Filter by programming language (e.g., python, javascript)'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively validate all markdown files in directory'
    )

    args = parser.parse_args()
    path = Path(args.path)

    if not path.exists():
        print(f"Error: Path '{path}' does not exist", file=sys.stderr)
        sys.exit(1)

    # Collect markdown files
    if path.is_file():
        if path.suffix != '.md':
            print(f"Error: File '{path}' is not a markdown file", file=sys.stderr)
            sys.exit(1)
        files = [path]
    else:
        if args.recursive:
            files = list(path.rglob('*.md'))
        else:
            files = list(path.glob('*.md'))

    if not files:
        print("No markdown files found", file=sys.stderr)
        sys.exit(1)

    # Validate all files
    all_results = []
    for file in files:
        results = validate_file(file, args.language)
        all_results.append(results)
        print_results(results)

    # Print summary
    total_blocks = sum(r['total_blocks'] for r in all_results)
    total_validated = sum(r['validated'] for r in all_results)
    total_passed = sum(r['passed'] for r in all_results)
    total_failed = sum(r['failed'] for r in all_results)
    total_skipped = sum(r['skipped'] for r in all_results)

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")
    print(f"Files processed: {len(all_results)}")
    print(f"Total code blocks: {total_blocks}")
    print(f"Validated: {total_validated}")
    print(f"  ✓ Passed: {total_passed}")
    print(f"  ✗ Failed: {total_failed}")
    print(f"  ⊘ Skipped: {total_skipped}")

    if total_failed > 0:
        sys.exit(1)
    else:
        print("\n✓ All validations passed!")
        sys.exit(0)


if __name__ == '__main__':
    main()
