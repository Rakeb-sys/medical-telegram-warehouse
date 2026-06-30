# api/schemas.py
from pydantic import BaseModel
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