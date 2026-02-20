from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from bson import ObjectId
from app.core.database import orders_collection, payments_collection, users_collection, products_collection
from app.core.dependencies import get_current_admin_user
from app.schemas.user import UserInDB
from app.schemas.order import OrderStatus
from app.schemas.payment import PaymentStatus

router = APIRouter(prefix="/api/admin", tags=["Admin"])


@router.get("/dashboard")
async def get_dashboard_stats(current_admin: UserInDB = Depends(get_current_admin_user)):
    """Get dashboard statistics (Admin only)"""
    # Total counts
    total_users = await users_collection.count_documents({"role": "customer"})
    total_products = await products_collection.count_documents({"is_active": True})
    total_orders = await orders_collection.count_documents({})
    
    # Orders by status
    pending_orders = await orders_collection.count_documents({"status": OrderStatus.PENDING})
    confirmed_orders = await orders_collection.count_documents({"status": OrderStatus.CONFIRMED})
    processing_orders = await orders_collection.count_documents({"status": OrderStatus.PROCESSING})
    shipped_orders = await orders_collection.count_documents({"status": OrderStatus.SHIPPED})
    delivered_orders = await orders_collection.count_documents({"status": OrderStatus.DELIVERED})
    cancelled_orders = await orders_collection.count_documents({"status": OrderStatus.CANCELLED})
    
    # Revenue statistics
    pipeline = [
        {
            "$match": {
                "status": PaymentStatus.COMPLETED
            }
        },
        {
            "$group": {
                "_id": None,
                "total_revenue": {"$sum": "$amount"}
            }
        }
    ]
    
    revenue_result = await payments_collection.aggregate(pipeline).to_list(1)
    total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
    
    # Recent orders (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    recent_orders = await orders_collection.count_documents({
        "created_at": {"$gte": seven_days_ago}
    })
    
    # Top selling products
    top_products_pipeline = [
        {"$unwind": "$items"},
        {
            "$group": {
                "_id": "$items.product_id",
                "product_name": {"$first": "$items.product_name"},
                "total_quantity": {"$sum": "$items.quantity"},
                "total_revenue": {"$sum": "$items.subtotal"}
            }
        },
        {"$sort": {"total_quantity": -1}},
        {"$limit": 10}
    ]
    
    top_products = await orders_collection.aggregate(top_products_pipeline).to_list(10)
    
    return {
        "overview": {
            "total_users": total_users,
            "total_products": total_products,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "recent_orders_7_days": recent_orders
        },
        "orders_by_status": {
            "pending": pending_orders,
            "confirmed": confirmed_orders,
            "processing": processing_orders,
            "shipped": shipped_orders,
            "delivered": delivered_orders,
            "cancelled": cancelled_orders
        },
        "top_selling_products": top_products
    }


@router.get("/analytics/revenue")
async def get_revenue_analytics(
    days: int = 30,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Get revenue analytics for the last N days (Admin only)"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {
            "$match": {
                "status": PaymentStatus.COMPLETED,
                "created_at": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "daily_revenue": {"$sum": "$amount"},
                "transaction_count": {"$sum": 1}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    daily_revenue = await payments_collection.aggregate(pipeline).to_list(days)
    
    return {
        "period_days": days,
        "daily_revenue": daily_revenue
    }


@router.get("/analytics/orders")
async def get_order_analytics(
    days: int = 30,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Get order analytics for the last N days (Admin only)"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    pipeline = [
        {
            "$match": {
                "created_at": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": "$created_at"
                    }
                },
                "order_count": {"$sum": 1},
                "total_value": {"$sum": "$total_amount"}
            }
        },
        {"$sort": {"_id": 1}}
    ]
    
    daily_orders = await orders_collection.aggregate(pipeline).to_list(days)
    
    return {
        "period_days": days,
        "daily_orders": daily_orders
    }
