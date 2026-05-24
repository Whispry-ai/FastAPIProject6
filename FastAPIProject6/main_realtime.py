"""
Real-time Hyperlocal News Application Main Entry Point
Enhanced version with WebSocket support and real-time features
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse

from database import Base, engine
from scheduler import start_notification_cleaner
from realtime_notifications import notification_service

# Import all route modules
from routes import (
    base_location_routes,
    insights_router,
    user_routes,
    news_routes,
    content_routes,
    engagement_routes,
    guest_routes,
    admin_routes,
    csv_routes,
    websocket_routes,
    realtime_news,
    realtime_engagement,
    realtime_admin
)

app = FastAPI(
    title="Hyperlocal News API - Real-time",
    description="Real-time hyperlocal news application with WebSocket support",
    version="2.0.0"
)

# SessionMiddleware (required for Google OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-session-key",
    same_site="lax",
    https_only=False
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (only once)
Base.metadata.create_all(bind=engine)

# Start background tasks
start_notification_cleaner()

# Start real-time notification service
import asyncio
@app.on_event("startup")
async def startup_event():
    """Initialize real-time services"""
    await notification_service.start()
    print("🚀 Real-time notification service started")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup real-time services"""
    await notification_service.stop()
    print("🛑 Real-time notification service stopped")

# Include all routers
app.include_router(base_location_routes.router, prefix="/base", tags=["Base Location"])
app.include_router(user_routes.router, prefix="/user", tags=["User"])
app.include_router(news_routes.router, prefix="/news", tags=["News"])
app.include_router(content_routes.router, prefix="/content", tags=["Content"])
app.include_router(engagement_routes.router, prefix="/engagement", tags=["Engagement"])
app.include_router(guest_routes.router, prefix="/guest", tags=["Guest"])
app.include_router(admin_routes.router, prefix="/admin", tags=["Admin"])
app.include_router(csv_routes.router, prefix="/csv", tags=["CSV"])
app.include_router(insights_router.router, prefix="/insights", tags=["Insights"])

# Real-time routes
app.include_router(websocket_routes.router, prefix="/ws", tags=["WebSocket"])
app.include_router(realtime_news.router, prefix="/realtime", tags=["Real-time News"])
app.include_router(realtime_engagement.router, prefix="/realtime", tags=["Real-time Engagement"])
app.include_router(realtime_admin.router, prefix="/realtime", tags=["Real-time Admin"])

# AI Routes
from gemini_ai import call_gemini_api_english, call_gemini_api_telugu
from fastapi import APIRouter

ai_router = APIRouter()

@ai_router.post("/ai/suggest-category", response_model=dict, tags=["AI"])
def suggest_category(request: dict):
    """Suggest news category using AI"""
    try:
        title = request.get("title", "")
        content = request.get("content", "")
        
        if not title or not content:
            return {"error": "Title and content are required"}
        
        # Call AI service
        result = call_gemini_api_english(title, content)
        
        return {
            "suggested_category": result.get("title", ""),
            "confidence": 0.85,
            "ai_analysis": result
        }
    except Exception as e:
        return {"error": str(e)}

@ai_router.post("/ai/analyze-sentiment", response_model=dict, tags=["AI"])
def analyze_sentiment(request: dict):
    """Analyze sentiment using AI"""
    try:
        text = request.get("text", "")
        
        if not text:
            return {"error": "Text is required"}
        
        # Simple sentiment analysis (positive focus)
        positive_words = ["good", "great", "excellent", "amazing", "wonderful", "fantastic", "positive", "success", "thriving", "beautiful", "innovative"]
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        
        # Calculate sentiment score
        sentiment_score = min(positive_count * 0.1, 1.0)
        
        sentiment = "positive" if sentiment_score > 0.3 else "neutral"
        
        return {
            "sentiment": sentiment,
            "score": round(sentiment_score, 3),
            "positive_words_found": positive_count,
            "text_length": len(text)
        }
    except Exception as e:
        return {"error": str(e)}

app.include_router(ai_router, prefix="/ai", tags=["AI"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    from websocket_manager import manager
    
    return {
        "status": "healthy",
        "service": "hyperlocal-news-realtime",
        "version": "2.0.0",
        "websocket_connections": manager.get_connection_stats(),
        "timestamp": "2026-05-03T00:00:00Z"
    }

# Root endpoint with real-time info
@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with real-time connection info"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Hyperlocal News API - Real-time</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            h1 { color: #2c3e50; }
            .status { background: #27ae60; color: white; padding: 10px; border-radius: 5px; display: inline-block; }
            .endpoint { background: #3498db; color: white; padding: 5px 10px; border-radius: 3px; margin: 5px 0; display: inline-block; }
            .feature { margin: 20px 0; padding: 15px; border-left: 4px solid #3498db; background: #ecf0f1; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Hyperlocal News API - Real-time</h1>
            <div class="status">✅ Real-time Services Active</div>
            
            <div class="feature">
                <h3>📡 WebSocket Features</h3>
                <div class="endpoint">/ws/{user_uid}?city_id=1&district_id=2&state_id=3</div>
                <p>Real-time news updates, notifications, and engagement</p>
            </div>
            
            <div class="feature">
                <h3>📰 Real-time News</h3>
                <div class="endpoint">GET /realtime/feed</div>
                <p>Live news feed with location-based filtering</p>
            </div>
            
            <div class="feature">
                <h3>💬 Real-time Engagement</h3>
                <div class="endpoint">POST /realtime/like/{news_uid}</div>
                <p>Live likes, comments, shares with instant updates</p>
            </div>
            
            <div class="feature">
                <h3>🚨 Breaking News</h3>
                <div class="endpoint">POST /realtime/breaking-news</div>
                <p>Urgent breaking news alerts to all users</p>
            </div>
            
            <div class="feature">
                <h3>📊 Admin Dashboard</h3>
                <div class="endpoint">GET /realtime/admin/dashboard</div>
                <p>Real-time analytics and content management</p>
            </div>
            
            <div class="feature">
                <h3>🔔 Notifications</h3>
                <div class="endpoint">WebSocket notifications</div>
                <p>Push notifications, email alerts, in-app messages</p>
            </div>
            
            <h3>📖 API Documentation</h3>
            <p><a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a></p>
            
            <h3>🏥 Health Check</h3>
            <p><a href="/health">System Health Status</a></p>
        </div>
    </body>
    </html>
    """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_realtime:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ws_ping_interval=20,
        ws_ping_timeout=10
    )
