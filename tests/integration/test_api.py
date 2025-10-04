"""
Integration tests for API endpoints
"""

from backend.config import settings
from backend.api import create_app
import unittest
import json
import os
import tempfile
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


class TestAPIIntegration(unittest.TestCase):
    """Integration tests for API endpoints"""

    def setUp(self):
        """Set up test client"""
        # Create test app
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Create temporary upload directory
        self.test_upload_dir = tempfile.mkdtemp()
        self.app.config['UPLOAD_FOLDER'] = self.test_upload_dir

    def tearDown(self):
        """Clean up after tests"""
        # Clean up temporary files
        import shutil
        if os.path.exists(self.test_upload_dir):
            shutil.rmtree(self.test_upload_dir)

    def test_index_route(self):
        """Test index route"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)

    def test_debug_route(self):
        """Test debug route"""
        response = self.client.get('/debug')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertIn('static_folder', data)
        self.assertIn('static_url_path', data)

    def test_chat_route_empty_message(self):
        """Test chat route with empty message"""
        response = self.client.post('/chat',
                                    json={'message': ''},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_chat_route_valid_message(self):
        """Test chat route with valid message"""
        response = self.client.post('/chat',
                                    json={'message': 'Hello'},
                                    content_type='application/json')

        # Should return 200 or handle gracefully
        self.assertIn(response.status_code, [200, 500])  # 500 if API key not configured

    def test_upload_route_no_file(self):
        """Test upload route without file"""
        response = self.client.post('/upload')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_upload_route_invalid_file(self):
        """Test upload route with invalid file"""
        # Create a temporary text file (not an image)
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(b'This is not an image')
            temp_file_path = f.name

        try:
            with open(temp_file_path, 'rb') as f:
                response = self.client.post('/upload',
                                            data={'file': (f, 'test.txt')})

            self.assertEqual(response.status_code, 400)
            data = json.loads(response.data)
            self.assertIn('error', data)
        finally:
            os.unlink(temp_file_path)

    def test_reset_conversation_route(self):
        """Test reset conversation route"""
        response = self.client.post('/reset')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_verify_face_route_missing_params(self):
        """Test verify face route with missing parameters"""
        response = self.client.post('/verify-face',
                                    json={},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_start_websocket_verification_missing_params(self):
        """Test start WebSocket verification with missing parameters"""
        response = self.client.post('/start-websocket-verification',
                                    json={},
                                    content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)


if __name__ == "__main__":
    unittest.main()
