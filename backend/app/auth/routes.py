
from fastapi import APIRouter, HTTPException
from app.utils.jwt_utils import create_jwt
from app.utils.hashing import verify_password, hash_password
from app.auth.schemas import LoginRequest
from pydantic import BaseModel

router = APIRouter()

users = {
    "rohit@example.com": {
        "password": "$2b$12$zc81wPrtMlbMslePGUzc4.H278WzKNs1jPjpRBghxkNq8xCnkKe7m"
    }
}

class AuthRequest(BaseModel):
    email: str
    password: str
    action: str  # 'register' or 'login'


@router.post("/auth")
def auth(data: AuthRequest):
    email = data.email
    password = data.password
    action = data.action.lower()

    if action == "register":
        if email in users:
            raise HTTPException(status_code=400, detail="User already exists")
        users[email] = {"password": hash_password(password)}
        token = create_jwt({"email": email})
        return {"token": token, "message": "Registration successful"}

    elif action == "login":
        if email not in users:
            raise HTTPException(status_code=400, detail="User not found")
        if not verify_password(password, users[email]["password"]):
            raise HTTPException(status_code=400, detail="Invalid password")
        token = create_jwt({"email": email})
        return {"token": token, "message": "Login successful"}

    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'register' or 'login'.")
