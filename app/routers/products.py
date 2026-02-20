from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse
from app.core.database import products_collection
from app.core.dependencies import get_current_admin_user, get_current_active_user
from app.schemas.user import UserInDB
from app.services.file_service import save_product_image, delete_file, get_file_url

router = APIRouter(prefix="/api/products", tags=["Products"])


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    name: str = Form(...),
    description: str = Form(None),
    price: float = Form(...),
    category: str = Form(...),
    stock_quantity: int = Form(...),
    images: List[UploadFile] = File(None),
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Create a new product with images (Admin only)"""
    
    # Validate price and stock
    if price <= 0:
        raise HTTPException(status_code=400, detail="Price must be greater than 0")
    if stock_quantity < 0:
        raise HTTPException(status_code=400, detail="Stock quantity cannot be negative")
    
    # Save uploaded images
    image_urls = []
    if images:
        for image in images:
            if image.filename:  # Check if file was actually uploaded
                try:
                    filename = await save_product_image(image)
                    image_url = get_file_url(filename, "product")
                    image_urls.append(image_url)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error uploading image: {str(e)}")
    
    product_dict = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "stock_quantity": stock_quantity,
        "images": image_urls,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await products_collection.insert_one(product_dict)
    product_dict["_id"] = str(result.inserted_id)
    
    return ProductResponse(**product_dict)


@router.get("/", response_model=List[ProductResponse])
async def get_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all products with optional filters"""
    query = {"is_active": True}
    
    if category:
        query["category"] = category
    
    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    
    cursor = products_collection.find(query).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)
    
    for product in products:
        product["_id"] = str(product["_id"])
    
    return [ProductResponse(**product) for product in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str):
    """Get a specific product by ID"""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product["_id"] = str(product["_id"])
    return ProductResponse(**product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    category: Optional[str] = Form(None),
    stock_quantity: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(None),
    images: List[UploadFile] = File(None),
    remove_existing_images: bool = Form(False),
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Update a product with optional new images (Admin only)"""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    # Get existing product
    existing_product = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not existing_product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    update_data = {}
    
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if price is not None:
        if price <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0")
        update_data["price"] = price
    if category is not None:
        update_data["category"] = category
    if stock_quantity is not None:
        if stock_quantity < 0:
            raise HTTPException(status_code=400, detail="Stock quantity cannot be negative")
        update_data["stock_quantity"] = stock_quantity
    if is_active is not None:
        update_data["is_active"] = is_active
    
    # Handle images
    if remove_existing_images:
        # Delete old images from disk
        for old_image_url in existing_product.get("images", []):
            filename = old_image_url.split("/")[-1]
            delete_file(filename, "product")
        update_data["images"] = []
    else:
        # Keep existing images
        update_data["images"] = existing_product.get("images", [])
    
    # Add new images
    if images:
        for image in images:
            if image.filename:
                try:
                    filename = await save_product_image(image)
                    image_url = get_file_url(filename, "product")
                    update_data["images"].append(image_url)
                except Exception as e:
                    raise HTTPException(status_code=400, detail=f"Error uploading image: {str(e)}")
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    
    update_data["updated_at"] = datetime.utcnow()
    
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": update_data}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    updated_product = await products_collection.find_one({"_id": ObjectId(product_id)})
    updated_product["_id"] = str(updated_product["_id"])
    
    return ProductResponse(**updated_product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: str,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Delete a product and its images (Admin only)"""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    # Get product to delete its images
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Delete images from disk
    for image_url in product.get("images", []):
        filename = image_url.split("/")[-1]
        delete_file(filename, "product")
    
    # Soft delete by marking as inactive
    result = await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return None


@router.post("/{product_id}/images", response_model=ProductResponse)
async def add_product_images(
    product_id: str,
    images: List[UploadFile] = File(...),
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Add more images to an existing product (Admin only)"""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Upload new images
    new_image_urls = []
    for image in images:
        if image.filename:
            try:
                filename = await save_product_image(image)
                image_url = get_file_url(filename, "product")
                new_image_urls.append(image_url)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Error uploading image: {str(e)}")
    
    # Append to existing images
    existing_images = product.get("images", [])
    updated_images = existing_images + new_image_urls
    
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"images": updated_images, "updated_at": datetime.utcnow()}}
    )
    
    updated_product = await products_collection.find_one({"_id": ObjectId(product_id)})
    updated_product["_id"] = str(updated_product["_id"])
    
    return ProductResponse(**updated_product)


@router.delete("/{product_id}/images", response_model=ProductResponse)
async def remove_product_image(
    product_id: str,
    image_url: str = Query(..., description="URL of the image to remove"),
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Remove a specific image from a product (Admin only)"""
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = await products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    existing_images = product.get("images", [])
    
    if image_url not in existing_images:
        raise HTTPException(status_code=404, detail="Image not found in product")
    
    # Delete from disk
    filename = image_url.split("/")[-1]
    delete_file(filename, "product")
    
    # Remove from database
    updated_images = [img for img in existing_images if img != image_url]
    
    await products_collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"images": updated_images, "updated_at": datetime.utcnow()}}
    )
    
    updated_product = await products_collection.find_one({"_id": ObjectId(product_id)})
    updated_product["_id"] = str(updated_product["_id"])
    
    return ProductResponse(**updated_product)
