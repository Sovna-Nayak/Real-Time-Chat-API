from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from chat_router import router as chat_router
from db import Base, engine



Base.metadata.create_all(bind=engine)

app = FastAPI(title="Real-Time Chat API")
# ⚡ Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # allow all origins for testing
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
