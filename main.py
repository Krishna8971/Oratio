"""
Oratio Backend - AI Bias Detection API
Using Google Gemini API for comprehensive bias detection
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

# Load environment variables first
try:
    import environment
except ImportError:
    print("⚠️ environment.py not found, using system environment variables")

import google.generativeai as genai
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import secrets
from passlib.context import CryptContext

# Configuration
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, ALLOWED_ORIGINS, DATABASE_URL, GEMINI_API_KEY, GEMINI_MODEL

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Global Gemini model
gemini_model = None

# Database Models
class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: str

class AnalyzeRequest(BaseModel):
    text: str

class BiasedSpan(BaseModel):
    text: str
    start: int
    end: int
    type: str

class SentenceAnalysis(BaseModel):
    sentence: str
    biased_spans: List[BiasedSpan]
    suggestion: str

class AnalyzeResponse(BaseModel):
    original_text: str
    summary: Dict[str, Any]
    sentences: List[SentenceAnalysis]

def init_database():
    """Initialize MySQL database with users table"""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Error creating database tables: {e}")
        raise

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = secrets.token_urlsafe(32)  # Simple token for demo
    return encoded_jwt

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email from database"""
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user:
        return User(id=user.id, email=user.email)
    return None

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate user with email and password"""
    user = db.query(UserModel).filter(UserModel.email == email).first()
    if user and verify_password(password, user.hashed_password):
        return User(id=user.id, email=user.email)
    return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), 
                    db: Session = Depends(get_db)) -> User:
    """Get current authenticated user"""
    # Simple token validation for demo - in production use proper JWT
    if not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # For demo purposes, we'll just return a mock user
    # In production, decode JWT and get user from database
    return User(id=1, email="demo@example.com")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Gemini API on startup"""
    global gemini_model
    
    print("Initializing Gemini API...")
    print("=" * 50)
    
    try:
        if not GEMINI_API_KEY:
            print("❌ GEMINI_API_KEY not found in environment variables")
            print("Please set GEMINI_API_KEY environment variable")
            raise ValueError("GEMINI_API_KEY is required")
        
        # Configure Gemini API
        genai.configure(api_key=GEMINI_API_KEY)
        
        # Initialize the model
        gemini_model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Test the connection
        test_response = gemini_model.generate_content("Hello, this is a test.")
        print(f"✅ Gemini API initialized successfully")
        print(f"Model: {GEMINI_MODEL}")
        print(f"Test response: {test_response.text[:50]}...")
        
    except Exception as e:
        print(f"❌ Error initializing Gemini API: {e}")
        print("\nPlease make sure:")
        print("1. GEMINI_API_KEY is set correctly")
        print("2. You have access to Google AI Studio")
        print("3. Your API key has the necessary permissions")
        gemini_model = None
    
    print("=" * 50)
    
    yield
    
    # Cleanup on shutdown
    print("Shutting down...")

app = FastAPI(
    title="Oratio Bias Detection API",
    description="AI-powered text bias detection using Google Gemini API",
    version="2.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_database()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/auth/signup", response_model=Dict[str, str])
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    """User registration"""
    # Check if user already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    db_user = UserModel(
        email=user_data.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Generate access token
    access_token = create_access_token({"sub": user_data.email})
    return {"access_token": access_token}

@app.post("/auth/login", response_model=Dict[str, str])
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """User authentication"""
    user = authenticate_user(db, user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token({"sub": user.email})
    return {"access_token": access_token}

@app.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

def analyze_text_with_gemini(text: str) -> Dict[str, Any]:
    """Analyze text for bias using Gemini API"""
    if not gemini_model:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Gemini API not available"
        )
    
    # Create a comprehensive prompt for bias detection
    prompt = f"""
    Analyze the following text for bias and provide a detailed analysis in JSON format.

    Text to analyze: "{text}"

    Please provide your analysis in the following JSON format:
    {{
        "biased_count": <number of biased elements found>,
        "score": <overall bias score from 0.0 to 1.0>,
        "sentences": [
            {{
                "sentence": "<the sentence>",
                "biased_spans": [
                    {{
                        "text": "<biased text>",
                        "start": <start position>,
                        "end": <end position>,
                        "type": "<bias type: gender_bias, racial_bias, ageist, ableist, religious_bias, etc.>"
                    }}
                ],
                "suggestion": "<neutral alternative>"
            }}
        ]
    }}

    Guidelines for bias detection:
    1. Look for gender bias (stereotypes about men/women abilities)
    2. Look for racial/ethnic bias
    3. Look for ageist language (discrimination based on age)
    4. Look for ableist language (discrimination against disabilities)
    5. Look for religious bias
    6. Look for socioeconomic bias
    7. Look for toxic or offensive language
    8. Look for stereotyping or generalizations

    Provide neutral, inclusive alternatives for any biased language found.
    If no bias is found, set biased_count to 0 and score to 0.0.
    """
    
    try:
        response = gemini_model.generate_content(prompt)
        
        # Parse the JSON response
        response_text = response.text.strip()
        
        # Remove any markdown formatting if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        # Parse JSON
        analysis = json.loads(response_text)
        
        return analysis
        
    except json.JSONDecodeError as e:
        print(f"JSON parsing error: {e}")
        print(f"Raw response: {response.text}")
        # Fallback to simple analysis
        return {
            "biased_count": 0,
            "score": 0.0,
            "sentences": [{
                "sentence": text,
                "biased_spans": [],
                "suggestion": text
            }]
        }
    except Exception as e:
        print(f"Gemini API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error analyzing text: {str(e)}"
        )

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest, current_user: User = Depends(get_current_user)):
    """Analyze text for bias using Gemini API"""
    text = request.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        raise HTTPException(status_code=400, detail="No valid sentences found")
    
    sentence_analyses = []
    total_biased_count = 0
    
    for sentence in sentences:
        if not sentence:
            continue
        
        try:
            # Analyze each sentence with Gemini
            analysis = analyze_text_with_gemini(sentence)
            
            # Extract sentence analysis
            sentence_data = analysis.get("sentences", [{}])[0] if analysis.get("sentences") else {}
            
            biased_spans = sentence_data.get("biased_spans", [])
            suggestion = sentence_data.get("suggestion", sentence)
            
            # Convert to BiasedSpan objects
            biased_span_objects = [
                BiasedSpan(**span) for span in biased_spans
            ]
            
            sentence_analyses.append(SentenceAnalysis(
                sentence=sentence,
                biased_spans=biased_span_objects,
                suggestion=suggestion
            ))
            
            total_biased_count += len(biased_spans)
            
        except Exception as e:
            print(f"Error analyzing sentence '{sentence}': {e}")
            # Fallback: no bias detected
            sentence_analyses.append(SentenceAnalysis(
                sentence=sentence,
                biased_spans=[],
                suggestion=sentence
            ))
    
    # Calculate bias score
    bias_score = min(total_biased_count / len(sentences), 1.0) if sentences else 0.0
    
    return AnalyzeResponse(
        original_text=text,
        summary={
            "biased_count": total_biased_count,
            "score": round(bias_score, 2)
        },
        sentences=sentence_analyses
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)