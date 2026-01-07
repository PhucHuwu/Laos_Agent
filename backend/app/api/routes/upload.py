"""
Upload API routes
"""

import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from app.api.deps import get_session_id, get_bot
from app.config import settings
from app.models.requests import UploadResponse
from app.utils.formatters import format_scan_result


router = APIRouter()


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in settings.ALLOWED_EXTENSIONS
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    session_id: str = Depends(get_session_id),
):
    """Handle file upload and OCR scan"""
    print("=" * 80)
    print("UPLOAD REQUEST RECEIVED")

    try:
        bot = get_bot(session_id)
        print(f"Bot instance retrieved successfully")
    except Exception as e:
        print(f"Error getting bot: {str(e)}")
        return UploadResponse(success=False, error=f"Error initializing bot: {str(e)}")

    if not file.filename:
        print("Empty filename")
        return UploadResponse(success=False, error="No file selected")

    if not allowed_file(file.filename):
        print(f"File extension not allowed: {file.filename}")
        return UploadResponse(success=False, error="File format not supported")

    print(f"File received: {file.filename}")

    try:
        # Read file content
        file_content = await file.read()

        # Process image
        print("Calling bot.process_image_upload...")
        result = await bot.process_image_upload(file_content, file.filename)
        print(f"OCR Result: {result}")

        if result.get("success"):
            scan_data = result.get("scan_result")
            formatted_html = format_scan_result(scan_data) if scan_data else "<p>No scan data</p>"

            return UploadResponse(
                success=True,
                image_url=result.get("image_url"),
                scan_result=scan_data,
                formatted_html=formatted_html,
                message="Upload and scan successful!",
                id_card_url=result.get("image_url"),
                tool_call={
                    "function": {
                        "name": "open_face_verification",
                        "arguments": "{\"message\": \"ກະລຸນາຖ່າຍຮູບໃບໜ້າຂອງທ່ານເພື່ອຢັ້ງຢືນຕົວຕົນ\"}"
                    },
                    "auto_execute": True
                }
            )
        else:
            print(f"OCR failed: {result.get('error')}")
            return UploadResponse(success=False, error=result.get("error", "Could not process image"))

    except Exception as e:
        print(f"Exception during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return UploadResponse(success=False, error=f"Error processing image: {str(e)}")
