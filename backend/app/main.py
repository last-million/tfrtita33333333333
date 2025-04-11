from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from .database import create_tables, get_db_connection, Error as DBError
from .routes import credentials, calls
from .config import settings
import logging
import json
import base64
import audioop # For mulaw/pcm conversion
import asyncio
import websockets # For Ultravox connection
import requests # For creating Ultravox call
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import UltravoxSession based on documentation
UltravoxSession = None
try:
    from ultravox_client import UltravoxSession # Correct class name based on docs
    logger.info("Successfully imported UltravoxSession from ultravox_client")
except ImportError as e:
    logger.error(f"Failed to import UltravoxSession from ultravox_client: {e}. Check package installation.")


app = FastAPI()

# Keep track of active sessions (Twilio CallSid -> Session Data)
# WARNING: This in-memory store is not suitable for production
sessions = {}

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(credentials.router, prefix="/api/credentials", tags=["Credentials"])
app.include_router(calls.router, prefix="/api/calls", tags=["Calls"])

@app.on_event("startup")
def startup_event():
    logger.info("Running startup event: Ensuring database tables exist.")
    create_tables()

@app.get("/")
async def root():
    return {"message": "Voice AI Call Agent Backend"}

# --- Ultravox Call Creation ---
async def create_ultravox_call(system_prompt: str, first_message: str) -> str:
    """
    Creates a new Ultravox call in serverWebSocket mode and returns the joinUrl.
    """
    url = "https://api.ultravox.ai/api/calls"
    if not settings.ultravox_api_key:
        logger.error("ULTRAVOX_API_KEY is not configured.")
        return ""

    headers = {
        "X-API-Key": settings.ultravox_api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "systemPrompt": system_prompt,
        "model": "fixie-ai/ultravox-70B", # TODO: Make configurable
        "voice": "Tanya-English", # TODO: Make configurable
        "initialMessages": [{"role": "MESSAGE_ROLE_USER", "text": first_message}],
        "medium": {
            "serverWebSocket": {
                "inputSampleRate": 8000, # Match Twilio
                "outputSampleRate": 8000, # Match Twilio
                "clientBufferSizeMs": 60
            }
        }
        # "call_ended_webhook_url": f"{settings.base_url}/ultravox-webhook" # Removed invalid parameter based on API error
    }
    logger.info(f"Creating Ultravox call with payload: {json.dumps(payload, indent=2)}")
    try:
        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: requests.post(url, headers=headers, json=payload))

        if not resp.ok:
            logger.error(f"Ultravox create call error: {resp.status_code} {resp.text}")
            return ""
        body = resp.json()
        join_url = body.get("joinUrl") or ""
        logger.info(f"Ultravox joinUrl received: {join_url}")
        return join_url
    except Exception as e:
        logger.error(f"Ultravox create call request failed: {e}", exc_info=True)
        return ""

# --- WebSocket Media Stream Handling ---
@app.websocket("/media-stream")
async def websocket_endpoint(websocket: WebSocket):
    """
    Handles the Twilio <Stream> WebSocket and connects to Ultravox via WebSocket.
    """
    await websocket.accept()
    logger.info("Twilio WebSocket connection accepted.")

    call_sid = None
    stream_sid = None
    uv_ws = None
    session = None
    twilio_task = None
    uv_task = None
    uv_session = None # Variable for the UltravoxSession instance

    async def handle_ultravox_messages():
        nonlocal uv_ws, stream_sid, call_sid, session
        try:
            async for raw_message in uv_ws:
                if isinstance(raw_message, bytes):
                    try:
                        mu_law_bytes = audioop.lin2ulaw(raw_message, 2)
                        payload_base64 = base64.b64encode(mu_law_bytes).decode('ascii')
                        await websocket.send_text(json.dumps({
                            "event": "media",
                            "streamSid": stream_sid,
                            "media": {"payload": payload_base64}
                        }))
                        logger.debug(f"Sent {len(mu_law_bytes)} bytes from Ultravox to Twilio")
                    except Exception as e:
                        logger.error(f"Error transcoding/sending Ultravox audio: {e}")
                else:
                    try:
                        msg_data = json.loads(raw_message)
                        msg_type = msg_data.get("type") or msg_data.get("eventType")
                        logger.debug(f"Received data from Ultravox: type={msg_type}")

                        if msg_type == "transcript":
                            role = msg_data.get("role")
                            text = msg_data.get("text") or msg_data.get("delta")
                            if role and text and session:
                                session['transcript'] += f"{role.capitalize()}: {text}\n"
                        elif msg_type == "client_tool_invocation":
                             toolName = msg_data.get("toolName", "")
                             invocationId = msg_data.get("invocationId")
                             logger.warning(f"Received unhandled tool invocation: {toolName} (ID: {invocationId})")
                             error_result = {
                                 "type": "client_tool_result",
                                 "invocationId": invocationId,
                                 "error_type": "not-implemented",
                                 "error_message": f"Tool '{toolName}' is not implemented."
                             }
                             await uv_ws.send(json.dumps(error_result))
                        else:
                            logger.info(f"Received Ultravox message: {msg_type} - {msg_data}")
                    except Exception as e:
                        logger.error(f"Error processing Ultravox data message: {e} - Data: {raw_message}")
        except websockets.exceptions.ConnectionClosedOK:
             logger.info(f"Ultravox WebSocket closed normally for CallSid={call_sid}.")
        except Exception as e:
            logger.error(f"Error in handle_ultravox_messages for CallSid={call_sid}: {e}", exc_info=True)
        finally:
             logger.info(f"Ultravox message handler finished for CallSid={call_sid}.")
             if websocket.client_state == websockets.protocol.State.OPEN:
                 await websocket.close(code=1011, reason="Ultravox connection closed")

    async def handle_twilio_messages():
        nonlocal call_sid, session, stream_sid, uv_ws, uv_task, uv_session
        try:
            while True:
                message = await websocket.receive_text()
                data = json.loads(message)
                event = data.get('event')

                if event == 'start':
                    stream_sid = data['start']['streamSid']
                    call_sid = data['start'].get('customParameters', {}).get('callSid')
                    caller_number = data['start'].get('customParameters', {}).get('callerNumber')
                    first_message = data['start'].get('customParameters', {}).get('firstMessage', "Hello?")

                    if not call_sid:
                         call_sid = data['start'].get('callSid')
                         logger.warning(f"CallSid not found in customParameters, using start.callSid: {call_sid}")
                    if not call_sid:
                         logger.error("Could not determine CallSid from start event. Closing.")
                         await websocket.close(code=1011, reason="Missing CallSid")
                         return

                    logger.info(f"Twilio stream started: streamSid={stream_sid}, callSid={call_sid}, caller={caller_number}")

                    if call_sid in sessions:
                        session = sessions[call_sid]
                        session['streamSid'] = stream_sid
                    else:
                        logger.warning(f"Session not found for CallSid {call_sid} on start event. Creating.")
                        session = {"transcript": "", "callerNumber": caller_number, "callDetails": {}, "firstMessage": first_message, "streamSid": stream_sid}
                        sessions[call_sid] = session

                    system_prompt = "You are a helpful AI assistant." # TODO: Use prompts.py
                    uv_join_url = await create_ultravox_call(system_prompt, first_message)

                    if not uv_join_url:
                        logger.error(f"Failed to create Ultravox call for CallSid {call_sid}. Closing connection.")
                        await websocket.close(code=1011, reason="Ultravox call creation failed")
                        return

                    try:
                        # Initialize and connect Ultravox Session if import succeeded
                        if UltravoxSession:
                             # Use the imported Session class
                             uv_session = UltravoxSession(api_key=settings.ultravox_api_key) # Assuming API key needed
                             uv_ws = await uv_session.connect(uv_join_url) # Assuming connect method exists
                             logger.info(f"Ultravox WebSocket connected via Session for CallSid {call_sid}.")
                             uv_task = asyncio.create_task(handle_ultravox_messages()) # Start listener
                        else:
                             logger.error("UltravoxSession class not available. Cannot connect.")
                             await websocket.close(code=1011, reason="Ultravox client unavailable")
                             return

                    except Exception as e:
                        logger.error(f"Error connecting/starting Ultravox WebSocket for CallSid {call_sid}: {e}", exc_info=True)
                        await websocket.close(code=1011, reason="Ultravox connection failed")
                        return

                elif event == 'media':
                    payload_base64 = data['media']['payload']
                    if uv_ws and uv_ws.state == websockets.protocol.State.OPEN:
                        try:
                            mu_law_bytes = base64.b64decode(payload_base64)
                            pcm_bytes = audioop.ulaw2lin(mu_law_bytes, 2)
                            # Use the uv_session object if it exists and has a send method
                            if uv_session and hasattr(uv_session, 'send_audio'):
                                await uv_session.send_audio(pcm_bytes) # Assuming send_audio method
                            else:
                                await uv_ws.send(pcm_bytes) # Fallback to direct websocket send
                            logger.debug(f"Sent {len(pcm_bytes)} PCM bytes to Ultravox for CallSid={call_sid}")
                        except Exception as e:
                            logger.error(f"Error transcoding/sending Twilio audio to Ultravox for CallSid={call_sid}: {e}")
                    else:
                         logger.warning(f"Received Twilio media but Ultravox WS not open for CallSid={call_sid}")

                elif event == 'stop':
                    logger.info(f"Twilio stream stopped for CallSid={call_sid}: {data}")
                    break

                elif event == 'mark':
                     logger.info(f"Received Twilio mark event for CallSid={call_sid}: {data.get('mark')}")

                else:
                    logger.warning(f"Received unknown Twilio event for CallSid={call_sid}: {event}")

        except WebSocketDisconnect:
            logger.info(f"Twilio WebSocket disconnected for CallSid={call_sid}.")
        except Exception as e:
            logger.error(f"Error in handle_twilio_messages for CallSid={call_sid}: {e}", exc_info=True)
        finally:
            logger.info(f"Twilio message handler finished for CallSid={call_sid}.")
            if uv_task and not uv_task.done(): uv_task.cancel()
            if uv_ws and uv_ws.state == websockets.protocol.State.OPEN: await uv_ws.close()
            if uv_session and hasattr(uv_session, 'close'): # If using the Session class approach
                 await uv_session.close() # Assuming a close method
            if call_sid and call_sid in sessions:
                del sessions[call_sid]
                logger.info(f"Removed session data for CallSid={call_sid}")

    twilio_task = asyncio.create_task(handle_twilio_messages())
    try:
        await twilio_task
    except asyncio.CancelledError:
        logger.info(f"WebSocket endpoint task cancelled for CallSid={call_sid}")

# --- Ultravox Webhook ---
@app.post("/ultravox-webhook")
async def ultravox_webhook_handler(request: Request):
    """
    Handle incoming webhooks from Ultravox, specifically 'call.ended'.
    """
    conn = None
    cursor = None
    payload = {}
    try:
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
        logger.error(f"Unexpected error processing Ultravox webhook for call {payload.get('call', {}).get('id')}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# Allow running directly via uvicorn for local testing
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
