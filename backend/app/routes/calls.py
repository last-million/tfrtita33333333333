from fastapi import APIRouter, HTTPException, Request, Response, Depends, status as http_status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
# Updated database import for MySQL connection pool
from ..database import get_db_connection, Error as DBError # Using mysql.connector.Error as DBError
# Import services
from ..services.twilio_service import TwilioService
from ..config import settings # To get base_url if needed for TwiML URL
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream
import logging

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# --- Pydantic Models ---

class CallLogBase(BaseModel):
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
    agent_hangup_reason: Optional[str] = None
    ultravox_recording_url: Optional[str] = None

class CallLog(CallLogBase):
    call_sid: str

    class Config:
        orm_mode = True # For compatibility if using ORM later
        from_attributes = True # Pydantic v2 way

class CallLogResponse(BaseModel):
    page: int
    limit: int
    total_calls: int
    calls: List[CallLog]

class BulkCallRequest(BaseModel):
    phone_numbers: List[str]
    message_template: Optional[str] = None # Placeholder for potential future use

class ClientBase(BaseModel):
    name: str
    phone_number: str
    email: Optional[str] = None
    address: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class Client(ClientBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class InitiateCallRequest(BaseModel):
    to_number: str
    from_number: Optional[str] = None # Make from_number optional here

class InitiateCallResponse(BaseModel):
    status: str
    call_sid: str
    to: str
    from_num: str # Renamed to avoid conflict with Python keyword

class BulkCallResult(BaseModel):
    number: str
    status: str
    call_sid: Optional[str] = None
    error: Optional[str] = None

class BulkCallResponse(BaseModel):
    total_numbers: int
    results: List[BulkCallResult]

class ClientImportResponse(BaseModel):
    message: str
    inserted: int
    skipped: int

# --- Service Instantiation ---
twilio_service = TwilioService()

# --- API Endpoints ---

@router.post("/initiate", response_model=InitiateCallResponse)
async def initiate_single_call(call_request: InitiateCallRequest):
    """
    Initiate an outbound call via Twilio. Accepts JSON body.
    """
    try:
        # Use provided from_number or default from settings
        effective_from_number = call_request.from_number or settings.twilio_from_number
        if not effective_from_number:
             logger.error("Missing 'from_number' in request and no default configured.")
             raise HTTPException(status_code=400, detail="Missing 'from_number' and no default configured.")

        # Generate TwiML to connect to WebSocket stream
        server_domain = settings.base_url.replace("http://", "").replace("https://", "")
        stream_url = f"wss://{server_domain}/media-stream"
        twiml = VoiceResponse()
        connect = Connect()
        stream = Stream(url=stream_url)
        stream.parameter(name="callerNumber", value=effective_from_number)
        stream.parameter(name="calleeNumber", value=call_request.to_number)
        connect.append(stream)
        twiml.append(connect)
        twiml_string = str(twiml)

        logger.info(f"Attempting to initiate call via TwilioService to {call_request.to_number} from {effective_from_number}...")
        call = twilio_service.make_call(to_number=call_request.to_number, from_number=effective_from_number, twiml=twiml_string)

        if not call or not call.sid:
             # Handle case where make_call failed internally but didn't raise exception
             raise HTTPException(status_code=500, detail="Failed to initiate call via Twilio service.")

        logger.info(f"Twilio call object created with SID: {call.sid}")
        return InitiateCallResponse(
            status="call_initiated",
            call_sid=call.sid,
            to=call_request.to_number,
            from_num=effective_from_number
        )
    except Exception as e:
        logger.error(f"Failed to initiate call to {call_request.to_number}: {e}", exc_info=True)
        # Check if it's a TwilioRestException and provide more specific feedback if possible
        detail_msg = f"Failed to initiate call: {e}"
        status_code = 500
        if "TwilioRestException" in str(type(e)):
             detail_msg = f"Twilio API Error: {e}"
             # Keep 500 or adjust based on Twilio error if needed
        raise HTTPException(status_code=status_code, detail=detail_msg)


@router.post("/bulk", response_model=BulkCallResponse)
async def bulk_call_campaign(request: BulkCallRequest):
    """
    Initiate bulk calls to multiple phone numbers.
    Note: Consider using background tasks for large lists.
    """
    results = []
    from_number = settings.twilio_from_number
    if not from_number:
         logger.error("Missing TWILIO_FROM_NUMBER in configuration for bulk call.")
         raise HTTPException(status_code=500, detail="Twilio 'from' number not configured.")

    logger.info(f"Starting bulk call campaign from {from_number} to {len(request.phone_numbers)} numbers.")
    server_domain = settings.base_url.replace("http://", "").replace("https://", "")
    stream_url = f"wss://{server_domain}/media-stream"

    for number in request.phone_numbers:
        try:
            # Generate TwiML for this specific call
            twiml = VoiceResponse()
            connect = Connect()
            stream = Stream(url=stream_url)
            stream.parameter(name="callerNumber", value=from_number)
            stream.parameter(name="calleeNumber", value=number)
            connect.append(stream)
            twiml.append(connect)
            twiml_string = str(twiml)

            logger.info(f"Attempting bulk call via TwilioService to {number} from {from_number}...")
            call = twilio_service.make_call(to_number=number, from_number=from_number, twiml=twiml_string)

            if not call or not call.sid:
                 raise Exception("Twilio service did not return a valid call object.")

            logger.info(f"Bulk call initiated to {number} with SID: {call.sid}")
            results.append(BulkCallResult(
                number=number,
                status="call_initiated",
                call_sid=call.sid
            ))
        except Exception as e:
            logger.error(f"Failed to initiate bulk call to {number}: {e}", exc_info=True)
            results.append(BulkCallResult(
                number=number,
                status="failed",
                error=str(e)
            ))

    return BulkCallResponse(
        total_numbers=len(request.phone_numbers),
        results=results
    )


@router.get("/history", response_model=CallLogResponse)
def get_call_history(
    page: int = 1,
    limit: int = 50,
    status: Optional[str] = None,
    direction: Optional[str] = None
):
    """
    Retrieve paginated call history with optional filtering by status and direction from MySQL.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=503, detail="Database connection is not available.")

        cursor = conn.cursor(dictionary=True) # Use dictionary cursor for easy Pydantic conversion

        # Build WHERE clause
        conditions = []
        params = []
        if status:
            conditions.append("status = %s")
            params.append(status)
        if direction:
            conditions.append("direction = %s")
            params.append(direction)
        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM call_logs{where_clause}"
        cursor.execute(count_query, tuple(params))
        count_result = cursor.fetchone()
        total_calls = count_result['total'] if count_result else 0

        # Get paginated results
        offset = (page - 1) * limit
        base_query = f"SELECT * FROM call_logs{where_clause} ORDER BY start_time DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        cursor.execute(base_query, tuple(params))
        rows = cursor.fetchall()

        # Convert rows to CallLog objects
        call_logs_data = [CallLog(**row) for row in rows]

        return CallLogResponse(
            page=page,
            limit=limit,
            total_calls=total_calls,
            calls=call_logs_data
        )
    except DBError as e:
        logger.error(f"MySQL Database error in get_call_history: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in get_call_history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


# --- Client CRUD Operations ---

# TODO: Add GET endpoint to list clients with pagination

@router.post("/clients/import", response_model=ClientImportResponse)
async def import_clients(clients: List[ClientCreate]): # Use ClientCreate model
    """
    Import multiple clients into the database.
    Uses INSERT IGNORE to skip duplicates based on phone_number unique constraint.
    """
    conn = None
    cursor = None
    inserted_count = 0
    skipped_count = 0
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=503, detail="Database connection unavailable.")
        cursor = conn.cursor()

        sql = """
            INSERT IGNORE INTO clients (name, phone_number, email, address)
            VALUES (%s, %s, %s, %s)
        """
        # Use .dict() or .model_dump() for Pydantic v2
        values = [
            (c.name, c.phone_number, c.email, c.address) for c in clients
        ]

        cursor.executemany(sql, values)
        conn.commit()
        inserted_count = cursor.rowcount
        skipped_count = len(clients) - inserted_count
        logger.info(f"Imported {inserted_count} clients, skipped {skipped_count} duplicates.")

        return ClientImportResponse(
            message=f"Client import finished. Inserted: {inserted_count}, Skipped (duplicates): {skipped_count}",
            inserted=inserted_count,
            skipped=skipped_count
        )
    except DBError as e:
        logger.error(f"Database error importing clients: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error importing clients: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@router.post("/clients", response_model=Client, status_code=http_status.HTTP_201_CREATED)
async def create_client(client_data: ClientCreate): # Use ClientCreate model
    """
    Create a new client in the database.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=503, detail="Database connection unavailable.")
        cursor = conn.cursor(dictionary=True)

        sql = """
            INSERT INTO clients (name, phone_number, email, address)
            VALUES (%s, %s, %s, %s)
        """
        params = (client_data.name, client_data.phone_number, client_data.email, client_data.address)
        cursor.execute(sql, params)
        new_client_id = cursor.lastrowid
        conn.commit()
        logger.info(f"Created client with ID: {new_client_id}")

        # Fetch the created client to return it
        cursor.execute("SELECT * FROM clients WHERE id = %s", (new_client_id,))
        created_client_dict = cursor.fetchone()
        if not created_client_dict:
             raise HTTPException(status_code=500, detail="Failed to retrieve created client.")

        return Client(**created_client_dict)

    except DBError as e:
        if e.errno == 1062: # Duplicate phone number
             raise HTTPException(status_code=409, detail=f"Client with phone number {client_data.phone_number} already exists.")
        logger.error(f"Database error creating client: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error creating client: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@router.put("/clients/{client_id}", response_model=Client)
async def update_client(client_id: int, client_data: ClientCreate): # Use ClientCreate model
    """
    Update an existing client in the database.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=503, detail="Database connection unavailable.")
        cursor = conn.cursor(dictionary=True)

        sql = """
            UPDATE clients
            SET name = %s, phone_number = %s, email = %s, address = %s
            WHERE id = %s
        """
        params = (client_data.name, client_data.phone_number, client_data.email, client_data.address, client_id)
        cursor.execute(sql, params)

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Client with ID {client_id} not found.")

        conn.commit()
        logger.info(f"Updated client with ID: {client_id}")

        # Fetch the updated client to return it
        cursor.execute("SELECT * FROM clients WHERE id = %s", (client_id,))
        updated_client_dict = cursor.fetchone()
        if not updated_client_dict:
             raise HTTPException(status_code=500, detail="Failed to retrieve updated client.")

        return Client(**updated_client_dict)

    except DBError as e:
        if e.errno == 1062: # Duplicate phone number
             raise HTTPException(status_code=409, detail=f"Another client with phone number {client_data.phone_number} already exists.")
        logger.error(f"Database error updating client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error updating client {client_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()


@router.delete("/clients/{client_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int):
    """
    Delete a client from the database.
    """
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        if conn is None:
            raise HTTPException(status_code=503, detail="Database connection unavailable.")
        cursor = conn.cursor()

        sql = "DELETE FROM clients WHERE id = %s"
        cursor.execute(sql, (client_id,))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Client with ID {client_id} not found.")

        conn.commit()
        logger.info(f"Deleted client with ID: {client_id}")
        # Return No Content on success
        return Response(status_code=http_status.HTTP_204_NO_CONTENT)

    except DBError as e:
        logger.error(f"Database error deleting client {client_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error deleting client {client_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if cursor: cursor.close()
        if conn: conn.close()

# --- Twilio Webhook ---

@router.post("/incoming-call")
async def incoming_call(request: Request):
    """
    Handle the inbound call from Twilio.
    """
    server_domain = settings.base_url.replace("http://", "").replace("https://", "")
    stream_url = f"wss://{server_domain}/media-stream"

    try:
        form_data = await request.form()
        twilio_params = dict(form_data)
        logger.info(f"Incoming call received: {twilio_params}")

        caller_number = twilio_params.get('From', 'Unknown')
        call_sid = twilio_params.get('CallSid')
        to_number = twilio_params.get('To', 'Unknown') # Twilio's 'To' number

        if not call_sid:
            logger.error("Missing CallSid in Twilio request")
            raise HTTPException(status_code=400, detail="Missing CallSid")

        # Log the start of the incoming call immediately
        conn = None
        cursor = None
        try:
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                sql = """
                    INSERT INTO call_logs (call_sid, from_number, to_number, direction, status, start_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE status = VALUES(status)
                """
                start_time = datetime.utcnow()
                params = (call_sid, caller_number, to_number, 'inbound', 'initiated', start_time)
                cursor.execute(sql, params)
                conn.commit()
                logger.info(f"Logged start of incoming call: {call_sid}")
            else:
                logger.error(f"Database connection unavailable for logging incoming call: {call_sid}")
        except DBError as e:
            logger.error(f"Database error logging incoming call {call_sid}: {e}")
            # Don't fail the call TwiML generation, just log the error
        finally:
            if cursor: cursor.close()
            if conn: conn.close()

        # Prepare TwiML response
        twiml = VoiceResponse()
        connect = Connect()
        stream = Stream(url=stream_url)
        stream.parameter(name="callSid", value=call_sid)
        stream.parameter(name="callerNumber", value=caller_number)
        # Pass first message placeholder - WebSocket handler will fetch actual one if needed
        stream.parameter(name="firstMessage", value="Hello from TwiML")
        connect.append(stream)
        twiml.append(connect)

        return Response(content=str(twiml), media_type="application/xml")

    except Exception as e:
        logger.error(f"Error handling incoming call: {e}", exc_info=True)
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
    call_sid = None # Initialize call_sid
    try:
        form_data = await request.form()
        status_data = dict(form_data)
        call_sid = status_data.get('CallSid') # Get call_sid early for logging
        logger.info(f"Received call status update for {call_sid}: {status_data}")

        call_status = status_data.get('CallStatus')
        call_direction = status_data.get('Direction')
        duration = status_data.get('CallDuration')
        recording_url = status_data.get('RecordingUrl')

        if not call_sid:
            logger.error("CallSid missing in status update")
            return Response(status_code=200) # Ack Twilio

        conn = get_db_connection()
        if conn is None:
            logger.error(f"Database connection unavailable for call status update: {call_sid}")
            return Response(status_code=200) # Ack Twilio

        cursor = conn.cursor()
        update_fields = []
        params = []
        if call_status:
            update_fields.append("status = %s")
            params.append(call_status)
        if call_direction:
            update_fields.append("direction = %s")
            params.append(call_direction)
        if duration is not None: # Check for None explicitly
            try:
                 update_fields.append("duration = %s")
                 params.append(int(duration))
            except (ValueError, TypeError):
                 logger.warning(f"Invalid duration value '{duration}' for CallSid {call_sid}. Skipping duration update.")
        if recording_url:
            update_fields.append("recording_url = %s")
            params.append(recording_url)
        if call_status in ['completed', 'failed', 'busy', 'no-answer', 'canceled']:
             update_fields.append("end_time = %s")
             params.append(datetime.utcnow())

        if not update_fields:
            logger.info(f"No relevant fields to update from Twilio status for CallSid: {call_sid}")
            return Response(status_code=200)

        params.append(call_sid)
        sql = f"UPDATE call_logs SET {', '.join(update_fields)} WHERE call_sid = %s"

        logger.info(f"Executing SQL for Twilio status: {sql} with params: {params}")
        cursor.execute(sql, tuple(params))
        conn.commit()
        logger.info(f"Call log updated from Twilio status for CallSid: {call_sid}")

        return Response(status_code=200)

    except DBError as e:
        logger.error(f"Database error updating call status for {call_sid}: {e}")
        return Response(status_code=200) # Ack Twilio
    except Exception as e:
        logger.error(f"Unexpected error handling call status update for {call_sid}: {e}", exc_info=True)
        return Response(status_code=200) # Ack Twilio
    finally:
        if cursor: cursor.close()
        if conn: conn.close()
