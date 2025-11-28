from fastapi import APIRouter, HTTPException, status
from typing import List
from schemas.models import HospitalEventSchema, SocialPostSchema, EnvironmentDataSchema
from core.database import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ingest", tags=["Data Ingestion"])


@router.post("/hospital", status_code=status.HTTP_201_CREATED)
async def ingest_hospital_event(event: HospitalEventSchema):
    """
    Ingest hospital event data
    
    Args:
        event: Hospital event data including location, symptoms, patient count
        
    Returns:
        Inserted document ID
    """
    try:
        event_dict = event.model_dump()
        
        # Ensure timestamp is datetime
        if isinstance(event_dict.get('timestamp'), str):
            event_dict['timestamp'] = datetime.fromisoformat(event_dict['timestamp'])
        
        result = db.get_collection("hospital_events").insert_one(event_dict)
        
        logger.info(f"Hospital event ingested: {result.inserted_id} from {event.hospital_name}")
        
        return {
            "status": "success",
            "id": str(result.inserted_id),
            "message": "Hospital event ingested successfully"
        }
    except Exception as e:
        logger.error(f"Error ingesting hospital event: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest hospital event: {str(e)}"
        )


@router.post("/hospital/batch", status_code=status.HTTP_201_CREATED)
async def ingest_hospital_events_batch(events: List[HospitalEventSchema]):
    """
    Ingest multiple hospital events at once
    
    Args:
        events: List of hospital event data
        
    Returns:
        Number of inserted documents
    """
    try:
        events_dict = [event.model_dump() for event in events]
        
        # Ensure timestamps are datetime
        for event_dict in events_dict:
            if isinstance(event_dict.get('timestamp'), str):
                event_dict['timestamp'] = datetime.fromisoformat(event_dict['timestamp'])
        
        result = db.get_collection("hospital_events").insert_many(events_dict)
        
        logger.info(f"Batch ingested {len(result.inserted_ids)} hospital events")
        
        return {
            "status": "success",
            "count": len(result.inserted_ids),
            "message": f"Ingested {len(result.inserted_ids)} hospital events"
        }
    except Exception as e:
        logger.error(f"Error in batch hospital ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest hospital events: {str(e)}"
        )


@router.post("/social", status_code=status.HTTP_201_CREATED)
async def ingest_social_post(post: SocialPostSchema):
    """
    Ingest social media post data
    
    Args:
        post: Social media post with location, text, extracted keywords
        
    Returns:
        Inserted document ID
    """
    try:
        post_dict = post.model_dump()
        
        # Ensure timestamp is datetime
        if isinstance(post_dict.get('timestamp'), str):
            post_dict['timestamp'] = datetime.fromisoformat(post_dict['timestamp'])
        
        result = db.get_collection("social_posts").insert_one(post_dict)
        
        logger.info(f"Social post ingested: {result.inserted_id} from {post.platform}")
        
        return {
            "status": "success",
            "id": str(result.inserted_id),
            "message": "Social post ingested successfully"
        }
    except Exception as e:
        logger.error(f"Error ingesting social post: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest social post: {str(e)}"
        )


@router.post("/social/batch", status_code=status.HTTP_201_CREATED)
async def ingest_social_posts_batch(posts: List[SocialPostSchema]):
    """
    Ingest multiple social media posts at once
    
    Args:
        posts: List of social media posts
        
    Returns:
        Number of inserted documents
    """
    try:
        posts_dict = [post.model_dump() for post in posts]
        
        # Ensure timestamps are datetime
        for post_dict in posts_dict:
            if isinstance(post_dict.get('timestamp'), str):
                post_dict['timestamp'] = datetime.fromisoformat(post_dict['timestamp'])
        
        result = db.get_collection("social_posts").insert_many(posts_dict)
        
        logger.info(f"Batch ingested {len(result.inserted_ids)} social posts")
        
        return {
            "status": "success",
            "count": len(result.inserted_ids),
            "message": f"Ingested {len(result.inserted_ids)} social posts"
        }
    except Exception as e:
        logger.error(f"Error in batch social ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest social posts: {str(e)}"
        )


@router.post("/environment", status_code=status.HTTP_201_CREATED)
async def ingest_environment_data(data: EnvironmentDataSchema):
    """
    Ingest environmental data
    
    Args:
        data: Environmental data including temperature, humidity, mosquito index
        
    Returns:
        Inserted document ID
    """
    try:
        data_dict = data.model_dump()
        
        # Ensure timestamp is datetime
        if isinstance(data_dict.get('timestamp'), str):
            data_dict['timestamp'] = datetime.fromisoformat(data_dict['timestamp'])
        
        result = db.get_collection("environment_data").insert_one(data_dict)
        
        logger.info(f"Environment data ingested: {result.inserted_id}")
        
        return {
            "status": "success",
            "id": str(result.inserted_id),
            "message": "Environment data ingested successfully"
        }
    except Exception as e:
        logger.error(f"Error ingesting environment data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest environment data: {str(e)}"
        )


@router.post("/environment/batch", status_code=status.HTTP_201_CREATED)
async def ingest_environment_data_batch(data_list: List[EnvironmentDataSchema]):
    """
    Ingest multiple environmental data points at once
    
    Args:
        data_list: List of environmental data
        
    Returns:
        Number of inserted documents
    """
    try:
        data_dict_list = [data.model_dump() for data in data_list]
        
        # Ensure timestamps are datetime
        for data_dict in data_dict_list:
            if isinstance(data_dict.get('timestamp'), str):
                data_dict['timestamp'] = datetime.fromisoformat(data_dict['timestamp'])
        
        result = db.get_collection("environment_data").insert_many(data_dict_list)
        
        logger.info(f"Batch ingested {len(result.inserted_ids)} environment data points")
        
        return {
            "status": "success",
            "count": len(result.inserted_ids),
            "message": f"Ingested {len(result.inserted_ids)} environment data points"
        }
    except Exception as e:
        logger.error(f"Error in batch environment ingestion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest environment data: {str(e)}"
        )
