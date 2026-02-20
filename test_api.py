"""
Quick Start Script - Test the API with sample data
Run this after starting the server to populate the database with test data
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def main():
    print("🚀 Starting Ecommerce API Test...")
    
    # 1. Create Admin User
    print("\n📝 Creating Admin User...")
    admin_data = {
        "email": "admin@ecommerce.com",
        "password": "admin123",
        "full_name": "Admin User",
        "phone": "+1234567890"
    }
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=admin_data)
    print_response("Admin Signup", response)
    
    # 2. Login as Admin
    print("\n🔐 Logging in as Admin...")
    login_data = {
        "username": "admin@ecommerce.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    admin_token = response.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print_response("Admin Login", response)
    
    # Note: In real scenario, you'd manually set admin role in database
    # For testing, we'll continue with customer operations
    
    # 3. Create Customer User
    print("\n👤 Creating Customer User...")
    customer_data = {
        "email": "customer@example.com",
        "password": "customer123",
        "full_name": "John Doe",
        "phone": "+9876543210"
    }
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=customer_data)
    print_response("Customer Signup", response)
    
    # 4. Login as Customer
    print("\n🔐 Logging in as Customer...")
    login_data = {
        "username": "customer@example.com",
        "password": "customer123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    customer_token = response.json().get("access_token")
    customer_headers = {"Authorization": f"Bearer {customer_token}"}
    print_response("Customer Login", response)
    
    # 5. Create Products (as admin - but will use customer token for demo)
    print("\n📦 Creating Sample Products...")
    products = [
        {
            "name": "iPhone 15 Pro",
            "description": "Latest Apple iPhone with A17 Pro chip",
            "price": 999.99,
            "category": "Electronics",
            "stock_quantity": 50,
            "images": ["https://example.com/iphone15.jpg"]
        },
        {
            "name": "MacBook Pro 16",
            "description": "Powerful laptop for professionals",
            "price": 2499.99,
            "category": "Electronics",
            "stock_quantity": 30,
            "images": ["https://example.com/macbook.jpg"]
        },
        {
            "name": "AirPods Pro",
            "description": "Active noise cancellation headphones",
            "price": 249.99,
            "category": "Electronics",
            "stock_quantity": 100,
            "images": ["https://example.com/airpods.jpg"]
        }
    ]
    
    product_ids = []
    for product in products:
        # Note: This will fail if customer doesn't have admin role
        # In production, ensure the admin user has admin role set in DB
        response = requests.post(
            f"{BASE_URL}/api/products/",
            json=product,
            headers=admin_headers
        )
        if response.status_code == 201:
            product_ids.append(response.json()["id"])
            print(f"✅ Created: {product['name']}")
        else:
            print(f"❌ Failed to create: {product['name']}")
    
    # 6. Get All Products
    print("\n📋 Getting All Products...")
    response = requests.get(f"{BASE_URL}/api/products/")
    print_response("Products List", response)
    
    if response.status_code == 200 and response.json():
        product_ids = [p["id"] for p in response.json()]
    
    # 7. Add Items to Cart
    if product_ids:
        print("\n🛒 Adding Items to Cart...")
        for product_id in product_ids[:2]:  # Add first 2 products
            cart_item = {
                "product_id": product_id,
                "quantity": 2
            }
            response = requests.post(
                f"{BASE_URL}/api/cart/items",
                json=cart_item,
                headers=customer_headers
            )
            print_response(f"Add to Cart - Product {product_id}", response)
    
    # 8. Get Cart
    print("\n🛍️ Getting Cart...")
    response = requests.get(f"{BASE_URL}/api/cart/", headers=customer_headers)
    print_response("Cart", response)
    
    # 9. Create Order
    print("\n📦 Creating Order...")
    order_data = {
        "shipping_address": {
            "street": "123 Main St",
            "city": "New York",
            "state": "NY",
            "country": "USA",
            "postal_code": "10001"
        },
        "notes": "Please deliver between 9 AM - 5 PM"
    }
    response = requests.post(
        f"{BASE_URL}/api/orders/",
        json=order_data,
        headers=customer_headers
    )
    print_response("Create Order", response)
    
    order_id = None
    order_number = None
    if response.status_code == 201:
        order_id = response.json()["id"]
        order_number = response.json()["order_number"]
    
    # 10. Create Payment
    if order_id:
        print("\n💳 Creating Payment...")
        payment_data = {
            "order_id": order_id,
            "payment_method": "credit_card",
            "amount": response.json()["total_amount"]
        }
        response = requests.post(
            f"{BASE_URL}/api/payments/",
            json=payment_data,
            headers=customer_headers
        )
        print_response("Create Payment", response)
    
    # 11. Track Order
    if order_number:
        print("\n🔍 Tracking Order...")
        response = requests.get(f"{BASE_URL}/api/orders/tracking/{order_number}")
        print_response("Order Tracking", response)
    
    # 12. Get User's Orders
    print("\n📋 Getting User Orders...")
    response = requests.get(f"{BASE_URL}/api/orders/", headers=customer_headers)
    print_response("User Orders", response)
    
    # 13. Update Profile
    print("\n👤 Updating Profile...")
    profile_update = {
        "full_name": "John Doe Updated",
        "address": {
            "street": "456 Oak Ave",
            "city": "Los Angeles",
            "state": "CA",
            "country": "USA",
            "postal_code": "90001"
        }
    }
    response = requests.put(
        f"{BASE_URL}/api/auth/me",
        json=profile_update,
        headers=customer_headers
    )
    print_response("Update Profile", response)
    
    print("\n" + "="*60)
    print("✅ Test Script Completed!")
    print("="*60)
    print("\n📚 Next Steps:")
    print("1. Open http://localhost:8000/docs for interactive API documentation")
    print("2. Manually update admin role in MongoDB:")
    print("   db.users.updateOne({email: 'admin@ecommerce.com'}, {$set: {role: 'admin'}})")
    print("3. Test admin endpoints with the updated admin token")
    print("\n")

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the server is running at http://localhost:8000")
        print("Start it with: uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
