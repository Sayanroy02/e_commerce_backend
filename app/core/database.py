from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

client = AsyncIOMotorClient(settings.MONGODB_URL)
database = client[settings.DATABASE_NAME]

# Collections
users_collection = database.get_collection("users")
products_collection = database.get_collection("products")
carts_collection = database.get_collection("carts")
orders_collection = database.get_collection("orders")
payments_collection = database.get_collection("payments")


async def create_indexes():
    """Create database indexes for better performance"""
    # Users indexes
    await users_collection.create_index("email", unique=True)
    
    # Products indexes
    await products_collection.create_index("name")
    await products_collection.create_index("category")
    
    # Orders indexes
    await orders_collection.create_index("user_id")
    await orders_collection.create_index("order_number", unique=True)
    await orders_collection.create_index("status")
    
    # Carts indexes
    await carts_collection.create_index("user_id", unique=True)
    
    # Payments indexes
    await payments_collection.create_index("order_id")
    await payments_collection.create_index("user_id")
