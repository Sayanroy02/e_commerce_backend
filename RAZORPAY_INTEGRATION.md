# Razorpay Integration Guide

Complete guide for integrating Razorpay payment gateway with the Ecommerce API.

## 🏦 Why Razorpay?

Razorpay is India's leading payment gateway supporting:
- ✅ All major credit/debit cards
- ✅ UPI (Google Pay, PhonePe, Paytm, etc.)
- ✅ Net Banking (all major banks)
- ✅ Wallets (Paytm, Mobikwik, etc.)
- ✅ EMI options
- ✅ International payments
- ✅ Automatic payment reconciliation

## 🚀 Setup

### Step 1: Create Razorpay Account

1. Go to https://razorpay.com
2. Sign up for a free account
3. Complete KYC verification (for production)
4. Navigate to Settings → API Keys

### Step 2: Get API Keys

**Test Mode Keys (for development):**
- Key ID: `rzp_test_xxxxxxxxxxxxxxxx`
- Key Secret: `xxxxxxxxxxxxxxxxxxxxxxxx`

**Live Mode Keys (for production):**
- Key ID: `rzp_live_xxxxxxxxxxxxxxxx`
- Key Secret: `xxxxxxxxxxxxxxxxxxxxxxxx`

### Step 3: Configure Environment

Update your `.env` file:

```env
# Razorpay Configuration
RAZORPAY_KEY_ID=rzp_test_your_key_id_here
RAZORPAY_KEY_SECRET=your_secret_key_here
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret
```

### Step 4: Install Dependencies

```bash
pip install razorpay
```

## 🔄 Payment Flow

### Overview

```
Customer → Create Order → Create Razorpay Order → Open Checkout
         ↓
    Complete Payment on Razorpay
         ↓
    Verify Payment Signature → Mark as Paid → Confirm Order
```

### Detailed Flow

1. **Customer places order** → Order created in database (status: PENDING)
2. **Create Razorpay order** → API creates Razorpay order and returns order_id
3. **Open Razorpay checkout** → Flutter app opens Razorpay checkout with order_id
4. **Customer pays** → Razorpay processes payment
5. **Verify signature** → API verifies Razorpay signature to prevent tampering
6. **Update status** → Order status → CONFIRMED, Payment status → COMPLETED

## 📡 API Endpoints

### 1. Create Razorpay Order

**Endpoint:** `POST /api/payments/razorpay/create-order`

**When to call:** After customer creates an order, before opening Razorpay checkout

**Request:**
```json
{
  "order_id": "65abc123def456",
  "amount": 999.99,
  "currency": "INR"
}
```

**Response:**
```json
{
  "razorpay_order_id": "order_M1a2b3C4d5E6f7",
  "order_id": "65abc123def456",
  "amount": 999.99,
  "currency": "INR",
  "status": "created"
}
```

**cURL Example:**
```bash
curl -X POST "http://localhost:8000/api/payments/razorpay/create-order" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": "65abc123def456",
    "amount": 999.99,
    "currency": "INR"
  }'
```

### 2. Verify Payment

**Endpoint:** `POST /api/payments/razorpay/verify`

**When to call:** After customer completes payment on Razorpay checkout

**Request:**
```json
{
  "order_id": "65abc123def456",
  "razorpay_order_id": "order_M1a2b3C4d5E6f7",
  "razorpay_payment_id": "pay_X1y2Z3a4B5c6D7",
  "razorpay_signature": "signature_string_here"
}
```

**Response:**
```json
{
  "id": "65xyz789abc123",
  "order_id": "65abc123def456",
  "user_id": "65user123",
  "payment_method": "razorpay",
  "amount": 999.99,
  "status": "completed",
  "razorpay_order_id": "order_M1a2b3C4d5E6f7",
  "razorpay_payment_id": "pay_X1y2Z3a4B5c6D7",
  "transaction_id": "pay_X1y2Z3a4B5c6D7",
  "created_at": "2024-02-20T10:30:00",
  "updated_at": "2024-02-20T10:31:00"
}
```

### 3. Cash on Delivery

**Endpoint:** `POST /api/payments/cash-on-delivery`

**Request:**
```json
{
  "order_id": "65abc123def456",
  "payment_method": "cash_on_delivery",
  "amount": 999.99
}
```

## 📱 Flutter Integration

### Step 1: Add Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  razorpay_flutter: ^1.3.6
  http: ^1.1.0
```

### Step 2: Complete Payment Service

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:razorpay_flutter/razorpay_flutter.dart';
import 'package:flutter/material.dart';

class PaymentService {
  final String baseUrl = 'http://localhost:8000';
  final String razorpayKeyId = 'rzp_test_your_key_id';
  final String userToken;
  
  late Razorpay _razorpay;
  
  PaymentService({required this.userToken}) {
    _razorpay = Razorpay();
    _razorpay.on(Razorpay.EVENT_PAYMENT_SUCCESS, _handlePaymentSuccess);
    _razorpay.on(Razorpay.EVENT_PAYMENT_ERROR, _handlePaymentError);
    _razorpay.on(Razorpay.EVENT_EXTERNAL_WALLET, _handleExternalWallet);
  }
  
  // Step 1: Create Razorpay order
  Future<Map<String, dynamic>> createRazorpayOrder({
    required String orderId,
    required double amount,
  }) async {
    final url = Uri.parse('$baseUrl/api/payments/razorpay/create-order');
    
    final response = await http.post(
      url,
      headers: {
        'Authorization': 'Bearer $userToken',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'order_id': orderId,
        'amount': amount,
        'currency': 'INR',
      }),
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Failed to create Razorpay order: ${response.body}');
    }
  }
  
  // Step 2: Open Razorpay checkout
  void openCheckout({
    required String razorpayOrderId,
    required double amount,
    required String orderId,
    required String userName,
    required String userEmail,
    required String userPhone,
  }) {
    var options = {
      'key': razorpayKeyId,
      'amount': (amount * 100).toInt(), // Amount in paise
      'order_id': razorpayOrderId,
      'name': 'Your Store Name',
      'description': 'Order Payment',
      'prefill': {
        'contact': userPhone,
        'email': userEmail,
        'name': userName,
      },
      'theme': {
        'color': '#3399cc'
      },
      'retry': {'enabled': true, 'max_count': 3},
      'send_sms_hash': true,
      'remember_customer': true,
      'modal': {
        'ondismiss': () {
          print('Checkout dismissed');
        }
      }
    };
    
    try {
      _razorpay.open(options);
    } catch (e) {
      print('Error opening Razorpay: $e');
    }
  }
  
  // Step 3: Handle payment success
  Future<void> _handlePaymentSuccess(PaymentSuccessResponse response) async {
    print('Payment Success: ${response.paymentId}');
    
    // Verify payment on backend
    await verifyPayment(
      orderId: response.orderId ?? '',
      razorpayOrderId: response.orderId ?? '',
      razorpayPaymentId: response.paymentId ?? '',
      razorpaySignature: response.signature ?? '',
    );
  }
  
  void _handlePaymentError(PaymentFailureResponse response) {
    print('Payment Error: ${response.code} - ${response.message}');
  }
  
  void _handleExternalWallet(ExternalWalletResponse response) {
    print('External Wallet: ${response.walletName}');
  }
  
  // Step 4: Verify payment signature
  Future<Map<String, dynamic>> verifyPayment({
    required String orderId,
    required String razorpayOrderId,
    required String razorpayPaymentId,
    required String razorpaySignature,
  }) async {
    final url = Uri.parse('$baseUrl/api/payments/razorpay/verify');
    
    final response = await http.post(
      url,
      headers: {
        'Authorization': 'Bearer $userToken',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'order_id': orderId,
        'razorpay_order_id': razorpayOrderId,
        'razorpay_payment_id': razorpayPaymentId,
        'razorpay_signature': razorpaySignature,
      }),
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Payment verification failed: ${response.body}');
    }
  }
  
  void dispose() {
    _razorpay.clear();
  }
}
```

### Step 3: Complete Flutter UI Example

```dart
class CheckoutScreen extends StatefulWidget {
  final String orderId;
  final double totalAmount;
  
  const CheckoutScreen({
    required this.orderId,
    required this.totalAmount,
  });
  
  @override
  _CheckoutScreenState createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  late PaymentService _paymentService;
  bool _isProcessing = false;
  String _selectedPaymentMethod = 'razorpay';
  
  @override
  void initState() {
    super.initState();
    _paymentService = PaymentService(userToken: 'YOUR_USER_TOKEN');
  }
  
  @override
  void dispose() {
    _paymentService.dispose();
    super.dispose();
  }
  
  Future<void> _processRazorpayPayment() async {
    setState(() => _isProcessing = true);
    
    try {
      // Step 1: Create Razorpay order on backend
      final razorpayOrder = await _paymentService.createRazorpayOrder(
        orderId: widget.orderId,
        amount: widget.totalAmount,
      );
      
      // Step 2: Open Razorpay checkout
      _paymentService.openCheckout(
        razorpayOrderId: razorpayOrder['razorpay_order_id'],
        amount: widget.totalAmount,
        orderId: widget.orderId,
        userName: 'John Doe',
        userEmail: 'john@example.com',
        userPhone: '9876543210',
      );
      
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isProcessing = false);
    }
  }
  
  Future<void> _processCODPayment() async {
    setState(() => _isProcessing = true);
    
    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/payments/cash-on-delivery'),
        headers: {
          'Authorization': 'Bearer YOUR_TOKEN',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'order_id': widget.orderId,
          'payment_method': 'cash_on_delivery',
          'amount': widget.totalAmount,
        }),
      );
      
      if (response.statusCode == 201) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Order placed! Pay on delivery.')),
        );
        Navigator.popUntil(context, (route) => route.isFirst);
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isProcessing = false);
    }
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Payment')),
      body: Column(
        children: [
          // Order Summary
          Container(
            padding: EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Order Total', 
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                SizedBox(height: 8),
                Text('₹${widget.totalAmount.toStringAsFixed(2)}',
                  style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
          
          Divider(),
          
          // Payment Methods
          RadioListTile(
            title: Text('Razorpay (Cards, UPI, Net Banking)'),
            subtitle: Text('Pay online securely'),
            value: 'razorpay',
            groupValue: _selectedPaymentMethod,
            onChanged: (value) {
              setState(() => _selectedPaymentMethod = value as String);
            },
          ),
          
          RadioListTile(
            title: Text('Cash on Delivery'),
            subtitle: Text('Pay when you receive'),
            value: 'cod',
            groupValue: _selectedPaymentMethod,
            onChanged: (value) {
              setState(() => _selectedPaymentMethod = value as String);
            },
          ),
          
          Spacer(),
          
          // Pay Button
          Container(
            width: double.infinity,
            padding: EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: _isProcessing ? null : () {
                if (_selectedPaymentMethod == 'razorpay') {
                  _processRazorpayPayment();
                } else {
                  _processCODPayment();
                }
              },
              style: ElevatedButton.styleFrom(
                padding: EdgeInsets.symmetric(vertical: 16),
              ),
              child: _isProcessing
                ? CircularProgressIndicator(color: Colors.white)
                : Text(
                    _selectedPaymentMethod == 'razorpay'
                      ? 'Pay ₹${widget.totalAmount.toStringAsFixed(2)}'
                      : 'Place Order',
                    style: TextStyle(fontSize: 18),
                  ),
            ),
          ),
        ],
      ),
    );
  }
}
```

## 🔒 Security Best Practices

### 1. Never Expose Key Secret

❌ **NEVER** include Razorpay Key Secret in Flutter app
✅ **ALWAYS** keep it on backend only

```dart
// ❌ WRONG - Don't do this!
final keySecret = 'your_secret_key';

// ✅ CORRECT - Only use Key ID in Flutter
final keyId = 'rzp_test_xxxxx';
```

### 2. Always Verify Signature

The signature verification step is **critical** to prevent payment tampering. Never skip it!

```dart
// After payment success, ALWAYS verify on backend
await verifyPayment(...);
```

### 3. Use HTTPS in Production

```dart
// Production URL should always be HTTPS
final baseUrl = 'https://your-domain.com';
```

## 🧪 Testing

### Test Cards

Razorpay provides test cards for development:

**Successful Payment:**
- Card: 4111 1111 1111 1111
- CVV: Any 3 digits
- Expiry: Any future date

**Failed Payment:**
- Card: 4000 0000 0000 0002
- CVV: Any 3 digits
- Expiry: Any future date

### Test UPI

- UPI ID: success@razorpay
- Result: Payment succeeds

### Testing Flow

1. Use test API keys (rzp_test_xxxx)
2. Create order with small amount (₹1)
3. Use test card numbers
4. Verify payment verification works
5. Check order status updates correctly

## 📊 Razorpay Dashboard

Access your Razorpay dashboard at https://dashboard.razorpay.com to:

- View all transactions
- Download reports
- Manage refunds
- Track settlements
- View analytics
- Set up webhooks

## 🔔 Webhooks (Optional but Recommended)

Webhooks notify your backend about payment events automatically.

### Setup Webhooks

1. Go to Razorpay Dashboard → Settings → Webhooks
2. Add webhook URL: `https://your-domain.com/api/webhooks/razorpay`
3. Select events: `payment.authorized`, `payment.captured`, `payment.failed`
4. Save webhook secret

### Implement Webhook Endpoint

```python
from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib

router = APIRouter()

@router.post("/api/webhooks/razorpay")
async def razorpay_webhook(request: Request):
    # Get webhook signature
    signature = request.headers.get("X-Razorpay-Signature")
    
    # Get request body
    body = await request.body()
    
    # Verify signature
    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    if signature != expected_signature:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # Process webhook
    data = await request.json()
    event = data.get("event")
    
    if event == "payment.captured":
        # Update payment status
        payment_id = data["payload"]["payment"]["entity"]["id"]
        # Update in database
        
    return {"status": "ok"}
```

## 💡 Common Issues

### Issue: "Key ID not set"
**Solution:** Ensure RAZORPAY_KEY_ID is set in .env file

### Issue: "Invalid signature"
**Solution:** Check that you're passing all three parameters correctly:
- razorpay_order_id
- razorpay_payment_id
- razorpay_signature

### Issue: Payment succeeds but order not confirmed
**Solution:** Check that verify endpoint is being called after payment success

### Issue: Amount mismatch
**Solution:** Razorpay expects amount in paise (multiply by 100)

## 🚀 Going Live

### Checklist

- [ ] Complete KYC verification on Razorpay
- [ ] Switch to Live API keys (rzp_live_xxxx)
- [ ] Update .env with live keys
- [ ] Test with real transactions (small amounts)
- [ ] Set up webhooks for production
- [ ] Enable 3D Secure for cards
- [ ] Configure settlement schedule
- [ ] Set up email notifications
- [ ] Test refund flow
- [ ] Monitor first few transactions

### Production Best Practices

1. Use environment variables for all keys
2. Enable logging for payment failures
3. Implement retry logic for network failures
4. Show clear error messages to users
5. Handle edge cases (network timeout, app close, etc.)
6. Implement order status polling as backup
7. Test thoroughly before launch

## 📚 Additional Resources

- Razorpay Documentation: https://razorpay.com/docs/
- Flutter Plugin: https://pub.dev/packages/razorpay_flutter
- Payment Gateway Guide: https://razorpay.com/docs/payments/
- API Reference: https://razorpay.com/docs/api/

---

**Questions or issues?** Check the Razorpay docs or contact their support team.
