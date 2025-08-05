import logging
from fastapi import APIRouter, HTTPException, Path, Body, Query
from src.models.hydration_tracker import HydrationTracker, CreateHydrationTracker
from database.schemas.hydration_tracker_schema import HydrationTrackerSchema
from datetime import date, datetime
from typing import List, Optional

logger = logging.getLogger("hydration_tracker.controllers")

router = APIRouter()
schema = HydrationTrackerSchema()

@router.get("/user/{user_id}/tracker/", response_model=HydrationTracker, tags=["tracker"])
async def today_tracker(
    user_id: str = Path(..., description="The ID of the user to get the tracker for")
):
    """
    Get today's hydration tracker for a specific user.
    
    Creates a new tracker for today if one doesn't exist.
    
    Args:
        user_id: The ID of the user to get the tracker for
        
    Returns:
        HydrationTracker: The hydration tracker for today
    """
    try:
        logger.info(f"Getting today's tracker for user: {user_id}")
        return schema.today_tracker(user_id)
    except HTTPException as e:
        logger.warning(f"HTTP error when getting tracker: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when getting today's tracker: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving today's tracker")

@router.get("/user/{user_id}/tracker/{tracker_date}/", response_model=HydrationTracker, tags=["tracker"])
async def get_tracker(
    user_id: str = Path(..., description="The ID of the user to get the tracker for"),
    tracker_date: date = Path(..., description="The date of the tracker to retrieve")
):
    """
    Get a hydration tracker for a specific user on a specific date.
    
    Args:
        user_id: The ID of the user to get the tracker for
        tracker_date: The date of the tracker to retrieve
        
    Returns:
        HydrationTracker: The hydration tracker for the specified date
    """
    try:
        logger.info(f"Getting tracker for user: {user_id} on date: {tracker_date}")
        return schema.get_tracker(user_id, tracker_date)
    except HTTPException as e:
        logger.warning(f"HTTP error when getting tracker: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when getting tracker: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the tracker")

@router.put("/user/{user_id}/tracker/{tracker_date}/", response_model=HydrationTracker, tags=["tracker"])
async def update_tracker_consume(
    user_id: str = Path(..., description="The ID of the user to update the tracker for"),
    tracker_date: date = Path(..., description="The date of the tracker to update"),
    update: dict = Body(..., description="The update data with cup size")
):
    """
    Update a user's hydration consumption for a specific date.
    
    Args:
        user_id: The ID of the user to update the tracker for
        tracker_date: The date of the tracker to update
        update: Dictionary containing the 'cupsize' to add to consumption
        
    Returns:
        HydrationTracker: The updated hydration tracker
    """
    try:
        if 'cupsize' not in update or not isinstance(update['cupsize'], (int, float)) or update['cupsize'] <= 0:
            raise HTTPException(status_code=422, detail="Invalid cupsize value. Must be a positive number.")
            
        logger.info(f"Updating tracker for user: {user_id} on date: {tracker_date} with data: {update}")
        return schema.tracker_update_consume(user_id, tracker_date, update)
    except HTTPException as e:
        logger.warning(f"HTTP error when updating tracker: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when updating tracker: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while updating the tracker")

@router.post("/user/{user_id}/tracker/{tracker_date}/", response_model=HydrationTracker, tags=["tracker"])
async def create_specific_tracker(
    user_id: str = Path(..., description="The ID of the user to create a tracker for"),
    tracker_date: date = Path(..., description="The date for which to create a tracker")
):
    """
    Create a hydration tracker for a specific user on a specific date.
    
    Args:
        user_id: The ID of the user to create a tracker for
        tracker_date: The date for which to create a tracker
        
    Returns:
        HydrationTracker: The newly created hydration tracker
    """
    try:
        if tracker_date > datetime.now().date():
            raise HTTPException(status_code=400, detail="Cannot create tracker for future dates")
            
        logger.info(f"Creating tracker for user: {user_id} on date: {tracker_date}")
        return schema.create_tracker(user_id, tracker_date)
    except HTTPException as e:
        logger.warning(f"HTTP error when creating tracker: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when creating tracker: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the tracker")

@router.get("/user/{user_id}/history/", response_model=List[HydrationTracker], tags=["tracker"])
async def list_trackers(
    user_id: str = Path(..., description="The ID of the user to get trackers for"),
    limit: Optional[int] = Query(None, description="Limit the number of records returned")
):
    """
    Get all hydration trackers for a specific user.
    
    Args:
        user_id: The ID of the user to get trackers for
        limit: Optional limit on the number of records to return
        
    Returns:
        List[HydrationTracker]: A list of all hydration trackers for the user
    """
    try:
        logger.info(f"Getting tracker history for user: {user_id}")
        return schema.get_trackers(user_id, limit)
    except HTTPException as e:
        logger.warning(f"HTTP error when getting tracker history: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error when getting tracker history: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while retrieving the tracker history")
