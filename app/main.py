from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.users.endpoints import router as auth_router
from app.modules.clients.endpoints import router as clients_router
from app.modules.proposals.endpoints import router as proposals_router
from app.modules.proposals.webhooks import router as webhook_router

app = FastAPI(
    title="Credit Management API",
    description="API para gerenciamento de propostas de crédito",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(clients_router, prefix="/api")
app.include_router(proposals_router, prefix="/api")
app.include_router(webhook_router, prefix="/api")



@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "credit-api",
        "version": "1.0.0"
    }

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "Welcome to Credit Management API. Go to /docs for documentation."}