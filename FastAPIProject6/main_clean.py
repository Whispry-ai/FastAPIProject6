"""
Clean Hyperlocal News Application
Fixed version without indentation errors
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse

from database import Base, engine
from scheduler import start_notification_cleaner

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
    csv_routes
)

# Import AI routes
from routes import ai_routes as ai_router

app = FastAPI(
    title="Hyperlocal News API - Clean",
    description="Hyperlocal news application",
    version="1.0.0"
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
app.include_router(ai_router, prefix="/ai", tags=["AI"])

@app.get("/", response_class=HTMLResponse)
def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hyperlocal News API - Clean</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: #f4f6f8;
                margin: 0;
                padding: 0;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                color: #333;
            }
            .container {
                text-align: center;
                background: white;
                padding: 50px;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            }
            h1 {
                color: #0077b6;
            }
            p {
                font-size: 1.2em;
            }
            a {
                color: #0077b6;
                text-decoration: none;
                font-weight: bold;
            }
            a:hover {
                text-decoration: underline;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📰 Hyperlocal News API - Clean</h1>
            <div class="status">✅ Server Running</div>
            
            <h3>📰 Available Features:</h3>
            <p>• News Management</p>
            <p>• User Management</p>
            <p>• AI Analysis Features</p>
            <p>• Admin Dashboard</p>
            <p>• CSV Import/Export</p>
            <p>• Location Services</p>
            <p>• Analytics & Insights</p>
            
            <h3>📖 API Documentation:</h3>
            <p><a href="/docs">Swagger UI</a> | <a href="/redoc">ReDoc</a></p>
            
            <h3>🏥 Health Check:</h3>
            <p><a href="/health">System Health Status</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "hyperlocal-news-clean",
        "version": "1.0.0",
        "timestamp": "2026-05-03T00:00:00Z"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main_clean:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
