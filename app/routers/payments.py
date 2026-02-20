from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from bson import ObjectId
from app.schemas.payment import (
    PaymentCreate, PaymentResponse, PaymentStatus, PaymentMethod,
    RazorpayOrderCreate, RazorpayOrderResponse, RazorpayPaymentVerify
)
from app.core.database import payments_collection, orders_collection
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.schemas.user import UserInDB
from app.schemas.order import OrderStatus
from app.services.razorpay_service import (
    create_razorpay_order,
    verify_razorpay_payment,
    fetch_razorpay_payment,
    refund_razorpay_payment
)

router = APIRouter(prefix="/api/payments", tags=["Payments"])


@router.post("/razorpay/create-order", response_model=RazorpayOrderResponse)
async def create_razorpay_payment_order(
    order_data: RazorpayOrderCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Step 1: Create a Razorpay order for payment
    This should be called before opening Razorpay checkout
    """
    # Validate order exists and belongs to user
    if not ObjectId.is_valid(order_data.order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    order = await orders_collection.find_one({
        "_id": ObjectId(order_data.order_id),
        "user_id": current_user.id
    })
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if order amount matches
    if order_data.amount != order["total_amount"]:
        raise HTTPException(
            status_code=400,
            detail="Payment amount does not match order total"
        )
    
    # Create Razorpay order
    razorpay_order = create_razorpay_order(
        amount=order_data.amount,
        currency=order_data.currency,
        receipt=order["order_number"]
    )
    
    # Save payment record
    payment = {
        "order_id": order_data.order_id,
        "user_id": current_user.id,
        "payment_method": PaymentMethod.RAZORPAY,
        "amount": order_data.amount,
        "status": PaymentStatus.CREATED,
        "razorpay_order_id": razorpay_order["id"],
        "razorpay_payment_id": None,
        "transaction_id": razorpay_order["id"],
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await payments_collection.insert_one(payment)
    
    return RazorpayOrderResponse(
        razorpay_order_id=razorpay_order["id"],
        order_id=order_data.order_id,
        amount=order_data.amount / 100,  # Convert paise to rupees
        currency=razorpay_order["currency"],
        status=razorpay_order["status"]
    )


@router.post("/razorpay/verify", response_model=PaymentResponse)
async def verify_razorpay_payment_signature(
    verify_data: RazorpayPaymentVerify,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """
    Step 2: Verify Razorpay payment after successful checkout
    This should be called after user completes payment on Razorpay
    """
    # Verify the payment signature
    is_valid = verify_razorpay_payment(
        verify_data.razorpay_order_id,
        verify_data.razorpay_payment_id,
        verify_data.razorpay_signature
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment signature. Payment verification failed."
        )
    
    # Find payment record
    payment = await payments_collection.find_one({
        "razorpay_order_id": verify_data.razorpay_order_id,
        "user_id": current_user.id
    })
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment record not found")
    
    # Fetch payment details from Razorpay
    razorpay_payment_details = fetch_razorpay_payment(verify_data.razorpay_payment_id)
    
    # Update payment status
    payment_status = PaymentStatus.COMPLETED
    if razorpay_payment_details:
        if razorpay_payment_details["status"] == "captured":
            payment_status = PaymentStatus.CAPTURED
        elif razorpay_payment_details["status"] == "authorized":
            payment_status = PaymentStatus.AUTHORIZED
    
    update_data = {
        "razorpay_payment_id": verify_data.razorpay_payment_id,
        "status": payment_status,
        "transaction_id": verify_data.razorpay_payment_id,
        "updated_at": datetime.utcnow()
    }
    
    await payments_collection.update_one(
        {"_id": payment["_id"]},
        {"$set": update_data}
    )
    
    # Update order status
    await orders_collection.update_one(
        {"_id": ObjectId(payment["order_id"])},
        {
            "$set": {
                "status": OrderStatus.CONFIRMED,
                "updated_at": datetime.utcnow()
            },
            "$push": {
                "status_history": {
                    "status": OrderStatus.CONFIRMED,
                    "timestamp": datetime.utcnow(),
                    "note": "Payment completed via Razorpay"
                }
            }
        }
    )
    
    # Get updated payment
    updated_payment = await payments_collection.find_one({"_id": payment["_id"]})
    updated_payment["_id"] = str(updated_payment["_id"])
    
    return PaymentResponse(**updated_payment)


@router.post("/cash-on-delivery", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_cod_payment(
    payment_data: PaymentCreate,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Create a Cash on Delivery payment"""
    # Validate order
    if not ObjectId.is_valid(payment_data.order_id):
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    order = await orders_collection.find_one({
        "_id": ObjectId(payment_data.order_id),
        "user_id": current_user.id
    })
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Check if payment already exists
    existing_payment = await payments_collection.find_one({
        "order_id": payment_data.order_id,
        "status": {"$in": [PaymentStatus.COMPLETED, PaymentStatus.CAPTURED]}
    })
    
    if existing_payment:
        raise HTTPException(
            status_code=400,
            detail="Payment already completed for this order"
        )
    
    # Validate amount
    if payment_data.amount != order["total_amount"]:
        raise HTTPException(
            status_code=400,
            detail="Payment amount does not match order total"
        )
    
    payment = {
        "order_id": payment_data.order_id,
        "user_id": current_user.id,
        "payment_method": PaymentMethod.CASH_ON_DELIVERY,
        "amount": payment_data.amount,
        "status": PaymentStatus.PENDING,
        "transaction_id": f"COD-{order['order_number']}",
        "razorpay_order_id": None,
        "razorpay_payment_id": None,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await payments_collection.insert_one(payment)
    
    # Update order status
    await orders_collection.update_one(
        {"_id": ObjectId(payment_data.order_id)},
        {
            "$set": {
                "status": OrderStatus.CONFIRMED,
                "updated_at": datetime.utcnow()
            },
            "$push": {
                "status_history": {
                    "status": OrderStatus.CONFIRMED,
                    "timestamp": datetime.utcnow(),
                    "note": "Cash on Delivery selected"
                }
            }
        }
    )
    
    payment["_id"] = str(result.inserted_id)
    return PaymentResponse(**payment)


@router.get("/", response_model=List[PaymentResponse])
async def get_payments(
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get current user's payments"""
    cursor = payments_collection.find({"user_id": current_user.id}).sort("created_at", -1)
    payments = await cursor.to_list(length=100)
    
    for payment in payments:
        payment["_id"] = str(payment["_id"])
    
    return [PaymentResponse(**payment) for payment in payments]


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get a specific payment by ID"""
    if not ObjectId.is_valid(payment_id):
        raise HTTPException(status_code=400, detail="Invalid payment ID")
    
    payment = await payments_collection.find_one({
        "_id": ObjectId(payment_id),
        "user_id": current_user.id
    })
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    payment["_id"] = str(payment["_id"])
    return PaymentResponse(**payment)


@router.get("/order/{order_id}", response_model=List[PaymentResponse])
async def get_payments_by_order(
    order_id: str,
    current_user: UserInDB = Depends(get_current_active_user)
):
    """Get payments for a specific order"""
    cursor = payments_collection.find({
        "order_id": order_id,
        "user_id": current_user.id
    })
    payments = await cursor.to_list(length=100)
    
    for payment in payments:
        payment["_id"] = str(payment["_id"])
    
    return [PaymentResponse(**payment) for payment in payments]


# Admin endpoints
@router.get("/admin/all", response_model=List[PaymentResponse])
async def get_all_payments_admin(
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Get all payments (Admin only)"""
    cursor = payments_collection.find({}).sort("created_at", -1)
    payments = await cursor.to_list(length=1000)
    
    for payment in payments:
        payment["_id"] = str(payment["_id"])
    
    return [PaymentResponse(**payment) for payment in payments]


@router.post("/admin/refund/{payment_id}")
async def refund_payment(
    payment_id: str,
    amount: float = None,
    current_admin: UserInDB = Depends(get_current_admin_user)
):
    """Refund a payment (Admin only)"""
    if not ObjectId.is_valid(payment_id):
        raise HTTPException(status_code=400, detail="Invalid payment ID")
    
    payment = await payments_collection.find_one({"_id": ObjectId(payment_id)})
    
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment["status"] != PaymentStatus.COMPLETED and payment["status"] != PaymentStatus.CAPTURED:
        raise HTTPException(
            status_code=400,
            detail="Can only refund completed/captured payments"
        )
    
    # Process refund based on payment method
    if payment["payment_method"] == PaymentMethod.RAZORPAY:
        if not payment.get("razorpay_payment_id"):
            raise HTTPException(status_code=400, detail="Razorpay payment ID not found")
        
        refund = refund_razorpay_payment(
            payment["razorpay_payment_id"],
            amount
        )
        
        # Update payment status
        await payments_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {
                "$set": {
                    "status": PaymentStatus.REFUNDED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Refund initiated successfully",
            "refund_id": refund["id"],
            "amount": refund["amount"] / 100,
            "status": refund["status"]
        }
    
    else:
        # For COD or other methods
        await payments_collection.update_one(
            {"_id": ObjectId(payment_id)},
            {
                "$set": {
                    "status": PaymentStatus.REFUNDED,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return {
            "message": "Payment marked as refunded",
            "payment_id": payment_id
        }
