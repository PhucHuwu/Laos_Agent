"""
Flask routes and API endpoints
"""

import os
import uuid
import json
from flask import Flask, render_template, request, jsonify, session, send_file, Response, stream_with_context
from flask_cors import CORS
from werkzeug.utils import secure_filename
from typing import Dict, Any

from ..config import settings
from ..core import LaosEKYCBot
from ..utils.formatters import format_scan_result


def create_app() -> Flask:
    """Create and configure Flask application"""

    app = Flask(__name__,
                template_folder='../../frontend',
                static_folder='../../frontend/assets',
                static_url_path='/static')
    app.secret_key = settings.FLASK_SECRET_KEY
    CORS(app)

    # Configure upload
    if not os.path.exists(settings.UPLOAD_FOLDER):
        os.makedirs(settings.UPLOAD_FOLDER)

    app.config['UPLOAD_FOLDER'] = settings.UPLOAD_FOLDER
    app.config['MAX_CONTENT_LENGTH'] = settings.MAX_CONTENT_LENGTH

    # Initialize bot
    bot = LaosEKYCBot()

    # Global WebSocket client for real-time verification
    websocket_client = None

    def allowed_file(filename: str) -> bool:
        """Check if file extension is allowed"""
        return ('.' in filename and
                filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS)

    @app.route('/')
    def index():
        """Main page"""
        return render_template('index.html')

    @app.route('/test')
    def test():
        """Test page"""
        return render_template('test.html')

    @app.route('/debug')
    def debug():
        """Debug route to check static files"""
        static_path = os.path.join(app.static_folder, 'css', 'style.css')
        exists = os.path.exists(static_path)
        return jsonify({
            'static_folder': app.static_folder,
            'static_url_path': app.static_url_path,
            'css_exists': exists,
            'css_path': static_path
        })

    @app.route('/upload', methods=['POST'])
    def upload_file():
        """Handle file upload"""
        if 'file' not in request.files:
            return jsonify({'error': 'ບໍ່ໄດ້ເລືອກໄຟລ໌'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'ບໍ່ໄດ້ເລືອກໄຟລ໌'}), 400

        if file and allowed_file(file.filename):
            # Create unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

            # Save file
            file.save(filepath)

            try:
                # Process image
                result = bot.process_image_upload(filepath)

                # Remove temporary file
                os.remove(filepath)

                if result.get('success'):
                    scan_data = result.get('scan_result')
                    formatted_html = format_scan_result(scan_data) if scan_data else "<p>Không có dữ liệu scan</p>"

                    # Lưu ID card URL vào context trước khi gọi AI
                    bot.conversation.set_context('id_card_url', result.get('image_url'))
                    bot.conversation.set_context('scan_result', scan_data)

                    # Cập nhật progress: đã upload và scan thành công
                    bot.conversation.set_progress('id_scanned')
                    print(f"✅ Progress updated in upload route: {bot.conversation.get_progress()}")

                    # Sau khi scan thành công, AI tự động gọi camera verification
                    ai_response = bot.chat("Tôi đã upload và scan ảnh căn cước công dân thành công. Bây giờ hãy tiến hành xác thực khuôn mặt.")

                    return jsonify({
                        'success': True,
                        'image_url': result.get('image_url'),
                        'scan_result': scan_data,
                        'formatted_html': formatted_html,
                        'message': 'ອັບໂຫຼດ ແລະ ສະແກນສຳເລັດ! ກະລຸນາກວດສອບຂໍ້ມູນຂ້າງລຸ່ມນີ້.',
                        'id_card_url': result.get('image_url'),
                        'ai_response': ai_response  # AI response với tool calls
                    })
                else:
                    return jsonify({'error': result.get('error', 'ບໍ່ສາມາດປຸງແຕ່ງຮູບໄດ້')}), 500

            except Exception as e:
                # Remove temporary file on error
                if os.path.exists(filepath):
                    os.remove(filepath)
                return jsonify({'error': f'ຂໍ້ຜິດພາດໃນການປຸງແຕ່ງຮູບ: {str(e)}'}), 500

        return jsonify({'error': 'ຮູບແບບໄຟລ໌ບໍ່ຮອງຮັບ'}), 400

    @app.route('/chat', methods=['POST'])
    def chat():
        """Handle chat messages"""
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'ຂໍ້ຄວາມບໍ່ສາມາດເປົ່າໄດ້'}), 400

        try:
            response = bot.chat(user_message)

            # Check if response contains tool calls
            if isinstance(response, dict) and 'tool_calls' in response:
                return jsonify({
                    'success': True,
                    'tool_calls': response['tool_calls']
                })
            else:
                return jsonify({
                    'success': True,
                    'response': response.get('response', response.get('error', 'Unknown error'))
                })
        except Exception as e:
            return jsonify({'error': f'ຂໍ້ຜິດພາດໃນການປຸງແຕ່ງຂໍ້ຄວາມ: {str(e)}'}), 500

    @app.route('/chat-stream', methods=['POST'])
    def chat_stream():
        """Handle streaming chat messages with thinking/reasoning"""
        data = request.get_json()
        user_message = data.get('message', '')

        if not user_message:
            return jsonify({'error': 'ຂໍ້ຄວາມບໍ່ສາມາດເປົ່າໄດ້'}), 400

        def generate():
            """Generator function for streaming response"""
            try:
                # Stream responses from AI service
                for chunk in bot.ai_service.chat_stream(user_message):
                    # Format as Server-Sent Events
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"

                # Send done signal
                yield "data: [DONE]\n\n"

            except Exception as e:
                error_data = {
                    'type': 'error',
                    'error': f'ຂໍ້ຜິດພາດໃນການປຸງແຕ່ງຂໍ້ຄວາມ: {str(e)}'
                }
                yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"

        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )

    @app.route('/start-websocket-verification', methods=['POST'])
    def start_websocket_verification():
        """Start WebSocket verification"""
        nonlocal websocket_client

        data = request.get_json()
        id_card_image_url = data.get('id_card_image_url')

        print(f"Starting WebSocket verification for: {id_card_image_url}")

        if not id_card_image_url:
            return jsonify({'error': 'ຂາດ URL ຮູບບັດປະຈໍາຕົວ'}), 400

        try:
            # Create new client
            websocket_client = bot.start_realtime_verification(id_card_image_url)

            if websocket_client and websocket_client.is_connected:
                return jsonify({
                    'success': True,
                    'message': 'ເລີ່ມການຢັ້ງຢືນ WebSocket ສຳເລັດແລ້ວ'
                })
            else:
                error_msg = 'ບໍ່ສາມາດເຊື່ອມຕໍ່ຫາ WebSocket server'
                if websocket_client:
                    error_msg += f' (URL: {websocket_client.websocket_url})'
                return jsonify({'error': error_msg}), 500

        except Exception as e:
            print(f"Exception in start_websocket_verification: {str(e)}")
            return jsonify({'error': f'ຂໍ້ຜິດພາດໃນການເລີ່ມ WebSocket: {str(e)}'}), 500

    @app.route('/send-frame', methods=['POST'])
    def send_frame():
        """Send frame for real-time verification"""
        nonlocal websocket_client

        data = request.get_json()
        frame_base64 = data.get('frame_base64')

        if not frame_base64:
            return jsonify({'error': 'ຂາດຂໍ້ມູນ frame'}), 400

        if not websocket_client:
            return jsonify({'error': 'WebSocket client ຍັງບໍ່ໄດ້ເລີ່ມຕົ້ນ'}), 400

        if not websocket_client.is_connected:
            return jsonify({'error': 'WebSocket ຍັງບໍ່ໄດ້ເຊື່ອມຕໍ່ຫາ server'}), 400

        try:
            # Send frame via WebSocket
            success = websocket_client.send_frame(frame_base64)

            if success:
                # Get last result
                result = websocket_client.get_last_result()

                return jsonify({
                    'success': True,
                    'message': 'ສົ່ງ frame ສຳເລັດແລ້ວ',
                    'result': result
                })
            else:
                return jsonify({'error': 'ບໍ່ສາມາດສົ່ງ frame ໄດ້'}), 500

        except Exception as e:
            print(f"Exception in send_frame: {str(e)}")
            return jsonify({'error': f'ຂໍ້ຜິດພາດໃນການສົ່ງ frame: {str(e)}'}), 500

    @app.route('/stop-websocket-verification', methods=['POST'])
    def stop_websocket_verification():
        """Stop WebSocket verification"""
        nonlocal websocket_client

        try:
            if websocket_client:
                bot.stop_realtime_verification()
                websocket_client = None

            return jsonify({
                'success': True,
                'message': 'ຢຸດການຢັ້ງຢືນ WebSocket ແລ້ວ'
            })

        except Exception as e:
            print(f"Exception in stop_websocket_verification: {str(e)}")
            return jsonify({'error': f'ຂໍ້ຜິດພາດໃນການຢຸດ WebSocket: {str(e)}'}), 500

    @app.route('/verify-face-realtime', methods=['POST'])
    def verify_face_realtime():
        """Handle real-time face verification"""
        data = request.get_json()
        id_card_image_url = data.get('id_card_image_url')
        selfie_image_url = data.get('selfie_image_url')

        print(f"Realtime verification request: {id_card_image_url}, {selfie_image_url}")

        if not id_card_image_url or not selfie_image_url:
            return jsonify({'error': 'ຂາດ URL ຮູບບັດປະຈໍາຕົວ ຫຼື selfie'}), 400

        try:
            # Cập nhật progress: đang xác thực
            bot.conversation.set_progress('face_verifying')
            print(f"✅ Progress updated in verify route: {bot.conversation.get_progress()}")

            result = bot.verify_face_from_urls(id_card_image_url, selfie_image_url)
            print(f"Verification result: {result}")

            if result.get('success'):
                result_data = result.get('result', {})

                # Kiểm tra kết quả verification
                if result_data.get('status') == 'success' and result_data.get('same_person'):
                    bot.conversation.set_progress('completed')
                    bot.conversation.set_context('verification_success', True)
                    print(f"✅ Verification successful, progress: {bot.conversation.get_progress()}")
                else:
                    # Verification failed - quay lại id_scanned
                    bot.conversation.set_progress('id_scanned')
                    print(f"⚠️ Verification failed, progress reverted: {bot.conversation.get_progress()}")

                return jsonify({
                    'success': True,
                    'result': result_data
                })
            else:
                # Error - quay lại id_scanned
                bot.conversation.set_progress('id_scanned')
                print(f"⚠️ Verification error, progress reverted: {bot.conversation.get_progress()}")

                return jsonify({
                    'success': False,
                    'error': result.get('error', 'ຂໍ້ຜິດພາດໃນການຢັ້ງຢືນໃບໜ້າ')
                }), 500
        except Exception as e:
            # Error - quay lại id_scanned nếu có lỗi
            try:
                bot.conversation.set_progress('id_scanned')
                print(f"⚠️ Exception occurred, progress reverted: {bot.conversation.get_progress()}")
            except:
                pass
            print(f"Exception in verify_face_realtime: {str(e)}")
            return jsonify({'error': f'ຂໍ້ຜິດພາດໃນການຢັ້ງຢືນໃບໜ້າ: {str(e)}'}), 500

    @app.route('/verify-face', methods=['POST'])
    def verify_face():
        """Handle face verification"""
        data = request.get_json()
        id_card_image_url = data.get('id_card_image_url')
        selfie_image_url = data.get('selfie_image_url')

        if not id_card_image_url or not selfie_image_url:
            return jsonify({'error': 'ຂາດ URL ຮູບບັດປະຈໍາຕົວ ຫຼື selfie'}), 400

        try:
            # Cập nhật progress: đang xác thực
            bot.conversation.set_progress('face_verifying')
            print(f"✅ Progress updated in verify route: {bot.conversation.get_progress()}")

            result = bot.verify_face_from_urls(id_card_image_url, selfie_image_url)

            if result.get('success'):
                result_data = result.get('result', {})

                # Kiểm tra kết quả verification
                if result_data.get('status') == 'success' and result_data.get('same_person'):
                    bot.conversation.set_progress('completed')
                    bot.conversation.set_context('verification_success', True)
                    print(f"✅ Verification successful, progress: {bot.conversation.get_progress()}")
                else:
                    # Verification failed - quay lại id_scanned
                    bot.conversation.set_progress('id_scanned')
                    print(f"⚠️ Verification failed, progress reverted: {bot.conversation.get_progress()}")

                return jsonify({
                    'success': True,
                    'result': result_data
                })
            else:
                # Error - quay lại id_scanned
                bot.conversation.set_progress('id_scanned')
                print(f"⚠️ Verification error, progress reverted: {bot.conversation.get_progress()}")

                return jsonify({
                    'success': False,
                    'error': result.get('error', 'ຂໍ້ຜິດພາດໃນການຢັ້ງຢືນໃບໜ້າ')
                }), 500
        except Exception as e:
            # Error - quay lại id_scanned nếu có lỗi
            try:
                bot.conversation.set_progress('id_scanned')
                print(f"⚠️ Exception occurred, progress reverted: {bot.conversation.get_progress()}")
            except:
                pass
            return jsonify({'error': f'ຂໍ້ຜິດພາດໃນການຢັ້ງຢືນໃບໜ້າ: {str(e)}'}), 500

    @app.route('/test-camera')
    def test_camera():
        """Test camera page"""
        return send_file('test_camera.html')

    @app.route('/reset', methods=['POST'])
    def reset_conversation():
        """Reset conversation"""
        try:
            bot.reset_conversation()
            return jsonify({'success': True, 'message': 'ໄດ້ reset ການສົນທະນາແລ້ວ'})
        except Exception as e:
            return jsonify({'error': f'ຂໍ້ຜິດພາດໃນການ reset: {str(e)}'}), 500

    return app
