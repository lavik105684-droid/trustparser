"""
Native Telegram Publisher for "Искра и Росток".
Uses pure Python (urllib.request) to avoid pip dependencies.
Supports sending text and media groups (albums) to Telegram.
"""

import os
import json
import logging
import mimetypes
import uuid
import urllib.request
from typing import List
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DotEnv:
    """Simple .env parser without using python-dotenv"""
    @staticmethod
    def load():
        env_path = Path('.env')
        if not env_path.exists():
            logger.warning(".env file not found. Ensure environment variables are set.")
            return

        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

DotEnv.load()

class TelegramPublisher:
    def __init__(self):
        self.token = os.environ.get('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.environ.get('TELEGRAM_CHAT_ID')

        if not self.token or not self.chat_id:
            logger.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID in environment.")

        self.base_url = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, text: str) -> bool:
        """Sends a plain text message to the channel."""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown" # Or HTML, based on preference
        }

        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})

        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    logger.info("Successfully sent text message to Telegram.")
                    return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")

        return False

    def send_media_group(self, text: str, image_paths: List[Path]) -> bool:
        """
        Sends an album of images with a caption attached to the first image.
        Uses multipart/form-data via urllib to upload local files.
        """
        if not image_paths:
            return self.send_message(text)

        url = f"{self.base_url}/sendMediaGroup"

        boundary = uuid.uuid4().hex
        headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}

        media_arr = []
        for i, path in enumerate(image_paths):
            if not path.exists():
                logger.error(f"Image not found: {path}")
                continue

            media_item = {
                "type": "photo",
                "media": f"attach://photo{i}"
            }
            # Attach caption to the first image only
            if i == 0:
                media_item["caption"] = text
                media_item["parse_mode"] = "Markdown"

            media_arr.append(media_item)

        if not media_arr:
            return False

        # Build multipart payload
        body = []

        # Add the media JSON string
        body.append(f"--{boundary}")
        body.append('Content-Disposition: form-data; name="chat_id"')
        body.append('')
        body.append(self.chat_id)

        body.append(f"--{boundary}")
        body.append('Content-Disposition: form-data; name="media"')
        body.append('')
        body.append(json.dumps(media_arr))

        # Add files
        file_data_blocks = []
        for i, path in enumerate(image_paths):
            if not path.exists():
                continue

            mime_type, _ = mimetypes.guess_type(str(path))
            mime_type = mime_type or 'application/octet-stream'

            body.append(f"--{boundary}")
            body.append(f'Content-Disposition: form-data; name="photo{i}"; filename="{path.name}"')
            body.append(f'Content-Type: {mime_type}')
            body.append('')

            # Since body will be joined and encoded, we need to handle binary file data carefully
            # We'll encode the string parts to bytes and append binary data
            file_data_blocks.append((len(body), path))
            body.append('FILE_PLACEHOLDER')

        body.append(f"--{boundary}--")
        body.append('')

        # Construct final binary payload
        payload_bytes = bytearray()
        for i, line in enumerate(body):
            is_file = False
            for idx, path in file_data_blocks:
                if i == idx:
                    with open(path, 'rb') as f:
                        payload_bytes.extend(f.read())
                    payload_bytes.extend(b'\r\n')
                    is_file = True
                    break

            if not is_file:
                if line != 'FILE_PLACEHOLDER':
                    payload_bytes.extend(line.encode('utf-8'))
                    payload_bytes.extend(b'\r\n')

        req = urllib.request.Request(url, data=payload_bytes, headers=headers)

        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    logger.info("Successfully sent media group to Telegram.")
                    return True
        except Exception as e:
            logger.error(f"Failed to send media group: {e}")
            if hasattr(e, 'read'):
                logger.error(f"API Response: {e.read().decode('utf-8')}")

        return False

if __name__ == "__main__":
    # Quick test stub
    logger.info("TG Publisher loaded.")
