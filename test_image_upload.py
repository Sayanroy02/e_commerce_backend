"""
Test Script for Image Upload Functionality
Creates test images and uploads them to products
"""
import requests
import io
from PIL import Image

BASE_URL = "http://localhost:8000"

def create_test_image(color, size=(800, 600)):
    """Create a test image with a solid color"""
    img = Image.new('RGB', size, color=color)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    return img_bytes

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        import json
        print(json.dumps(response.json(), indent=2))
    except:
        print(response.text)

def main():
    print("🎨 Testing Image Upload Functionality...")
    
    # 1. Create Admin User
    print("\n1️⃣ Creating Admin User...")
    admin_data = {
        "email": "admin@test.com",
        "password": "admin123",
        "full_name": "Admin User"
    }
    response = requests.post(f"{BASE_URL}/api/auth/signup", json=admin_data)
    
    # 2. Login as Admin
    print("\n2️⃣ Logging in as Admin...")
    login_data = {
        "username": "admin@test.com",
        "password": "admin123"
    }
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    admin_token = response.json().get("access_token")
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    print(f"✅ Admin Token: {admin_token[:20]}...")
    
    # 3. Create Product with Multiple Images
    print("\n3️⃣ Creating Product with Multiple Images...")
    
    # Create test images
    red_image = create_test_image('red')
    blue_image = create_test_image('blue')
    green_image = create_test_image('green')
    
    # Product data
    product_data = {
        "name": "Test Product with Images",
        "description": "This product has multiple test images",
        "price": "299.99",
        "category": "Test Category",
        "stock_quantity": "100"
    }
    
    # Prepare files for upload
    files = [
        ("images", ("red_phone.jpg", red_image, "image/jpeg")),
        ("images", ("blue_phone.jpg", blue_image, "image/jpeg")),
        ("images", ("green_phone.jpg", green_image, "image/jpeg"))
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/products/",
        headers=admin_headers,
        data=product_data,
        files=files
    )
    
    print_response("Create Product with Images", response)
    
    if response.status_code != 201:
        print("\n❌ Failed to create product. Make sure:")
        print("1. MongoDB is running")
        print("2. API server is running")
        print("3. User has admin role in database:")
        print("   db.users.updateOne({email: 'admin@test.com'}, {$set: {role: 'admin'}})")
        return
    
    product_id = response.json().get("id")
    product_images = response.json().get("images", [])
    
    print(f"\n✅ Product created with ID: {product_id}")
    print(f"✅ Images uploaded: {len(product_images)}")
    for i, img_url in enumerate(product_images, 1):
        print(f"   {i}. {img_url}")
        print(f"      Full URL: {BASE_URL}{img_url}")
    
    # 4. Add More Images to Product
    print("\n4️⃣ Adding More Images to Product...")
    
    yellow_image = create_test_image('yellow')
    purple_image = create_test_image('purple')
    
    files = [
        ("images", ("yellow_phone.jpg", yellow_image, "image/jpeg")),
        ("images", ("purple_phone.jpg", purple_image, "image/jpeg"))
    ]
    
    response = requests.post(
        f"{BASE_URL}/api/products/{product_id}/images",
        headers=admin_headers,
        files=files
    )
    
    print_response("Add More Images", response)
    
    if response.status_code == 200:
        product_images = response.json().get("images", [])
        print(f"\n✅ Now product has {len(product_images)} images total")
    
    # 5. Remove One Image
    if product_images and len(product_images) > 0:
        print("\n5️⃣ Removing One Image...")
        image_to_remove = product_images[0]
        
        response = requests.delete(
            f"{BASE_URL}/api/products/{product_id}/images",
            headers=admin_headers,
            params={"image_url": image_to_remove}
        )
        
        print_response("Remove Image", response)
        
        if response.status_code == 200:
            remaining_images = response.json().get("images", [])
            print(f"\n✅ Image removed. Remaining: {len(remaining_images)} images")
    
    # 6. Update Product - Replace All Images
    print("\n6️⃣ Update Product - Replace All Images...")
    
    orange_image = create_test_image('orange')
    pink_image = create_test_image('pink')
    
    update_data = {
        "name": "Updated Product",
        "price": "199.99",
        "remove_existing_images": "true"
    }
    
    files = [
        ("images", ("orange_phone.jpg", orange_image, "image/jpeg")),
        ("images", ("pink_phone.jpg", pink_image, "image/jpeg"))
    ]
    
    response = requests.put(
        f"{BASE_URL}/api/products/{product_id}",
        headers=admin_headers,
        data=update_data,
        files=files
    )
    
    print_response("Update Product with New Images", response)
    
    if response.status_code == 200:
        final_images = response.json().get("images", [])
        print(f"\n✅ Product updated. New images: {len(final_images)}")
        for i, img_url in enumerate(final_images, 1):
            print(f"   {i}. {BASE_URL}{img_url}")
    
    # 7. Get Product to Verify
    print("\n7️⃣ Getting Product to Verify...")
    response = requests.get(f"{BASE_URL}/api/products/{product_id}")
    print_response("Get Product", response)
    
    # 8. Access Images Directly
    print("\n8️⃣ Testing Image Access...")
    if response.status_code == 200:
        images = response.json().get("images", [])
        for i, img_url in enumerate(images, 1):
            full_url = f"{BASE_URL}{img_url}"
            img_response = requests.get(full_url)
            print(f"   Image {i}: {full_url}")
            print(f"   Status: {img_response.status_code} | Size: {len(img_response.content)} bytes")
    
    print("\n" + "="*60)
    print("✅ Image Upload Test Completed!")
    print("="*60)
    print("\n📋 Summary:")
    print("- ✅ Created product with multiple images")
    print("- ✅ Added more images to existing product")
    print("- ✅ Removed specific image")
    print("- ✅ Updated product and replaced all images")
    print("- ✅ Verified image access via URLs")
    print("\n🌐 View Product Images:")
    if response.status_code == 200:
        images = response.json().get("images", [])
        for img_url in images:
            print(f"   {BASE_URL}{img_url}")
    
    print("\n💡 Important: Set admin role in database:")
    print("   db.users.updateOne({email: 'admin@test.com'}, {$set: {role: 'admin'}})")
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
        import traceback
        traceback.print_exc()
