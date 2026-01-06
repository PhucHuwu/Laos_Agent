"""
Face Verification API routes
"""

import asyncio
import json
import websockets
from fastapi import APIRouter, Depends
from app.api.deps import get_session_id, get_bot
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
):
    """Handle batch face verification"""
    bot = get_bot(session_id)

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
                bot.conversation.set_progress("completed")
                bot.conversation.set_context("verification_success", True)
                print(f"Verification successful, progress: {bot.conversation.progress}")
            else:
                bot.conversation.set_progress("id_scanned")
                print(f"Verification failed, progress reverted: {bot.conversation.progress}")

            return VerifyFaceResponse(success=True, result=result_data)
        else:
            bot.conversation.set_progress("id_scanned")
            print(f"Verification error, progress reverted: {bot.conversation.progress}")
            return VerifyFaceResponse(success=False, error=result.get("error", "Face verification error"))

    except Exception as e:
        try:
            bot.conversation.set_progress("id_scanned")
            print(f"Exception occurred, progress reverted: {bot.conversation.progress}")
        except:
            pass
        print(f"Exception in verify_face: {str(e)}")
        return VerifyFaceResponse(success=False, error=f"Face verification error: {str(e)}")


@router.post("/start-ws-verification", response_model=VerifyFaceResponse)
async def start_websocket_verification(
    request: StartVerificationRequest,
    session_id: str = Depends(get_session_id),
):
    """Start WebSocket verification"""
    print("\n" + "="*80)
    print("[START] START WEBSOCKET VERIFICATION REQUEST")
    print("="*80)
    print(f"[SESSION] Session ID: {session_id}")
    print(f"[IMAGE]  ID Card Image URL: {request.id_card_image_url}")
    
    bot = get_bot(session_id)
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
):
    """Send frame for real-time verification"""
    print("\n" + "="*80)
    print("[FRAME] SEND FRAME REQUEST RECEIVED")
    print("="*80)
    
    bot = get_bot(session_id)
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
):
    """Get WebSocket connection status for debugging"""
    bot = get_bot(session_id)
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
):
    """Stop WebSocket verification"""
    bot = get_bot(session_id)

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
