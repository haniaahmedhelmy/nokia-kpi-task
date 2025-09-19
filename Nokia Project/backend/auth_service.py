from fastapi import FastAPI, HTTPException, Depends, Response, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
import asyncpg, os, ssl
from dotenv import load_dotenv
from project_pipeline.email_service import send_email_report

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")
ALGORITHM = "HS256"
TOKEN_MIN = int(os.getenv("TOKEN_MINUTES", "1440"))
CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pool: asyncpg.Pool | None = None


async def auth_startup():
    global pool
    ssl_ctx = ssl.create_default_context()
    pool = await asyncpg.create_pool(DATABASE_URL, ssl=ssl_ctx)

async def auth_shutdown():
    if pool:
        await pool.close()


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


def create_token(sub: str):
    exp = datetime.utcnow() + timedelta(minutes=TOKEN_MIN)
    return jwt.encode({"sub": sub, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)

async def get_user_by_id(user_id: int):
    row = await pool.fetchrow("SELECT id, email, created_at FROM users WHERE id=$1", user_id)
    return dict(row) if row else None

async def current_user(request: Request) -> UserOut:
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


@app.post("/register", status_code=201)
async def register(body: RegisterIn):
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
    row = await pool.fetchrow("SELECT id, password_hash FROM users WHERE email=$1", body.email)
    if not row or not pwd_ctx.verify(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(str(row["id"]))
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=TOKEN_MIN * 60,
        path="/",
    )
    return {"ok": True}

@app.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token", path="/")
    return {"ok": True}

@app.get("/me", response_model=UserOut)
async def me(user: UserOut = Depends(current_user)):
    return user

@app.post("/send-email")
def send_email():
    try:
        send_email_report()
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
