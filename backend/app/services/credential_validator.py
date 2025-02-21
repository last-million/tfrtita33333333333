import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import re
import requests

class CredentialValidator:
    def __init__(self):
        # Generate encryption key from environment variable or generate a secure one
        self.encryption_key = self._generate_encryption_key()

    def _generate_encryption_key(self):
        """
        Generate a secure encryption key
        Uses a combination of system entropy and a secret salt
        """
        # Use a combination of system entropy and a secret salt
        salt = os.environ.get('ENCRYPTION_SALT', 'default_salt').encode()
        
        # Use PBKDF2 for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000
        )
        
        # Derive key from a secret
        key = base64.urlsafe_b64encode(
            kdf.derive(os.environ.get('SECRET_KEY', 'fallback_secret').encode())
        )
        return key

    def encrypt_credentials(self, credentials):
        """
        Encrypt sensitive credentials
        """
        f = Fernet(self.encryption_key)
        encrypted_creds = {}
        
        for key, value in credentials.items():
            if self._is_sensitive_field(key):
                encrypted_value = f.encrypt(str(value).encode()).decode()
                encrypted_creds[key] = encrypted_value
            else:
                encrypted_creds[key] = value
        
        return encrypted_creds

    def decrypt_credentials(self, encrypted_credentials):
        """
        Decrypt sensitive credentials
        """
        f = Fernet(self.encryption_key)
        decrypted_creds = {}
        
        for key, value in encrypted_credentials.items():
            try:
                if self._is_sensitive_field(key):
                    decrypted_value = f.decrypt(str(value).encode()).decode()
                    decrypted_creds[key] = decrypted_value
                else:
                    decrypted_creds[key] = value
            except Exception as e:
                # Log decryption errors
                print(f"Decryption error for {key}: {e}")
                return None
        
        return decrypted_creds

    def _is_sensitive_field(self, field_name):
        """
        Identify sensitive fields that need encryption
        """
        sensitive_patterns = [
            'password', 'token', 'key', 'secret', 
            'auth', 'credentials', 'access_token'
        ]
        return any(pattern in field_name.lower() for pattern in sensitive_patterns)

    def validate_credentials(self, service, credentials):
        """
        Validate credentials for different services
        """
        validation_methods = {
            'Supabase': self._validate_supabase,
            'Twilio': self._validate_twilio,
            'SERP API': self._validate_serp_api,
            'Airtable': self._validate_airtable,
            'Google Calendar': self._validate_google_calendar,
            'Gmail': self._validate_gmail,
            'Google Drive': self._validate_google_drive
        }

        # Get the validation method for the specific service
        validator = validation_methods.get(service)
        if not validator:
            return {
                'valid': False, 
                'error': f'No validation method for {service}'
            }

        # Perform validation
        return validator(credentials)

    def _validate_supabase(self, credentials):
        """
        Validate Supabase credentials
        """
        try:
            # Basic URL and key format validation
            if not credentials.get('url') or not credentials.get('apiKey'):
                return {
                    'valid': False, 
                    'error': 'Missing Supabase URL or API Key'
                }

            # Validate URL format
            url_pattern = re.compile(
                r'^https://[a-zA-Z0-9-]+\.supabase\.co$'
            )
            if not url_pattern.match(credentials['url']):
                return {
                    'valid': False, 
                    'error': 'Invalid Supabase URL format'
                }

            # Optional: Add API call to verify credentials
            # This would be a lightweight endpoint check
            response = requests.get(
                f"{credentials['url']}/rest/v1/",
                headers={
                    'apikey': credentials['apiKey'],
                    'Authorization': f'Bearer {credentials["apiKey"]}'
                },
                timeout=5
            )
            
            return {
                'valid': response.status_code == 200,
                'error': 'Invalid Supabase credentials' if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'valid': False, 
                'error': f'Supabase validation error: {str(e)}'
            }

    def _validate_twilio(self, credentials):
        """
        Validate Twilio credentials
        """
        try:
            # Check required fields
            required_fields = ['accountSid', 'authToken']
            for field in required_fields:
                if not credentials.get(field):
                    return {
                        'valid': False, 
                        'error': f'Missing {field}'
                    }

            # Validate format of Account SID and Auth Token
            sid_pattern = re.compile(r'^AC[a-f0-9]{32}$')
            token_pattern = re.compile(r'^[a-f0-9]{32}$')

            if not sid_pattern.match(credentials['accountSid']):
                return {
                    'valid': False, 
                    'error': 'Invalid Twilio Account SID format'
                }

            if not token_pattern.match(credentials['authToken']):
                return {
                    'valid': False, 
                    'error': 'Invalid Twilio Auth Token format'
                }

            return {'valid': True}
        except Exception as e:
            return {
                'valid': False, 
                'error': f'Twilio validation error: {str(e)}'
            }

    def _validate_serp_api(self, credentials):
        """
        Validate SERP API credentials
        """
        try:
            if not credentials.get('apiKey'):
                return {
                    'valid': False, 
                    'error': 'Missing SERP API Key'
                }

            # Test API key with a simple search
            response = requests.get(
                'https://serpapi.com/search',
                params={
                    'q': 'test',
                    'api_key': credentials['apiKey']
                },
                timeout=5
            )
            
            return {
                'valid': response.status_code == 200,
                'error': 'Invalid SERP API Key' if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'valid': False, 
                'error': f'SERP API validation error: {str(e)}'
            }

    def _validate_airtable(self, credentials):
        """
        Validate Airtable credentials
        """
        try:
            if not credentials.get('apiKey') or not credentials.get('baseId'):
                return {
                    'valid': False, 
                    'error': 'Missing Airtable API Key or Base ID'
                }

            # Test Airtable API
            response = requests.get(
                f'https://api.airtable.com/v0/{credentials["baseId"]}',
                headers={
                    'Authorization': f'Bearer {credentials["apiKey"]}'
                },
                timeout=5
            )
            
            return {
                'valid': response.status_code == 200,
                'error': 'Invalid Airtable credentials' if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'valid': False, 
                'error': f'Airtable validation error: {str(e)}'
            }

    def _validate_google_calendar(self, credentials):
        """
        Validate Google Calendar credentials
        """
        try:
            if not credentials.get('apiKey') or not credentials.get('clientId'):
                return {
                    'valid': False, 
                    'error': 'Missing Google Calendar API Key or Client ID'
                }

            # Basic format validation
            if not re.match(r'^[A-Za-z0-9_-]+$', credentials['clientId']):
                return {
                    'valid': False, 
                    'error': 'Invalid Google Client ID format'
                }

            return {'valid': True}
        except Exception as e:
            return {
                'valid': False, 
                'error': f'Google Calendar validation error: {str(e)}'
            }

    def _validate_gmail(self, credentials):
        """
        Validate Gmail credentials
        """
        try:
            if not credentials.get('email') or not credentials.get('appPassword'):
                return {
                    'valid': False, 
                    'error': 'Missing Email or App Password'
                }

            # Email format validation
            email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@gmail\.com$')
            if not email_pattern.match(credentials['email']):
                return {
                    'valid': False, 
                    'error': 'Invalid Gmail email format'
                }

            # App password length and format (16 characters, alphanumeric)
            app_password_pattern = re.compile(r'^[A-Za-z0-9]{16}$')
            if not app_password_pattern.match(credentials['appPassword']):
                return {
                    'valid': False, 
                    'error': 'Invalid App Password format'
                }

            return {'valid': True}
        except Exception as e:
            return {
                'valid': False, 
                'error': f'Gmail validation error: {str(e)}'
            }

    def _validate_google_drive(self, credentials):
        """
        Validate Google Drive credentials
        """
        try:
            if not credentials.get('apiKey') or not credentials.get('clientId'):
                return {
                    'valid': False, 
                    'error': 'Missing Google Drive API Key or Client ID'
                }

            # Basic format validation
            if not re.match(r'^[A-Za-z0-9_-]+$', credentials['clientId']):
                return {
                    'valid': False, 
                    'error': 'Invalid Google Client ID format'
                }

            return {'valid': True}
        except Exception as e:
            return {
                'valid': False, 
                'error': f'Google Drive validation error: {str(e)}'
            }

# Create a singleton instance
credential_validator = CredentialValidator()
