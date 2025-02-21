from twilio.rest import Client
from ..config import settings

class TwilioService:
    def __init__(self):
        self.client = Client(settings.twilio_account_sid, settings.twilio_auth_token)
    
    def make_call(self, to_number: str, from_number: str, url: str):
        return self.client.calls.create(
            to=to_number,
            from_=from_number,
            url=url
        )
