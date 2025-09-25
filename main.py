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
from groq import Groq
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

# Get Groq API key from environment
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Global models for fallback system
gemini_model = None
groq_client = None
current_provider = "gemini"  # Track which provider is currently active
gemini_quota_exceeded = False  # Track if Gemini quota is exceeded

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
    """Initialize AI APIs with fallback system"""
    global gemini_model, groq_client, current_provider, gemini_quota_exceeded
    
    print("Initializing AI APIs with fallback system...")
    print("=" * 60)
    
    # Initialize Gemini API
    print("🤖 Initializing Gemini API...")
    try:
        if not GEMINI_API_KEY:
            print("❌ GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY is required")
        
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel(GEMINI_MODEL)
        
        # Test Gemini connection
        try:
            test_response = gemini_model.generate_content("Hello, this is a test.")
            print(f"✅ Gemini API initialized successfully")
            print(f"Model: {GEMINI_MODEL}")
            print(f"Test response: {test_response.text[:50]}...")
        except Exception as test_error:
            if "quota" in str(test_error).lower() or "429" in str(test_error):
                print(f"⚠️ Gemini API initialized but quota exceeded")
                print(f"Model: {GEMINI_MODEL}")
                gemini_quota_exceeded = True
            else:
                print(f"⚠️ Gemini API initialized but test failed: {test_error}")
                print(f"Model: {GEMINI_MODEL}")
        
    except Exception as e:
        print(f"❌ Error initializing Gemini API: {e}")
        if "quota" in str(e).lower() or "429" in str(e):
            print("⚠️ Quota exceeded - will use fallback when available")
            gemini_quota_exceeded = True
        else:
            print("❌ Gemini API failed to initialize")
            gemini_model = None
    
    # Initialize Groq API (fallback)
    print("\n🚀 Initializing Groq API (fallback)...")
    try:
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            print("⚠️ GROQ_API_KEY not set - fallback will not be available")
            print("Set GROQ_API_KEY in .env file to enable fallback")
        else:
            groq_client = Groq(api_key=GROQ_API_KEY)
            
            # Test Groq connection
            try:
                test_response = groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": "Hello, this is a test."}],
                    model="llama-3.1-8b-instant",
                    max_tokens=10
                )
                print(f"✅ Groq API initialized successfully")
                print(f"Model: llama-3.1-8b-instant")
                print(f"Test response: {test_response.choices[0].message.content[:50]}...")
            except Exception as test_error:
                print(f"⚠️ Groq API initialized but test failed: {test_error}")
                print("Fallback will be attempted but may not work")
        
    except Exception as e:
        print(f"❌ Error initializing Groq API: {e}")
        groq_client = None
    
    # Determine active provider
    if gemini_model and not gemini_quota_exceeded:
        current_provider = "gemini"
        print(f"\n🎯 Active provider: Gemini ({GEMINI_MODEL})")
    elif groq_client:
        current_provider = "groq"
        print(f"\n🎯 Active provider: Groq (llama-3.1-8b-instant)")
    else:
        current_provider = "none"
        print(f"\n❌ No AI providers available!")
    
    print("=" * 60)
    
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

def analyze_text_with_groq(text: str) -> Dict[str, Any]:
    """Analyze text for bias using Groq API (fallback)"""
    if not groq_client:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Groq API not available"
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
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            max_tokens=2000,
            temperature=0.1
        )
        
        # Parse the JSON response
        response_text = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
            return analysis
        else:
            # Fallback if JSON parsing fails
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
        print(f"Groq API error: {e}")
        error_str = str(e)
        if "quota" in error_str.lower() or "429" in error_str:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Groq API quota exceeded. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing text with Groq: {error_str}"
            )

def analyze_text_with_fallback(text: str) -> Dict[str, Any]:
    """Analyze text with automatic fallback between Gemini and Groq"""
    global current_provider, gemini_quota_exceeded
    
    # Try Gemini first if available and quota not exceeded
    if current_provider == "gemini" and gemini_model and not gemini_quota_exceeded:
        try:
            return analyze_text_with_gemini(text)
        except Exception as e:
            error_str = str(e)
            if "quota" in error_str.lower() or "429" in error_str:
                print("🔄 Gemini quota exceeded, switching to Groq fallback...")
                gemini_quota_exceeded = True
                current_provider = "groq"
                # Fall through to try Groq
            else:
                print(f"❌ Gemini error: {e}")
                # Fall through to try Groq
    
    # Try Groq if available
    if current_provider == "groq" and groq_client:
        try:
            return analyze_text_with_groq(text)
        except Exception as e:
            print(f"❌ Groq error: {e}")
            # If Groq also fails, try to fall back to Gemini if quota reset
            if gemini_model and not gemini_quota_exceeded:
                print("🔄 Trying Gemini again...")
                current_provider = "gemini"
                try:
                    return analyze_text_with_gemini(text)
                except Exception as gemini_error:
                    print(f"❌ Gemini still failing: {gemini_error}")
    
    # If both fail, return error
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="All AI providers are currently unavailable. Please try again later."
    )

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
        error_str = str(e)
        if "quota" in error_str.lower() or "429" in error_str:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="API quota exceeded. Please try again later when your quota resets."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error analyzing text: {error_str}"
            )

@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(request: AnalyzeRequest, current_user: User = Depends(get_current_user)):
    """Analyze text for bias using AI with automatic fallback"""
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
            # Analyze each sentence with fallback system
            analysis = analyze_text_with_fallback(sentence)
            
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

@app.get("/status")
async def get_status():
    """Get current AI provider status"""
    global current_provider, gemini_quota_exceeded
    
    status_info = {
        "current_provider": current_provider,
        "gemini_available": gemini_model is not None,
        "gemini_quota_exceeded": gemini_quota_exceeded,
        "groq_available": groq_client is not None,
        "fallback_enabled": groq_client is not None
    }
    
    return status_info

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)