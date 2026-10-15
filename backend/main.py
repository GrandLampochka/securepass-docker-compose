import os
import json

import httpx
import psycopg

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="SecurePass Backend")

DATABASE_URL = os.getenv("DATABASE_URL")
CRYPTO_SERVICE_URL = os.getenv(
    "CRYPTO_SERVICE_URL",
    "http://web-service:8001"
)


class PasswordRequest(BaseModel):
    length: int = Field(default=16, ge=8, le=128)
    uppercase: bool = True
    lowercase: bool = True
    digits: bool = True
    symbols: bool = True


class HashRequest(BaseModel):
    text: str
    algorithm: str = "sha256"


class VerifyRequest(BaseModel):
    text: str
    hashed: str


def save_audit(operation, algorithm, status="success", details=None):
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO audit_logs
                (operation, algorithm, status, details)
                VALUES (%s, %s, %s, %s)
                """,
                (
                    operation,
                    algorithm,
                    status,
                    json.dumps(details or {})
                )
            )


async def call_crypto(endpoint, payload):
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{CRYPTO_SERVICE_URL}{endpoint}",
                json=payload
            )

        return JSONResponse(
            status_code=response.status_code,
            content=response.json()
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=503,
            detail="Crypto service unavailable"
        )


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "backend"}


@app.post("/api/password/generate")
async def generate_password(request: PasswordRequest):
    response = await call_crypto(
        "/generate-password",
        request.model_dump()
    )

    save_audit(
        "PASSWORD_GENERATION",
        "CSPRNG",
        "success" if response.status_code == 200 else "failed",
        {"length": request.length}
    )

    return response


@app.post("/api/hash/generate")
async def generate_hash(request: HashRequest):
    response = await call_crypto(
        "/hash",
        request.model_dump()
    )

    save_audit(
        "HASH_GENERATION",
        request.algorithm,
        "success" if response.status_code == 200 else "failed"
    )

    return response


@app.post("/api/hash/verify")
async def verify_hash(request: VerifyRequest):
    response = await call_crypto(
        "/verify",
        request.model_dump()
    )

    save_audit(
        "HASH_VERIFICATION",
        "bcrypt",
        "success" if response.status_code == 200 else "failed"
    )

    return response


@app.get("/api/audit")
def get_audit():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, operation, algorithm,
                       status, details, created_at
                FROM audit_logs
                ORDER BY created_at DESC, id DESC
                LIMIT 100
                """
            )

            rows = cur.fetchall()

    return [
        {
            "id": row[0],
            "operation": row[1],
            "algorithm": row[2],
            "status": row[3],
            "details": row[4],
            "created_at": row[5].isoformat()
        }
        for row in rows
    ]


@app.delete("/api/audit")
def clear_audit():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM audit_logs")

    return {"message": "Audit log cleared"}
