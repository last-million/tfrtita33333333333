from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables, get_db_connection, DBError # Import create_tables and DB helpers
# Import routes
from .routes import credentials, calls # Added calls router
# Import services (assuming ultravox service exists)
from .services import ultravox_service
import logging
import json
import base64

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

                    # --- Placeholder for Ultravox Interaction ---
                    try:
                        # This function needs to exist in ultravox_service and handle raw audio bytes
                        # It might be async or sync depending on its implementation
                        # response_audio = await ultravox_service.process_speech_chunk(call_sid, audio_chunk)
                        response_audio = None # Replace with actual call

                        if response_audio:
                            # If Ultravox responds with audio to play back, encode it and send via Twilio Mark/Media message
                            # response_payload = base64.b64encode(response_audio).decode('utf-8')
                            # await websocket.send_text(json.dumps({
                            #     "event": "media",
                            #     "streamSid": stream_sid,
                            #     "media": {
                            #         "payload": response_payload
                            #     }
                            # }))
                            pass # Placeholder for sending response audio
                    except Exception as e:
                        logger.error(f"Error processing audio chunk with Ultravox for {call_sid}: {e}")
                    # --- End Placeholder ---


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
