import base64
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import requests
import jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from typing import List
import base64
import httpx
from fastapi import FastAPI, File, UploadFile, HTTPException
from anthropic import Anthropic

load_dotenv()

# JWT configuration
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM')
JWT_EXPIRATION_MINUTES = int(os.getenv('JWT_EXPIRATION_MINUTES'))

app = FastAPI()

# Database configuration
SQLALCHEMY_DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Claude 3 Opus API configuration
OPUS_API_URL = os.getenv('OPUS_API_URL')
OPUS_API_KEY = os.getenv('OPUS_API_KEY')
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')


# Database models
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

class WasteEntry(Base):
    __tablename__ = 'waste_entries'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    category = Column(String)
    timestamp = Column(DateTime)

    user = relationship('User')

# Pydantic models
class UserCreate(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class WasteEntryCreate(BaseModel):
    user_id: int
    category: str
    timestamp: datetime

class WasteEntryResponse(BaseModel):
    id: int
    category: str
    timestamp: datetime

    class Config:
        orm_mode = True

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

# User Registration and Authentication
@app.post('/api/users/register', status_code=201)
def register_user(user: UserCreate, db: SessionLocal = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail='Username already exists')
    new_user = User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'message': 'User registered successfully'}

@app.post('/api/users/login', response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or user.password != form_data.password:
        raise HTTPException(status_code=401, detail='Invalid username or password')
    access_token = generate_access_token(user.id)
    return {'access_token': access_token, 'token_type': 'bearer'}

# Waste Classification
@app.post('/api/waste/classify')
def classify_waste(image: UploadFile = File(...)):
    try:
        # Read the image file and convert
        image_data = base64.b64encode(image.file.read()).decode("utf-8")
        
        # Prepare the prompt for the Anthropic API
        prompt = "Classify the waste image into one of the following categories: recyclable, compostable, general waste."
        
        # Send the image and prompt to the Anthropic API
        client = Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": image.content_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "data": prompt,
                        },
                    ],
                }
            ],
        )
        
        # Extract the classified waste category from the API response
        waste_category = message["completion"].strip().lower()
        
        # Validate the classified waste category
        valid_categories = ['recyclable', 'compostable', 'general waste']
        if waste_category not in valid_categories:
            raise HTTPException(status_code=400, detail='Invalid waste category')
        
        return {'category': waste_category}
    except httpx.HTTPStatusError as e:
        print(f"Error: {e}")
        print(f"Response Content: {e.response.content}")
        raise HTTPException(status_code=500, detail='Failed to classify waste')
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail='An error occurred')
    
    
# User Waste History
@app.post('/api/waste/history', status_code=201)
def record_waste_entry(entry: WasteEntryCreate, db: SessionLocal = Depends(get_db)):
    new_entry = WasteEntry(**entry.dict())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return {'message': 'Waste entry recorded successfully'}

@app.get('/api/waste/history', response_model=List[WasteEntryResponse])
def get_waste_history(user_id: int, start_date: str = None, end_date: str = None, category: str = None, db: SessionLocal = Depends(get_db)):
    query = db.query(WasteEntry).filter(WasteEntry.user_id == user_id)
    if start_date and end_date:
        query = query.filter(WasteEntry.timestamp.between(start_date, end_date))
    if category:
        query = query.filter(WasteEntry.category == category)
    waste_entries = query.all()
    return waste_entries

# Eco-Friendly Product Alternatives
@app.get('/api/products/alternatives')
def get_product_alternatives(product: str):
    # Query the database or an external API for eco-friendly alternatives
    alternatives = find_eco_friendly_alternatives(product)
    return {'alternatives': alternatives}

# Food Waste Reduction Tips
@app.get('/api/tips/food-waste')
def get_food_waste_tips():
    # Retrieve food waste reduction tips from the database or an external source
    tips = get_food_waste_reduction_tips()
    return {'tips': tips}

# Helper functions
def generate_access_token(user_id: int):
    # Set the token expiration time
    expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
    # Create the token payload
    payload = {
        'user_id': user_id,
        'exp': expiration
    }
    # Generate the JWT access token
    access_token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return access_token

def find_eco_friendly_alternatives(product: str):
    # Prepare the prompt for the Opus API
    prompt = f"Find eco-friendly alternatives for {product}:"
    # Send the prompt to the Opus API for generating alternatives
    headers = {'Authorization': f'Bearer {OPUS_API_KEY}'}
    data = {'prompt': prompt, 'max_tokens': 100}
    response = requests.post(OPUS_API_URL + '/completions', headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        alternatives = result['choices'][0]['text'].strip().split('\n')
        return alternatives
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

def get_food_waste_reduction_tips():
    # Prepare the prompt for the Opus API
    prompt = "Provide tips for reducing food waste:"
    # Send the prompt to the Opus API for generating tips
    headers = {'Authorization': f'Bearer {OPUS_API_KEY}'}
    data = {'prompt': prompt, 'max_tokens': 200}
    response = requests.post(OPUS_API_URL + '/completions', headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        tips = result['choices'][0]['text'].strip().split('\n')
        return tips
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return []

# Create database tables
Base.metadata.create_all(bind=engine)