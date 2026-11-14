#!/usr/bin/env python3
"""
compile_report_pdf.py - Compiles report/FINAL_TECHNICAL_REPORT.md to styled HTML and PDF.
Uses mistune for Markdown parsing, embeds fully offline academic CSS, and compiles to PDF via Edge headless.
"""

import os
import sys
import subprocess
from pathlib import Path
import mistune

ROOT_DIR = Path(__file__).resolve().parent.parent
REPORT_MD = ROOT_DIR / "report" / "FINAL_TECHNICAL_REPORT.md"
REPORT_HTML = ROOT_DIR / "report" / "FINAL_TECHNICAL_REPORT.html"
REPORT_PDF = ROOT_DIR / "report" / "FINAL_TECHNICAL_REPORT.pdf"

# Pure offline CSS - no external font imports or CDN scripts
ACADEMIC_CSS = """
<style>
:root {
  --primary: #1e3a8a;
  --secondary: #0f766e;
  --accent: #2563eb;
  --text: #1f2937;
  --text-light: #4b5563;
  --bg: #ffffff;
  --code-bg: #f8fafc;
  --border: #e2e8f0;
  --table-border: #cbd5e1;
}

* {
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: var(--text);
  background-color: var(--bg);
  line-height: 1.6;
  font-size: 10.5pt;
  margin: 0;
  padding: 30px;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

h1, h2, h3, h4, h5, h6 {
  font-family: Georgia, "Times New Roman", serif;
  color: #0f172a;
  font-weight: 700;
  line-height: 1.25;
  margin-top: 1.6em;
  margin-bottom: 0.5em;
}

h1 {
  font-size: 22pt;
  border-bottom: 3px solid var(--primary);
  padding-bottom: 8px;
  color: var(--primary);
  margin-top: 0;
}

h2 {
  font-size: 15pt;
  border-bottom: 1.5px solid var(--border);
  padding-bottom: 5px;
  color: #1e293b;
  page-break-after: avoid;
}

h3 {
  font-size: 12pt;
  color: var(--secondary);
  page-break-after: avoid;
}

h4 {
  font-size: 11pt;
  color: #334155;
  page-break-after: avoid;
}

p, ul, ol {
  margin-top: 0.4em;
  margin-bottom: 0.7em;
}

ul, ol {
  padding-left: 1.6em;
}

li {
  margin-bottom: 0.3em;
}

code {
  font-family: Consolas, "Courier New", monospace;
  font-size: 0.9em;
  background-color: var(--code-bg);
  padding: 0.15em 0.35em;
  border-radius: 3px;
  border: 1px solid #e2e8f0;
  color: #0f172a;
}

pre {
  background-color: #0f172a;
  color: #f8fafc;
  padding: 14px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85em;
  line-height: 1.45;
  border: 1px solid #334155;
  page-break-inside: avoid;
}

pre code {
  background-color: transparent;
  color: inherit;
  padding: 0;
  border: none;
  font-size: 1em;
}

blockquote {
  border-left: 4px solid var(--accent);
  margin: 1.2em 0;
  padding: 8px 16px;
  background-color: #f8fafc;
  color: #334155;
  font-style: italic;
  border-radius: 0 4px 4px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.2em 0;
  font-size: 0.85em;
  page-break-inside: avoid;
}

th, td {
  border: 1px solid var(--table-border);
  padding: 7px 10px;
  text-align: left;
  vertical-align: top;
}

th {
  background-color: #f1f5f9;
  font-weight: 700;
  color: #0f172a;
  border-bottom: 2px solid #94a3b8;
}

tr:nth-child(even) {
  background-color: #f8fafc;
}

hr {
  border: none;
  border-top: 1.5px solid #cbd5e1;
  margin: 1.8em 0;
}

a {
  color: var(--accent);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

@media print {
  body {
    padding: 0;
    max-width: 100%;
    font-size: 9.5pt;
    line-height: 1.45;
  }
  @page {
    margin: 1.5cm 1.2cm 1.5cm 1.2cm;
    size: letter portrait;
  }
  h1, h2, h3 {
    page-break-after: avoid;
  }
  table, pre, blockquote {
    page-break-inside: avoid;
  }
  a {
    color: #000;
    text-decoration: none;
  }
}
</style>
"""

def compile_markdown_to_html(md_path: Path, html_path: Path) -> str:
    print(f"Reading markdown: {md_path}")
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    markdown_parser = mistune.create_markdown(
        plugins=['table', 'url', 'strikethrough', 'task_lists']
    )
    body_html = markdown_parser(md_text)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Final Technical Report - Optimization Techniques</title>
  {ACADEMIC_CSS}
</head>
<body>
  {body_html}
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"Generated HTML: {html_path} ({os.path.getsize(html_path):,} bytes)")
    return full_html


def compile_html_to_pdf(html_path: Path, pdf_path: Path):
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_bin = None
    for p in edge_paths:
        if os.path.exists(p):
            edge_bin = p
            break

    if not edge_bin:
        raise FileNotFoundError("Microsoft Edge executable not found.")

    if pdf_path.exists():
        pdf_path.unlink()

    cmd = [
        edge_bin,
        "--headless=new",
        "--disable-gpu",
        "--no-sandbox",
        f"--print-to-pdf={str(pdf_path.resolve())}",
        str(html_path.resolve()),
    ]
    print(f"Compiling PDF using Edge headless: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

    # Edge on Windows may return teardown exit code 3221225477 (0xC0000005) after writing the PDF
    if pdf_path.exists() and pdf_path.stat().st_size > 0:
        print(f"Successfully generated PDF: {pdf_path} ({pdf_path.stat().st_size:,} bytes)")
    else:
        print(f"Edge exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        raise RuntimeError("PDF compilation failed: file was not generated.")


def main():
    if not REPORT_MD.exists():
        print(f"Error: {REPORT_MD} does not exist.")
        sys.exit(1)

    compile_markdown_to_html(REPORT_MD, REPORT_HTML)
    compile_html_to_pdf(REPORT_HTML, REPORT_PDF)
    print("Compilation completed successfully!")


if __name__ == "__main__":
    main()
