import logging
import bcrypt
from src.models.user import User, CreateUser
from database.database import db
from bson import ObjectId
from fastapi import HTTPException
from typing import List, Optional

logger = logging.getLogger("hydration_tracker.schemas")

class UserSchema():
    """Schema for user operations with enhanced security"""
    
    @staticmethod
    def hash_password(password: str) -> bytes:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt)
    
    @staticmethod
    def verify_password(password: str, hashed_password: bytes) -> bool:
        """Verify a password against a hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password)
    
    @staticmethod
    def user_serializer(user) -> User:
        """Convert MongoDB user document to User model"""
        user_id = str(user["_id"])
        return User(id=user_id, 
                    name=user["name"], 
                    weight=user["weight"])
    
    @db.retry_operation()
    def users_serializer(self, users) -> List[User]:
        """Convert multiple MongoDB user documents to User models"""
        return [self.user_serializer(user) for user in users]
    
    @db.retry_operation()
    def create_user(self, user: CreateUser) -> User:
        """Create a new user in the database"""
        try:
            # Create user data object
            user_data = {
                "name": user.name,
                "weight": user.weight,
                # Add hashed password field for future authentication
                # "password": self.hash_password("default_password")
            }
            
            # Insert user into database
            user_id = db.users.insert_one(user_data).inserted_id
            
            # Create User model with ID
            user_with_id = user.dict()
            user_with_id["id"] = str(user_id)
            
            logger.info(f"Created new user: {user.name} (ID: {user_id})")
            return User(**user_with_id)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create user")

    @db.retry_operation()
    def get_user(self, user_id: str) -> User:
        """Get a user by ID"""
        try:
            # Validate ObjectId
            if not ObjectId.is_valid(user_id):
                raise HTTPException(status_code=400, detail="Invalid user ID format")
                
            # Find user in database
            user = db.users.find_one({"_id": ObjectId(user_id)})
            
            if user is None:
                logger.warning(f"User not found: {user_id}")
                raise HTTPException(status_code=404, detail="User not found")
                
            return self.user_serializer(user)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve user")
            
    @db.retry_operation()
    def update_user(self, user_id: str, update_data: dict) -> User:
        """Update a user's information"""
        try:
            # Validate ObjectId
            if not ObjectId.is_valid(user_id):
                raise HTTPException(status_code=400, detail="Invalid user ID format")
            
            # Validate update data
            allowed_fields = ["name", "weight"]
            update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}
            
            if not update_fields:
                raise HTTPException(status_code=400, detail="No valid fields to update")
                
            # Update user in database
            result = db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_fields}
            )
            
            if result.matched_count == 0:
                raise HTTPException(status_code=404, detail="User not found")
                
            # Get updated user
            updated_user = db.users.find_one({"_id": ObjectId(user_id)})
            
            logger.info(f"Updated user {user_id}: {update_fields.keys()}")
            return self.user_serializer(updated_user)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update user")
            
    @db.retry_operation()
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            # Validate ObjectId
            if not ObjectId.is_valid(user_id):
                raise HTTPException(status_code=400, detail="Invalid user ID format")
                
            # Delete user from database
            result = db.users.delete_one({"_id": ObjectId(user_id)})
            
            if result.deleted_count == 0:
                raise HTTPException(status_code=404, detail="User not found")
                
            # Also delete user's trackers
            db.trackers.delete_many({"id_owner": user_id})
            
            logger.info(f"Deleted user: {user_id}")
            return True
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to delete user")