"""
Botany Orchestrator Stub
Scans the /knowledge directory for unprocessed .md files and queues them for content generation.
"""

import os
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path("knowledge")
DRAFTS_DIR = Path("drafts")

class KnowledgeOrchestrator:
    def __init__(self):
        self.knowledge_dir = KNOWLEDGE_DIR
        self.drafts_dir = DRAFTS_DIR

    def get_all_knowledge_files(self):
        """Returns a list of all .md files in the knowledge directory."""
        return list(self.knowledge_dir.glob("*.md"))

    def get_processed_files(self):
        """
        Determines which knowledge files have already been processed based on
        some metadata or naming convention in the drafts directory.
        For now, returns a dummy list.
        """
        # In a real implementation, we might parse frontmatter or maintain a database
        return []

    def get_unprocessed_files(self):
        """Returns a list of .md files that haven't been processed yet."""
        all_files = self.get_all_knowledge_files()
        processed = self.get_processed_files()
        unprocessed = [f for f in all_files if f not in processed]
        return unprocessed

    def queue_for_generation(self, file_path: Path):
        """Places the file in a queue for the agent to generate an article from."""
        logger.info(f"Queuing {file_path.name} for article generation...")
        # TODO: Implement actual queuing mechanism (e.g., Redis, database, or a simple text list)

    def run_scan(self):
        """Main orchestrator cycle to scan and queue files."""
        logger.info("Initializing knowledge base scan...")
        unprocessed_files = self.get_unprocessed_files()

        if not unprocessed_files:
            logger.info("No new knowledge files found. All files processed.")
            return

        logger.info(f"Found {len(unprocessed_files)} unprocessed files.")
        for file in unprocessed_files:
            self.queue_for_generation(file)

        logger.info("Scan and queue cycle completed.")

if __name__ == "__main__":
    orchestrator = KnowledgeOrchestrator()
    orchestrator.run_scan()
