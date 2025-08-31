#!/usr/bin/env python3
"""
generate_langgraph_docling.py

Use Docling to read the LangGraph Motivation PDF and generate a narrative
Markdown file with one section per detected chunk (preferably per-slide).

This script will attempt to install `docling` if it's not already present.

Usage:
  python3 scripts/generate_langgraph_docling.py \
      --pdf docs/papers/LangChain_Academy_-_Introduction_to_LangGraph_-_Motivation.pdf \
      --out docs/langgraph-intro-motivation.md

"""
from __future__ import annotations

import argparse
import datetime
import subprocess
import sys
from pathlib import Path
import re


def ensure_docling():
    try:
        import docling  # type: ignore
    except Exception:
        print("Installing docling via pip... (this may take a while)")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "docling"]) 


def convert_with_docling(pdf_path: Path):
    from docling.document_converter import DocumentConverter
    converter = DocumentConverter()
    print(f"Converting {pdf_path} with Docling...")
    result = converter.convert(str(pdf_path))

    # Normalize to a document-like object
    doc = getattr(result, 'document', None) or getattr(result, 'doc', None) or result

    # 1) Try structured pages first
    pages = getattr(doc, 'pages', None)
    if pages:
        texts = []
        any_text = False
        for p in pages:
            text = None
            if hasattr(p, 'plain_text'):
                text = p.plain_text
            elif hasattr(p, 'text'):
                text = p.text
            elif isinstance(p, dict):
                text = p.get('text') or p.get('plain_text')
            text = (text or '').strip()
            texts.append(text)
            if len(text) > 20:
                any_text = True
        if any_text:
            print(f"Extracted {len(texts)} page(s) from doc.pages")
            return texts

    # 2) Try export to markdown
    if hasattr(doc, 'export_to_markdown'):
        try:
            md = doc.export_to_markdown()
        except Exception:
            md = ''
    else:
        md = ''

    if md and len(md) > 40:
        # Prefer splitting by explicit page markers if present, otherwise by top headings
        if '---PAGE' in md.upper() or '--- PAGE' in md.upper():
            chunks = re.split(r'-{3,}\s*PAGE\s*\d+', md, flags=re.IGNORECASE)
        else:
            parts = re.split(r'\n(?=#{1,3}\s)', md)
            chunks = [p.strip() for p in parts if p.strip()]
        print(f"Extracted markdown fallback with {len(chunks)} chunk(s)")
        return chunks

    # 3) Last resort: recursively search the object for long strings
    print("Attempting recursive search for text inside Docling result...")
    seen = set()

    def gather(obj, depth=0):
        if id(obj) in seen or depth > 6:
            return []
        seen.add(id(obj))
        texts = []
        if isinstance(obj, str):
            s = obj.strip()
            if len(s) > 40:
                texts.append(s)
            return texts
        if isinstance(obj, dict):
            for k, v in obj.items():
                texts += gather(v, depth + 1)
            return texts
        if isinstance(obj, (list, tuple, set)):
            for v in obj:
                texts += gather(v, depth + 1)
            return texts
        # try attributes
        for attr in dir(obj):
            if attr.startswith('_'):
                continue
            try:
                val = getattr(obj, attr)
            except Exception:
                continue
            texts += gather(val, depth + 1)
        return texts

    found = gather(doc)
    # Deduplicate and filter
    uniq = []
    for t in found:
        if t not in uniq:
            uniq.append(t)
    if uniq:
        print(f"Recursive search found {len(uniq)} text block(s)")
        return uniq

    # Nothing found; return an empty placeholder list with one empty string to keep downstream logic
    print("No text found via Docling result; returning empty placeholder")
    return ['']


def make_narrative(chunks: list[str], out_path: Path, source: Path):
    now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'
    header = ["---", "title: \"LangGraph — Pengantar & Motivasi (Docling)\"", "---", "", f"Sumber: {source}", f"Dihasilkan: {now}", ""]
    sections = []
    for i, c in enumerate(chunks, start=1):
        # Remove bullets and collapse lines into paragraphs
        text = re.sub(r'^[\s•\-–—]+', '', c, flags=re.M)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        if not text:
            text = '(Tidak ada teks yang terdeteksi pada bagian ini)'
        section = f"## Bagian {i}\n\n{text}\n"
        sections.append(section)

    out_path.write_text('\n'.join(header + sections), encoding='utf-8')
    print(f"Wrote narrative markdown to {out_path}")


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf', type=Path, default=Path('docs/papers/LangChain_Academy_-_Introduction_to_LangGraph_-_Motivation.pdf'))
    parser.add_argument('--out', type=Path, default=Path('docs/langgraph-intro-motivation.md'))
    parser.add_argument('--no-install', action='store_true')
    args = parser.parse_args(argv)

    pdf_path = args.pdf
    out_path = args.out

    if not pdf_path.exists():
        print(f"PDF not found: {pdf_path}")
        return 2

    if not args.no_install:
        ensure_docling()

    chunks = convert_with_docling(pdf_path)
    make_narrative(chunks, out_path, pdf_path)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
