# api/main.py
from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from api.database import get_db
import api.schemas as schemas

app = FastAPI(
    title="Kara Solutions Medical Analytics API",
    description="REST API delivering data insights on Ethiopian medical Telegram channels from a dbt star schema.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"status": "online", "documentation": "/docs"}


@app.get("/api/reports/top-products", response_model=List[schemas.TopProductResponse], tags=["Reports"])
def get_top_products(limit: int = Query(10, description="Number of top products to return"), db: Session = Depends(get_db)):
    """
    **Endpoint 1: Top Products**
    Parses clean message content strings and counts mentions of explicit health sector keywords.
    """
    # A list of common medical keywords to cross-reference against the text fields
    keywords = ['paracetamol', 'amoxicillin', 'insulin', 'cosmetics', 'pharma', 'syrup', 'tablet', 'mask', 'vitamin']
    
    query = text("""
        WITH unnested_keywords AS (
            SELECT unnest(:keywords) AS keyword
        )
        SELECT 
            k.keyword AS product_keyword,
            COUNT(*)::int AS mention_count
        FROM unnested_keywords k
        JOIN public.fct_messages m 
          ON LOWER(m.message_text) LIKE '%' || LOWER(k.keyword) || '%'
        GROUP BY k.keyword
        ORDER BY mention_count DESC
        LIMIT :limit;
    """)
    
    result = db.execute(query, {"keywords": keywords, "limit": limit}).fetchall()
    return [{"product_keyword": row[0], "mention_count": row[1]} for row in result]


@app.get("/api/channels/{channel_name}/activity", response_model=List[schemas.ChannelActivityResponse], tags=["Channels"])
def get_channel_activity(channel_name: str, db: Session = Depends(get_db)):
    """
    **Endpoint 2: Channel Activity**
    Tracks dynamic operational histories and rolling traffic trends for a specific tracking target.
    """
    query = text("""
        SELECT 
            c.channel_name,
            CAST(d.full_date AS VARCHAR) AS post_date,
            COUNT(m.message_id)::int AS daily_posts,
            SUM(m.view_count)::int AS total_views,
            SUM(m.forward_count)::int AS total_forwards
        FROM public.fct_messages m
        JOIN public.dim_channels c ON m.channel_key = c.channel_key
        JOIN public.dim_dates d ON m.date_key = d.date_key
        WHERE LOWER(c.channel_name) = LOWER(:channel_name)
        GROUP BY c.channel_name, d.full_date
        ORDER BY d.full_date DESC;
    """)
    
    result = db.execute(query, {"channel_name": channel_name}).fetchall()
    if not result:
        raise HTTPException(status_code=404, detail=f"No activity records found for channel '{channel_name}'")
        
    return [{
        "channel_name": row[0], "post_date": row[1], 
        "daily_posts": row[2], "total_views": row[3], "total_forwards": row[4]
    } for row in result]


@app.get("/api/search/messages", response_model=List[schemas.MessageSearchResponse], tags=["Search"])
def search_messages(query: str = Query(..., min_length=3, description="Search keyword"), limit: int = 20, db: Session = Depends(get_db)):
    """
    **Endpoint 3: Message Search**
    Runs filter queries on historical text records to find specific context mentions.
    """
    sql_query = text("""
        SELECT 
            m.message_id,
            c.channel_name,
            d.full_date + CASE WHEN m.date_key = d.date_key THEN '00:00:00'::time END as message_date,
            m.message_text,
            m.view_count,
            m.forward_count
        FROM public.fct_messages m
        JOIN public.dim_channels c ON m.channel_key = c.channel_key
        JOIN public.dim_dates d ON m.date_key = d.date_key
        WHERE m.message_text ILIKE :search_term
        ORDER BY m.view_count DESC
        LIMIT :limit;
    """)
    
    result = db.execute(sql_query, {"search_term": f"%{query}%", "limit": limit}).fetchall()
    return [{
        "message_id": row[0], "channel_name": row[1], "message_date": row[2],
        "message_text": row[3], "view_count": row[4], "forward_count": row[5]
    } for row in result]


@app.get("/api/reports/visual-content", response_model=List[schemas.VisualContentStatsResponse], tags=["Reports"])
def get_visual_content_stats(db: Session = Depends(get_db)):
    """
    **Endpoint 4: Visual Content Stats**
    Aggregates metrics from the YOLO object detection layer to evaluate product placement trends.
    """
    query = text("""
        SELECT 
            c.channel_name,
            f.detected_class,
            COUNT(f.message_id)::int AS total_detections,
            ROUND(AVG(f.confidence_score), 4)::float AS average_confidence
        FROM public.fct_image_detections f
        JOIN public.dim_channels c ON f.channel_key = c.channel_key
        GROUP BY c.channel_name, f.detected_class
        ORDER BY total_detections DESC;
    """)
    
    result = db.execute(query).fetchall()
    return [{
        "channel_name": row[0], "detected_class": row[1],
        "total_detections": row[2], "average_confidence": row[3]
    } for row in result]