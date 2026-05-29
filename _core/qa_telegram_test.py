import os
import sys
import unittest
import json
from unittest.mock import patch, MagicMock

# Import Leo's test script
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import telegram_test

class TestTelegramBotConnection(unittest.TestCase):
    
    def setUp(self):
        # Clear environment variables before test
        self.old_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.old_chat = os.environ.get("TELEGRAM_CHAT_ID")
        if "TELEGRAM_BOT_TOKEN" in os.environ: del os.environ["TELEGRAM_BOT_TOKEN"]
        if "TELEGRAM_CHAT_ID" in os.environ: del os.environ["TELEGRAM_CHAT_ID"]

    def tearDown(self):
        # Restore environment variables
        if self.old_token: os.environ["TELEGRAM_BOT_TOKEN"] = self.old_token
        if self.old_chat: os.environ["TELEGRAM_CHAT_ID"] = self.old_chat

    def test_missing_credentials_fails_gracefully(self):
        print("\n[QA TEST] Проверка обработки отсутствия учетных данных...")
        with self.assertRaises(SystemExit) as cm:
            telegram_test.send_telegram_test()
        self.assertEqual(cm.exception.code, 1, "Скрипт должен завершаться с кодом 1 при отсутствии .env настроек")
        print("[QA PASS] Скрипт корректно завершил работу с кодом ошибки.")

    @patch("telegram_test.load_env")
    @patch("urllib.request.urlopen")
    def test_successful_mock_delivery(self, mock_urlopen, mock_load_env):
        print("\n[QA TEST] Симуляция успешной отправки с корректными токенами...")
        
        # Setup mock environment
        os.environ["TELEGRAM_BOT_TOKEN"] = "123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"
        os.environ["TELEGRAM_CHAT_ID"] = "@mock_channel"
        
        # Configure mock response from Telegram API
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({
            "ok": True,
            "result": {
                "message_id": 999,
                "chat": {"id": -100123456, "title": "Mock Channel", "type": "channel"},
                "date": 1779555555,
                "text": "⚡ Тест связи Pixel Office..."
            }
        }).encode("utf-8")
        mock_urlopen.return_value.__enter__.return_value = mock_response

        # Execute connection test
        result = telegram_test.send_telegram_test()
        self.assertTrue(result, "Тест отправки должен возвращать True при успешном ответе API")
        
        # Verify call parameters
        args, kwargs = mock_urlopen.call_args
        req = args[0]
        self.assertEqual(req.full_url, "https://api.telegram.org/bot123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ/sendMessage")
        self.assertEqual(req.get_header("Content-type"), "application/json")
        
        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["chat_id"], "@mock_channel")
        self.assertIn("Тест связи", body["text"])
        
        print("[QA PASS] Симуляция доставки успешно завершена. Все структуры JSON-запроса проверены.")

if __name__ == "__main__":
    print("=== ЗАПУСК QA ИНТЕГРАЦИОННОГО ТЕСТИРОВАНИЯ (Квентин) ===")
    unittest.main()
