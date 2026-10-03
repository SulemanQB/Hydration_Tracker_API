
import logging
import os

from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")

logger = logging.getLogger(__name__)


def verify_db_connection(uri: str | None = None) -> bool:
    """Return whether MongoDB accepts a connection using the supplied URI."""
    uri = uri or MONGODB_URI or "mongodb://localhost:27017"
    client_test = None
    try:
        client_test = MongoClient(uri, serverSelectionTimeoutMS=3000)
        server_info = client_test.server_info()
        logger.info("Connected to MongoDB %s (status=%s)", server_info["version"], server_info["ok"])
        return True
    except Exception as e:
        logger.error("Could not connect to MongoDB: %s", e)
        return False
    finally:
        if client_test is not None:
            client_test.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    raise SystemExit(0 if verify_db_connection() else 1)