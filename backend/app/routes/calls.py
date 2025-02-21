from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from ..database import db  # Import the database connection
from fastapi.responses import Response
from twilio.twiml.voice_response import VoiceResponse, Connect, Stream

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
    id: int
    name: str
    phone_number: str
    email: Optional[str] = None
    address: Optional[str] = None  # Add address field

@router.post("/initiate")
async def initiate_call(to_number: str, from_number: str):
    """
    Initiate an outbound call via Twilio
    """
    # Implement Twilio call initiation logic
    return {
        "status": "call_initiated",
        "to": to_number,
        "from": from_number
    }

@router.post("/bulk")
async def bulk_call_campaign(request: BulkCallRequest):
    """
    Initiate bulk calls to multiple phone numbers
    """
    results = []
    for number in request.phone_numbers:
        try:
            # Simulate or actually initiate call for each number
            result = await initiate_call(number, "+1234567890")
            results.append(result)
        except Exception as e:
            results.append({
                "number": number, 
                "status": "failed", 
                "error": str(e)
            })
    
    return {
        "total_numbers": len(request.phone_numbers),
        "results": results
    }

@router.get("/history")
async def get_call_history(
    page: int = 1, 
    limit: int = 50, 
    status: Optional[str] = None
):
    """
    Retrieve paginated call history with optional filtering
    """
    if db is None:
        raise HTTPException(status_code=500, detail="Database connection is not available.")

    try:
        # Construct the base query
        query = "SELECT * FROM call_logs"
        conditions = []
        params = {}

        # Add status filter if provided
        if status:
            conditions.append("status = :status")
            params["status"] = status

        # Combine conditions
        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Add pagination
        query += " LIMIT :limit OFFSET :offset"
        params["limit"] = limit
        params["offset"] = (page - 1) * limit

        # Execute the query
        rows = await db.execute(query, params)

        # Convert rows to CallLog objects
        call_logs = [CallLog(**dict(row)) for row in rows]

        # Get total count (for pagination)
        count_query = "SELECT COUNT(*) FROM call_logs"
        if conditions:
            count_query += " WHERE " + " AND ".join(conditions)
        count_result = await db.execute(count_query, params)
        total_calls = count_result[0][0]

        return {
            "page": page,
            "limit": limit,
            "total_calls": total_calls,
            "calls": call_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")

@router.post("/clients/import")
async def import_clients(clients: List[Client]):
    """
    Import clients from Google Sheet (simulated)
    """
    # In a real application, you would store this data in the database
    # For this example, we just return the data
    return {
        "message": "Clients imported successfully (simulated)",
        "clients": clients
    }

@router.post("/clients")
async def create_client(client: Client):
    """
    Create a new client (simulated)
    """
    # In a real application, you would store this data in the database
    # For this example, we just return the data
    return {
        "message": "Client created successfully (simulated)",
        "client": client
    }

@router.put("/clients/{client_id}")
async def update_client(client_id: int, client: Client):
    """
    Update an existing client (simulated)
    """
    # In a real application, you would update this data in the database
    # For this example, we just return the data
    return {
        "message": "Client updated successfully (simulated)",
        "client": client
    }

@router.delete("/clients/{client_id}")
async def delete_client(client_id: int):
    """
    Delete a client (simulated)
    """
    # In a real application, you would delete this data from the database
    # For this example, we just return a success message
    return {
        "message": "Client deleted successfully (simulated)",
        "client_id": client_id
    }

@router.post("/incoming-call")
async def incoming_call(request: Request):
    """
    Handle the inbound call from Twilio.
    """
    form_data = await request.form()
    twilio_params = dict(form_data)
    print('Incoming call')

    caller_number = twilio_params.get('From', 'Unknown')
    call_sid = twilio_params.get('CallSid')

    # Replace with your actual server domain
    server_domain = "your-server-domain.com"  
    stream_url = f"wss://{server_domain}/media-stream"

    twiml = VoiceResponse()
    connect = Connect()
    stream = Stream(url=stream_url)
    stream.parameter(name="callSid", value=call_sid)
    stream.parameter(name="callerNumber", value=caller_number)
    connect.append(stream)
    twiml.append(connect)

    return Response(content=str(twiml), media_type="application/xml")
