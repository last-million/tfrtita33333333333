from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import create_tables  # Import create_tables
# Import routes
from .routes import credentials

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(credentials.router, prefix="/api/credentials", tags=["Credentials"])

@app.on_event("startup")
async def startup_event():
    create_tables()  # Call create_tables on startup

@app.get("/")
async def root():
    return {"message": "Credential Validation Service"}
