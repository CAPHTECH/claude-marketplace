#!/usr/bin/env python3
"""
trace_doc_code.py - shirushi Doc-ID ↔ Code トレーサビリティ検証

使用方法:
  python3 trace_doc_code.py --src-dir src --docs-dir docs
  python3 trace_doc_code.py --src-dir src --docs-dir docs --output report.json
  python3 trace_doc_code.py --check  # CI用: エラーがあれば非ゼロ終了
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# Doc-ID パターン（shirushi形式）
DOC_ID_PATTERN = re.compile(r'<!--\s*Doc-ID:\s*([A-Z]+-[A-Z]+-\d{4}-[A-Z])\s*-->')
CODE_REF_PATTERN = re.compile(r'@shirushi\s+([A-Z]+-[A-Z]+-\d{4}-[A-Z])')

# 対象ファイル拡張子
CODE_EXTENSIONS = ['.ts', '.tsx', '.js', '.jsx', '.py', '.go', '.java', '.rs', '.rb']
DOC_EXTENSIONS = ['.md', '.mdx']


@dataclass
class DocId:
    """Doc-ID情報"""
    id: str
    file: str
    line: Optional[int] = None


@dataclass
class CodeRef:
    """コード内参照情報"""
    doc_id: str
    file: str
    line: int


@dataclass
class TraceReport:
    """トレーサビリティレポート"""
    doc_ids: list[DocId] = field(default_factory=list)
    code_refs: list[CodeRef] = field(default_factory=list)
    implemented: list[tuple[DocId, list[CodeRef]]] = field(default_factory=list)
    not_implemented: list[DocId] = field(default_factory=list)
    orphan_refs: list[CodeRef] = field(default_factory=list)

    def coverage(self) -> float:
        if not self.doc_ids:
            return 0.0
        return len(self.implemented) / len(self.doc_ids) * 100


def find_doc_ids(docs_dir: Path) -> list[DocId]:
    """ドキュメントからDoc-IDを収集"""
    doc_ids = []
    for ext in DOC_EXTENSIONS:
        for f in docs_dir.rglob(f'*{ext}'):
            try:
                content = f.read_text(encoding='utf-8')
                for i, line in enumerate(content.splitlines(), 1):
                    for match in DOC_ID_PATTERN.finditer(line):
                        doc_ids.append(DocId(
                            id=match.group(1),
                            file=str(f.relative_to(docs_dir.parent) if docs_dir.parent != f.parent else f),
                            line=i
                        ))
            except (UnicodeDecodeError, PermissionError):
                continue
    return doc_ids


def find_code_refs(src_dir: Path) -> list[CodeRef]:
    """コードからDoc-ID参照を収集"""
    refs = []
    for ext in CODE_EXTENSIONS:
        for f in src_dir.rglob(f'*{ext}'):
            try:
                content = f.read_text(encoding='utf-8')
                for i, line in enumerate(content.splitlines(), 1):
                    for match in CODE_REF_PATTERN.finditer(line):
                        refs.append(CodeRef(
                            doc_id=match.group(1),
                            file=str(f.relative_to(src_dir.parent) if src_dir.parent != f.parent else f),
                            line=i
                        ))
            except (UnicodeDecodeError, PermissionError):
                continue
    return refs


def analyze_traceability(doc_ids: list[DocId], code_refs: list[CodeRef]) -> TraceReport:
    """トレーサビリティを分析"""
    report = TraceReport(doc_ids=doc_ids, code_refs=code_refs)

    # Doc-IDをセットに変換
    doc_id_set = {d.id for d in doc_ids}

    # コード参照をDoc-IDでグループ化
    refs_by_doc_id: dict[str, list[CodeRef]] = {}
    for ref in code_refs:
        refs_by_doc_id.setdefault(ref.doc_id, []).append(ref)

    # 実装済みと未実装を分類
    for doc_id in doc_ids:
        if doc_id.id in refs_by_doc_id:
            report.implemented.append((doc_id, refs_by_doc_id[doc_id.id]))
        else:
            report.not_implemented.append(doc_id)

    # 孤立参照を検出
    for ref in code_refs:
        if ref.doc_id not in doc_id_set:
            report.orphan_refs.append(ref)

    return report


def print_report(report: TraceReport) -> None:
    """レポートを出力"""
    print("=" * 60)
    print("トレーサビリティ検証レポート")
    print("=" * 60)

    print(f"\n## サマリ")
    print(f"- 総Doc-ID数: {len(report.doc_ids)}")
    print(f"- コード参照あり: {len(report.implemented)} ({report.coverage():.1f}%)")
    print(f"- コード参照なし: {len(report.not_implemented)}")
    print(f"- 孤立参照: {len(report.orphan_refs)}件")

    if report.implemented:
        print(f"\n## ✅ 実装済み ({len(report.implemented)}件)")
        print("| Doc-ID | ドキュメント | コード参照 |")
        print("|--------|-------------|-----------|")
        for doc_id, refs in report.implemented:
            ref_str = ", ".join(f"{r.file}:{r.line}" for r in refs[:3])
            if len(refs) > 3:
                ref_str += f" (+{len(refs)-3})"
            print(f"| {doc_id.id} | {doc_id.file} | {ref_str} |")

    if report.not_implemented:
        print(f"\n## ⚠️ 未実装 ({len(report.not_implemented)}件)")
        print("| Doc-ID | ドキュメント |")
        print("|--------|-------------|")
        for doc_id in report.not_implemented:
            print(f"| {doc_id.id} | {doc_id.file} |")

    if report.orphan_refs:
        print(f"\n## ❌ 孤立参照 ({len(report.orphan_refs)}件)")
        print("| ファイル | 参照Doc-ID |")
        print("|---------|-----------|")
        for ref in report.orphan_refs:
            print(f"| {ref.file}:{ref.line} | {ref.doc_id} |")


def export_json(report: TraceReport) -> dict:
    """JSON形式でエクスポート"""
    return {
        "summary": {
            "total_doc_ids": len(report.doc_ids),
            "implemented": len(report.implemented),
            "not_implemented": len(report.not_implemented),
            "orphan_refs": len(report.orphan_refs),
            "coverage": report.coverage()
        },
        "implemented": [
            {
                "doc_id": doc_id.id,
                "doc_file": doc_id.file,
                "code_refs": [{"file": r.file, "line": r.line} for r in refs]
            }
            for doc_id, refs in report.implemented
        ],
        "not_implemented": [
            {"doc_id": d.id, "file": d.file}
            for d in report.not_implemented
        ],
        "orphan_refs": [
            {"doc_id": r.doc_id, "file": r.file, "line": r.line}
            for r in report.orphan_refs
        ]
    }


def main():
    parser = argparse.ArgumentParser(description='shirushi Doc-ID ↔ Code トレーサビリティ検証')
    parser.add_argument('--src-dir', type=Path, default=Path('src'), help='ソースコードディレクトリ')
    parser.add_argument('--docs-dir', type=Path, default=Path('docs'), help='ドキュメントディレクトリ')
    parser.add_argument('--output', type=Path, help='JSON出力ファイル')
    parser.add_argument('--check', action='store_true', help='CI用: エラーがあれば非ゼロ終了')
    args = parser.parse_args()

    # ディレクトリ存在確認
    if not args.src_dir.exists():
        print(f"警告: ソースディレクトリが存在しません: {args.src_dir}")
    if not args.docs_dir.exists():
        print(f"警告: ドキュメントディレクトリが存在しません: {args.docs_dir}")

    # 収集と分析
    doc_ids = find_doc_ids(args.docs_dir) if args.docs_dir.exists() else []
    code_refs = find_code_refs(args.src_dir) if args.src_dir.exists() else []
    report = analyze_traceability(doc_ids, code_refs)

    # レポート出力
    print_report(report)

    # JSON出力
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(export_json(report), f, indent=2, ensure_ascii=False)
        print(f"\nJSON出力: {args.output}")

    # CI用終了コード
    if args.check:
        if report.orphan_refs:
            print(f"\n❌ 孤立参照が{len(report.orphan_refs)}件あります")
            sys.exit(1)
        if report.not_implemented:
            print(f"\n⚠️ 未実装Doc-IDが{len(report.not_implemented)}件あります")
            # 未実装は警告のみ（終了コード0）
        print("\n✅ チェック完了")
        sys.exit(0)


if __name__ == '__main__':
    main()
