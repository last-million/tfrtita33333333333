from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    twilio_account_sid: str
    twilio_auth_token: str
    supabase_url: str
    supabase_key: str
    google_client_id: str
    airtable_api_key: str = ""  # Default value if not provided in .env
    ultravox_api_key: str
    database_url: str = "file:./data.db"  # LibSQL database URL

    class Config:
        env_file = ".env"
        extra = "allow"  # Allow extra keys in your .env file

settings = Settings()
