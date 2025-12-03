from fastapi import APIRouter, HTTPException
from app.utils.jwt_utils import create_jwt
from app.utils.hashing import verify_password
from app.auth.schemas import LoginRequest

router = APIRouter()

fake_users = {
    "rohit@example.com": {
        "password": "$2b$12$zc81wPrtMlbMslePGUzc4.H278WzKNs1jPjpRBghxkNq8xCnkKe7m"
    }
}

@router.post("/login")
def login(data: LoginRequest):
    email = data.email
    password = data.password
    
    if email not in fake_users:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(password, fake_users[email]["password"]):
        raise HTTPException(status_code=400, detail="Invalid password")

    token = create_jwt({"email": email})
    return {"token": token, "message": "Login successful"}
