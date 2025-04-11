from pydantic_settings import BaseSettings
from typing import Optional # Import Optional

class Settings(BaseSettings):
    twilio_account_sid: str
    twilio_auth_token: str
    twilio_from_number: str # Added Twilio 'From' number for outbound calls
    supabase_url: str
    supabase_key: str
    google_client_id: str
    google_client_secret: str # Added Google Client Secret
    airtable_api_key: str = ""  # Default value if not provided in .env
    ultravox_api_key: str
    openai_api_key: Optional[str] = None # Added OpenAI API Key (optional)
    ultravox_model: str = "fixie-ai/ultravox-70B" # Added default Ultravox model
    ultravox_voice: str = "Tanya-English" # Added default Ultravox voice
    # database_url: str = "file:./data.db" # Removed, using specific DB vars now
    base_url: str = "http://localhost:8000" # Added Base URL for callbacks, default to localhost

    # MySQL specific settings (loaded from .env)
    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra keys in your .env file

settings = Settings()
