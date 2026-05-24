# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from database import Base, engine

# from scheduler import start_notification_cleaner

# from fastapi.responses import HTMLResponse

# from routes import (
#     base_location_routes,
#     insights_router,
#     user_routes,
#     news_routes,
#     content_routes,
#     engagement_routes,
#     guest_routes,
#     admin_routes,
#     insights_router,
#     csv_routes,
#     ai_routes as ai_router
#     csv_routes
# )
# from starlette.middleware.sessions import SessionMiddleware

# app = FastAPI(title="Hyperlocal News API", version="1.0.0")

# # ✅ SessionMiddleware MUST come first
# app.add_middleware(
#     SessionMiddleware,
#     secret_key="super-secret-session-key",
#     same_site="lax",
#     https_only=False
# )

# # ✅ Then CORS (only once)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://127.0.0.1:8000"],  # 🔥 important
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# # Create tables
# Base.metadata.create_all(bind=engine)
# # Create tables
# Base.metadata.create_all(bind=engine)

# # Start background tasks
# start_notification_cleaner()

# # CORS setup
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Include routers
# app.include_router(base_location_routes.router, prefix="/base", tags=["Base Location"])
# app.include_router(user_routes.router, prefix="/user", tags=["User"])
# app.include_router(news_routes.router, prefix="/news", tags=["News"])
# app.include_router(content_routes.router, prefix="/content", tags=["Content"])
# app.include_router(engagement_routes.router, prefix="/engagement", tags=["Engagement"])
# app.include_router(guest_routes.router, prefix="/guest", tags=["Guest"])
# app.include_router(admin_routes.router)


from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import HTMLResponse

from database import Base, engine
from scheduler import start_notification_cleaner
from routes import (
    base_location_routes,
    insights_router,
    user_routes,
    news_routes,
    content_routes,
    engagement_routes,
    engagement_routes_new,
    engagement_social_routes,
    guest_routes,
    admin_routes,
    insights_router,
    csv_routes,
    ai_routes_simple as ai_routes,
    search_routes,
    analytics_routes,
    file_upload_routes_fixed as file_upload_routes,
    core_routes,
    news_enhanced_routes,
    user_enhanced_routes,
    location_enhanced_routes,
    content_enhanced_routes,
    ad_placement_routes,
    rewards_routes_fixed,
    rewards_routes
)



app = FastAPI(title="Hyperlocal News API", version="1.0.0")

# ✅ SessionMiddleware (required for Google OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-session-key",
    same_site="lax",
    https_only=False
)

# ✅ Only ONE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables (only once)
Base.metadata.create_all(bind=engine)

# Start background tasks
start_notification_cleaner()

# Include routers
app.include_router(base_location_routes.router, prefix="/base", tags=["Base Location"])
app.include_router(user_routes.router, prefix="/user", tags=["User"])
app.include_router(news_routes.router, prefix="/news", tags=["News"])
app.include_router(content_routes.router, prefix="/content", tags=["Content"])
app.include_router(engagement_routes_new.router, prefix="/engagement", tags=["Engagement"])
app.include_router(engagement_social_routes.router, prefix="/engagement/social", tags=["Engagement Social"])
app.include_router(guest_routes.router, prefix="/guest", tags=["Guest"])
app.include_router(admin_routes.router)
app.include_router(csv_routes.router, prefix="/csv", tags=["CSV"])
app.include_router(insights_router.router, prefix="/insights", tags=["Insights"])
app.include_router(ai_routes.router, prefix="/ai", tags=["AI"])
app.include_router(search_routes.router, prefix="/search", tags=["Search"])
app.include_router(analytics_routes.router, prefix="/analytics", tags=["Analytics"])
app.include_router(file_upload_routes.router, prefix="/files", tags=["File Upload"])
app.include_router(core_routes.router, tags=["Core"])
app.include_router(news_enhanced_routes.router, tags=["News Enhanced"])
app.include_router(user_enhanced_routes.router, tags=["User Enhanced"])
app.include_router(location_enhanced_routes.router, tags=["Location Enhanced"])
app.include_router(content_enhanced_routes.router, tags=["Content Enhanced"])
app.include_router(ad_placement_routes.router, tags=["Ad Placement"])
app.include_router(rewards_routes_fixed.router, tags=["Rewards Fixed"])
app.include_router(rewards_routes.router, prefix="/rewards", tags=["Rewards"])

@app.get("/ad_placement_client.html", response_class=HTMLResponse)
def ad_placement_client():
    import os
    file_path = os.path.join(os.path.dirname(__file__), "ad_placement_client.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return HTMLResponse(content="<h1>Ad Placement Client Not Found</h1><p>Please create the ad_placement_client.html file</p>", status_code=404)

@app.get("/news_sharing_demo.html", response_class=HTMLResponse)
def news_sharing_demo():
    import os
    file_path = os.path.join(os.path.dirname(__file__), "news_sharing_demo.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return HTMLResponse(content="<h1>News Sharing Demo Not Found</h1><p>Please create the news_sharing_demo.html file</p>", status_code=404)

@app.get("/ai_analysis_client.html", response_class=HTMLResponse)
def ai_analysis_client():
    import os
    file_path = os.path.join(os.path.dirname(__file__), "ai_analysis_client.html")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        return HTMLResponse(content="<h1>AI Analysis Client Not Found</h1><p>Please create the ai_analysis_client.html file</p>", status_code=404)

@app.get("/", response_class=HTMLResponse)
def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Our News API</title>
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
            <h1>News API</h1>
            <p>Welcome! The API is running successfully.</p>
            <p>Check the👉 <a href="/docs">API Documentation</a></p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
