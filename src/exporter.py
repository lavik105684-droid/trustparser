"""
Local HTML Exporter for Markdown Drafts.
This module parses a specified markdown file from the `/drafts` directory
and generates a clean, readable HTML file for local preview and manual approval.
"""

import os
import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DRAFTS_DIR = Path("drafts")
HTML_OUTPUT_DIR = Path("drafts/preview")

# Basic CSS template for clean local viewing
# Note: Using %s instead of {} to avoid KeyError with curly braces in CSS.
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>%s</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f9f9f9;
        }
        .container {
            background-color: #fff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        h1 {
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        code {
            background-color: #f1f1f1;
            padding: 2px 4px;
            border-radius: 4px;
            font-family: monospace;
        }
        pre code {
            display: block;
            padding: 15px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <pre style="white-space: pre-wrap; font-family: inherit;">%s</pre>
    </div>
</body>
</html>
"""

def create_preview_dir():
    if not HTML_OUTPUT_DIR.exists():
        HTML_OUTPUT_DIR.mkdir(parents=True)

def parse_and_export(filename: str):
    """Reads a markdown file and saves it inside an HTML template for easy viewing."""
    input_path = DRAFTS_DIR / filename

    if not input_path.exists():
        logger.error(f"File not found: {input_path}")
        return False

    logger.info(f"Parsing markdown from {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        md_text = f.read()

    # Extract a title (first h1 or just filename)
    title = filename
    first_line = md_text.split('\n')[0]
    if first_line.startswith('# '):
        title = first_line[2:].strip()

    # Wrap in template. Using basic text insertion inside a pre tag since external markdown lib is not available.
    final_html = HTML_TEMPLATE % (title, md_text)

    output_filename = input_path.stem + ".html"
    output_path = HTML_OUTPUT_DIR / output_filename

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_html)

    logger.info(f"Successfully generated HTML preview: {output_path}")
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export markdown draft to HTML.")
    parser.add_argument("filename", help="Name of the markdown file in the drafts directory (e.g., article_05_pest_control.md)")
    args = parser.parse_args()

    create_preview_dir()
    parse_and_export(args.filename)
