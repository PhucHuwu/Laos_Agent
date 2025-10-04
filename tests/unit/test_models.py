"""
Unit tests for data models
"""

import unittest
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.conversation import Message, Conversation
from backend.models.verification import ScanResult, VerificationResult


class TestMessage(unittest.TestCase):
    """Test Message model"""

    def test_message_creation(self):
        """Test message creation"""
        message = Message(role="user", content="Hello")
        self.assertEqual(message.role, "user")
        self.assertEqual(message.content, "Hello")
        self.assertIsInstance(message.timestamp, datetime)

    def test_message_to_dict(self):
        """Test message to dictionary conversion"""
        message = Message(role="assistant", content="Hi there")
        data = message.to_dict()

        self.assertEqual(data["role"], "assistant")
        self.assertEqual(data["content"], "Hi there")
        self.assertIn("role", data)
        self.assertIn("content", data)

    def test_message_with_tool_calls(self):
        """Test message with tool calls"""
        tool_calls = [{"function": {"name": "test", "arguments": "{}"}}]
        message = Message(role="assistant", content="", tool_calls=tool_calls)

        data = message.to_dict()
        self.assertEqual(data["tool_calls"], tool_calls)


class TestConversation(unittest.TestCase):
    """Test Conversation model"""

    def setUp(self):
        """Set up test conversation"""
        self.conversation = Conversation()

    def test_conversation_creation(self):
        """Test conversation creation"""
        self.assertEqual(len(self.conversation.messages), 0)
        self.assertIsNone(self.conversation.session_id)
        self.assertIsInstance(self.conversation.created_at, datetime)

    def test_add_message(self):
        """Test adding messages"""
        message = Message(role="user", content="Test message")
        self.conversation.add_message(message)

        self.assertEqual(len(self.conversation.messages), 1)
        self.assertEqual(self.conversation.get_last_message(), message)
        self.assertEqual(self.conversation.get_message_count(), 1)

    def test_clear_conversation(self):
        """Test clearing conversation"""
        message = Message(role="user", content="Test message")
        self.conversation.add_message(message)
        self.conversation.clear()

        self.assertEqual(len(self.conversation.messages), 0)

    def test_get_messages_for_api(self):
        """Test getting messages formatted for API"""
        message = Message(role="user", content="Test message")
        self.conversation.add_message(message)

        api_messages = self.conversation.get_messages_for_api()
        self.assertEqual(len(api_messages), 1)
        self.assertEqual(api_messages[0]["role"], "user")
        self.assertEqual(api_messages[0]["content"], "Test message")


class TestScanResult(unittest.TestCase):
    """Test ScanResult model"""

    def test_scan_result_creation(self):
        """Test scan result creation"""
        result = ScanResult(text="Test text", document_type="ID")

        self.assertEqual(result.text, "Test text")
        self.assertEqual(result.document_type, "ID")
        self.assertEqual(result.status, "success")
        self.assertIsInstance(result.timestamp, datetime)

    def test_scan_result_to_dict(self):
        """Test scan result to dictionary conversion"""
        result = ScanResult(text="Test text", document_type="ID")
        data = result.to_dict()

        self.assertEqual(data["text"], "Test text")
        self.assertEqual(data["document_type"], "ID")
        self.assertEqual(data["status"], "success")
        self.assertIsNotNone(data["timestamp"])

    def test_scan_result_from_dict(self):
        """Test scan result creation from dictionary"""
        data = {
            "text": "Test text",
            "document_type": "ID",
            "status": "success"
        }

        result = ScanResult.from_dict(data)

        self.assertEqual(result.text, "Test text")
        self.assertEqual(result.document_type, "ID")
        self.assertEqual(result.status, "success")


class TestVerificationResult(unittest.TestCase):
    """Test VerificationResult model"""

    def test_verification_result_creation(self):
        """Test verification result creation"""
        result = VerificationResult(
            same_person=True,
            similarity=0.95,
            status="success"
        )

        self.assertTrue(result.same_person)
        self.assertEqual(result.similarity, 0.95)
        self.assertEqual(result.status, "success")
        self.assertIsInstance(result.timestamp, datetime)

    def test_verification_result_to_dict(self):
        """Test verification result to dictionary conversion"""
        result = VerificationResult(same_person=True, similarity=0.95)
        data = result.to_dict()

        self.assertTrue(data["same_person"])
        self.assertEqual(data["similarity"], 0.95)
        self.assertEqual(data["status"], "success")
        self.assertIsNotNone(data["timestamp"])

    def test_is_successful(self):
        """Test successful verification check"""
        # Successful case
        result = VerificationResult(
            same_person=True,
            similarity=0.95,
            status="success"
        )
        self.assertTrue(result.is_successful())

        # Failed case - low similarity
        result.similarity = 0.5
        self.assertFalse(result.is_successful())

        # Failed case - not same person
        result.same_person = False
        result.similarity = 0.95
        self.assertFalse(result.is_successful())


if __name__ == "__main__":
    unittest.main()
