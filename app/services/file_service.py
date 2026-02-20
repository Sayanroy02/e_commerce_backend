import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException
from PIL import Image
import aiofiles

# Allowed image extensions
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Upload directories
UPLOAD_DIR = Path("app/static/uploads")
PRODUCTS_DIR = UPLOAD_DIR / "products"
PROFILES_DIR = UPLOAD_DIR / "profiles"

# Create directories if they don't exist
PRODUCTS_DIR.mkdir(parents=True, exist_ok=True)
PROFILES_DIR.mkdir(parents=True, exist_ok=True)


def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename to prevent conflicts"""
    ext = original_filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    return unique_name


async def save_upload_file(upload_file: UploadFile, destination_dir: Path) -> str:
    """
    Save uploaded file to disk
    Returns the filename of the saved file
    """
    if not upload_file:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Check file extension
    if not is_allowed_file(upload_file.filename):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Read file content
    content = await upload_file.read()
    
    # Check file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Generate unique filename
    filename = generate_unique_filename(upload_file.filename)
    file_path = destination_dir / filename
    
    # Save file
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    
    # Optimize image (resize if too large)
    try:
        optimize_image(file_path)
    except Exception as e:
        print(f"Image optimization failed: {e}")
    
    return filename


def optimize_image(file_path: Path, max_width: int = 1200, max_height: int = 1200):
    """Optimize image size while maintaining aspect ratio"""
    try:
        with Image.open(file_path) as img:
            # Convert RGBA to RGB if necessary
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            # Resize if image is too large
            if img.width > max_width or img.height > max_height:
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Save optimized image
            img.save(file_path, optimize=True, quality=85)
    except Exception as e:
        print(f"Error optimizing image: {e}")


async def save_product_image(upload_file: UploadFile) -> str:
    """Save product image and return the filename"""
    return await save_upload_file(upload_file, PRODUCTS_DIR)


async def save_profile_image(upload_file: UploadFile) -> str:
    """Save profile image and return the filename"""
    return await save_upload_file(upload_file, PROFILES_DIR)


def delete_file(filename: str, file_type: str = "product"):
    """Delete a file from disk"""
    try:
        if file_type == "product":
            file_path = PRODUCTS_DIR / filename
        else:
            file_path = PROFILES_DIR / filename
        
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"Error deleting file: {e}")
        return False


def get_file_url(filename: str, file_type: str = "product") -> str:
    """Generate URL for accessing the file"""
    if file_type == "product":
        return f"/static/uploads/products/{filename}"
    else:
        return f"/static/uploads/profiles/{filename}"
