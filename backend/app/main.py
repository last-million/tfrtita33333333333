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

# Import Ultravox client library (Trying attribute access)
UltravoxClient = None # Initialize as None
try:
    import ultravox_client
    try:
        # Attempt to access Client as an attribute of the imported package
        UltravoxClient = ultravox_client.Client
        logger.info("Successfully imported UltravoxClient via attribute access")
    except AttributeError:
        logger.error("Failed to find 'Client' attribute in 'ultravox_client' package.")
except ImportError as e:
    logger.error(f"Failed to import base 'ultravox_client' package: {e}. Check package installation.")


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
    uv_client = None # Initialize client variable

    try:
        # Initialize Ultravox client here if the import succeeded
        if UltravoxClient:
            # Assuming synchronous context manager or direct instantiation is needed
            # Adjust based on actual ultravox-client library usage
            # uv_client = UltravoxClient(api_key=settings.ultravox_api_key)
            # await uv_client.connect() # Or similar connection method if needed
            logger.info("UltravoxClient imported, ready for use (actual usage commented out).")
        else:
            logger.error("UltravoxClient could not be imported or found. WebSocket cannot process audio.")
            await websocket.close(code=1011, reason="Ultravox client unavailable")
            return

        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            event = data.get('event')

            if event == "connected":
                logger.info("WebSocket connected event received.")

            elif event == "start":
                stream_sid = data.get('streamSid')
                call_sid = data.get('start', {}).get('customParameters', {}).get('callSid')
                caller_number = data.get('start', {}).get('customParameters', {}).get('callerNumber')
                logger.info(f"Media stream started: streamSid={stream_sid}, callSid={call_sid}, caller={caller_number}")
                # TODO: Potentially log stream start or update call log

            elif event == "media":
                payload = data.get('media', {}).get('payload')
                if payload: # Removed 'and uv_client' check for now as usage is commented
                    audio_chunk = base64.b64decode(payload)
                    logger.debug(f"Received audio chunk: {len(audio_chunk)} bytes for stream {stream_sid}")

                    # --- Placeholder Ultravox Interaction ---
                    # TODO: Implement actual audio processing and response generation
                    # Ensure uv_client is properly initialized before uncommenting below
                    # try:
                    #     # 1. Convert Twilio's mulaw/8kHz to PCM/16kHz
                    #     audio_segment = AudioSegment(data=audio_chunk, sample_width=1, frame_rate=8000, channels=1)
                    #     pcm_segment = audio_segment.set_frame_rate(16000).set_sample_width(2)
                    #     pcm_chunk = pcm_segment.raw_data
                    #
                    #     # 2. Send to Ultravox
                    #     # async with uv_client: # Or however the client manages sessions
                    #     #    ultravox_response = await uv_client.streaming_process(pcm_chunk) # Replace with actual method
                    #     ultravox_response = None # Placeholder
                    #
                    #     # 3. Handle Ultravox response
                    #     if ultravox_response and ultravox_response.audio:
                    #         response_pcm_chunk = ultravox_response.audio
                    #         # 4. Convert response PCM back to mulaw/8kHz for Twilio
                    #         response_segment = AudioSegment(data=response_pcm_chunk, sample_width=2, frame_rate=16000, channels=1)
                    #         twilio_segment = response_segment.set_frame_rate(8000).set_sample_width(1)
                    #         mulaw_response_bytes = audioop.lin2ulaw(twilio_segment.raw_data, 1)
                    #         # 5. Send audio back to Twilio
                    #         response_payload = base64.b64encode(mulaw_response_bytes).decode('utf-8')
                    #         await websocket.send_text(json.dumps({
                    #             "event": "media",
                    #             "streamSid": stream_sid,
                    #             "media": {"payload": response_payload}
                    #         }))
                    #         logger.debug(f"Sent {len(mulaw_response_bytes)} bytes back to Twilio for stream {stream_sid}")
                    #
                    # except Exception as e:
                    #     logger.error(f"Error processing audio chunk with Ultravox for {call_sid}: {e}")
                    # --- End Ultravox Interaction ---
                    pass # Keep pass until TODO is implemented

            elif event == "mark":
                logger.info(f"Received mark event: {data.get('mark')}")

            elif event == "stop":
                logger.info(f"Media stream stopped: {data}")
                # TODO: Clean up Ultravox client session if needed
                break

            else:
                logger.warning(f"Received unknown WebSocket event: {event}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: streamSid={stream_sid}, callSid={call_sid}")
    except Exception as e:
        logger.error(f"WebSocket error: {e} (streamSid={stream_sid}, callSid={call_sid})")
        try:
            await websocket.close(code=1011)
        except RuntimeError: pass
    finally:
        logger.info(f"Closing WebSocket handler for streamSid={stream_sid}, callSid={call_sid}")
        # TODO: Ensure any Ultravox resources (like uv_client) are properly closed if necessary

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
        # TODO: Implement webhook signature verification

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
