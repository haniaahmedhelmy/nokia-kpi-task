from fastapi import FastAPI, HTTPException, Depends, Response, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import asyncpg, os, ssl
from dotenv import load_dotenv
from project_pipeline.email_service import send_email_report

# Load environment variables
load_dotenv()

# Config
DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")  # JWT secret
ALGORITHM = "HS256"
TOKEN_MIN = int(os.getenv("TOKEN_MINUTES", "1440"))  # Token expiry in minutes
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")

# Password hashing
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DB connection pool
pool: asyncpg.Pool | None = None

# --- Startup & Shutdown ---

async def auth_startup():
    """Initialize async DB pool with SSL."""
    global pool
    ssl_ctx = ssl.create_default_context()
    pool = await asyncpg.create_pool(DATABASE_URL, ssl=ssl_ctx)

async def auth_shutdown():
    """Close DB pool."""
    if pool:
        await pool.close()

# --- Models ---

class RegisterIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

class User(BaseModel):
    email: str

# --- Auth helpers ---

def create_token(sub: str):
    """Create JWT token with expiration."""
    exp = datetime.utcnow() + timedelta(minutes=TOKEN_MIN)
    return jwt.encode({"sub": sub, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)

async def get_user_by_id(user_id: int):
    """Fetch user by ID from DB."""
    row = await pool.fetchrow("SELECT id, email, created_at FROM users WHERE id=$1", user_id)
    return dict(row) if row else None

async def current_user(request: Request) -> UserOut:
    """Get logged-in user from cookie token."""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get("sub"))
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return UserOut(**user)

# --- Routes ---

@app.post("/register", status_code=201)
async def register(body: RegisterIn):
    """Register new user with hashed password."""
    hashed = pwd_ctx.hash(body.password)
    try:
        row = await pool.fetchrow(
            "INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id, email, created_at",
            body.email, hashed
        )
        return {"user": dict(row)}
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Email already registered")

@app.post("/login")
async def login(body: LoginIn, response: Response):
    """Login user, set JWT in cookie."""
    row = await pool.fetchrow("SELECT id, password_hash FROM users WHERE email=$1", body.email)
    if not row or not pwd_ctx.verify(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(str(row["id"]))
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,  # change to True in production with HTTPS
        max_age=TOKEN_MIN * 60,
        path="/",
    )
    return {"ok": True}

@app.post("/logout")
async def logout(response: Response):
    """Clear cookie to log out user."""
    response.delete_cookie("access_token", path="/")
    return {"ok": True}

@app.get("/me", response_model=UserOut)
async def me(user: UserOut = Depends(current_user)):
    """Get current logged-in user info."""
    return user

@app.post("/send-email")
def send_email():
    """Manually trigger email report send."""
    try:
        send_email_report()
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
