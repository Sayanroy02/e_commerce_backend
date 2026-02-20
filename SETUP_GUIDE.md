# Step-by-Step Setup Guide

This guide will walk you through setting up the Ecommerce API from scratch.

## Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.9+ installed (`python --version`)
- [ ] pip installed (`pip --version`)
- [ ] MongoDB installed or MongoDB Atlas account
- [ ] A code editor (VS Code, PyCharm, etc.)
- [ ] Terminal/Command Prompt access

## Step 1: Install Python (if not installed)

### Windows
1. Download Python from https://www.python.org/downloads/
2. Run installer
3. ✅ **IMPORTANT**: Check "Add Python to PATH"
4. Verify: Open CMD and type `python --version`

### macOS
```bash
# Using Homebrew
brew install python3

# Verify
python3 --version
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify
python3 --version
```

## Step 2: Install MongoDB

### Option A: Local MongoDB (Recommended for Learning)

**Windows:**
1. Download MongoDB Community Server: https://www.mongodb.com/try/download/community
2. Run installer (use default settings)
3. MongoDB runs automatically as a Windows service
4. Verify: Open MongoDB Compass (included) or run `mongosh` in terminal

**macOS:**
```bash
# Install using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Verify
mongosh
```

**Linux (Ubuntu):**
```bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-7.0.asc | sudo apt-key add -

# Add MongoDB repository
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/7.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-7.0.list

# Install MongoDB
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# Verify
mongosh
```

### Option B: MongoDB Atlas (Cloud - Free Tier)

1. Go to https://www.mongodb.com/cloud/atlas
2. Create free account
3. Create a free cluster (M0)
4. Create database user (username + password)
5. Whitelist IP: Click "Network Access" → "Add IP Address" → "Allow Access from Anywhere" (0.0.0.0/0)
6. Get connection string: Click "Connect" → "Connect your application"
7. Connection string looks like: `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/`

## Step 3: Set Up Project

### 3.1 Navigate to Project Directory
```bash
cd /path/to/ecommerce-api
# Example: cd ~/Downloads/ecommerce-api
```

### 3.2 Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# You should see (venv) in your terminal prompt
```

### 3.3 Install Dependencies
```bash
pip install -r requirements.txt

# This will install:
# - FastAPI
# - Uvicorn
# - Motor (MongoDB async driver)
# - Pydantic
# - Python-Jose (JWT)
# - Passlib (password hashing)
# - And other dependencies
```

## Step 4: Configure Environment

### 4.1 Create .env file
```bash
# Copy the example file
cp .env.example .env

# Windows (if cp doesn't work)
copy .env.example .env
```

### 4.2 Edit .env file

Open `.env` in your code editor and update:

**For Local MongoDB:**
```env
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=ecommerce_db
SECRET_KEY=generate-a-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**For MongoDB Atlas:**
```env
MONGODB_URL=mongodb+srv://your-username:your-password@cluster0.xxxxx.mongodb.net/
DATABASE_NAME=ecommerce_db
SECRET_KEY=generate-a-random-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4.3 Generate SECRET_KEY

Run one of these commands:

```bash
# Using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Using OpenSSL (macOS/Linux)
openssl rand -hex 32

# Manual: Visit https://randomkeygen.com/ and copy a 256-bit key
```

Paste the generated key as your `SECRET_KEY` value in `.env`

## Step 5: Start the Application

### 5.1 Run the Server
```bash
# Make sure you're in the ecommerce-api directory
# and virtual environment is activated (you see (venv) in prompt)

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
Creating database indexes...
Application started successfully!
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 5.2 Verify Installation

Open your browser and visit:
- http://localhost:8000 - Should show welcome message
- http://localhost:8000/docs - Interactive API documentation (Swagger UI)
- http://localhost:8000/health - Health check endpoint

## Step 6: Test the API

### Option 1: Using Swagger UI (Easiest)

1. Open http://localhost:8000/docs
2. Find `POST /api/auth/signup`
3. Click "Try it out"
4. Enter test data:
```json
{
  "email": "test@example.com",
  "password": "password123",
  "full_name": "Test User",
  "phone": "+1234567890"
}
```
5. Click "Execute"
6. You should get a 201 response with user data!

### Option 2: Using Python Script

In a new terminal (keep server running):
```bash
# Activate virtual environment first
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows

# Run test script
python test_api.py
```

### Option 3: Using cURL

```bash
# Create user
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# Login
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=password123"
```

## Step 7: Create Admin User

### 7.1 Create User via API
Use any method from Step 6 to create a user with email like `admin@example.com`

### 7.2 Set Admin Role in Database

**Using MongoDB Compass (GUI):**
1. Open MongoDB Compass
2. Connect to `mongodb://localhost:27017`
3. Navigate to `ecommerce_db` → `users` collection
4. Find the user with `admin@example.com`
5. Edit document and change `"role": "customer"` to `"role": "admin"`
6. Save

**Using MongoDB Shell:**
```bash
# Connect to MongoDB
mongosh

# Use the database
use ecommerce_db

# Update user role
db.users.updateOne(
  { email: "admin@example.com" },
  { $set: { role: "admin" } }
)

# Verify
db.users.findOne({ email: "admin@example.com" })
```

### 7.3 Test Admin Access

1. Login as admin in Swagger UI
2. Copy the access token
3. Click "Authorize" button
4. Enter: `Bearer <your-token>`
5. Try admin endpoints like `POST /api/products/`

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'fastapi'"
**Solution:** Virtual environment not activated or dependencies not installed
```bash
source venv/bin/activate  # Activate venv
pip install -r requirements.txt  # Install dependencies
```

### Issue: "Connection refused" when connecting to MongoDB
**Solution:** MongoDB not running
```bash
# Windows: Check Services → MongoDB Server should be running
# macOS: brew services start mongodb-community
# Linux: sudo systemctl start mongod
```

### Issue: Port 8000 already in use
**Solution:** Use different port or kill existing process
```bash
# Use different port
uvicorn app.main:app --reload --port 8001

# Or find and kill process
# Linux/macOS
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: "Could not validate credentials"
**Solution:** Token expired or invalid
- Login again to get new token
- Make sure you're using `Bearer <token>` format in Authorization header

### Issue: MongoDB Atlas connection timeout
**Solution:**
- Check IP whitelist in Atlas (add 0.0.0.0/0 for testing)
- Verify username/password in connection string
- Ensure network allows outbound connections

## Next Steps

1. ✅ API is running successfully
2. 📚 Explore the API documentation at http://localhost:8000/docs
3. 🧪 Test all endpoints using Swagger UI
4. 🛠️ Create products as admin
5. 🛒 Test shopping flow as customer
6. 📊 Check admin dashboard
7. 🚀 Deploy to production when ready

## Production Deployment Checklist

Before deploying to production:

- [ ] Change SECRET_KEY to a strong random value
- [ ] Set DEBUG=False
- [ ] Use environment variables for all sensitive data
- [ ] Configure CORS properly (don't use allow_origins=["*"])
- [ ] Set up HTTPS/SSL
- [ ] Use MongoDB authentication
- [ ] Enable MongoDB replica sets
- [ ] Implement rate limiting
- [ ] Set up logging and monitoring
- [ ] Use a reverse proxy (nginx)
- [ ] Set up automated backups
- [ ] Implement proper error handling
- [ ] Add API versioning
- [ ] Set up CI/CD pipeline

## Getting Help

- 📖 FastAPI Docs: https://fastapi.tiangolo.com
- 📖 MongoDB Docs: https://docs.mongodb.com
- 📖 Motor Docs: https://motor.readthedocs.io
- 💬 FastAPI Discord: https://discord.gg/fastapi

## Congratulations! 🎉

You've successfully set up a complete ecommerce backend API with:
- User authentication (signup/login)
- Product management
- Shopping cart
- Order processing
- Payment handling
- Admin dashboard
- Order tracking

Happy coding! 🚀
