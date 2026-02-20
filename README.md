# Ecommerce FastAPI Backend

A complete, production-ready ecommerce backend API built with FastAPI and MongoDB.

## Features

### Customer Features
- **Authentication**: User signup, login with JWT tokens
- **Profile Management**: Update user profile and shipping address
- **Product Browsing**: Search, filter by category, pagination, view product images
- **Shopping Cart**: Add/update/remove items, automatic total calculation
- **Order Management**: Place orders, view order history
- **Payment Processing**: Razorpay (Cards, UPI, Net Banking, Wallets), Cash on Delivery
- **Order Tracking**: Track order status with tracking numbers

### Admin Features
- **Product Management**: CRUD operations with **multiple image uploads**
- **Image Management**: Upload, add, remove product images with automatic optimization
- **Order Management**: View all orders, update order status, add tracking
- **Payment Oversight**: View all payments and transactions
- **Analytics Dashboard**: Revenue analytics, order statistics, top products
- **Customer Management**: View all registered customers

### Image Features
- ✅ Multiple images per product
- ✅ Real-time image serving via static URLs
- ✅ Automatic image optimization (resize to 1200x1200, 85% quality)
- ✅ Support for JPG, PNG, WebP, GIF
- ✅ 5MB file size limit
- ✅ Add/remove images from existing products
- ✅ Secure unique filenames (UUID-based)

## Tech Stack

- **FastAPI**: Modern, fast web framework
- **MongoDB**: NoSQL database with Motor (async driver)
- **Pydantic**: Data validation and settings management
- **JWT**: Secure authentication
- **Bcrypt**: Password hashing
- **Razorpay**: Payment processing (Cards, UPI, Net Banking, Wallets)
- **Pillow**: Image processing and optimization
- **Aiofiles**: Async file operations

## Project Structure

```
ecommerce-api/
├── app/
│   ├── core/
│   │   ├── config.py          # Configuration settings
│   │   ├── database.py        # MongoDB connection
│   │   ├── security.py        # JWT and password utilities
│   │   └── dependencies.py    # Auth dependencies
│   ├── schemas/
│   │   ├── user.py           # User schemas
│   │   ├── product.py        # Product schemas
│   │   ├── cart.py           # Cart schemas
│   │   ├── order.py          # Order schemas
│   │   └── payment.py        # Payment schemas
│   ├── routers/
│   │   ├── auth.py           # Authentication endpoints
│   │   ├── products.py       # Product endpoints
│   │   ├── cart.py           # Cart endpoints
│   │   ├── orders.py         # Order endpoints
│   │   ├── payments.py       # Payment endpoints
│   │   └── admin.py          # Admin endpoints
│   └── main.py               # Application entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.9 or higher
- MongoDB 4.4 or higher (running locally or MongoDB Atlas)
- pip (Python package manager)

### Step 1: Clone or Download the Project

```bash
cd ecommerce-api
```

### Step 2: Create Virtual Environment

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Motor (async MongoDB driver)
- Pydantic (data validation)
- Python-Jose (JWT tokens)
- Passlib (password hashing)
- Pillow (image processing)
- Aiofiles (async file operations)
- And other dependencies

### Step 4: Install and Start MongoDB

#### Option A: Local MongoDB (Recommended for Development)

**Windows:**
1. Download MongoDB Community Server from https://www.mongodb.com/try/download/community
2. Install with default settings
3. MongoDB will start automatically as a service
4. Default connection: `mongodb://localhost:27017`

**macOS (using Homebrew):**
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install -y mongodb
sudo systemctl start mongodb
sudo systemctl enable mongodb
```

#### Option B: MongoDB Atlas (Cloud)

1. Create free account at https://www.mongodb.com/cloud/atlas
2. Create a cluster
3. Get connection string (looks like: `mongodb+srv://username:password@cluster.mongodb.net/`)
4. Whitelist your IP address

### Step 5: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
```

**Required Configuration (.env file):**

```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
# For MongoDB Atlas use: mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=ecommerce_db

# JWT Configuration (Change SECRET_KEY to a random string)
SECRET_KEY=your-super-secret-key-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Razorpay Configuration (Get from https://dashboard.razorpay.com)
RAZORPAY_KEY_ID=rzp_test_your_key_id
RAZORPAY_KEY_SECRET=your_razorpay_secret_key
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret

# Application Configuration
APP_NAME=Ecommerce API
DEBUG=True
```

**Generate a secure SECRET_KEY:**
```bash
# On macOS/Linux
openssl rand -hex 32

# On Windows (using Python)
python -c "import secrets; print(secrets.token_hex(32))"
```

### Step 6: Run the Application

```bash
# Make sure you're in the ecommerce-api directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs (Swagger)**: http://localhost:8000/docs
- **Alternative Docs (ReDoc)**: http://localhost:8000/redoc

### Step 7: Create Admin User (Optional)

Use the signup endpoint to create a user, then manually update their role to admin:

**Using MongoDB Compass or Mongo Shell:**
```javascript
db.users.updateOne(
  { email: "admin@example.com" },
  { $set: { role: "admin" } }
)
```

**Or using Python:**
```python
from pymongo import MongoClient
client = MongoClient("mongodb://localhost:27017")
db = client["ecommerce_db"]
db.users.update_one(
    {"email": "admin@example.com"},
    {"$set": {"role": "admin"}}
)
```

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get token
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update profile

### Products
- `GET /api/products/` - List all products (with pagination, search, filter)
- `GET /api/products/{id}` - Get product details with images
- `POST /api/products/` - Create product with images (Admin, multipart/form-data)
- `PUT /api/products/{id}` - Update product with images (Admin, multipart/form-data)
- `DELETE /api/products/{id}` - Delete product (Admin)
- `POST /api/products/{id}/images` - Add more images to product (Admin)
- `DELETE /api/products/{id}/images` - Remove specific image (Admin)

**📸 For detailed image upload examples, see [IMAGE_UPLOAD_GUIDE.md](IMAGE_UPLOAD_GUIDE.md)**

### Cart
- `GET /api/cart/` - Get user's cart
- `POST /api/cart/items` - Add item to cart
- `PUT /api/cart/items` - Update item quantity
- `DELETE /api/cart/items/{product_id}` - Remove item
- `DELETE /api/cart/` - Clear cart

### Orders
- `POST /api/orders/` - Create order from cart
- `GET /api/orders/` - Get user's orders
- `GET /api/orders/{id}` - Get order details
- `GET /api/orders/tracking/{order_number}` - Track order (public)
- `GET /api/orders/admin/all` - Get all orders (Admin)
- `PUT /api/orders/{id}` - Update order status (Admin)

### Payments
- `POST /api/payments/razorpay/create-order` - Create Razorpay order
- `POST /api/payments/razorpay/verify` - Verify Razorpay payment
- `POST /api/payments/cash-on-delivery` - Create COD payment
- `GET /api/payments/` - Get user's payments
- `GET /api/payments/{id}` - Get payment details
- `GET /api/payments/order/{order_id}` - Get payments for order
- `GET /api/payments/admin/all` - Get all payments (Admin)
- `POST /api/payments/admin/refund/{payment_id}` - Refund payment (Admin)

**💳 For detailed Razorpay integration, see [RAZORPAY_INTEGRATION.md](RAZORPAY_INTEGRATION.md)**

### Admin Dashboard
- `GET /api/admin/dashboard` - Dashboard statistics
- `GET /api/admin/analytics/revenue?days=30` - Revenue analytics
- `GET /api/admin/analytics/orders?days=30` - Order analytics

## Testing the API

### Using Swagger UI (Recommended)

1. Open http://localhost:8000/docs
2. Create a user via `POST /api/auth/signup`
3. Login via `POST /api/auth/login` - copy the access token
4. Click "Authorize" button (top right)
5. Enter: `Bearer <your-access-token>`
6. Now you can test all authenticated endpoints!

### Using cURL

**Create Account:**
```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "securepass123",
    "full_name": "John Doe",
    "phone": "+1234567890"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=customer@example.com&password=securepass123"
```

**Get Products:**
```bash
curl -X GET "http://localhost:8000/api/products/?limit=10"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Signup
response = requests.post(f"{BASE_URL}/api/auth/signup", json={
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
})
print(response.json())

# Login
response = requests.post(f"{BASE_URL}/api/auth/login", data={
    "username": "test@example.com",
    "password": "password123"
})
token = response.json()["access_token"]

# Get profile
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
print(response.json())
```

## Common Issues & Troubleshooting

### MongoDB Connection Issues

**Error: "Connection refused"**
- Ensure MongoDB is running: `sudo systemctl status mongodb` (Linux)
- Check MongoDB logs: `tail -f /var/log/mongodb/mongod.log`
- Verify MONGODB_URL in .env is correct

**Error: "Authentication failed"**
- If using MongoDB Atlas, check username/password
- Whitelist your IP in Atlas dashboard

### Import Errors

**Error: "No module named 'app'"**
```bash
# Make sure you're running from the ecommerce-api directory
cd ecommerce-api
uvicorn app.main:app --reload
```

### Port Already in Use

**Error: "Address already in use"**
```bash
# Use a different port
uvicorn app.main:app --reload --port 8001

# Or kill the process using port 8000 (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Production Deployment

### Security Checklist

1. ✅ Change `SECRET_KEY` to a strong random value
2. ✅ Set `DEBUG=False` in production
3. ✅ Use environment variables for sensitive data
4. ✅ Configure CORS properly (don't use `allow_origins=["*"]`)
5. ✅ Use HTTPS
6. ✅ Set up MongoDB authentication
7. ✅ Enable MongoDB replica sets for production
8. ✅ Implement rate limiting
9. ✅ Set up logging and monitoring
10. ✅ Use a reverse proxy (nginx)

### Deployment Options

**Option 1: Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Option 2: Cloud Platforms**
- **Railway**: Easy deployment with MongoDB addon
- **Render**: Free tier available
- **AWS**: EC2 + MongoDB Atlas
- **Google Cloud**: Cloud Run + MongoDB Atlas
- **Heroku**: Heroku + MongoDB Atlas

## API Documentation

Full interactive API documentation is available at `/docs` when the server is running.

## Support

For issues, questions, or contributions, please refer to the FastAPI and MongoDB documentation:
- FastAPI: https://fastapi.tiangolo.com
- MongoDB: https://docs.mongodb.com
- Motor (Async MongoDB): https://motor.readthedocs.io

## License

MIT License
