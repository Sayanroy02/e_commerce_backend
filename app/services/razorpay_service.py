import razorpay
from typing import Optional, Dict, Any
from fastapi import HTTPException
from app.core.config import settings

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def create_razorpay_order(amount: float, currency: str = "INR", receipt: str = None) -> Dict[str, Any]:
    """
    Create a Razorpay order
    
    Args:
        amount: Amount in rupees (will be converted to paise)
        currency: Currency code (default: INR)
        receipt: Order receipt/reference
    
    Returns:
        Razorpay order details
    """
    try:
        # Razorpay expects amount in paise (smallest currency unit)
        amount_in_paise = int(amount * 100)
        
        order_data = {
            "amount": amount_in_paise,
            "currency": currency,
            "receipt": receipt or f"order_{int(amount)}",
            "payment_capture": 1  # Auto capture payment
        }
        
        order = razorpay_client.order.create(data=order_data)
        return order
    
    except razorpay.errors.BadRequestError as e:
        raise HTTPException(status_code=400, detail=f"Razorpay error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Payment service error: {str(e)}")


def verify_razorpay_payment(
    razorpay_order_id: str,
    razorpay_payment_id: str,
    razorpay_signature: str
) -> bool:
    """
    Verify Razorpay payment signature
    
    Args:
        razorpay_order_id: Order ID from Razorpay
        razorpay_payment_id: Payment ID from Razorpay
        razorpay_signature: Signature from Razorpay
    
    Returns:
        True if signature is valid, False otherwise
    """
    try:
        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }
        
        # Verify signature
        razorpay_client.utility.verify_payment_signature(params_dict)
        return True
    
    except razorpay.errors.SignatureVerificationError:
        return False
    except Exception as e:
        print(f"Payment verification error: {e}")
        return False


def fetch_razorpay_payment(payment_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch payment details from Razorpay
    
    Args:
        payment_id: Razorpay payment ID
    
    Returns:
        Payment details or None
    """
    try:
        payment = razorpay_client.payment.fetch(payment_id)
        return payment
    except Exception as e:
        print(f"Error fetching payment: {e}")
        return None


def refund_razorpay_payment(payment_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
    """
    Initiate a refund for a Razorpay payment
    
    Args:
        payment_id: Razorpay payment ID
        amount: Amount to refund (None for full refund)
    
    Returns:
        Refund details
    """
    try:
        refund_data = {}
        if amount is not None:
            refund_data["amount"] = int(amount * 100)  # Convert to paise
        
        refund = razorpay_client.payment.refund(payment_id, refund_data)
        return refund
    
    except razorpay.errors.BadRequestError as e:
        raise HTTPException(status_code=400, detail=f"Refund error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refund service error: {str(e)}")


def capture_razorpay_payment(payment_id: str, amount: float) -> Dict[str, Any]:
    """
    Capture a Razorpay payment (if not auto-captured)
    
    Args:
        payment_id: Razorpay payment ID
        amount: Amount to capture
    
    Returns:
        Captured payment details
    """
    try:
        amount_in_paise = int(amount * 100)
        payment = razorpay_client.payment.capture(payment_id, amount_in_paise)
        return payment
    
    except razorpay.errors.BadRequestError as e:
        raise HTTPException(status_code=400, detail=f"Capture error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Capture service error: {str(e)}")
