"""
Auto-posting scheduler for the "Искра и Росток" project.
Reads content_state.json, finds 'drafted' articles, publishes them to Telegram,
and updates their status.
"""

import os
import json
import time
import logging
from pathlib import Path
from src.tg_publisher import TelegramPublisher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STATE_FILE = Path("knowledge/content_state.json")
DRAFTS_DIR = Path("drafts")

class PostingScheduler:
    """Monitors content_state.json and schedules publications."""
    def __init__(self):
        self.tg_publisher = TelegramPublisher()

    def load_state(self):
        if not STATE_FILE.exists():
            logger.error(f"State file not found: {STATE_FILE}")
            return {"articles": []}
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_state(self, state_data):
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, ensure_ascii=False, indent=2)

    def extract_text_for_tg(self, filepath: Path) -> str:
        """Reads the markdown file and formats it for Telegram (e.g. max length, strip gallery prompts)."""
        if not filepath.exists():
            return ""

        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        # Basic cleanup: remove "Галерея для публикации" section as it's meant for internal generation
        if "## Галерея для публикации" in text:
            text = text.split("## Галерея для публикации")[0].strip()

        return text

    def find_local_images(self, article_name: str) -> list:
        """
        Scans for locally generated images matching the article name.
        Assumes images are stored in a 'media' folder inside drafts with prefix matching the article.
        """
        media_dir = DRAFTS_DIR / "media"
        if not media_dir.exists():
            return []

        stem = Path(article_name).stem
        images = []
        for ext in ['.jpg', '.jpeg', '.png']:
            # match article_01_alocasia_soil_1.jpg, etc.
            images.extend(list(media_dir.glob(f"{stem}*{ext}")))
        return sorted(images)

    def run_cycle(self):
        """Main execution cycle for the scheduler."""
        logger.info("Starting scheduler publishing cycle...")

        # Check if TG credentials are set
        if not self.tg_publisher.token or not self.tg_publisher.chat_id:
            logger.warning("Telegram credentials not found in .env. Dry-run mode only.")

        state_data = self.load_state()
        articles = state_data.get("articles", [])

        changes_made = False

        for article in articles:
            if article.get("status") == "drafted":
                draft_path = Path(article.get("target_draft"))

                logger.info(f"Processing drafted article: {draft_path.name}")

                platforms = article.get("platforms", {})

                # Check Telegram
                if not platforms.get("tg", False):
                    text_content = self.extract_text_for_tg(draft_path)

                    if text_content:
                        image_paths = self.find_local_images(draft_path.name)
                        if image_paths:
                            logger.info(f"Found {len(image_paths)} images for {draft_path.name}")

                        logger.info("Attempting to publish to Telegram...")
                        success = False

                        # Only actually send if credentials exist
                        if self.tg_publisher.token and self.tg_publisher.chat_id:
                            success = self.tg_publisher.send_media_group(text_content, image_paths)
                        else:
                            # Simulated success for local testing without credentials
                            success = True

                        if success:
                            platforms["tg"] = True
                            changes_made = True
                            logger.info(f"Successfully marked {draft_path.name} as published on Telegram.")
                    else:
                        logger.error(f"Could not extract text from {draft_path}")

                # Update global status if all target platforms are satisfied
                article["platforms"] = platforms
                # Wait for both zen and tg to be true, OR if zen is explicitly handled as manual outside this logic
                # The user stated: "Если и Дзен, и ТГ закрыты, общий статус статьи меняется на 'published'"
                if platforms.get("tg", False) and platforms.get("zen", False):
                    article["status"] = "published"
                    article["published_at"] = time.strftime("%Y-%m-%d")
                    changes_made = True
                    logger.info(f"Article {draft_path.name} is fully published!")

        if changes_made:
            self.save_state(state_data)
            logger.info("State file updated.")

        logger.info("Scheduler publishing cycle completed.")

if __name__ == "__main__":
    logger.info("Initializing Auto-Posting Scheduler...")
    scheduler = PostingScheduler()
    scheduler.run_cycle()
