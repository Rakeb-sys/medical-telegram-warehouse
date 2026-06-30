# api/schemas.py
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# 1. Product Discovery Schemas
class TopProductResponse(BaseModel):
    product_keyword: str
    mention_count: int

    class Config:
        from_attributes = True

# 2. Channel Activity Schemas
class ChannelActivityResponse(BaseModel):
    channel_name: str
    post_date: str
    daily_posts: int
    total_views: int
    total_forwards: int

    class Config:
        from_attributes = True

# 3. Message Search Schemas
class MessageSearchResponse(BaseModel):
    message_id: int
    channel_name: str
    message_date: datetime
    message_text: str
    view_count: int
    forward_count: int

    class Config:
        from_attributes = True

# 4. Computer Vision Image Stats Schemas
class VisualContentStatsResponse(BaseModel):
    channel_name: str
    detected_class: str
    total_detections: int
    average_confidence: float

    class Config:
        from_attributes = True

class MessageResponse(BaseModel):
    message_id: int
    channel_key: str
    # If text is null or blank, default it to a placeholder string automatically
    message_text: Optional[str] = Field(default="[No text content captured]")
    view_count: int = Field(default=0, ge=0) # Guarantees view count is never negative
    forward_count: int = Field(default=0, ge=0)
    date_key: datetime

    class Config:
        from_attributes = True # Enables seamless ORM (SQLAlchemy) serialization