from twilio.rest import Client
from ..config import settings
from ..database import get_db_connection, Error as DBError # Added DB imports (using mysql.connector.Error as DBError)
from datetime import datetime # Added datetime
import logging # Added logging

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    def make_call(self, to_number: str, from_number: str, url: str):
        call = None # Initialize call to None
        try:
            call = self.client.calls.create(
                to=to_number,
                from_=from_number,
                url=url,
                # Add status callback to receive updates for outbound calls too
                status_callback=f"{settings.base_url}/api/calls/call-status", # BASE_URL must be in .env
                status_callback_method="POST",
                status_callback_event=["initiated", "ringing", "answered", "completed"]
            )
            logger.info(f"Twilio call initiated successfully: SID={call.sid}")

            # Log the start of the outbound call only if creation succeeded
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
                    params = (call.sid, from_number, to_number, 'outbound', 'initiated', start_time)
                    cursor.execute(sql, params)
                    conn.commit()
                    logger.info(f"Logged start of outbound call: {call.sid}")
                else:
                    logger.error(f"Database connection unavailable for logging outbound call: {call.sid}")
            except DBError as e:
                logger.error(f"Database error logging outbound call {call.sid}: {e}")
            except Exception as e:
                 logger.error(f"Unexpected error logging outbound call {call.sid}: {e}")
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

            return call # Return the call object if successful

        except Exception as e:
            logger.error(f"Failed to initiate Twilio call to {to_number} from {from_number}: {e}")
            # Re-raise the exception or handle it as needed
            raise e # Or return None, or a custom error response
