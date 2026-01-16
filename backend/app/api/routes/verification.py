"""
Face Verification API routes
"""

import asyncio
import json
import uuid
import websockets
from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_session_id, get_bot, delete_bot_session
from app.database import get_db
from app.services.chat_persistence import ChatPersistenceService
from app.core.bot import LaosEKYCBot
from app.models.requests import (
    VerifyFaceRequest,
    VerifyFaceResponse,
    StartVerificationRequest,
    FrameRequest,
    FrameResponse,
)


router = APIRouter()


@router.post("/verify-face", response_model=VerifyFaceResponse)
async def verify_face(
    request: VerifyFaceRequest,
    session_id: str = Depends(get_session_id),
    bot: LaosEKYCBot = Depends(get_bot),
):
    """Handle batch face verification"""

    try:
        # Update progress
        bot.conversation.set_progress("face_verifying")
        print(f"Progress updated in verify route: {bot.conversation.progress}")

        result = await bot.verify_face_from_urls(
            request.id_card_image_url,
            request.selfie_image_url
        )
        print(f"Verification result: {result}")

        if result.get("success"):
            result_data = result.get("result", {})

            # Check verification result
            if result_data.get("same_person") is True:
                # --- Persistence Logic START ---
                # --- Persistence Logic START ---
                # Save to Chat History with IDLE state
                chat_service = ChatPersistenceService(db)
                user_uuid = uuid.UUID(session_id)
                current_context = jsonable_encoder(bot.conversation.context)

                # Save "Verification Successful" message
                # Preserve scan_result for sidebar display, only clear other temp data
                preserved_context = {
                    "scan_result": current_context.get("scan_result"),
                    "id_card_url": current_context.get("id_card_url"),
                }
                await chat_service.save_message(
                    user_id=user_uuid,
                    role="assistant",
                    content="ການຢັ້ງຢືນໃບໜ້າສຳເລັດ! ຕົວຕົນຂອງທ່ານໄດ້ຖືກຢືນຢັນແລ້ວ.",
                    context=preserved_context,  # Keep scan_result for sidebar
                    progress="idle"  # Reset progress to idle
                )

                # Also update User status (if not done elsewhere)
                from app.database.models import User
                user = await db.get(User, user_uuid)
                if user:
                    user.is_verified = True
                    db.add(user)
                    await db.commit()
                # --- Persistence Logic END ---
                # --- Persistence Logic END ---

                # Delete bot session completely - next request will create fresh instance
                delete_bot_session(session_id)
                print(f"Verification successful, bot session deleted for: {session_id}")
            else:
                bot.conversation.set_progress("id_scanned")
                print(f"Verification failed, progress reverted: {bot.conversation.progress}")

            return VerifyFaceResponse(success=True, result=result_data)
        else:
            bot.conversation.set_progress("id_scanned")
            print(f"Verification error, progress reverted: {bot.conversation.progress}")
            return VerifyFaceResponse(success=False, error=result.get("error", "ເກີດຂໍ້ຜິດພາດໃນການຢັ້ງຢືນໃບໜ້າ"))

    except Exception as e:
        try:
            bot.conversation.set_progress("id_scanned")
            print(f"Exception occurred, progress reverted: {bot.conversation.progress}")
        except:
            pass
        print(f"Exception in verify_face: {str(e)}")
        return VerifyFaceResponse(success=False, error=f"ເກີດຂໍ້ຜິດພາດໃນການຢັ້ງຢືນໃບໜ້າ: {str(e)}")


@router.post("/start-ws-verification", response_model=VerifyFaceResponse)
async def start_websocket_verification(
    request: StartVerificationRequest,
    session_id: str = Depends(get_session_id),
    bot: LaosEKYCBot = Depends(get_bot),
):
    """Start WebSocket verification"""
    print("\n" + "="*80)
    print("[START] START WEBSOCKET VERIFICATION REQUEST")
    print("="*80)
    print(f"[SESSION] Session ID: {session_id}")
    print(f"[IMAGE]  ID Card Image URL: {request.id_card_image_url}")

    print(f"[BOT] Bot instance: {bot}")
    print(f"[SERVICE] Face verification service: {bot.face_verification_service}")

    try:
        print("[WAIT] Starting realtime verification...")
        # Run sync method in thread executor to avoid blocking
        loop = asyncio.get_event_loop()
        websocket_client = await loop.run_in_executor(
            None,
            bot.start_realtime_verification,
            request.id_card_image_url
        )
        print(f"[WS] WebSocket client returned: {websocket_client}")

        if websocket_client:
            print(f"[OK] Client created, checking connection status...")
            status = websocket_client.get_status()
            print(f"[DATA] Client Status:")
            print(json.dumps(status, indent=2))

            if websocket_client.is_connected:
                print("[OK] WebSocket verification started successfully!")
                print("="*80 + "\n")
                return VerifyFaceResponse(
                    success=True,
                    result={"message": "WebSocket verification started successfully"}
                )
            else:
                print("[ERROR] Client created but not connected")
                print("="*80 + "\n")
                return VerifyFaceResponse(
                    success=False,
                    error="WebSocket client created but failed to connect"
                )
        else:
            print("[ERROR] Could not create WebSocket client")
            print("="*80 + "\n")
            return VerifyFaceResponse(
                success=False,
                error="Could not connect to WebSocket server"
            )

    except Exception as e:
        print(f"[ERROR] Exception in start_websocket_verification: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        return VerifyFaceResponse(success=False, error=f"Error starting WebSocket: {str(e)}")


@router.post("/send-frame", response_model=FrameResponse)
async def send_frame(
    request: FrameRequest,
    session_id: str = Depends(get_session_id),
    bot: LaosEKYCBot = Depends(get_bot),
    db: AsyncSession = Depends(get_db),
):
    """Send frame for real-time verification"""
    print("\n" + "="*80)
    print("[FRAME] SEND FRAME REQUEST RECEIVED")
    print("="*80)

    realtime_client = bot.face_verification_service.realtime_client

    if not realtime_client:
        print("[ERROR] WebSocket client not initialized")
        return FrameResponse(success=False, error="WebSocket client not initialized")

    # Log current status
    status = realtime_client.get_status()
    print(f"[DATA] Current WebSocket Status:")
    print(json.dumps(status, indent=2))

    # Check connection health
    if not realtime_client.is_healthy():
        error_msg = f"WebSocket connection not healthy: connected={realtime_client.is_connected}, ws_exists={realtime_client.ws is not None}"
        print(f"[WARN]  {error_msg}")
        return FrameResponse(success=False, error="WebSocket connection is not healthy. Please restart verification.")

    try:
        # Send frame via WebSocket (SYNC method)
        print("[SEND] Attempting to send frame...")
        success = realtime_client.send_frame(request.frame_base64)

        if success:
            print("[OK] Frame sent successfully, waiting for result...")
            await asyncio.sleep(0.05)

            # Try to get result
            result = realtime_client.get_last_result()

            if result and "bbox" in result:
                print("="*80)
                print("[OK] RESPONSE FROM WEBSOCKET (Valid):")
                print(json.dumps(result, indent=2, ensure_ascii=False))
                print("="*80 + "\n")

                # Check if verification succeeded
                if result.get("same_person") is True:
                    print(f"[RESET] Verification successful! Saving record and deleting bot session: {session_id}")

                    # --- Persistence Logic START ---
                    # --- Persistence Logic START ---
                    # 1. Save Selfie Image
                    import base64
                    import os
                    from app.database.models import EKYCRecord, User
                    from uuid import UUID
                    from datetime import datetime

                    # Create filename
                    file_ext = "jpg"
                    filename = f"selfie_{session_id}_{int(datetime.utcnow().timestamp())}.{file_ext}"
                    upload_dir = "static/uploads"
                    # Ensure dir exists (should exist)
                    os.makedirs(upload_dir, exist_ok=True)
                    file_path = os.path.join(upload_dir, filename)

                    # Decode and save
                    # frame_base64 format usually: "data:image/jpeg;base64,....." or just raw base64
                    base64_data = request.frame_base64
                    if "," in base64_data:
                        base64_data = base64_data.split(",")[1]

                    with open(file_path, "wb") as f:
                        f.write(base64.b64decode(base64_data))

                    selfie_url = f"/static/uploads/{filename}"  # Relative URL serving

                    # 2. Create EKYC Record
                    # Get context data
                    context = bot.conversation.context or {}

                    user_uuid = UUID(session_id)

                    new_record = EKYCRecord(
                        user_id=user_uuid,
                        id_card_image_url=context.get("id_card_url"),
                        selfie_image_url=selfie_url,
                        ocr_data=jsonable_encoder(context.get("scan_result")),  # Fix serialization
                        face_match_score=result.get("similarity"),
                        is_verified=True,
                        verified_at=datetime.utcnow()
                    )
                    db.add(new_record)

                    # 3. Update User Status
                    # Fetch user to update
                    user = await db.get(User, user_uuid)
                    if user:
                        user.is_verified = True
                        user.updated_at = datetime.utcnow()
                        db.add(user)  # Should be tracked automatically but explicit add is safe

                    await db.commit()
                    print(f"[DB] EKYC Record saved and User verified: {session_id}")

                    # 4. Save to Chat History
                    chat_service = ChatPersistenceService(db)
                    msg_content = "ການຢັ້ງຢືນໃບໜ້າສຳເລັດ! ຕົວຕົນຂອງທ່ານໄດ້ຖືກຢືນຢັນແລ້ວ."

                    # Preserve scan_result for sidebar display
                    # Apply jsonable_encoder to serialize datetime objects
                    preserved_context = jsonable_encoder({
                        "scan_result": context.get("scan_result"),
                        "id_card_url": context.get("id_card_url"),
                    })
                    await chat_service.save_message(
                        user_id=user_uuid,
                        role="assistant",
                        content=msg_content,
                        context=preserved_context,  # Keep scan_result for sidebar
                        progress="idle"  # Reset progress to idle
                    )

                    # --- Persistence Logic END ---

                    # --- Persistence Logic END ---

                    delete_bot_session(session_id)

                return FrameResponse(
                    success=True,
                    message="Frame sent successfully",
                    result=result
                )
            else:
                # No bbox in result yet
                print(f"[WARN]  No bbox in result: {result}")
                print("="*80 + "\n")
                return FrameResponse(
                    success=True,
                    message="Frame sent successfully",
                    result=result
                )
        else:
            print(f"[ERROR] Frame send failed")
            print("="*80 + "\n")
            return FrameResponse(success=False, error="Could not send frame to WebSocket server")

    except Exception as e:
        print(f"[ERROR] Exception in send_frame: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        print("="*80 + "\n")
        return FrameResponse(success=False, error=f"Error sending frame: {str(e)}")


@router.get("/ws-status")
async def get_websocket_status(
    session_id: str = Depends(get_session_id),
    bot: LaosEKYCBot = Depends(get_bot),
):
    """Get WebSocket connection status for debugging"""
    realtime_client = bot.face_verification_service.realtime_client

    if not realtime_client:
        return {
            "status": "not_initialized",
            "message": "WebSocket client not initialized"
        }

    status = realtime_client.get_status()
    return {
        "status": "initialized",
        "details": status
    }


@router.post("/stop-ws-verification", response_model=VerifyFaceResponse)
async def stop_websocket_verification(
    session_id: str = Depends(get_session_id),
    bot: LaosEKYCBot = Depends(get_bot),
):
    """Stop WebSocket verification"""

    try:
        # Run sync method in thread executor
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, bot.stop_realtime_verification)
        return VerifyFaceResponse(
            success=True,
            result={"message": "WebSocket verification stopped"}
        )

    except Exception as e:
        print(f"Exception in stop_websocket_verification: {str(e)}")
        return VerifyFaceResponse(success=False, error=f"Error stopping WebSocket: {str(e)}")
