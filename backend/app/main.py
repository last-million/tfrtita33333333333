from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from .database import create_tables, get_db_connection, Error as DBError # Import create_tables and DB helpers (using mysql.connector.Error as DBError)
# Import routes
from .routes import credentials, calls # Added calls router
# Import services
# from .services import ultravox_service # Assuming this contains setup/API key logic if needed - Keep commented for now
from .config import settings # Import settings to get API keys etc.
import logging
import json
import base64
from pydub import AudioSegment # For audio conversion
import io # For handling audio bytes in memory
import sys # Import sys
import audioop # For mulaw conversion

# Configure logging (Ensure this is very early)
logging.basicConfig(level=logging.INFO) # Basic config for root logger
logger = logging.getLogger(__name__)

# Print sys.path right before the import that fails
# logger.info(f"Python sys.path: {sys.path}") # Keep commented out for now

# Import Ultravox client library (Corrected import path again)
# import ultravox_client # Trying base import
# from ultravox_client import Client as UltravoxClient # Import Client directly from the package - This caused ImportError
# Let's assume the service handles the client for now, or comment out usage below


app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(credentials.router, prefix="/api/credentials", tags=["Credentials"])
app.include_router(calls.router, prefix="/api/calls", tags=["Calls"]) # Added calls router

@app.on_event("startup")
def startup_event(): # Changed to sync for MySQL
    logger.info("Running startup event: Ensuring database tables exist.")
    create_tables()

@app.get("/")
async def root():
    return {"message": "Voice AI Call Agent Backend"}

@app.websocket("/media-stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handle WebSocket connection for Twilio Media Streams.
    Receives audio from Twilio, sends to Ultravox (placeholder), potentially receives response.
    """
    await websocket.accept()
    logger.info("WebSocket connection accepted.")
    call_sid = None
    caller_number = None
    stream_sid = None # Twilio sends a streamSid in the 'start' message

    # Placeholder for Ultravox client instance if needed outside the loop
    # uv_client_instance = None

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)

            event = data.get('event')

            if event == "connected":
                logger.info("WebSocket connected event received.")

            elif event == "start":
                stream_sid = data.get('streamSid')
                # Extract parameters passed from TwiML
                call_sid = data.get('start', {}).get('customParameters', {}).get('callSid')
                caller_number = data.get('start', {}).get('customParameters', {}).get('callerNumber')
                logger.info(f"Media stream started: streamSid={stream_sid}, callSid={call_sid}, caller={caller_number}")
                # TODO: Initialize Ultravox client session here if needed

            elif event == "media":
                # Process incoming audio chunk
                payload = data.get('media', {}).get('payload')
                if payload:
                    audio_chunk = base64.b64decode(payload)
                    logger.debug(f"Received audio chunk: {len(audio_chunk)} bytes for stream {stream_sid}")

                    # --- Placeholder Ultravox Interaction ---
                    # TODO: Implement actual audio processing and response generation
                    # 1. Convert audio_chunk (mulaw) to PCM
                    # 2. Send pcm_chunk to Ultravox service/client
                    # 3. Receive response_pcm_chunk from Ultravox
                    # 4. Convert response_pcm_chunk back to mulaw
                    # 5. Send mulaw_response_bytes back to Twilio via WebSocket
                    pass # Remove this pass when implementing

            elif event == "mark":
                logger.info(f"Received mark event: {data.get('mark')}")

            elif event == "stop":
                logger.info(f"Media stream stopped: {data}")
                # TODO: Clean up Ultravox client session if needed
                break # Exit loop on stop event

            else:
                logger.warning(f"Received unknown WebSocket event: {event}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: streamSid={stream_sid}, callSid={call_sid}")
        # TODO: Handle disconnection, maybe update call log status if needed
    except Exception as e:
        logger.error(f"WebSocket error: {e} (streamSid={stream_sid}, callSid={call_sid})")
        try:
            await websocket.close(code=1011) # Internal Error
        except RuntimeError:
            pass # Already closed
    finally:
        logger.info(f"Closing WebSocket handler for streamSid={stream_sid}, callSid={call_sid}")
        # TODO: Ensure any Ultravox resources are cleaned up

# --- Ultravox Webhook ---
@app.post("/ultravox-webhook")
async def ultravox_webhook_handler(request: Request):
    """
    Handle incoming webhooks from Ultravox, specifically 'call.ended'.
    Updates the call log with transcription, recording URL, and hangup reason.
    """
    conn = None
    cursor = None
    payload = {}
    try:
        # TODO: Implement webhook signature verification (HMAC-SHA256) for security

        payload = await request.json()
        event_type = payload.get('event')

        if event_type == 'call.ended':
            call_data = payload.get('call', {})
            call_sid = call_data.get('id')
            transcription = call_data.get('transcription')
            recording_url = call_data.get('recording_url')
            agent_hangup_reason = call_data.get('agent_hangup_reason')

            if not call_sid:
                logger.error("Call ID missing in Ultravox call.ended webhook.")
                return Response(status_code=400, detail="Missing call ID")

            logger.info(f"Received Ultravox call.ended webhook for CallSid: {call_sid}")

            conn = get_db_connection()
            if conn is None:
                logger.error(f"Database connection unavailable for Ultravox webhook: {call_sid}")
                raise HTTPException(status_code=503, detail="Database unavailable")

            cursor = conn.cursor()
            update_fields = []
            params = []
            if transcription:
                update_fields.append("transcription = %s")
                params.append(transcription)
            if recording_url:
                update_fields.append("ultravox_recording_url = %s")
                params.append(recording_url)
            if agent_hangup_reason:
                update_fields.append("agent_hangup_reason = %s")
                params.append(agent_hangup_reason)

            if not update_fields:
                logger.info(f"No relevant fields to update from Ultravox webhook for CallSid: {call_sid}")
                return Response(status_code=200)

            params.append(call_sid)
            sql = f"UPDATE call_logs SET {', '.join(update_fields)} WHERE call_sid = %s"

            logger.info(f"Executing SQL from Ultravox webhook: {sql} with params: {params}")
            cursor.execute(sql, tuple(params))
            conn.commit()
            logger.info(f"Call log updated from Ultravox webhook for CallSid: {call_sid}")

            return Response(status_code=200)
        else:
            logger.info(f"Received unhandled Ultravox event type: {event_type}")
            return Response(status_code=200)

    except json.JSONDecodeError:
        logger.error("Failed to decode JSON from Ultravox webhook.")
        raise HTTPException(status_code=400, detail="Invalid JSON")
    except DBError as e:
        logger.error(f"Database error processing Ultravox webhook for call {payload.get('call', {}).get('id')}: {e}")
        raise HTTPException(status_code=500, detail="Database processing error")
    except Exception as e:
        logger.error(f"Unexpected error processing Ultravox webhook for call {payload.get('call', {}).get('id')}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
