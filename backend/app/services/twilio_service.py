from twilio.rest import Client
from ..config import settings
from ..database import get_db_connection, Error as DBError # Added DB imports (using mysql.connector.Error as DBError)
from datetime import datetime # Added datetime
import logging # Added logging

logger = logging.getLogger(__name__)

class TwilioService:
    def __init__(self):
        # Ensure credentials are valid
        if not settings.twilio_account_sid or not settings.twilio_auth_token:
             logger.error("Twilio credentials missing in settings.")
             # Handle this case appropriately, maybe raise an exception
             # For now, initialization might proceed but calls will fail
             self.client = None
        else:
            self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)

    def make_call(self, to_number: str, from_number: str, twiml: str): # Changed url to twiml
        call_resource = None # Initialize call resource to None
        if not self.client:
             logger.error("Twilio client not initialized due to missing credentials.")
             raise Exception("Twilio client not initialized.") # Or a more specific exception

        try:
            logger.info(f"Attempting Twilio API call: to={to_number}, from={from_number}, twiml provided.")
            # Use twiml parameter instead of url
            call_resource = self.client.calls.create(
                to=to_number,
                from_=from_number,
                twiml=twiml,
                # Add status callback to receive updates for outbound calls too
                status_callback=f"{settings.base_url}/api/calls/call-status", # BASE_URL must be in .env
                status_callback_method="POST",
                status_callback_event=["initiated", "ringing", "answered", "completed"]
            )
            # Log success immediately after API call returns
            logger.info(f"Twilio API call successful. SID={call_resource.sid}, Status={call_resource.status}")

            # Now attempt database logging (uncommented)
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
                    # Use call_resource.sid from the Twilio response
                    params = (call_resource.sid, from_number, to_number, 'outbound', call_resource.status, start_time)
                    cursor.execute(sql, params)
                    conn.commit()
                    logger.info(f"Logged start of outbound call: {call_resource.sid}")
                else:
                    logger.error(f"Database connection unavailable for logging outbound call: {call_resource.sid}")
            except DBError as db_e:
                logger.error(f"Database error logging outbound call {call_resource.sid}: {db_e}")
                # Log DB error but don't fail the whole operation
            except Exception as log_e:
                 logger.error(f"Unexpected error logging outbound call {call_resource.sid}: {log_e}")
                 # Log other error but don't fail the whole operation
            finally:
                if cursor: cursor.close()
                if conn: conn.close()

            return call_resource # Return the Twilio call resource object

        except Exception as e:
            # Log the specific Twilio API error
            logger.error(f"Twilio API call failed: to={to_number}, from={from_number}. Error: {e}", exc_info=True)
            # Re-raise the exception so the calling route knows it failed
            raise e
