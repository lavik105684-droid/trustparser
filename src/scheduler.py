"""
Simple Workflow Generator for "Искра и Росток".
Checks which knowledge files need drafts, runs the orchestrator to generate them,
and triggers the HTML exporter for manual review.
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to sys.path to allow running directly from project root
sys.path.append(str(Path(__file__).parent.parent))

from src.botany_orchestrator import KnowledgeOrchestrator
from src.exporter import parse_and_export, create_preview_dir

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DRAFTS_DIR = Path("drafts")

def process_workflow():
    logger.info("Starting simplified content generation workflow...")

    # 1. Run the orchestrator to check for unprocessed knowledge files
    orchestrator = KnowledgeOrchestrator()
    orchestrator.run_scan()

    # 2. Automatically export any generated markdown drafts to HTML for manual review
    logger.info("Exporting available drafts to HTML...")
    create_preview_dir()

    if not DRAFTS_DIR.exists():
        logger.warning(f"Drafts directory not found: {DRAFTS_DIR}")
        return

    drafts = list(DRAFTS_DIR.glob("*.md"))
    if not drafts:
        logger.info("No drafts found to export.")
        return

    for draft in drafts:
        # Skip the .gitkeep or other non-content files
        if draft.stem.startswith("."):
            continue
        logger.info(f"Processing export for {draft.name}...")
        parse_and_export(draft.name)

    logger.info("Workflow completed successfully. Drafts and HTML previews are ready.")

if __name__ == "__main__":
    process_workflow()
