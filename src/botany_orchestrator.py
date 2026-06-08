"""
Botany Orchestrator
Scans the /knowledge directory for unprocessed .md files, using content_state.json
to keep track of files already drafted or published.
"""

import os
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path("knowledge")
DRAFTS_DIR = Path("drafts")
STATE_FILE = KNOWLEDGE_DIR / "content_state.json"

class KnowledgeOrchestrator:
    def __init__(self):
        self.knowledge_dir = KNOWLEDGE_DIR
        self.drafts_dir = DRAFTS_DIR
        self.state_file = STATE_FILE

    def load_state(self):
        """Loads the JSON state file."""
        if not self.state_file.exists():
            return {"articles": []}
        with open(self.state_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_all_knowledge_files(self):
        """Returns a list of all .md files in the knowledge directory."""
        return [f.name for f in self.knowledge_dir.glob("*.md")]

    def get_processed_files(self):
        """
        Determines which knowledge files have already been processed based on
        content_state.json. Returns a set of filenames.
        """
        state = self.load_state()
        processed = set()
        for article in state.get("articles", []):
            status = article.get("status")
            if status in ["drafted", "published"]:
                for src in article.get("source_files", []):
                    processed.add(src)
        return processed

    def get_unprocessed_files(self):
        """Returns a list of .md files that haven't been processed yet."""
        all_files = self.get_all_knowledge_files()
        processed = self.get_processed_files()

        # Don't try to process the state file itself or non-content MD files if any
        ignored = ["knowledge_map.md", "monetization_playbook.md"]

        unprocessed = [f for f in all_files if f not in processed and f not in ignored]
        return unprocessed

    def queue_for_generation(self, file_name: str):
        """Places the file in a queue for the agent to generate an article from."""
        logger.info(f"Queuing {file_name} for article generation...")
        # TODO: Implement actual queuing mechanism (e.g., Redis, database, or a simple text list)

    def run_scan(self):
        """Main orchestrator cycle to scan and queue files."""
        logger.info("Initializing knowledge base scan with state management...")
        unprocessed_files = self.get_unprocessed_files()

        if not unprocessed_files:
            logger.info("No new knowledge files found. All files processed or ignored.")
            return

        logger.info(f"Found {len(unprocessed_files)} unprocessed files.")
        for file in unprocessed_files:
            self.queue_for_generation(file)

        logger.info("Scan and queue cycle completed.")

if __name__ == "__main__":
    orchestrator = KnowledgeOrchestrator()
    orchestrator.run_scan()
