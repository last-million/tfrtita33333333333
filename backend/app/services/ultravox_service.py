import os
import requests
import audioop
import asyncio
import base64
import json
import logging
from fastapi import WebSocket
import websockets
from twilio.rest import Client

logger = logging.getLogger(__name__)

class UltravoxService:
    def __init__(self):
        self.api_key = os.getenv("ULTRAVOX_API_KEY")
        self.base_url = "https://api.ultravox.ai/api/calls"  # Replace with the actual Ultravox API base URL if different
        self.model = "fixie-ai/ultravox-70B"
        self.voice = "Tanya-English"
        self.sample_rate = 8000
        self.buffer_size = 60
        if not self.api_key:
            logger.warning("Ultravox API key not found in environment variables.")

    async def create_ultravox_call(self, system_prompt: str, first_message: str, voice: str = None, call_history: str = "") -> str:
        """
        Creates a new Ultravox call in serverWebSocket mode and returns the joinUrl.
        """
        url = self.base_url
        headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "systemPrompt": f"{system_prompt}\n\nPrevious Call History:\n{call_history}",
            "model": self.model,
            "voice": voice or self.voice,  # Use specified voice or default
            "temperature": 0.1,
            "initialMessages": [
                {
                    "role": "MESSAGE_ROLE_USER",
                    "text": first_message
                }
            ],
            "medium": {
                "serverWebSocket": {
                    "inputSampleRate": self.sample_rate,
                    "outputSampleRate": self.sample_rate,
                    "clientBufferSizeMs": self.buffer_size
                }
            },
            "selectedTools": [
                {
                    "temporaryTool": {
                        "modelToolName": "question_and_answer",
                        "description": "Get answers to customer questions especially about AI employees",
                        "dynamicParameters": [
                            {
                                "name": "question",
                                "location": "PARAMETER_LOCATION_BODY",
                                "schema": {
                                    "type": "string",
                                    "description": "Question to be answered"
                                },
                                "required": True
                            }
                        ],
                        "timeout": "20s",
                        "client": {},
                    },
                },
                {
                    "temporaryTool": {
                        "modelToolName": "schedule_meeting",
                        "description": "Schedule a meeting for a customer. Returns a message indicating whether the booking was successful or not.",
                        "dynamicParameters": [
                            {
                                "name": "name",
                                "location": "PARAMETER_LOCATION_BODY",
                                "schema": {
                                    "type": "string",
                                    "description": "Customer's name"
                                },
                                "required": True
                            },
                            {
                                "name": "email",
                                "location": "PARAMETER_LOCATION_BODY",
                                "schema": {
                                    "type": "string",
                                    "description": "Customer's email"
                                },
                                "required": True
                            },
                            {
                                "name": "purpose",
                                "location": "PARAMETER_LOCATION_BODY",
                                "schema": {
                                    "type": "string",
                                    "description": "Purpose of the Meeting"
                                },
                                "required": True
                            },
                            {
                                "name": "datetime",
                                "location": "PARAMETER_LOCATION_BODY",
                                "schema": {
                                    "type": "string",
                                    "description": "Meeting Datetime"
                                },
                                "required": True
                            },
                            {
                                "name": "location",
                                "location": "PARAMETER_LOCATION_BODY",
                                "schema": {
                                    "type": "string",
                                    "description": "Meeting location"
                                },
                                "required": True
                            }
                        ],
                        "timeout": "20s",
                        "client": {},
                    },
                },
                {"temporaryTool": {
                    "modelToolName": "hangUp",
                    "description": "End the call",
                    "client": {},
                }
                }
            ]
        }

        try:
            resp = requests.post(url, headers=headers, json=payload)
            if not resp.ok:
                logger.error(f"Ultravox create call error: {resp.status_code} {resp.text}")
                return ""
            body = resp.json()
            join_url = body.get("joinUrl") or ""
            logger.info(f"Ultravox joinUrl received: {join_url}")
            return join_url
        except Exception as e:
            logger.error(f"Ultravox create call request failed: {e}")
            return ""

    async def handle_question_and_answer(self, uv_ws, invocation_id: str, question: str):
        """
        Handle "question_and_answer" - simplified version without Pinecone.
        """
        try:
            # Replace with a simple static response or a call to another service
            answer_message = f"Answering question: {question}.  (This is a placeholder response.)"

            # Respond back to Ultravox
            tool_result = {
                "type": "client_tool_result",
                "invocationId": invocationId,
                "result": answer_message,
                "response_type": "tool-response"
            }
            await uv_ws.send(json.dumps(tool_result))
        except Exception as e:
            logger.error(f"Error in Q&A tool: {e}")
            # Send error result back to Ultravox
            error_result = {
                "type": "client_tool_result",
                "invocationId": invocationId,
                "error_type": "implementation-error",
                "error_message": "An error occurred while processing your request."
            }
            await uv_ws.send(json.dumps(error_result))

    async def handle_schedule_meeting(self, uv_ws, session, invocation_id: str, parameters):
        """
        Uses N8N to finalize a meeting schedule.
        """
        # This function needs to be implemented to interact with N8N
        # Since N8N is not available, a placeholder response is used
        try:
            name = parameters.get("name")
            email = parameters.get("email")
            purpose = parameters.get("purpose")
            datetime_str = parameters.get("datetime")
            location = parameters.get("location")

            logger.info(f"Received schedule_meeting parameters: name={name}, email={email}, purpose={purpose}, datetime={datetime_str}, location={location}")

            # Placeholder response
            booking_message = f"Meeting scheduled successfully for {name} at {location} on {datetime_str} to discuss {purpose}."

            # Simulate Google Calendar integration
            # In a real implementation, you would use the Google Calendar API to schedule the meeting
            # and store the event details in a database

            # Return the final outcome to Ultravox
            tool_result = {
                "type": "client_tool_result",
                "invocationId": invocationId,
                "result": booking_message,
                "response_type": "tool-response"
            }
            await uv_ws.send(json.dumps(tool_result))
            logger.info(f"Sent schedule_meeting result to Ultravox: {booking_message}")

        except Exception as e:
            logger.error(f"Error scheduling meeting: {e}")
            # Send error result back to Ultravox
            error_result = {
                "type": "client_tool_result",
                "invocationId": invocationId,
                "error_type": "implementation-error",
                "error_message": "An error occurred while scheduling your meeting."
            }
            await uv_ws.send(json.dumps(error_result))
            logger.info("Sent error message for schedule_meeting to Ultravox.")

    async def process_media_stream(self, websocket: WebSocket, call_sid: str, stream_sid: str, first_message: str, voice: str = None):
        """
        Handles the Twilio <Stream> WebSocket and connects to Ultravox via WebSocket.
        """
        uv_ws = None  # Ultravox WebSocket connection
        try:
            # Simulate getting call history
            call_history = "Previous calls: No previous calls found."

            # Create Ultravox call with first_message
            uv_join_url = await self.create_ultravox_call(
                system_prompt="You are a helpful AI assistant.",
                first_message=first_message,
                voice=voice,
                call_history=call_history
            )

            if not uv_join_url:
                logger.error("Ultravox joinUrl is empty. Cannot establish WebSocket connection.")
                return

            # Connect to Ultravox WebSocket
            try:
                uv_ws = await websockets.connect(uv_join_url)
                logger.info("Ultravox WebSocket connected.")
            except Exception as e:
                logger.error(f"Error connecting to Ultravox WebSocket: {e}")
                return

            # Handle messages from Ultravox
            async def handle_ultravox():
                try:
                    call_duration = 0
                    start_time = datetime.now()
                    end_reason = None
                    twilio_cost = 0
                    segments = 0
                    transcription = ""

                    async for raw_message in uv_ws:
                        if isinstance(raw_message, bytes):
                            # Agent audio in PCM s16le
                            try:
                                mu_law_bytes = audioop.lin2ulaw(raw_message, 2)
                                payload_base64 = base64.b64encode(mu_law_bytes).decode('ascii')
                            except Exception as e:
                                logger.error(f"Error transcoding PCM to µ-law: {e}")
                                continue  # Skip this payload

                            # Send to Twilio as media payload
                            try:
                                await websocket.send_text(json.dumps({
                                    "event": "media",
                                    "streamSid": stream_sid,
                                    "media": {
                                        "payload": payload_base64
                                    }
                                }))
                            except Exception as e:
                                logger.error(f"Error sending media to Twilio: {e}")

                        else:
                            # Text data message from Ultravox
                            try:
                                msg_data = json.loads(raw_message)
                            except Exception as e:
                                logger.error(f"Ultravox non-JSON data: {raw_message}")
                                continue

                            msg_type = msg_data.get("type") or msg_data.get("eventType")

                            if msg_type == "transcript":
                                role = msg_data.get("role")
                                text = msg_data.get("text") or msg_data.get("delta")
                                final = msg_data.get("final", False)

                                if role and text:
                                    role_cap = role.capitalize()
                                    logger.info(f"{role_cap} says: {text}")
                                    transcription += f"{role_cap} says: {text}\n"

                            elif msg_type == "client_tool_invocation":
                                toolName = msg_data.get("toolName", "")
                                invocationId = msg_data.get("invocationId")
                                parameters = msg_data.get("parameters", {})
                                logger.info(f"Invoking tool: {toolName} with invocationId: {invocationId} and parameters: {parameters}")

                                if toolName == "question_and_answer":
                                    question = parameters.get('question')
                                    await self.handle_question_and_answer(uv_ws, invocationId, question)
                                elif toolName == "schedule_meeting":
                                    await self.handle_schedule_meeting(uv_ws, {}, invocationId, parameters) # Removed session
                                elif toolName == "hangUp":
                                    logger.info("Received hangUp tool invocation")
                                    # Send success response back to the agent
                                    tool_result = {
                                        "type": "client_tool_result",
                                        "invocationId": invocationId,
                                        "result": "Call ended successfully",
                                        "response_type": "tool-response"
                                    }
                                    await uv_ws.send(json.dumps(tool_result))

                                    # End the call process:
                                    logger.info(f"Ending call (CallSid={call_sid})")
                                    end_reason = "agent_hangup"

                                    # Close Ultravox WebSocket
                                    if uv_ws and uv_ws.state == websockets.protocol.State.OPEN:
                                        await uv_ws.close()

                                    # End Twilio call - This part needs to be handled in the main app
                                    return  # Exit the Ultravox handler
                            elif msg_type == "new_stage":
                                # Handle new call stage
                                logger.info("Received new_stage event")
                                # Extract the new stage parameters from the message
                                # Update the system prompt, tools, etc. based on the new stage parameters
                                # This is a placeholder - implement the actual logic here
                                pass
                            elif msg_type in ['response.content.done', 'response.done', 'session.created', 'conversation.item.input_audio_transcription.completed']:
                                logger.info(f"Ultravox event: {msg_type} - {msg_data}")
                            else:
                                logger.info(f"Unhandled Ultravox message type: {msg_type} - {msg_data}")

                    end_time = datetime.now()
                    call_duration = (end_time - start_time).total_seconds()

                except Exception as e:
                    logger.error(f"Error in handle_ultravox: {e}")
                finally:
                    if uv_ws and uv_ws.state == websockets.protocol.State.OPEN:
                        await uv_ws.close()

                # Simulate getting Twilio stats
                twilio_cost = 0.50  # Example cost
                segments = 3  # Example segments

                # Simulate getting Google Calendar event
                calendar_event = {"summary": "Meeting with John Doe", "start_time": "2024-01-01T10:00:00Z"}
                # Simulate getting Gmail event
                gmail_event = {"subject": "Meeting Summary", "to": "john.doe@example.com"}

            # Start handling Twilio media as a separate task
            twilio_task = asyncio.create_task(handle_twilio())

            try:
                # Handle messages from Twilio
                while True:
                    message = await websocket.receive_text()
                    data = json.loads(message)

                    if data.get('event') == 'media':
                        # Twilio sends media from user
                        payload_base64 = data['media']['payload']

                        try:
                            # Decode base64 to get raw µ-law bytes
                            mu_law_bytes = base64.b64decode(payload_base64)

                        except Exception as e:
                            logger.error(f"Error decoding base64 payload: {e}")
                            continue  # Skip this payload

                        try:
                            # Transcode µ-law to PCM (s16le)
                            pcm_bytes = audioop.ulaw2lin(mu_law_bytes, 2)
                            
                        except Exception as e:
                            logger.error(f"Error transcoding µ-law to PCM: {e}")
                            continue  # Skip this payload

                        # Send PCM bytes to Ultravox
                        if uv_ws and uv_ws.state == websockets.protocol.State.OPEN:
                            try:
                                await uv_ws.send(pcm_bytes)
                       
                            except Exception as e:
                                logger.error(f"Error sending PCM to Ultravox: {e}")

            except Exception as e:
                logger.error(f"Error in process_media_stream: {e}")
            finally:
                if uv_ws and uv_ws.state == websockets.protocol.State.OPEN:
                    await uv_ws.close()
                if not twilio_task.done():
                    twilio_task.cancel()

        except Exception as e:
            logger.error(f"Error in process_media_stream: {e}")
        finally:
            if uv_ws and uv_ws.state == websockets.protocol.State.OPEN:
                await uv_ws.close()

twilio_task = None # Define twilio_task outside the try block
ultravox_service = UltravoxService()
