"""
Upload API routes
"""

import os
import uuid
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_session_id, get_bot
from app.database import get_db
from app.services.chat_persistence import ChatPersistenceService
from app.config import settings
from app.core.bot import LaosEKYCBot
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
    bot: "LaosEKYCBot" = Depends(get_bot),
    db: AsyncSession = Depends(get_db),
):
    """Handle file upload and OCR scan"""
    print("=" * 80)
    print("UPLOAD REQUEST RECEIVED")

    # Bot is now injected and guaranteed to be initialized

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
            formatted_html = format_scan_result(scan_data) if scan_data else "ບໍ່ມີຂໍ້ມູນການສະແກນ"

            # Save to chat history
            try:
                chat_service = ChatPersistenceService(db)
                session_uuid = uuid.UUID(session_id)

                # Save User Action
                await chat_service.save_message(
                    session_id=session_uuid,
                    role="user",
                    content=f"ອັບໂຫລດບັດປະຈຳຕົວ: {file.filename}",
                    context=jsonable_encoder(bot.conversation.context),
                    progress=bot.conversation.progress
                )

                # Save Assistant Response
                await chat_service.save_message(
                    session_id=session_uuid,
                    role="assistant",
                    content=formatted_html,
                    context=jsonable_encoder(bot.conversation.context),
                    progress=bot.conversation.progress
                )
            except Exception as e:
                print(f"Error saving chat history: {e}")

            return UploadResponse(
                success=True,
                image_url=result.get("image_url"),
                scan_result=scan_data,
                formatted_html=formatted_html,
                message="ອັບໂຫລດ ແລະ ສະແກນສຳເລັດ!",
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
            return UploadResponse(success=False, error=result.get("error", "ບໍ່ສາມາດປະມວນຜົນຮູບພາບໄດ້"))

    except Exception as e:
        print(f"Exception during processing: {str(e)}")
        import traceback
        traceback.print_exc()
        return UploadResponse(success=False, error=f"ເກີດຂໍ້ຜິດພາດໃນການປະມວນຜົນຮູບພາບ: {str(e)}")
