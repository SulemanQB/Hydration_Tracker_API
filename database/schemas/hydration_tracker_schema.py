import logging
from src.models.hydration_tracker import HydrationTracker
from database.database import trackers_collection, users_collection
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime, date
from typing import List, Optional

logger = logging.getLogger("hydration_tracker.schemas")

class HydrationTrackerSchema():
    
    def verify_last_tracker(self, user_id: str):
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
                
            last_tracker = trackers_collection.find_one({"id_owner": user_id}, sort=[("date", -1)])
            if last_tracker is not None:
                last_tracker["id"] = str(last_tracker["_id"])
                return self.tracker_serializer(last_tracker)
            return None
        except Exception as e:
            logger.error(f"Error verifying last tracker: {str(e)}")
            raise
    
    def create_tracker(self, user_id: str, tracker_date: date) -> HydrationTracker:
        try:
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
                
            tracker_on_date = self.get_tracker(user_id, tracker_date, skip_404=True)
            if tracker_on_date is not None:
                raise HTTPException(status_code=409, detail="Tracker already exists")
                
            if tracker_date > datetime.now().date():
                raise HTTPException(status_code=400, detail="Cannot create tracker for future date")
                
            # Calculate recommended hydration based on weight
            daily_hydration_ml = user["weight"] * 35
            
            tracker = {
                "id_owner": user_id,
                "weight_at_time": user["weight"],
                "date": tracker_date.strftime("%Y-%m-%d"),
                "goal": daily_hydration_ml,
                "missing": daily_hydration_ml,
                "consumed": 0,
                "goal_percent": 0,
                "goal_reached": False,
            }
            
            tracker_id = trackers_collection.insert_one(tracker).inserted_id
            tracker_with_id = tracker.copy()
            tracker_with_id["id"] = str(tracker_id)
            
            logger.info(f"Created new tracker for user {user_id} on date {tracker_date}")
            return self.tracker_serializer(tracker_with_id)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating tracker: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to create tracker")
    
    def today_tracker(self, user_id: str) -> HydrationTracker:
        try:
            last_tracker = self.verify_last_tracker(user_id)
            today = datetime.now().date()
            
            if (last_tracker is None) or (last_tracker.date < today):
                return self.create_tracker(user_id, today)
                
            return last_tracker
        except Exception as e:
            logger.error(f"Error getting today's tracker: {str(e)}")
            raise
    
    def get_tracker(self, user_id: str, tracker_date: date, skip_404: bool = False) -> HydrationTracker:
        try:
            date_str = tracker_date.strftime("%Y-%m-%d")
            tracker = trackers_collection.find_one({"id_owner": user_id, "date": date_str})
            
            if tracker is None:
                if skip_404:
                    return None
                raise HTTPException(status_code=404, detail=f"No tracker found for date {date_str}")
                
            return self.tracker_serializer(tracker)
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting tracker: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve tracker")

    @staticmethod
    def tracker_serializer(tracker) -> HydrationTracker:
        try:
            tracker_id = tracker.get("_id", tracker.get("id"))
            return HydrationTracker(
                id=str(tracker_id),
                id_owner=str(tracker["id_owner"]),
                weight_at_time=tracker["weight_at_time"],
                date=tracker["date"],
                goal=tracker["goal"],
                missing=tracker["missing"],
                consumed=tracker["consumed"],
                goal_percent=tracker["goal_percent"],
                goal_reached=tracker["goal_reached"],
            )
        except Exception as e:
            logger.error(f"Error serializing tracker: {str(e)}")
            raise
        
    def trackers_serializer(self, trackers) -> List[HydrationTracker]:
        return [self.tracker_serializer(tracker) for tracker in trackers]
    
    def tracker_update_consume(self, user_id: str, tracker_date: date, update: dict) -> HydrationTracker:
        try:
            tracker = self.get_tracker(user_id, tracker_date)
            quantity = update.get("cupsize", 0)
            
            if quantity <= 0:
                raise HTTPException(status_code=400, detail="Cup size must be positive")
                
            consumed = tracker.consumed + quantity
            missing = max(0, tracker.missing - quantity)
            goal_reached = missing == 0
            goal_percent = min(100, round((consumed / tracker.goal) * 100, 2))
                
            tracker_data = {
                "id_owner": tracker.id_owner,
                "weight_at_time": tracker.weight_at_time,
                "date": tracker.date.strftime("%Y-%m-%d"),
                "goal": tracker.goal,
                "missing": missing,
                "consumed": consumed,
                "goal_percent": goal_percent,
                "goal_reached": goal_reached,
                "id": tracker.id
            }
            
            trackers_collection.update_one(
                {"_id": ObjectId(tracker.id)}, 
                {"$set": {
                    "missing": missing,
                    "consumed": consumed,
                    "goal_percent": goal_percent,
                    "goal_reached": goal_reached
                }}
            )
            
            logger.info(f"Updated tracker for user {user_id} on {tracker_date}: +{quantity}ml")
            return tracker_data
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error updating tracker consumption: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to update tracker")
        
    def get_trackers(self, user_id: str, limit: Optional[int] = None) -> List[HydrationTracker]:
        try:
            # Validate user exists
            user = users_collection.find_one({"_id": ObjectId(user_id)})
            if user is None:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Build query
            query = {"id_owner": user_id}
            
            # Add limit if provided
            options = {"sort": [("date", -1)]}
            if limit:
                options["limit"] = limit
                
            trackers = trackers_collection.find(query, **options)
            
            result = self.trackers_serializer(trackers)
            logger.info(f"Retrieved {len(result)} trackers for user {user_id}")
            return result
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error retrieving trackers: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve trackers")
