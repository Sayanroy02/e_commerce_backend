from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import random
import string
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderStatus, OrderTracking
from app.core.database import orders_collection, carts_collection, products_collection
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.schemas.user import UserInDB

router = APIRouter(prefix="/api/orders", tags=["Orders"])


def generate_order_number() -> str:
    """Generate a unique order number"""
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ORD-{timestamp}-{random_str}"


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Create a new order from cart"""
    # Get user's cart
    cart = await carts_collection.find_one({"user_id": current_user.id})
    
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Validate stock for all items
    for item in cart["items"]:
        product = await products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if not product or product["stock_quantity"] < item["quantity"]:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for {item['product_name']}"
            )
    
    # Create order
    order = {
        "order_number": generate_order_number(),
        "user_id": current_user.id,
        "items": cart["items"],
        "total_amount": cart["total_amount"],
        "shipping_address": order_data.shipping_address.model_dump(),
        "status": OrderStatus.PENDING,
        "notes": order_data.notes,
        "tracking_number": None,
        "status_history": [
            {
                "status": OrderStatus.PENDING,
                "timestamp": datetime.utcnow(),
                "note": "Order placed"
            }
        ],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await orders_collection.insert_one(order)
    
    # Update product stock
    for item in cart["items"]:
        await products_collection.update_one(
            {"_id": ObjectId(item["product_id"])},
            {"$inc": {"stock_quantity": -item["quantity"]}}
        )
    
    # Clear cart
    await carts_collection.update_one(
        {"_id": cart["_id"]},
        {"$set": {"items": [], "total_amount": 0.0, "updated_at": datetime.utcnow()}}
    )
    
    order["_id"] = str(result.inserted_id)
    return OrderResponse(**order)


@router.get("/", response_model=List[OrderResponse])
async def get_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get current user's orders"""
    query = {"user_id": current_user.id}
    
    if status:
        query["status"] = status
    
    cursor = orders_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    orders = await cursor.to_list(length=limit)
    
    for order in orders:
        order["_id"] = str(order["_id"])
    
    return [OrderResponse(**order) for order in orders]


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a specific order by ID"""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    order = await orders_collection.find_one({
        "_id": ObjectId(order_id),
        "user_id": current_user.id
    })
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order["_id"] = str(order["_id"])
    return OrderResponse(**order)


@router.get("/tracking/{order_number}", response_model=OrderTracking)
async def track_order(order_number: str):
    """Track order by order number (public endpoint)"""
    order = await orders_collection.find_one({"order_number": order_number})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return OrderTracking(
        order_number=order["order_number"],
        status=order["status"],
        tracking_number=order.get("tracking_number"),
        status_history=order.get("status_history", []),
        created_at=order["created_at"],
        updated_at=order["updated_at"]
    )


# Admin endpoints
@router.get("/admin/all", response_model=List[OrderResponse])
async def get_all_orders_admin(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[OrderStatus] = None,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Get all orders (Admin only)"""
    query = {}
    
    if status:
        query["status"] = status
    
    cursor = orders_collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
    orders = await cursor.to_list(length=limit)
    
    for order in orders:
        order["_id"] = str(order["_id"])
    
    return [OrderResponse(**order) for order in orders]


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    order_update: OrderUpdate,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Update order status (Admin only)"""
    if not ObjectId.is_valid(order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    update_data = order_update.model_dump(exclude_unset=True)
    
    if "status" in update_data:
        # Add to status history
        status_history = order.get("status_history", [])
        status_history.append({
            "status": update_data["status"],
            "timestamp": datetime.utcnow(),
            "note": f"Status updated to {update_data['status']}"
        })
        update_data["status_history"] = status_history
    
    update_data["updated_at"] = datetime.utcnow()
    
    await orders_collection.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": update_data}
    )
    
    updated_order = await orders_collection.find_one({"_id": ObjectId(order_id)})
    updated_order["_id"] = str(updated_order["_id"])
    
    return OrderResponse(**updated_order)
