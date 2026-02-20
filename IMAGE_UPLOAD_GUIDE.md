# Image Upload & Management Guide

Complete guide for handling product images in the Ecommerce API.

## 📸 Features

- ✅ Upload multiple images per product
- ✅ Automatic image optimization (resize & compress)
- ✅ Real-time image serving via static URLs
- ✅ Add/remove images from existing products
- ✅ Automatic file validation (type, size)
- ✅ Secure unique filenames to prevent conflicts
- ✅ Images stored locally on server

## 🗂️ Directory Structure

```
app/
└── static/
    └── uploads/
        ├── products/      # Product images
        └── profiles/      # User profile pictures (future)
```

## 📋 Supported Formats

- JPG/JPEG
- PNG
- WebP
- GIF

**File Size Limit:** 5MB per image
**Image Optimization:** Automatically resized to max 1200x1200px while maintaining aspect ratio

## 🔧 API Endpoints

### 1. Create Product with Images

**Endpoint:** `POST /api/products/`

**Content-Type:** `multipart/form-data`

**Fields:**
- `name` (string, required) - Product name
- `description` (string, optional) - Product description
- `price` (float, required) - Product price
- `category` (string, required) - Product category
- `stock_quantity` (integer, required) - Available stock
- `images` (file[], optional) - Multiple image files

**Example using cURL:**
```bash
curl -X POST "http://localhost:8000/api/products/" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "name=iPhone 15 Pro" \
  -F "description=Latest Apple iPhone" \
  -F "price=999.99" \
  -F "category=Electronics" \
  -F "stock_quantity=50" \
  -F "images=@/path/to/image1.jpg" \
  -F "images=@/path/to/image2.jpg"
```

**Example using Python:**
```python
import requests

url = "http://localhost:8000/api/products/"
headers = {"Authorization": "Bearer YOUR_ADMIN_TOKEN"}

# Product data
data = {
    "name": "iPhone 15 Pro",
    "description": "Latest Apple iPhone with A17 Pro chip",
    "price": 999.99,
    "category": "Electronics",
    "stock_quantity": 50
}

# Image files
files = [
    ("images", open("iphone_front.jpg", "rb")),
    ("images", open("iphone_back.jpg", "rb")),
    ("images", open("iphone_side.jpg", "rb"))
]

response = requests.post(url, headers=headers, data=data, files=files)
print(response.json())

# Don't forget to close files
for _, file in files:
    file.close()
```

**Response:**
```json
{
  "id": "65abc123def456",
  "name": "iPhone 15 Pro",
  "description": "Latest Apple iPhone with A17 Pro chip",
  "price": 999.99,
  "category": "Electronics",
  "stock_quantity": 50,
  "images": [
    "/static/uploads/products/a1b2c3d4e5f6.jpg",
    "/static/uploads/products/f6e5d4c3b2a1.jpg",
    "/static/uploads/products/1a2b3c4d5e6f.jpg"
  ],
  "is_active": true,
  "created_at": "2024-02-20T10:30:00",
  "updated_at": "2024-02-20T10:30:00"
}
```

### 2. Update Product with Images

**Endpoint:** `PUT /api/products/{product_id}`

**Content-Type:** `multipart/form-data`

**Fields (all optional):**
- `name` (string)
- `description` (string)
- `price` (float)
- `category` (string)
- `stock_quantity` (integer)
- `is_active` (boolean)
- `images` (file[]) - New images to add
- `remove_existing_images` (boolean) - If true, removes all existing images

**Example - Add new images (keep existing):**
```bash
curl -X PUT "http://localhost:8000/api/products/65abc123def456" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "images=@new_image.jpg"
```

**Example - Replace all images:**
```bash
curl -X PUT "http://localhost:8000/api/products/65abc123def456" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "remove_existing_images=true" \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg"
```

**Example - Update price without touching images:**
```python
import requests

url = "http://localhost:8000/api/products/65abc123def456"
headers = {"Authorization": "Bearer YOUR_ADMIN_TOKEN"}

data = {"price": 899.99}

response = requests.put(url, headers=headers, data=data)
print(response.json())
```

### 3. Add Images to Existing Product

**Endpoint:** `POST /api/products/{product_id}/images`

**Content-Type:** `multipart/form-data`

**Use Case:** Add more images to a product without modifying other fields

**Example:**
```bash
curl -X POST "http://localhost:8000/api/products/65abc123def456/images" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "images=@additional_image1.jpg" \
  -F "images=@additional_image2.jpg"
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/products/65abc123def456/images"
headers = {"Authorization": "Bearer YOUR_ADMIN_TOKEN"}

files = [
    ("images", open("detail1.jpg", "rb")),
    ("images", open("detail2.jpg", "rb"))
]

response = requests.post(url, headers=headers, files=files)
print(response.json())
```

### 4. Remove Specific Image

**Endpoint:** `DELETE /api/products/{product_id}/images`

**Query Parameters:**
- `image_url` (required) - The URL of the image to remove

**Example:**
```bash
curl -X DELETE "http://localhost:8000/api/products/65abc123def456/images?image_url=/static/uploads/products/a1b2c3d4e5f6.jpg" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

**Python Example:**
```python
import requests

url = "http://localhost:8000/api/products/65abc123def456/images"
headers = {"Authorization": "Bearer YOUR_ADMIN_TOKEN"}
params = {"image_url": "/static/uploads/products/a1b2c3d4e5f6.jpg"}

response = requests.delete(url, headers=headers, params=params)
print(response.json())
```

### 5. Get Product with Images

**Endpoint:** `GET /api/products/{product_id}`

No authentication required for viewing products.

**Example:**
```bash
curl -X GET "http://localhost:8000/api/products/65abc123def456"
```

**Access Images:**
Images are served as static files. To display an image:

```
Full URL: http://localhost:8000/static/uploads/products/a1b2c3d4e5f6.jpg
```

**HTML Example:**
```html
<img src="http://localhost:8000/static/uploads/products/a1b2c3d4e5f6.jpg" 
     alt="Product Image" 
     width="300">
```

**Flutter Example:**
```dart
import 'package:flutter/material.dart';

class ProductImage extends StatelessWidget {
  final String imageUrl;
  
  const ProductImage({required this.imageUrl});
  
  @override
  Widget build(BuildContext context) {
    return Image.network(
      'http://localhost:8000$imageUrl',
      fit: BoxFit.cover,
      loadingBuilder: (context, child, loadingProgress) {
        if (loadingProgress == null) return child;
        return Center(
          child: CircularProgressIndicator(
            value: loadingProgress.expectedTotalBytes != null
                ? loadingProgress.cumulativeBytesLoaded /
                    loadingProgress.expectedTotalBytes!
                : null,
          ),
        );
      },
      errorBuilder: (context, error, stackTrace) {
        return Icon(Icons.error);
      },
    );
  }
}
```

## 🎨 Using Swagger UI to Upload Images

1. Open http://localhost:8000/docs
2. Authorize with admin token
3. Find `POST /api/products/`
4. Click "Try it out"
5. Fill in the form fields
6. For images: Click "Choose File" and select your images
7. You can select multiple images at once
8. Click "Execute"

**Important:** Swagger UI will show the form with:
- Text fields for name, description, price, etc.
- File upload buttons for images

## 📱 Flutter Integration Example

### Complete Product Creation with Images

```dart
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';

class ProductService {
  final String baseUrl = 'http://localhost:8000';
  final String adminToken;
  
  ProductService({required this.adminToken});
  
  Future<Map<String, dynamic>> createProduct({
    required String name,
    required String description,
    required double price,
    required String category,
    required int stockQuantity,
    required List<File> images,
  }) async {
    final uri = Uri.parse('$baseUrl/api/products/');
    
    var request = http.MultipartRequest('POST', uri);
    
    // Add headers
    request.headers['Authorization'] = 'Bearer $adminToken';
    
    // Add form fields
    request.fields['name'] = name;
    request.fields['description'] = description;
    request.fields['price'] = price.toString();
    request.fields['category'] = category;
    request.fields['stock_quantity'] = stockQuantity.toString();
    
    // Add images
    for (var image in images) {
      var stream = http.ByteStream(image.openRead());
      var length = await image.length();
      var multipartFile = http.MultipartFile(
        'images',
        stream,
        length,
        filename: image.path.split('/').last,
      );
      request.files.add(multipartFile);
    }
    
    // Send request
    var response = await request.send();
    var responseData = await response.stream.bytesToString();
    
    if (response.statusCode == 201) {
      return json.decode(responseData);
    } else {
      throw Exception('Failed to create product: $responseData');
    }
  }
  
  Future<List<File>> pickImages() async {
    final ImagePicker picker = ImagePicker();
    final List<XFile>? images = await picker.pickMultiImage();
    
    if (images != null) {
      return images.map((xfile) => File(xfile.path)).toList();
    }
    return [];
  }
}

// Usage in your Flutter app:
class CreateProductScreen extends StatefulWidget {
  @override
  _CreateProductScreenState createState() => _CreateProductScreenState();
}

class _CreateProductScreenState extends State<CreateProductScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _priceController = TextEditingController();
  final _categoryController = TextEditingController();
  final _stockController = TextEditingController();
  
  List<File> _selectedImages = [];
  final ProductService _productService = ProductService(
    adminToken: 'YOUR_ADMIN_TOKEN'
  );
  
  Future<void> _pickImages() async {
    final images = await _productService.pickImages();
    setState(() {
      _selectedImages = images;
    });
  }
  
  Future<void> _createProduct() async {
    if (_formKey.currentState!.validate() && _selectedImages.isNotEmpty) {
      try {
        final product = await _productService.createProduct(
          name: _nameController.text,
          description: _descriptionController.text,
          price: double.parse(_priceController.text),
          category: _categoryController.text,
          stockQuantity: int.parse(_stockController.text),
          images: _selectedImages,
        );
        
        // Success! Navigate back or show success message
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Product created successfully!'))
        );
        Navigator.pop(context);
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $e'))
        );
      }
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Create Product')),
      body: Form(
        key: _formKey,
        child: ListView(
          padding: EdgeInsets.all(16),
          children: [
            TextFormField(
              controller: _nameController,
              decoration: InputDecoration(labelText: 'Product Name'),
              validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
            ),
            TextFormField(
              controller: _descriptionController,
              decoration: InputDecoration(labelText: 'Description'),
              maxLines: 3,
            ),
            TextFormField(
              controller: _priceController,
              decoration: InputDecoration(labelText: 'Price'),
              keyboardType: TextInputType.number,
              validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
            ),
            TextFormField(
              controller: _categoryController,
              decoration: InputDecoration(labelText: 'Category'),
              validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
            ),
            TextFormField(
              controller: _stockController,
              decoration: InputDecoration(labelText: 'Stock Quantity'),
              keyboardType: TextInputType.number,
              validator: (value) => value?.isEmpty ?? true ? 'Required' : null,
            ),
            SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _pickImages,
              icon: Icon(Icons.add_photo_alternate),
              label: Text('Select Images'),
            ),
            if (_selectedImages.isNotEmpty)
              Container(
                height: 120,
                child: ListView.builder(
                  scrollDirection: Axis.horizontal,
                  itemCount: _selectedImages.length,
                  itemBuilder: (context, index) {
                    return Padding(
                      padding: EdgeInsets.all(8),
                      child: Stack(
                        children: [
                          Image.file(_selectedImages[index], 
                            width: 100, 
                            height: 100, 
                            fit: BoxFit.cover
                          ),
                          Positioned(
                            right: 0,
                            top: 0,
                            child: IconButton(
                              icon: Icon(Icons.close, color: Colors.red),
                              onPressed: () {
                                setState(() {
                                  _selectedImages.removeAt(index);
                                });
                              },
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _createProduct,
              child: Text('Create Product'),
            ),
          ],
        ),
      ),
    );
  }
}
```

## 🔒 Security Considerations

1. **File Type Validation:** Only allowed image formats are accepted
2. **File Size Limit:** Maximum 5MB per file
3. **Unique Filenames:** UUID-based names prevent conflicts and overwrites
4. **Admin Only:** Only admins can upload/modify/delete product images
5. **Image Optimization:** Automatic resizing prevents large file attacks

## 📊 Image Optimization Details

The system automatically:
- Converts RGBA to RGB (for JPEG compatibility)
- Resizes images larger than 1200x1200 while maintaining aspect ratio
- Compresses with 85% quality
- Saves optimized version back to disk

## 🐛 Troubleshooting

### Issue: "File type not allowed"
**Solution:** Only upload JPG, PNG, WebP, or GIF files

### Issue: "File too large"
**Solution:** Compress image to under 5MB before uploading

### Issue: Images not displaying
**Solution:** 
- Check the full URL: `http://localhost:8000/static/uploads/products/filename.jpg`
- Ensure server is running
- Verify file exists in `app/static/uploads/products/`

### Issue: Permission denied when saving
**Solution:** Ensure the `app/static/uploads/products/` directory has write permissions

### Issue: Module 'PIL' not found
**Solution:** Install Pillow: `pip install Pillow`

## 📈 Best Practices

1. **Multiple Images:** Upload 3-5 images per product showing different angles
2. **Image Quality:** Use high-quality images but compress before upload
3. **Naming:** Use descriptive original filenames (system generates unique names)
4. **Dimensions:** Square images (1:1 ratio) work best for product grids
5. **First Image:** First image in array is typically used as primary/thumbnail
6. **Alt Text:** In your Flutter app, use product name as alt text for accessibility

## 🚀 Production Deployment

For production, consider:
1. **CDN:** Upload images to AWS S3, Cloudflare R2, or similar
2. **Image Processing:** Use services like Cloudinary or imgix
3. **Backup:** Regular backups of uploads directory
4. **Nginx:** Configure nginx to serve static files efficiently
5. **HTTPS:** Always use HTTPS for image URLs in production

## Example CDN Integration (AWS S3)

Update `file_service.py` to upload to S3:
```python
import boto3

s3_client = boto3.client('s3',
    aws_access_key_id='YOUR_KEY',
    aws_secret_access_key='YOUR_SECRET'
)

async def save_product_image_to_s3(upload_file: UploadFile) -> str:
    filename = generate_unique_filename(upload_file.filename)
    content = await upload_file.read()
    
    s3_client.put_object(
        Bucket='your-bucket-name',
        Key=f'products/{filename}',
        Body=content,
        ContentType=upload_file.content_type
    )
    
    return f"https://your-bucket.s3.amazonaws.com/products/{filename}"
```

---

**Questions or issues?** Check the main README or API documentation at `/docs`
