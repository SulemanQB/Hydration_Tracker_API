import logging
import time
import functools
import contextlib
from typing import Dict, Any, Callable, Optional
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError, PyMongoError
from config.settings import settings

# Configure logging
logger = logging.getLogger("hydration_tracker.database")

# Connection constants
MAX_RETRY_ATTEMPTS = 3
RETRY_DELAY = 2  # seconds

class Database:
    """MongoDB database manager with connection pooling and retries"""
    
    _instance = None
    client = None
    db = None
    
    def __new__(cls):
        """Singleton pattern to ensure only one database connection is created"""
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialize_connection()
        return cls._instance
    
    def _initialize_connection(self):
        """Establish connection to MongoDB with retry logic"""
        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                self.client = MongoClient(
                    settings.MONGODB_URI,
                    maxPoolSize=50,  # Connection pool size
                    connectTimeoutMS=5000,  # Connection timeout
                    serverSelectionTimeoutMS=5000,  # Server selection timeout
                    waitQueueTimeoutMS=5000  # Wait queue timeout
                )
                # Test connection
                server_info = self.client.server_info()
                logger.info(f"Connected to MongoDB (version: {server_info['version']})")
                
                # Set database
                self.db = self.client[settings.DB_NAME]
                
                # Initialize collections and indexes
                self._setup_collections()
                return
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                if attempt == MAX_RETRY_ATTEMPTS:
                    logger.error(f"Failed to connect to MongoDB after {MAX_RETRY_ATTEMPTS} attempts: {str(e)}")
                    raise
                else:
                    logger.warning(f"Connection attempt {attempt} failed, retrying in {RETRY_DELAY} seconds: {str(e)}")
                    time.sleep(RETRY_DELAY)
            except Exception as e:
                logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
                raise
    
    def _setup_collections(self):
        """Set up collections and indexes"""
        # Define collections
        self.users = self.db["users"]
        self.trackers = self.db["trackers"]
        
        # Create indexes for better performance
        self.users.create_index([("name", ASCENDING)])
        self.trackers.create_index([("id_owner", ASCENDING)])
        self.trackers.create_index([("date", DESCENDING)])
        self.trackers.create_index([("id_owner", ASCENDING), ("date", ASCENDING)], unique=True)
        
        logger.info("Database collections and indexes set up successfully")
    
    @contextlib.contextmanager
    def transaction(self):
        """Context manager for MongoDB transactions"""
        with self.client.start_session() as session:
            with session.start_transaction():
                try:
                    yield session
                except Exception as e:
                    logger.error(f"Transaction error: {str(e)}")
                    raise
    
    def retry_operation(self, max_attempts=MAX_RETRY_ATTEMPTS, delay=RETRY_DELAY):
        """Decorator for retrying database operations"""
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                for attempt in range(1, max_attempts + 1):
                    try:
                        return func(*args, **kwargs)
                    except PyMongoError as e:
                        if attempt == max_attempts:
                            logger.error(f"Database operation failed after {max_attempts} attempts: {func.__name__}")
                            raise
                        logger.warning(f"Retrying database operation {func.__name__} ({attempt}/{max_attempts}): {str(e)}")
                        time.sleep(delay)
            return wrapper
        return decorator

# Initialize database
db = Database()

# For backward compatibility
users_collection = db.users
trackers_collection = db.trackers