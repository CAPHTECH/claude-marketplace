#!/usr/bin/env python3
"""
Code Block Extractor for Technical Books

Extract code blocks from markdown files by language for external testing or compilation.

Usage:
    python extract_code_blocks.py <markdown_file> --language python --output ./code
    python extract_code_blocks.py <directory> --language javascript --recursive

Examples:
    # Extract all Python code from a chapter
    python extract_code_blocks.py chapter1.md --language python --output ./extracted

    # Extract all JavaScript code recursively
    python extract_code_blocks.py ./chapters --language javascript --recursive --output ./js_code
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict


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
    """Extract all code blocks from markdown content."""
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


def get_file_extension(language: str) -> str:
    """Map language name to file extension."""
    extensions = {
        'python': '.py',
        'py': '.py',
        'javascript': '.js',
        'js': '.js',
        'typescript': '.ts',
        'ts': '.ts',
        'java': '.java',
        'go': '.go',
        'rust': '.rs',
        'c': '.c',
        'cpp': '.cpp',
        'c++': '.cpp',
        'csharp': '.cs',
        'ruby': '.rb',
        'php': '.php',
        'swift': '.swift',
        'kotlin': '.kt',
        'dart': '.dart',
        'shell': '.sh',
        'bash': '.sh',
        'sql': '.sql',
        'html': '.html',
        'css': '.css',
        'json': '.json',
        'yaml': '.yaml',
        'yml': '.yml',
        'xml': '.xml',
        'markdown': '.md',
        'md': '.md',
    }
    return extensions.get(language.lower(), '.txt')


def extract_from_file(file_path: Path, language: str = None) -> List[CodeBlock]:
    """Extract code blocks from a single markdown file."""
    content = file_path.read_text(encoding='utf-8')
    blocks = extract_code_blocks(content, str(file_path))

    if language:
        blocks = [b for b in blocks if b.language == language.lower()]

    return blocks


def save_code_blocks(blocks: List[CodeBlock], output_dir: Path, merge: bool = False):
    """
    Save extracted code blocks to files.

    Args:
        blocks: List of code blocks to save
        output_dir: Directory to save extracted code
        merge: If True, merge all blocks into one file per language
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if merge:
        # Group by language
        by_language = {}
        for block in blocks:
            if block.language not in by_language:
                by_language[block.language] = []
            by_language[block.language].append(block)

        # Save one file per language
        for language, lang_blocks in by_language.items():
            ext = get_file_extension(language)
            output_file = output_dir / f"merged_{language}{ext}"

            with output_file.open('w', encoding='utf-8') as f:
                for i, block in enumerate(lang_blocks):
                    f.write(f"# Extracted from: {block.file_path}:{block.line_number}\n")
                    f.write(block.code)
                    f.write('\n\n')
                    if i < len(lang_blocks) - 1:
                        f.write(f"{'#' * 70}\n\n")

            print(f"✓ Saved {len(lang_blocks)} {language} block(s) to {output_file}")

    else:
        # Save individual files
        for i, block in enumerate(blocks):
            ext = get_file_extension(block.language)
            source_file = Path(block.file_path).stem
            output_file = output_dir / f"{source_file}_block{i+1}_{block.language}{ext}"

            with output_file.open('w', encoding='utf-8') as f:
                f.write(f"# Extracted from: {block.file_path}:{block.line_number}\n")
                f.write(block.code)
                f.write('\n')

            print(f"✓ Saved {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Extract code blocks from technical book markdown files'
    )
    parser.add_argument(
        'path',
        help='Markdown file or directory to extract from'
    )
    parser.add_argument(
        '--language', '-l',
        help='Filter by programming language (e.g., python, javascript)'
    )
    parser.add_argument(
        '--output', '-o',
        required=True,
        help='Output directory for extracted code'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Recursively process all markdown files in directory'
    )
    parser.add_argument(
        '--merge', '-m',
        action='store_true',
        help='Merge all blocks into one file per language'
    )

    args = parser.parse_args()
    path = Path(args.path)
    output_dir = Path(args.output)

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

    # Extract code blocks
    all_blocks = []
    for file in files:
        blocks = extract_from_file(file, args.language)
        all_blocks.extend(blocks)

    if not all_blocks:
        print(f"No code blocks found" + (f" for language '{args.language}'" if args.language else ""))
        sys.exit(0)

    print(f"\n{'='*70}")
    print(f"Extracted {len(all_blocks)} code block(s) from {len(files)} file(s)")
    print(f"{'='*70}\n")

    # Save extracted code
    save_code_blocks(all_blocks, output_dir, args.merge)

    print(f"\n✓ Code extraction complete!")
    print(f"  Output directory: {output_dir}")


if __name__ == '__main__':
    main()
