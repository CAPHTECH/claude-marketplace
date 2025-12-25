#!/usr/bin/env python3
"""
Book Structure Validator for Technical Books

Validates book structure including:
- Broken internal links
- Chapter numbering consistency
- Table of contents alignment
- Missing or duplicate chapter IDs

Usage:
    python check_book_structure.py <book_directory>
    python check_book_structure.py <book_directory> --toc table_of_contents.md

Examples:
    # Validate book structure
    python check_book_structure.py ./book

    # Validate with specific TOC file
    python check_book_structure.py ./book --toc toc.md
"""

import re
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Set, Tuple
from collections import defaultdict


class Chapter:
    """Represents a chapter in the book."""

    def __init__(self, path: Path, number: str = None, title: str = None):
        self.path = path
        self.number = number
        self.title = title
        self.links = []  # Internal links found in this chapter

    def __repr__(self):
        return f"Chapter(number={self.number}, title={self.title}, path={self.path.name})"


def extract_chapter_info(content: str) -> Tuple[str, str]:
    """
    Extract chapter number and title from markdown content.
    Looks for patterns like: # Chapter 1: Introduction
    """
    lines = content.split('\n')
    for line in lines:
        # Match: # Chapter N: Title or # N. Title
        match = re.match(r'^#\s+(?:Chapter\s+)?(\d+)[\.:]\s+(.+)$', line, re.IGNORECASE)
        if match:
            return match.group(1), match.group(2).strip()

        # Match: # Title (assume it's chapter 1 if no number found)
        match = re.match(r'^#\s+([^#\n]+)$', line)
        if match:
            return None, match.group(1).strip()

    return None, None


def extract_internal_links(content: str, file_path: Path) -> List[Dict]:
    """
    Extract internal links from markdown content.
    Returns list of dicts with link text, target, and line number.
    """
    links = []
    lines = content.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Match markdown links: [text](target)
        for match in re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', line):
            link_text = match.group(1)
            target = match.group(2)

            # Only process internal links (not URLs)
            if not target.startswith(('http://', 'https://', 'mailto:', '#')):
                links.append({
                    'text': link_text,
                    'target': target,
                    'line': line_num,
                    'file': str(file_path)
                })

    return links


def load_chapters(book_dir: Path) -> List[Chapter]:
    """Load all chapters from book directory."""
    chapters = []

    # Find all markdown files
    md_files = sorted(book_dir.rglob('*.md'))

    for md_file in md_files:
        # Skip TOC and README files
        if md_file.name.lower() in ['readme.md', 'toc.md', 'table_of_contents.md']:
            continue

        content = md_file.read_text(encoding='utf-8')
        number, title = extract_chapter_info(content)

        chapter = Chapter(md_file, number, title)
        chapter.links = extract_internal_links(content, md_file)
        chapters.append(chapter)

    return chapters


def check_broken_links(chapters: List[Chapter], book_dir: Path) -> List[Dict]:
    """Check for broken internal links."""
    errors = []

    # Build set of existing files
    existing_files = {f.relative_to(book_dir) for f in book_dir.rglob('*') if f.is_file()}

    for chapter in chapters:
        chapter_dir = chapter.path.parent

        for link in chapter.links:
            target = link['target']

            # Handle anchor links within same file
            if target.startswith('#'):
                continue

            # Remove anchor from target
            target_path = target.split('#')[0]

            # Resolve relative path
            full_path = (chapter_dir / target_path).resolve()
            relative_path = full_path.relative_to(book_dir.resolve())

            if relative_path not in existing_files:
                errors.append({
                    'type': 'broken_link',
                    'file': link['file'],
                    'line': link['line'],
                    'link_text': link['text'],
                    'target': target,
                    'message': f"Link target does not exist: {target}"
                })

    return errors


def check_chapter_numbering(chapters: List[Chapter]) -> List[Dict]:
    """Check for inconsistent or duplicate chapter numbering."""
    errors = []
    seen_numbers = defaultdict(list)

    for chapter in chapters:
        if chapter.number:
            seen_numbers[chapter.number].append(chapter)

    # Check for duplicates
    for number, chapter_list in seen_numbers.items():
        if len(chapter_list) > 1:
            for chapter in chapter_list:
                errors.append({
                    'type': 'duplicate_chapter_number',
                    'file': str(chapter.path),
                    'number': number,
                    'message': f"Duplicate chapter number: {number}"
                })

    # Check for gaps in numbering
    if seen_numbers:
        numbers = sorted([int(n) for n in seen_numbers.keys()])
        for i in range(len(numbers) - 1):
            if numbers[i+1] - numbers[i] > 1:
                errors.append({
                    'type': 'chapter_numbering_gap',
                    'message': f"Gap in chapter numbering: missing chapter(s) between {numbers[i]} and {numbers[i+1]}"
                })

    return errors


def check_toc_alignment(chapters: List[Chapter], toc_file: Path) -> List[Dict]:
    """Check if TOC aligns with actual chapters."""
    errors = []

    if not toc_file or not toc_file.exists():
        return errors

    toc_content = toc_file.read_text(encoding='utf-8')

    # Extract chapter references from TOC
    toc_chapters = {}
    for line in toc_content.split('\n'):
        # Match TOC entries like: - [Chapter 1: Title](path/to/chapter.md)
        match = re.search(r'\[(?:Chapter\s+)?(\d+)[\.:]\s+([^\]]+)\]\(([^)]+)\)', line, re.IGNORECASE)
        if match:
            number = match.group(1)
            title = match.group(2).strip()
            path = match.group(3)
            toc_chapters[number] = {'title': title, 'path': path}

    # Build actual chapters map
    actual_chapters = {c.number: c for c in chapters if c.number}

    # Check for chapters in TOC but not in book
    for number, toc_info in toc_chapters.items():
        if number not in actual_chapters:
            errors.append({
                'type': 'toc_missing_chapter',
                'file': str(toc_file),
                'number': number,
                'message': f"TOC references chapter {number} but it doesn't exist: {toc_info['path']}"
            })

    # Check for chapters in book but not in TOC
    for number, chapter in actual_chapters.items():
        if number not in toc_chapters:
            errors.append({
                'type': 'chapter_missing_in_toc',
                'file': str(chapter.path),
                'number': number,
                'message': f"Chapter {number} exists but is not in TOC: {chapter.path.name}"
            })

    return errors


def print_errors(errors: List[Dict], error_type: str):
    """Print errors of a specific type."""
    type_errors = [e for e in errors if e['type'] == error_type]

    if not type_errors:
        return

    print(f"\n{error_type.upper().replace('_', ' ')}:")
    print('─' * 70)

    for error in type_errors:
        if 'file' in error and 'line' in error:
            print(f"  {error['file']}:{error['line']}")
        elif 'file' in error:
            print(f"  {error['file']}")

        print(f"  → {error['message']}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description='Validate technical book structure and consistency'
    )
    parser.add_argument(
        'book_dir',
        help='Directory containing book chapters'
    )
    parser.add_argument(
        '--toc',
        help='Table of contents file (optional)'
    )

    args = parser.parse_args()
    book_dir = Path(args.book_dir)

    if not book_dir.exists() or not book_dir.is_dir():
        print(f"Error: '{book_dir}' is not a valid directory", file=sys.stderr)
        sys.exit(1)

    toc_file = Path(args.toc) if args.toc else None

    print(f"{'='*70}")
    print(f"Validating book structure: {book_dir}")
    print(f"{'='*70}")

    # Load chapters
    chapters = load_chapters(book_dir)
    print(f"\nFound {len(chapters)} chapter(s)")

    # Run validations
    all_errors = []

    print("\nChecking broken links...")
    all_errors.extend(check_broken_links(chapters, book_dir))

    print("Checking chapter numbering...")
    all_errors.extend(check_chapter_numbering(chapters))

    if toc_file:
        print(f"Checking TOC alignment ({toc_file})...")
        all_errors.extend(check_toc_alignment(chapters, toc_file))

    # Print results
    if all_errors:
        print(f"\n{'='*70}")
        print(f"FOUND {len(all_errors)} ERROR(S)")
        print(f"{'='*70}")

        error_types = set(e['type'] for e in all_errors)
        for error_type in sorted(error_types):
            print_errors(all_errors, error_type)

        sys.exit(1)
    else:
        print(f"\n{'='*70}")
        print("✓ All validations passed!")
        print(f"{'='*70}")
        sys.exit(0)


if __name__ == '__main__':
    main()
