from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
# Updated database import for MySQL connection pool
from ..database import get_db_connection, Error as DBError
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

class CallLog(BaseModel):
    call_sid: str
    from_number: str
    to_number: str
    direction: str = Field(..., description="inbound or outbound")
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[int] = None
    recording_url: Optional[str] = None
    transcription: Optional[str] = None
    cost: Optional[float] = None
    segments: Optional[int] = None
    ultravox_cost: Optional[float] = None
    scheduled_meeting: Optional[str] = None
    email_sent: Optional[bool] = None
    email_address: Optional[str] = None
    email_text: Optional[str] = None
    email_received: Optional[bool] = None
    email_received_text: Optional[str] = None
    agent_hung_up: Optional[bool] = None

class BulkCallRequest(BaseModel):
    phone_numbers: List[str]
    message_template: Optional[str] = None

class Client(BaseModel):
    id: int # Assuming client ID is an integer
    name: str
    phone_number: str
    email: Optional[str] = None
    address: Optional[str] = None

@router.post("/initiate")
async def initiate_call(to_number: str, from_number: str):
    """
    Initiate an outbound call via Twilio (Placeholder)
    """
    # TODO: Implement actual Twilio call initiation logic using services
    logger.info(f"Simulating call initiation to {to_number} from {from_number}")
    return {
        "status": "call_initiated",
        "to": to_number,
        "from": from_number
    }

@router.post("/bulk")
async def bulk_call_campaign(request: BulkCallRequest):
    """
    Initiate bulk calls to multiple phone numbers (Placeholder)
    """
    results = []
    # TODO: Replace with actual from_number logic
    from_number_placeholder = "+1234567890"
    for number in request.phone_numbers:
        try:
            # Simulate or actually initiate call for each number
            # In a real scenario, this might be a background task
            result = await initiate_call(number, from_number_placeholder)
            results.append(result)
        except Exception as e:
            logger.error(f"Failed to initiate call to {number}: {e}")
            results.append({
                "number": number,
                "status": "failed",
                "error": str(e)
            })

    return {
        "total_numbers": len(request.phone_numbers),
        "results": results
    }

# Changed to synchronous function to work with mysql.connector
@router.get("/history")
def get_call_history(
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None
):
    """
    Retrieve paginated call history with optional filtering from MySQL.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=503, detail="Database connection is not available.")

        cursor = conn.cursor(dictionary=True) # Use dictionary cursor

        # Construct the base query
        base_query = "SELECT * FROM call_logs"
        count_query = "SELECT COUNT(*) as total FROM call_logs"
        conditions = []
        params = []

        # Add status filter if provided
        if status:
            conditions.append("status = %s")
            params.append(status)

        # Combine conditions
        if conditions:
            where_clause = " WHERE " + " AND ".join(conditions)
            base_query += where_clause
            count_query += where_clause

        # Get total count first
        cursor.execute(count_query, tuple(params))
        count_result = cursor.fetchone()
        total_calls = count_result['total'] if count_result else 0

        # Add pagination to base query
        offset = (page - 1) * limit
        base_query += " ORDER BY start_time DESC LIMIT %s OFFSET %s" # Added ORDER BY
        params.extend([limit, offset])

        # Execute the main query
        cursor.execute(base_query, tuple(params))
        rows = cursor.fetchall()

        # Convert rows to CallLog objects (handle potential None values if needed)
        call_logs = [CallLog(**row) for row in rows]

        return {
            "page": page,
            "limit": limit,
            "total_calls": total_calls,
            "calls": call_logs
        }
    except DBError as e:
        logger.error(f"MySQL Database error in get_call_history: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_call_history: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# --- Client CRUD Operations (Simulated/Placeholders) ---
# These need to be updated to use the MySQL database connection

@router.post("/clients/import")
async def import_clients(clients: List[Client]):
    """
    Import clients from Google Sheet (simulated)
    """
    # TODO: Implement database insertion logic
    logger.info(f"Simulating import of {len(clients)} clients.")
    return {
        "message": "Clients imported successfully (simulated)",
        "count": len(clients)
    }

@router.post("/clients")
async def create_client(client: Client):
    """
    Create a new client (simulated)
    """
    # TODO: Implement database insertion logic
    logger.info(f"Simulating creation of client: {client.name}")
    # Assign a dummy ID for the response
    client_dict = client.dict()
    client_dict['id'] = 999 # Dummy ID
    return {
        "message": "Client created successfully (simulated)",
        "client": client_dict
    }

@router.put("/clients/{client_id}")
async def update_client(client_id: int, client: Client):
    """
    Update an existing client (simulated)
    """
    # TODO: Implement database update logic
    logger.info(f"Simulating update of client ID: {client_id}")
    client_dict = client.dict()
    client_dict['id'] = client_id # Ensure ID matches path param
    return {
        "message": "Client updated successfully (simulated)",
        "client": client_dict
    }

@router.delete("/clients/{client_id}")
async def delete_client(client_id: int):
    """
    Delete a client (simulated)
    """
    # TODO: Implement database deletion logic
    logger.info(f"Simulating deletion of client ID: {client_id}")
    return {
        "message": "Client deleted successfully (simulated)",
        "client_id": client_id
    }

# --- Twilio Webhook ---

@router.post("/incoming-call")
async def incoming_call(request: Request):
    """
    Handle the inbound call from Twilio.
    """
    # TODO: Replace with actual domain from config/env
    server_domain = "ajingolik.fun" # Use the actual domain
    stream_url = f"wss://{server_domain}/media-stream" # Ensure correct path

    try:
        form_data = await request.form()
        twilio_params = dict(form_data)
        logger.info(f"Incoming call received: {twilio_params}")

        caller_number = twilio_params.get('From', 'Unknown')
        call_sid = twilio_params.get('CallSid')

        if not call_sid:
            logger.error("Missing CallSid in Twilio request")
            raise HTTPException(status_code=400, detail="Missing CallSid")

        twiml = VoiceResponse()
        connect = Connect()
        stream = Stream(url=stream_url)
        # Pass necessary parameters to your WebSocket handler
        stream.parameter(name="callSid", value=call_sid)
        stream.parameter(name="callerNumber", value=caller_number)
        # Add any other parameters your WebSocket needs
        connect.append(stream)
        twiml.append(connect)

        # TODO: Log the start of the call in the database

        return Response(content=str(twiml), media_type="application/xml")

    except Exception as e:
        logger.error(f"Error handling incoming call: {e}")
        # Return a TwiML response indicating an error if possible
        twiml = VoiceResponse()
        twiml.say("An application error occurred. Please try again later.")
        return Response(content=str(twiml), media_type="application/xml", status_code=500)

# Webhook endpoint for call status updates from Twilio
@router.post("/call-status")
async def call_status_update(request: Request):
    """
    Receive call status updates from Twilio and update the database.
    """
    conn = None
    cursor = None
    try:
        form_data = await request.form()
        status_data = dict(form_data)
        logger.info(f"Received call status update: {status_data}")

        call_sid = status_data.get('CallSid')
        call_status = status_data.get('CallStatus')
        duration = status_data.get('CallDuration')
        recording_url = status_data.get('RecordingUrl')
        # Add other fields as needed: RecordingDuration, Timestamp, etc.

        if not call_sid:
            logger.error("CallSid missing in status update")
            # Return 200 OK anyway so Twilio doesn't retry excessively
            return Response(status_code=200)

        conn = get_db_connection()
        if conn is None:
            logger.error(f"Database connection unavailable for call status update: {call_sid}")
            # Return 503 Service Unavailable? Or 200? Twilio prefers 200.
            return Response(status_code=200)

        cursor = conn.cursor()

        # Construct update query dynamically based on available data
        update_fields = []
        params = []
        if call_status:
            update_fields.append("status = %s")
            params.append(call_status)
        if duration:
            update_fields.append("duration = %s")
            params.append(int(duration)) # Ensure duration is integer
        if recording_url:
            update_fields.append("recording_url = %s")
            params.append(recording_url)
        # Add end_time based on status if applicable
        if call_status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
             update_fields.append("end_time = %s")
             params.append(datetime.utcnow()) # Use current time as end time

        if not update_fields:
            logger.info(f"No fields to update for CallSid: {call_sid}")
            return Response(status_code=200)

        params.append(call_sid) # For the WHERE clause
        sql = f"UPDATE call_logs SET {', '.join(update_fields)} WHERE call_sid = %s"

        logger.info(f"Executing SQL: {sql} with params: {params}")
        cursor.execute(sql, tuple(params))
        conn.commit()
        logger.info(f"Call log updated for CallSid: {call_sid}")

        return Response(status_code=200)

    except DBError as e:
        logger.error(f"Database error updating call status for {call_sid}: {e}")
        # Return 200 OK to prevent Twilio retries
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Unexpected error handling call status update for {call_sid}: {e}")
        # Return 200 OK to prevent Twilio retries
        return Response(status_code=200)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# TODO: Add WebSocket endpoint for /media-stream
# This would typically be handled by a separate WebSocket framework integration
# or within FastAPI using WebSockets.
