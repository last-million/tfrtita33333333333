from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables, get_db_connection, DBError # Import create_tables and DB helpers
# Import routes
from .routes import credentials, calls # Added calls router
# Import services
from .services import ultravox_service # Assuming this contains setup/API key logic if needed
from .config import settings # Import settings to get API keys etc.
import logging
import json
import base64
from pydub import AudioSegment # For audio conversion
import io # For handling audio bytes in memory
# Import Ultravox client library
from ultravox.client import Client as UltravoxClient # Renamed to avoid conflict

# Configure logging
logger = logging.getLogger(__name__)

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
    # The create_tables function now runs within init_db_pool or directly if module is run
    # We might not need to explicitly call it here if database.py handles it on import.
    # However, calling it ensures tables exist if the module wasn't run directly.
    logger.info("Running startup event: Ensuring database tables exist.")
    # Check if pool was initialized successfully before trying to create tables
    # Note: database.py already tries to create tables if run directly.
    # Consider if this call is redundant or necessary based on deployment strategy.
    # For safety, we can call it, the function handles None connection.
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
                # TODO: Potentially log stream start or update call log

            elif event == "media":
                # Process incoming audio chunk
                payload = data.get('media', {}).get('payload')
                if payload:
                    # Audio is base64 encoded Mulaw
                    audio_chunk = base64.b64decode(payload)
                    logger.debug(f"Received audio chunk: {len(audio_chunk)} bytes for stream {stream_sid}")

                    # --- Ultravox Interaction ---
                    try:
                        # 1. Convert Twilio's mulaw/8kHz to PCM/16kHz (adjust target format if needed)
                        audio_segment = AudioSegment(
                            data=audio_chunk,
                            sample_width=1, # 8-bit for mulaw
                            frame_rate=8000,
                            channels=1
                        )
                        # Decode from mulaw (pydub doesn't have direct mulaw, treat as 8-bit PCM then convert)
                        # This might need adjustment or a different library if direct mulaw->PCM is required.
                        # Assuming pydub handles it as linear 8-bit for conversion purposes.
                        # Resample and set sample width for 16-bit PCM
                        pcm_segment = audio_segment.set_frame_rate(16000).set_sample_width(2)
                        pcm_chunk = pcm_segment.raw_data

                        # 2. Send to Ultravox (ensure client is initialized correctly)
                        # This assumes an async client interface. Adjust if sync.
                        # You might need to manage the Ultravox client lifecycle (connect/disconnect)
                        # or use a context manager if the library supports it.
                        # Ensure ULTRAVOX_API_KEY is loaded via settings
                        async with UltravoxClient(api_key=settings.ultravox_api_key) as uv_client:
                            # Example: Send audio chunk for processing
                            # The exact method depends on the ultravox-client library API
                            # This is a guess based on common streaming patterns
                            ultravox_response = await uv_client.streaming_process(pcm_chunk) # Fictional method

                            # 3. Handle Ultravox response (e.g., generated audio)
                            if ultravox_response and ultravox_response.audio:
                                response_pcm_chunk = ultravox_response.audio # Assuming response is PCM

                                # 4. Convert response PCM back to mulaw/8kHz for Twilio
                                response_segment = AudioSegment(
                                    data=response_pcm_chunk,
                                    sample_width=2, # Assuming 16-bit PCM response
                                    frame_rate=16000, # Assuming 16kHz response
                                    channels=1
                                )
                                twilio_segment = response_segment.set_frame_rate(8000).set_sample_width(1)
                                # Encode to mulaw (again, pydub might need help here, this is simplified)
                                # For proper mulaw encoding, you might need `audioop.lin2ulaw`
                                import audioop
                                mulaw_response_bytes = audioop.lin2ulaw(twilio_segment.raw_data, 1)

                                # 5. Send audio back to Twilio
                                response_payload = base64.b64encode(mulaw_response_bytes).decode('utf-8')
                                await websocket.send_text(json.dumps({
                                    "event": "media",
                                    "streamSid": stream_sid,
                                    "media": {
                                        "payload": response_payload
                                    }
                                }))
                                logger.debug(f"Sent {len(mulaw_response_bytes)} bytes back to Twilio for stream {stream_sid}")

                    except Exception as e:
                        logger.error(f"Error processing audio chunk with Ultravox for {call_sid}: {e}")
                    # --- End Ultravox Interaction ---


            elif event == "mark":
                logger.info(f"Received mark event: {data.get('mark')}")

            elif event == "stop":
                logger.info(f"Media stream stopped: {data}")
                # TODO: Potentially log stream end or update call log
                break # Exit loop on stop event

            else:
                logger.warning(f"Received unknown WebSocket event: {event}")

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: streamSid={stream_sid}, callSid={call_sid}")
        # TODO: Handle disconnection, maybe update call log status if needed
    except Exception as e:
        logger.error(f"WebSocket error: {e} (streamSid={stream_sid}, callSid={call_sid})")
        # Attempt to close gracefully if possible
        try:
            await websocket.close(code=1011) # Internal Error
        except RuntimeError:
            pass # Already closed
    finally:
        logger.info(f"Closing WebSocket handler for streamSid={stream_sid}, callSid={call_sid}")
        # Any final cleanup
