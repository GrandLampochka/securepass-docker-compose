import secrets
import string
import hashlib
import bcrypt

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="SecurePass Crypto Service")


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


@app.get("/health")
def health():
    return {"status": "healthy", "service": "crypto"}


@app.post("/generate-password")
def generate_password(request: PasswordRequest):
    groups = []

    if request.uppercase:
        groups.append(string.ascii_uppercase)

    if request.lowercase:
        groups.append(string.ascii_lowercase)

    if request.digits:
        groups.append(string.digits)

    if request.symbols:
        groups.append("!@#$%^&*()-_=+")

    if not groups:
        raise HTTPException(
            status_code=400,
            detail="Select at least one character type"
        )

    password = [secrets.choice(group) for group in groups]
    characters = "".join(groups)

    password.extend(
        secrets.choice(characters)
        for _ in range(request.length - len(password))
    )

    secrets.SystemRandom().shuffle(password)

    return {
        "password": "".join(password),
        "length": request.length
    }


@app.post("/hash")
def generate_hash(request: HashRequest):
    if request.algorithm == "sha256":
        result = hashlib.sha256(
            request.text.encode("utf-8")
        ).hexdigest()

    elif request.algorithm == "bcrypt":
        if len(request.text.encode("utf-8")) > 72:
            raise HTTPException(
                status_code=400,
                detail="bcrypt input must not exceed 72 bytes"
            )

        result = bcrypt.hashpw(
            request.text.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

    else:
        raise HTTPException(
            status_code=400,
            detail="Unsupported algorithm"
        )

    return {
        "algorithm": request.algorithm,
        "hash": result
    }


@app.post("/verify")
def verify_hash(request: VerifyRequest):
    try:
        valid = bcrypt.checkpw(
            request.text.encode("utf-8"),
            request.hashed.encode("utf-8")
        )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Invalid bcrypt hash"
        )

    return {"valid": valid}
