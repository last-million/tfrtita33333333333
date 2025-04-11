import openai
from ..config import settings
import logging
import os

logger = logging.getLogger(__name__)

# Initialize OpenAI client
# It will automatically look for OPENAI_API_KEY environment variable
try:
    # Check if the key exists in settings first (loaded from .env)
    api_key = getattr(settings, 'openai_api_key', None)
    if not api_key:
        # Fallback to checking environment directly (common practice for openai lib)
        api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        logger.warning("OPENAI_API_KEY not found in settings or environment variables. OpenAI functionality will be disabled.")
        openai_client = None
    else:
        openai.api_key = api_key # Set globally for older versions or use client instance
        # For newer openai versions (>= 1.0):
        # openai_client = openai.OpenAI(api_key=api_key)
        # For simplicity assuming older version or global key setting for now
        openai_client = openai # Use the module itself if key is set globally
        logger.info("OpenAI client initialized.")

except Exception as e:
    logger.error(f"Failed to initialize OpenAI client: {e}")
    openai_client = None

async def get_embedding(text: str, model="text-embedding-ada-002"):
    """
    Generates an embedding for the given text using the specified OpenAI model.
    """
    if not openai_client:
        logger.error("OpenAI client not initialized. Cannot get embedding.")
        return None

    try:
        # Adjust API call based on openai library version
        # Older versions (< 1.0):
        response = await openai_client.Embedding.acreate(input=[text], model=model)
        embedding = response['data'][0]['embedding']

        # Newer versions (>= 1.0):
        # response = await openai_client.embeddings.create(input=[text], model=model)
        # embedding = response.data[0].embedding

        logger.debug(f"Successfully generated embedding for text snippet (length {len(text)}).")
        return embedding
    except Exception as e:
        logger.error(f"OpenAI API call failed: {e}", exc_info=True)
        return None
