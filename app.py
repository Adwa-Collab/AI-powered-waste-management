import base64
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import jwt
from datetime import datetime, timedelta

# JWT configuration
JWT_SECRET_KEY = 'your_jwt_secret_key'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_MINUTES = 30

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://babi:password@localhost/wastewise'
db = SQLAlchemy(app)

# Claude 3 Opus API configuration
OPUS_API_URL = 'https://api.anthropic.com/v1/opus'
OPUS_API_KEY = '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'

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class WasteEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

# User Registration and Authentication
@app.route('/api/users/register', methods=['POST'])
def register_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password are required'}), 400

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400

    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/users/login', methods=['POST'])
def login_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or user.password != password:
        return jsonify({'error': 'Invalid username or password'}), 401

    # Generate and return access token
    access_token = generate_access_token(user.id)
    return jsonify({'access_token': access_token, "username": username}), 200

# Waste Classification
@app.route('/api/waste/classify', methods=['POST'])
def classify_waste():
    image = request.files['image']

    # Read the image file and convert it to base64
    image_data = image.read()
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    # Prepare the prompt for the Opus API
    prompt = f"Classify the waste image into one of the following categories: recyclable, compostable, general waste.\n\nImage: {image_base64}"

    # Send the prompt to the Opus API for classification
    headers = {'Authorization': f'Bearer {OPUS_API_KEY}'}
    data = {'prompt': prompt, 'max_tokens': 10}
    response = requests.post(OPUS_API_URL + '/completions', headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        waste_category = result['choices'][0]['text'].strip().lower()
        
        # Validate the classified waste category
        valid_categories = ['recyclable', 'compostable', 'general waste']
        if waste_category not in valid_categories:
            return jsonify({'error': 'Invalid waste category'}), 400
        
        return jsonify({'category': waste_category}), 200
    else:
        return jsonify({'error': 'Failed to classify waste'}), 500

# User Waste History
@app.route('/api/waste/history', methods=['POST'])
def record_waste_entry():
    data = request.json
    user_id = data.get('user_id')
    category = data.get('category')
    timestamp = data.get('timestamp')

    new_entry = WasteEntry(user_id=user_id, category=category, timestamp=timestamp)
    db.session.add(new_entry)
    db.session.commit()

    return jsonify({'message': 'Waste entry recorded successfully'}), 201

@app.route('/api/waste/history', methods=['GET'])
def get_waste_history():
    user_id = request.args.get('user_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')

    query = WasteEntry.query.filter_by(user_id=user_id)

    if start_date and end_date:
        query = query.filter(WasteEntry.timestamp.between(start_date, end_date))
    if category:
        query = query.filter_by(category=category)

    waste_entries = query.all()
    history = []
    for entry in waste_entries:
        history.append({
            'id': entry.id,
            'category': entry.category,
            'timestamp': entry.timestamp.isoformat()
        })

    return jsonify({'history': history}), 200

# Eco-Friendly Product Alternatives
@app.route('/api/products/alternatives', methods=['GET'])
def get_product_alternatives():
    product = request.args.get('product')

    # Query the database or an external API for eco-friendly alternatives
    alternatives = find_eco_friendly_alternatives(product)

    return jsonify({'alternatives': alternatives}), 200

# Food Waste Reduction Tips
@app.route('/api/tips/food-waste', methods=['GET'])
def get_food_waste_tips():
    # Retrieve food waste reduction tips from the database or an external source
    tips = get_food_waste_reduction_tips()

    return jsonify({'tips': tips}), 200

# Helper functions
def generate_access_token(user_id):
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

def find_eco_friendly_alternatives(product):
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

# # Automatically create database tables
# with app.app_context():
#     db.create_all()

if __name__ == '__main__':
    app.run()