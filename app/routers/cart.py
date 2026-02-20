from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime
from bson import ObjectId
from app.schemas.cart import CartAddItem, CartUpdateItem, CartResponse, CartItem
from app.core.database import carts_collection, products_collection
from app.core.dependencies import get_current_active_user
from app.schemas.user import UserInDB

router = APIRouter(prefix="/api/cart", tags=["Cart"])


async def calculate_cart_total(items: list) -> float:
    """Calculate total amount for cart items"""
    return sum(item["subtotal"] for item in items)


@router.get("/", response_model=CartResponse)
async def get_cart(current_user: UserInDB = Depends(get_current_active_user)):
    """Get current user's cart"""
    cart = await carts_collection.find_one({"user_id": current_user.id})
    
    if not cart:
        # Create empty cart
        cart = {
            "user_id": current_user.id,
            "items": [],
            "total_amount": 0.0,
            "updated_at": datetime.utcnow()
        }
        result = await carts_collection.insert_one(cart)
        cart["_id"] = str(result.inserted_id)
    else:
        cart["_id"] = str(cart["_id"])
    
    return CartResponse(**cart)


@router.post("/items", response_model=CartResponse)
async def add_to_cart(
    item: CartAddItem,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Add item to cart"""
    # Validate product
    if not ObjectId.is_valid(item.product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")
    
    product = await products_collection.find_one({"_id": ObjectId(item.product_id)})
    
    if not product or not product.get("is_active"):
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["stock_quantity"] < item.quantity:
        raise HTTPException(status_code=400, detail="Insufficient stock")
    
    # Get or create cart
    cart = await carts_collection.find_one({"user_id": current_user.id})
    
    if not cart:
        cart = {
            "user_id": current_user.id,
            "items": [],
            "total_amount": 0.0
        }
    
    # Check if product already in cart
    existing_item = None
    for cart_item in cart["items"]:
        if cart_item["product_id"] == item.product_id:
            existing_item = cart_item
            break
    
    if existing_item:
        # Update quantity
        existing_item["quantity"] += item.quantity
        existing_item["subtotal"] = existing_item["quantity"] * existing_item["price"]
    else:
        # Add new item
        new_item = {
            "product_id": item.product_id,
            "product_name": product["name"],
            "price": product["price"],
            "quantity": item.quantity,
            "subtotal": product["price"] * item.quantity
        }
        cart["items"].append(new_item)
    
    # Recalculate total
    cart["total_amount"] = await calculate_cart_total(cart["items"])
    cart["updated_at"] = datetime.utcnow()
    
    # Update or insert cart
    if "_id" in cart:
        await carts_collection.update_one(
            {"_id": cart["_id"]},
            {"$set": cart}
        )
        cart["_id"] = str(cart["_id"])
    else:
        result = await carts_collection.insert_one(cart)
        cart["_id"] = str(result.inserted_id)
    
    return CartResponse(**cart)


@router.put("/items", response_model=CartResponse)
async def update_cart_item(
    item: CartUpdateItem,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Update item quantity in cart"""
    cart = await carts_collection.find_one({"user_id": current_user.id})
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Find and update item
    item_found = False
    for cart_item in cart["items"]:
        if cart_item["product_id"] == item.product_id:
            item_found = True
            if item.quantity == 0:
                # Remove item
                cart["items"].remove(cart_item)
            else:
                # Update quantity
                cart_item["quantity"] = item.quantity
                cart_item["subtotal"] = cart_item["price"] * item.quantity
            break
    
    if not item_found:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    # Recalculate total
    cart["total_amount"] = await calculate_cart_total(cart["items"])
    cart["updated_at"] = datetime.utcnow()
    
    await carts_collection.update_one(
        {"_id": cart["_id"]},
        {"$set": cart}
    )
    
    cart["_id"] = str(cart["_id"])
    return CartResponse(**cart)


@router.delete("/items/{product_id}", response_model=CartResponse)
async def remove_from_cart(
    product_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Remove item from cart"""
    cart = await carts_collection.find_one({"user_id": current_user.id})
    
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Remove item
    cart["items"] = [item for item in cart["items"] if item["product_id"] != product_id]
    
    # Recalculate total
    cart["total_amount"] = await calculate_cart_total(cart["items"])
    cart["updated_at"] = datetime.utcnow()
    
    await carts_collection.update_one(
        {"_id": cart["_id"]},
        {"$set": cart}
    )
    
    cart["_id"] = str(cart["_id"])
    return CartResponse(**cart)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(current_user: UserInDB = Depends(get_current_active_user)):
    """Clear entire cart"""
    cart = await carts_collection.find_one({"user_id": current_user.id})
    
    if cart:
        await carts_collection.update_one(
            {"_id": cart["_id"]},
            {"$set": {"items": [], "total_amount": 0.0, "updated_at": datetime.utcnow()}}
        )
    
    return None
