# Database Setup Guide for Rewards System

## Step 1: Create Database in pgAdmin

1. **Open pgAdmin**
2. **Connect to your PostgreSQL server**
3. **Right-click on "Databases"** → **Create** → **Database**
4. **Enter database name**: `fastapi_news`
5. **Click "Save"**

## Step 2: Update Database Connection

Make sure your `.env` file has the correct database settings:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/fastapi_news
```

## Step 3: Run Database Migration

After creating the database, run:

```bash
python create_rewards_tables.py
```

## Step 4: Verify Tables Created

Connect to the database and check these tables exist:

- `user_referrals` - Referral tracking
- `user_wallets` - User coin wallets  
- `wallet_transactions` - Transaction history
- `coupons` - Coupon system
- `coupon_redemptions` - Redemption tracking
- `daily_engagement` - Daily engagement tracking
- `reward_settings` - System configuration
- `fraud_detection` - Fraud prevention
- `leaderboard` - User rankings

## Step 5: Start Server

```bash
python -m uvicorn main:app --port 8001 --host 0.0.0.0 --reload
```

## Step 6: Test Rewards System

Open: `http://localhost:8001/docs`

Look for "Rewards" section to test all endpoints.

---

## Quick Alternative: Auto-Create Database

If you want to auto-create the database, add this to your main.py:

```python
from sqlalchemy import create_engine, text

def create_database_if_not_exists():
    engine = create_engine("postgresql://username:password@localhost:5432/postgres")
    with engine.connect() as conn:
        conn.execute(text("COMMIT"))
        conn.execute(text("CREATE DATABASE fastapi_news"))
        conn.execute(text("COMMIT"))
    engine.dispose()

# Call this before Base.metadata.create_all()
```

But **pgAdmin method is recommended** for better control.
