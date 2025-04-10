import os
import magic
# from sentence_transformers import SentenceTransformer # Removed local model
from .openai_service import get_embedding # Import OpenAI embedding function
import PyPDF2
import docx
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class VectorizationService:
    # Removed __init__ as local model is no longer needed
    # def __init__(self):
    #     self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def detect_file_type(self, file_path):
        """
        Detect MIME type of the file
        """
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)

    def extract_content(self, file_path):
        """
        Extract text content from various file types
        """
        file_type = self.detect_file_type(file_path)
        
        try:
            if 'pdf' in file_type:
                return self._extract_pdf(file_path)
            elif 'word' in file_type or 'document' in file_type:
                return self._extract_docx(file_path)
            elif 'sheet' in file_type or 'excel' in file_type:
                return self._extract_excel(file_path)
            elif 'text' in file_type:
                with open(file_path, 'r') as f:
                    return f.read()
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            raise ValueError(f"Content extraction failed: {str(e)}") from e
        """
        Extract text from PDF files
        """
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ''
            for page in reader.pages:
                text += page.extract_text() + '\n'
            return text

    def _extract_docx(self, file_path):
        """
        Extract text from Word documents
        """
        doc = docx.Document(file_path)
        return '\n'.join([paragraph.text for paragraph in doc.paragraphs])

    def _extract_excel(self, file_path):
        """
        Extract text from Excel files
        """
        # Convert all data to string before joining
        return df.to_string(index=False)

    # Keep the original method name, ensure it's async
    async def vectorize(self, content: str):
        """
        Generate vector embedding for text content using OpenAI.
        """
        # Note: OpenAI models might have their own token limits.
        # Consider chunking strategies for very long content if needed.
        # The get_embedding function might need adjustments for handling limits.
        logger.info(f"Requesting OpenAI embedding for content snippet (length {len(content)})...")
        embedding = await get_embedding(content) # Use await for the async function
        if embedding:
            logger.info("Successfully received embedding from OpenAI.")
            return embedding
        else:
            logger.error("Failed to get embedding from OpenAI.")
            raise ValueError("Failed to generate embedding using OpenAI service.")
