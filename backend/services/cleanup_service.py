"""
Service xử lý tự động dọn dẹp dữ liệu sau khi hoàn tất eKYC
"""

import os
import shutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import glob
from ..config import settings


class CleanupService:
    """Service tự động dọn dẹp dữ liệu eKYC"""

    def __init__(self):
        self.logger = self._setup_logger()
        self.upload_folder = settings.UPLOAD_FOLDER

    def _setup_logger(self) -> logging.Logger:
        """Thiết lập logger cho cleanup service"""
        logger = logging.getLogger('cleanup_service')
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger

    def cleanup_after_ekyc_completion(self, conversation) -> Dict[str, Any]:
        """
        Tự động dọn dẹp sau khi hoàn tất eKYC thành công

        Args:
            conversation: Đối tượng conversation hiện tại

        Returns:
            Kết quả dọn dẹp
        """
        try:
            cleanup_results = {
                "context_cleared": False,
                "files_cleaned": 0,
                "temp_files_cleaned": 0,
                "errors": []
            }

            # 1. Xóa dữ liệu context liên quan đến eKYC
            self._clear_ekyc_context(conversation)
            cleanup_results["context_cleared"] = True
            self.logger.info("✅ Đã xóa dữ liệu context eKYC")

            # 2. Xóa các file tạm trong uploads (nếu có)
            temp_files_count = self._cleanup_temp_files()
            cleanup_results["temp_files_cleaned"] = temp_files_count
            self.logger.info(f"✅ Đã xóa {temp_files_count} files tạm")

            # 3. Xóa các file cũ (tuần tự 24 giờ)
            old_files_count = self._cleanup_old_files()
            cleanup_results["files_cleaned"] = old_files_count
            self.logger.info(f"✅ Đã xóa {old_files_count} files cũ")

            self.logger.info("🎉 Hoàn tất dọn dẹp tự động sau eKYC")

            return {
                "success": True,
                "result": cleanup_results,
                "message": "Dọn dẹp dữ liệu thành công"
            }

        except Exception as e:
            self.logger.error(f"❌ Lỗi trong quá trình dọn dẹp: {str(e)}")
            return {
                "success": False,
                "error": f"Lỗi dọn dẹp: {str(e)}"
            }

    def _clear_ekyc_context(self, conversation) -> None:
        """Xóa dữ liệu context eKYC khỏi conversation"""
        try:
            # Xóa các key liên quan đến eKYC
            ekyc_keys = [
                'id_card_url',
                'scan_result',
                'verification_result',
                'verification_success',
                'id_card_image_url',
                'selfie_image_url'
            ]

            for key in ekyc_keys:
                if key in conversation.context:
                    del conversation.context[key]

            # Reset progress về idle
            conversation.set_progress('idle')

        except Exception as e:
            self.logger.error(f"Lỗi xóa context: {str(e)}")
            raise

    def _cleanup_temp_files(self) -> int:
        """
        Xóa các file tạm trong thư mục uploads

        Returns:
            Số lượng files đã xóa
        """
        if not os.path.exists(self.upload_folder):
            return 0

        files_deleted = 0

        try:
            # Lấy danh sách tất cả files trong uploads
            for filename in os.listdir(self.upload_folder):
                filepath = os.path.join(self.upload_folder, filename)

                if os.path.isfile(filepath):
                    try:
                        os.remove(filepath)
                        files_deleted += 1
                        self.logger.debug(f"Đã xóa file tạm: {filename}")
                    except Exception as e:
                        self.logger.warning(f"Không thể xóa file {filename}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Lỗi khi dọn dẹp temp files: {str(e)}")

        return files_deleted

    def _cleanup_old_files(self, max_age_hours: int = 24) -> int:
        """
        Xóa các files cũ hơn thời gian quy định

        Args:
            max_age_hours: Số giờ tối đa để giữ file

        Returns:
            Số lượng files đã xóa
        """
        if not os.path.exists(self.upload_folder):
            return 0

        files_deleted = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        try:
            for filename in os.listdir(self.upload_folder):
                filepath = os.path.join(self.upload_folder, filename)

                if os.path.isfile(filepath):
                    try:
                        # Kiểm tra thời gian tạo file
                        file_time = datetime.fromtimestamp(os.path.getctime(filepath))

                        if file_time < cutoff_time:
                            os.remove(filepath)
                            files_deleted += 1
                            self.logger.debug(f"Đã xóa file cũ: {filename}")

                    except Exception as e:
                        self.logger.warning(f"Không thể xóa file cũ {filename}: {str(e)}")

        except Exception as e:
            self.logger.error(f"Lỗi khi dọn dẹp old files: {str(e)}")

        return files_deleted

    def cleanup_specific_files(self, file_patterns: List[str]) -> Dict[str, Any]:
        """
        Xóa các files theo pattern cụ thể

        Args:
            file_patterns: Danh sách patterns của files cần xóa

        Returns:
            Kết quả xóa files
        """
        try:
            files_deleted = 0
            errors = []

            for pattern in file_patterns:
                try:
                    # Tìm files theo pattern
                    full_pattern = os.path.join(self.upload_folder, pattern)
                    matching_files = glob.glob(full_pattern)

                    for filepath in matching_files:
                        try:
                            if os.path.isfile(filepath):
                                os.remove(filepath)
                                files_deleted += 1
                                self.logger.debug(f"Đã xóa file: {os.path.basename(filepath)}")
                        except Exception as e:
                            error_msg = f"Không thể xóa {filepath}: {str(e)}"
                            errors.append(error_msg)
                            self.logger.warning(error_msg)

                except Exception as e:
                    error_msg = f"Lỗi pattern {pattern}: {str(e)}"
                    errors.append(error_msg)
                    self.logger.error(error_msg)

            return {
                "success": True,
                "files_deleted": files_deleted,
                "errors": errors
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Lỗi cleanup specific files: {str(e)}"
            }

    def reset_all_data(self, conversation) -> Dict[str, Any]:
        """
        Reset toàn bộ dữ liệu (conversation + files)

        Args:
            conversation: Đối tượng conversation cần reset

        Returns:
            Kết quả reset
        """
        try:
            # 1. Clear conversation
            conversation.clear()
            conversation.context.clear()
            conversation.set_progress('idle')

            # 2. Xóa tất cả files trong uploads
            files_deleted = self._cleanup_temp_files()

            self.logger.info(f"🔄 Reset hoàn tất: {files_deleted} files đã xóa")

            return {
                "success": True,
                "files_deleted": files_deleted,
                "message": "Reset toàn bộ dữ liệu thành công"
            }

        except Exception as e:
            self.logger.error(f"❌ Lỗi reset: {str(e)}")
            return {
                "success": False,
                "error": f"Lỗi reset: {str(e)}"
            }

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Lấy thông tin về dung lượng lưu trữ

        Returns:
            Thông tin storage
        """
        try:
            if not os.path.exists(self.upload_folder):
                return {
                    "total_files": 0,
                    "total_size_mb": 0,
                    "folder_exists": False
                }

            total_files = 0
            total_size = 0

            for filename in os.listdir(self.upload_folder):
                filepath = os.path.join(self.upload_folder, filename)
                if os.path.isfile(filepath):
                    total_files += 1
                    total_size += os.path.getsize(filepath)

            return {
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "folder_exists": True,
                "upload_folder": self.upload_folder
            }

        except Exception as e:
            self.logger.error(f"Lỗi get storage info: {str(e)}")
            return {
                "error": f"Lỗi lấy thông tin storage: {str(e)}"
            }

    def schedule_cleanup(self, conversation, delay_seconds: int = 30) -> Dict[str, Any]:
        """
        Lên lịch dọn dẹp sau một khoảng thời gian

        Args:
            conversation: Conversation cần dọn dẹp
            delay_seconds: Số giây delay trước khi dọn dẹp

        Returns:
            Thông tin lên lịch
        """
        # Note: Đây là implementation đơn giản
        # Trong production có thể dùng Celery hoặc background tasks

        import threading
        import time

        def delayed_cleanup():
            time.sleep(delay_seconds)
            self.cleanup_after_ekyc_completion(conversation)

        try:
            cleanup_thread = threading.Thread(target=delayed_cleanup, daemon=True)
            cleanup_thread.start()

            self.logger.info(f"⏰ Đã lên lịch dọn dẹp sau {delay_seconds} giây")

            return {
                "success": True,
                "message": f"Đã lên lịch dọn dẹp sau {delay_seconds} giây",
                "delay_seconds": delay_seconds
            }

        except Exception as e:
            self.logger.error(f"Lỗi schedule cleanup: {str(e)}")
            return {
                "success": False,
                "error": f"Lỗi lên lịch: {str(e)}"
            }
