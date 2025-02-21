import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

class GoogleService:
    def __init__(self):
        self.creds = None
        try:
            # Load credentials from the environment
            self.creds, _ = google.auth.default()
            if not self.creds or not self.creds.valid:
                logger.warning("Google credentials not found or invalid. Ensure GOOGLE_APPLICATION_CREDENTIALS is set.")
        except Exception as e:
            logger.error(f"Failed to load Google credentials: {e}")

    def get_calendar_events(self, calendar_id='primary', max_results=10):
        """
        Retrieve upcoming events from Google Calendar.
        """
        try:
            service = build('calendar', 'v3', credentials=self.creds)
            now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
            events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                                maxResults=max_results, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])
            return events
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None

    def send_gmail_message(self, to, subject, message_text):
        """
        Send an email message using Gmail.
        """
        try:
            service = build('gmail', 'v1', credentials=self.creds)
            message = create_message("me", to, subject, message_text)
            send_message(service, "me", message)
            return True
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return False

    def list_drive_files(self, page_size=10):
        """
        List files from Google Drive.
        """
        try:
            service = build('drive', 'v3', credentials=self.creds)
            results = service.files().list(pageSize=page_size, fields="nextPageToken, files(id, name)").execute()
            items = results.get('files', [])
            return items
        except HttpError as error:
            logger.error(f"An error occurred: {error}")
            return None

# Helper functions for Gmail
def create_message(sender, to, subject, message_text):
    """Create a message for an email."""
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
    """Send an email message."""
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        logger.info(f'Message Id: {message["id"]}')
        return message
    except HttpError as error:
        logger.error(f'An error occurred: {error}')
        return None

# Example usage (can be removed or commented out)
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    google_service = GoogleService()
    
    # Example: List calendar events
    events = google_service.get_calendar_events()
    if events:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            logger.info(f"{start} - {event['summary']}")
    else:
        logger.warning("Could not retrieve calendar events.")
