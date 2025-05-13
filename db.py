from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List, Dict, Optional
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
client = None
db = None
keycaps_collection = None
scrapes_collection = None  # New collection for storing scrape results

def init_db(uri: str = None) -> bool:
    """Initialize MongoDB connection and get the collections."""
    global client, db, keycaps_collection, scrapes_collection
    try:
        if uri is None:
            uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
        
        logger.info(f"Connecting to MongoDB at {uri}")
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            connectTimeoutMS=5000,
            socketTimeoutMS=5000,
            maxPoolSize=1,
            retryWrites=True
        )
        
        # Test the connection
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        
        # Get or create database
        db = client.keycapvault
        logger.info(f"Using database: {db.name}")
        
        # Ensure collections exist
        collections = db.list_collection_names()
        logger.info(f"Existing collections: {collections}")
        
        if 'keycaps' not in collections:
            logger.info("Creating keycaps collection")
            db.create_collection('keycaps')
        if 'scrapes' not in collections:
            logger.info("Creating scrapes collection")
            db.create_collection('scrapes')
        
        keycaps_collection = db.keycaps
        scrapes_collection = db.scrapes
        
        # Ensure indexes
        keycaps_collection.create_index("vendor")
        keycaps_collection.create_index("name")
        scrapes_collection.create_index([("scraped_at", -1)])  # Index for latest scrape
        
        logger.info("Database initialization complete")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB connection: {str(e)}")
        return False

def is_connected() -> bool:
    """Check if the database connection is active."""
    try:
        if client is None:
            return False
        client.admin.command('ping')
        return True
    except:
        return False

def ensure_connection():
    """Ensure database connection is active, attempt to reconnect if not."""
    if not is_connected():
        logger.warning("Database connection lost, attempting to reconnect...")
        return init_db()
    return True

def store_scrape_results(products: List[Dict]) -> bool:
    """Store scrape results with timestamp."""
    if not ensure_connection():
        raise ConnectionError("Database connection failed")
    
    try:
        logger.info(f"Attempting to store {len(products)} products")
        
        # Extract only essential data for comparison
        simplified_products = [{
            "name": product["name"],
            "batch": product["batch"],
            "price": product["price"],
            "image_url": product["image_url"]
        } for product in products]
        
        # Create a scrape record with timestamp and products
        scrape_data = {
            "scraped_at": datetime.utcnow(),
            "products": simplified_products
        }
        
        # Store the scrape results
        result = scrapes_collection.insert_one(scrape_data)
        logger.info(f"Successfully stored scrape results with ID: {result.inserted_id}")
        
        # Verify the data was stored
        stored_count = scrapes_collection.count_documents({"_id": result.inserted_id})
        if stored_count == 1:
            logger.info("Verified data was stored successfully")
            return True
        else:
            logger.error("Failed to verify data storage")
            return False
    except Exception as e:
        logger.error(f"Error storing scrape results: {str(e)}")
        raise

def compare_with_collection() -> Dict[str, List[Dict]]:
    """Compare scraped items with collection and return matches/missing items."""
    if not ensure_connection():
        raise ConnectionError("Database connection failed")
    
    try:
        # Get latest scrape results
        latest_scrape = scrapes_collection.find_one(sort=[("scraped_at", -1)])
        logger.info(f"Latest scrape found: {latest_scrape is not None}")
        
        if not latest_scrape:
            logger.info("No scrape results found")
            return {"matches": [], "missing": []}
        
        # Get collection items
        collection_items = list(keycaps_collection.find({}, {"name": 1}))
        logger.info(f"Found {len(collection_items)} items in collection")
        logger.info(f"Collection items: {collection_items}")
        
        collection_names = {item["name"].lower() for item in collection_items}
        logger.info(f"Collection names (lowercase): {collection_names}")
        
        # Compare items
        matches = []
        missing = []
        
        for product in latest_scrape["products"]:
            product_name = product["name"].lower()
            logger.info(f"Comparing product: {product_name}")
            
            if product_name in collection_names:
                logger.info(f"Match found for: {product_name}")
                matches.append(product)
            else:
                logger.info(f"No match found for: {product_name}")
                missing.append(product)
        
        logger.info(f"Found {len(matches)} matches and {len(missing)} missing items")
        logger.info(f"Matches: {matches}")
        logger.info(f"Missing: {missing}")
        
        return {
            "matches": matches,
            "missing": missing
        }
    except Exception as e:
        logger.error(f"Error comparing items: {str(e)}")
        logger.exception("Full traceback:")
        raise

def get_latest_scrape() -> List[Dict]:
    """Get the most recent scrape results."""
    if not ensure_connection():
        raise ConnectionError("Database connection failed")
    
    try:
        # Find the most recent scrape
        latest_scrape = scrapes_collection.find_one(
            sort=[("scraped_at", -1)]
        )
        
        if latest_scrape:
            logger.info(f"Retrieved latest scrape from {latest_scrape['scraped_at']}")
            return latest_scrape["products"]
        else:
            logger.info("No previous scrape results found")
            return []
    except Exception as e:
        logger.error(f"Error retrieving latest scrape: {str(e)}")
        raise

def add_keycap(data: Dict) -> str:
    """Add a new keycap to the collection."""
    if not ensure_connection():
        raise ConnectionError("Database connection failed")
    
    try:
        result = keycaps_collection.insert_one(data)
        return str(result.inserted_id)
    except Exception as e:
        logger.error(f"Error adding keycap: {str(e)}")
        raise

def get_keycaps(vendor: Optional[str] = None) -> List[Dict]:
    """Get all keycaps, optionally filtered by vendor."""
    if not ensure_connection():
        raise ConnectionError("Database connection failed")
    
    try:
        query = {"vendor": vendor} if vendor else {}
        logger.info(f"Querying keycaps with filter: {query}")
        keycaps = list(keycaps_collection.find(query))
        logger.info(f"Found {len(keycaps)} keycaps")
        return keycaps
    except Exception as e:
        logger.error(f"Error getting keycaps: {str(e)}")
        raise

def update_keycap(keycap_id: str, updates: Dict) -> bool:
    """Update a keycap by ID."""
    if not ensure_connection():
        raise ConnectionError("Database connection failed")
    
    try:
        result = keycaps_collection.update_one(
            {"_id": ObjectId(keycap_id)},
            {"$set": updates}
        )
        return result.modified_count > 0
    except Exception as e:
        logger.error(f"Error updating keycap: {str(e)}")
        raise

def delete_keycap(keycap_id: str) -> bool:
    """Delete a keycap by ID."""
    if not ensure_connection():
        raise ConnectionError("Database connection failed")
    
    try:
        result = keycaps_collection.delete_one({"_id": ObjectId(keycap_id)})
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting keycap: {str(e)}")
        raise
