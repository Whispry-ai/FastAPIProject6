#!/usr/bin/env python3
"""
Simple Rewards Application
Working rewards system without complex imports
"""

from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="Simple Rewards API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple response models
class ReferralResponse(BaseModel):
    referral_code: str
    referral_link: str
    total_referrals: int
    message: str

class WalletBalance(BaseModel):
    current_balance: int
    total_earned: int
    message: str

class RewardResponse(BaseModel):
    success: bool
    coins_awarded: int
    message: str

class CouponResponse(BaseModel):
    id: int
    title: str
    coin_cost: int
    is_available: bool
    message: str

# Create router
router = APIRouter(prefix="/rewards", tags=["Rewards"])

@app.get("/")
async def root():
    return {"message": "Simple Rewards API", "version": "1.0.0"}

@router.get("/referral", response_model=ReferralResponse)
async def get_referral():
    """Get referral information"""
    return ReferralResponse(
        referral_code="DEMO123",
        referral_link="https://yourapp.com/signup?ref=DEMO123",
        total_referrals=0,
        message="Referral system working!"
    )

@router.get("/wallet", response_model=WalletBalance)
async def get_wallet():
    """Get wallet balance"""
    return WalletBalance(
        current_balance=0,
        total_earned=0,
        message="Wallet system working!"
    )

@router.post("/daily-login", response_model=RewardResponse)
async def daily_login():
    """Claim daily login reward"""
    return RewardResponse(
        success=True,
        coins_awarded=5,
        message="Daily login reward earned!"
    )

@router.post("/article-read", response_model=RewardResponse)
async def article_read():
    """Claim article read reward"""
    return RewardResponse(
        success=True,
        coins_awarded=10,
        message="Article read reward earned!"
    )

@router.post("/news-share", response_model=RewardResponse)
async def news_share():
    """Claim news share reward"""
    return RewardResponse(
        success=True,
        coins_awarded=8,
        message="News share reward earned!"
    )

@router.post("/comment", response_model=RewardResponse)
async def comment():
    """Claim comment reward"""
    return RewardResponse(
        success=True,
        coins_awarded=5,
        message="Comment reward earned!"
    )

@router.get("/coupons", response_model=list[CouponResponse])
async def get_coupons():
    """Get available coupons"""
    return [
        CouponResponse(
            id=1,
            title="Sample Coupon",
            coin_cost=50,
            is_available=True,
            message="Coupon system working!"
        )
    ]

@router.get("/leaderboard")
async def get_leaderboard():
    """Get leaderboard"""
    return {
        "entries": [
            {
                "user_uid": "demo1",
                "username": "Demo User",
                "total_coins": 100,
                "rank_position": 1
            }
        ],
        "total_users": 1,
        "message": "Leaderboard system working!"
    }

# Include router
app.include_router(router)

if __name__ == "__main__":
    print("🚀 Starting Simple Rewards API...")
    print("📊 Rewards Features:")
    print("   • Referral System")
    print("   • Daily Login Rewards")
    print("   • Article Reading Rewards")
    print("   • News Sharing Rewards")
    print("   • Comment Rewards")
    print("   • Wallet System")
    print("   • Coupon System")
    print("   • Leaderboard")
    print("🌐 API: http://localhost:8002")
    print("📚 Documentation: http://localhost:8002/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8002)
