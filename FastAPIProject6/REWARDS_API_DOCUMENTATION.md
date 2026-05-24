# Rewards System API Documentation

## Overview
The Rewards System provides a comprehensive gamification platform for users to earn coins through various activities like referrals, daily logins, reading articles, sharing news, and more.

## Base URL
`http://127.0.0.1:8000`

## Authentication
All rewards endpoints require JWT authentication. Include the access token in the Authorization header:
```
Authorization: Bearer <access_token>
```

---

## 🎯 Rewards System APIs

### 1. Referral System

#### GET `/rewards/referral`
**Purpose**: Get user's referral information and statistics
**Authentication**: Required
**Response**:
```json
{
  "referral_code": "DEMO123",
  "referral_link": "https://app.example.com/referral/DEMO123",
  "total_referrals": 5,
  "pending_referrals": 2,
  "completed_referrals": 3,
  "total_coins_earned": 150
}
```

#### POST `/rewards/referral/verify`
**Purpose**: Verify a referral code
**Authentication**: Required
**Request Body**:
```json
{
  "referral_code": "DEMO123"
}
```
**Response**:
```json
{
  "success": true,
  "message": "Referral code verified successfully",
  "referrer_uid": "USER123",
  "welcome_bonus": 20
}
```

#### POST `/rewards/referral/complete`
**Purpose**: Complete referral process after registration
**Authentication**: Required
**Request Body**:
```json
{
  "referral_code": "DEMO123"
}
```
**Response**:
```json
{
  "success": true,
  "coins_awarded": 20,
  "referrer_bonus": 50,
  "message": "Referral completed successfully"
}
```

---

### 2. Wallet System

#### GET `/rewards/wallet`
**Purpose**: Get user's wallet balance and statistics
**Authentication**: Required
**Response**:
```json
{
  "current_balance": 100,
  "total_earned": 150,
  "total_spent": 50,
  "daily_streak": 5,
  "longest_streak": 10
}
```

#### GET `/rewards/wallet/transactions`
**Purpose**: Get user's transaction history with pagination
**Authentication**: Required
**Query Parameters**:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)
**Response**:
```json
{
  "transactions": [
    {
      "id": 1,
      "transaction_type": "daily_login",
      "amount": 5,
      "description": "Daily login reward",
      "reference_id": "1",
      "created_at": "2025-05-13T10:00:00Z"
    }
  ],
  "total_count": 50,
  "page": 1,
  "limit": 20
}
```

---

### 3. Daily Rewards

#### POST `/rewards/daily-login`
**Purpose**: Claim daily login reward
**Authentication**: Required
**Response**:
```json
{
  "success": true,
  "coins_awarded": 5,
  "daily_streak": 5,
  "message": "Daily login reward earned! Current streak: 5"
}
```

---

### 4. Engagement Rewards

#### POST `/rewards/article-read`
**Purpose**: Claim reward for reading an article
**Authentication**: Required
**Request Body**:
```json
{
  "news_uid": "NEWS123"
}
```
**Response**:
```json
{
  "success": true,
  "coins_awarded": 10,
  "articles_read_today": 3,
  "max_articles_per_day": 5,
  "message": "Article read reward claimed"
}
```

#### POST `/rewards/news-share`
**Purpose**: Claim reward for sharing news
**Authentication**: Required
**Request Body**:
```json
{
  "news_uid": "NEWS123",
  "platform": "whatsapp"
}
```
**Response**:
```json
{
  "success": true,
  "coins_awarded": 8,
  "shares_today": 2,
  "max_shares_per_day": 3,
  "message": "News share reward claimed"
}
```

#### POST `/rewards/comment`
**Purpose**: Claim reward for posting a comment
**Authentication**: Required
**Request Body**:
```json
{
  "comment_uid": "COMMENT123"
}
```
**Response**:
```json
{
  "success": true,
  "coins_awarded": 3,
  "comments_today": 5,
  "max_comments_per_day": 10,
  "message": "Comment reward claimed"
}
```

---

### 5. Coupon System

#### GET `/rewards/coupons`
**Purpose**: Get available coupons for redemption
**Authentication**: Required
**Response**:
```json
{
  "coupons": [
    {
      "id": 1,
      "code": "SAVE20",
      "description": "20% off on premium subscription",
      "coins_required": 100,
      "valid_until": "2025-12-31",
      "status": "active"
    }
  ]
}
```

#### POST `/rewards/coupons/redeem`
**Purpose**: Redeem a coupon using coins
**Authentication**: Required
**Request Body**:
```json
{
  "coupon_code": "SAVE20"
}
```
**Response**:
```json
{
  "success": true,
  "coins_deducted": 100,
  "coupon_details": {
    "code": "SAVE20",
    "description": "20% off on premium subscription"
  },
  "message": "Coupon redeemed successfully"
}
```

---

### 6. Leaderboard

#### GET `/rewards/leaderboard`
**Purpose**: Get top users by coin balance
**Authentication**: Required
**Query Parameters**:
- `limit`: Number of top users to return (default: 10)
**Response**:
```json
{
  "leaderboard": [
    {
      "rank": 1,
      "user_uid": "USER001",
      "username": "john_doe",
      "coins": 5000,
      "streak": 15
    }
  ],
  "total_users": 1000,
  "user_rank": 25
}
```

---

### 7. Statistics & Analytics

#### GET `/rewards/stats`
**Purpose**: Get user's rewards statistics
**Authentication**: Required
**Response**:
```json
{
  "total_coins_earned": 500,
  "total_coins_spent": 200,
  "current_balance": 300,
  "referral_count": 5,
  "daily_streak": 7,
  "longest_streak": 15,
  "articles_read": 50,
  "news_shared": 20,
  "comments_posted": 30
}
```

#### GET `/rewards/engagement`
**Purpose**: Get user's engagement analytics
**Authentication**: Required
**Query Parameters**:
- `days`: Number of days to analyze (default: 30)
**Response**:
```json
{
  "period_days": 30,
  "daily_activity": [
    {
      "date": "2025-05-13",
      "articles_read": 3,
      "news_shared": 1,
      "comments_posted": 2,
      "coins_earned": 35
    }
  ],
  "total_engagement": {
    "articles_read": 45,
    "news_shared": 15,
    "comments_posted": 25,
    "coins_earned": 425
  }
}
```

---

### 8. Admin Endpoints

#### GET `/rewards/admin/analytics`
**Purpose**: Get system-wide rewards analytics (Admin only)
**Authentication**: Required (Admin role)
**Response**:
```json
{
  "total_users": 1000,
  "active_users": 750,
  "total_coins_distributed": 50000,
  "total_coins_redeemed": 20000,
  "top_referrers": [
    {
      "user_uid": "USER001",
      "referral_count": 25,
      "coins_earned": 1250
    }
  ]
}
```

#### POST `/rewards/admin/wallet/adjust`
**Purpose**: Adjust user wallet balance (Admin only)
**Authentication**: Required (Admin role)
**Request Body**:
```json
{
  "user_uid": "USER123",
  "amount": 100,
  "reason": "Bonus for contest winner"
}
```
**Response**:
```json
{
  "success": true,
  "new_balance": 200,
  "message": "Wallet balance adjusted successfully"
}
```

---

## 📊 Reward Configuration

Default reward values (configurable via database):

- **Referral Bonus**: 50 coins (referrer)
- **Welcome Bonus**: 20 coins (new user)
- **Daily Login**: 5 coins
- **Article Read**: 10 coins (max 5/day)
- **News Share**: 8 coins (max 3/day)
- **Comment Post**: 3 coins (max 10/day)
- **Weekly Streak Bonus**: 50 coins

---

## 🔐 Authentication Flow

1. **Send OTP**:
   ```
   POST /user/auth/send-otp
   {
     "type": "mobile",
     "value": "8967452312"
   }
   ```

2. **Verify OTP & Login**:
   ```
   POST /user/token/verify/login
   {
     "identifier": "8967452312",
     "otp": "1234",
     "role": 4
   }
   ```

3. **Use Access Token**:
   ```
   Authorization: Bearer <access_token>
   ```

---

## 🧪 Test User

- **Phone**: 8967452312
- **Email**: test8967@example.com
- **Role**: 4 (Publisher)
- **Wallet**: 100 coins

---

## 📈 Current Status

✅ **Working Endpoints**: 7/9 (77.8%)
- Referral Info ✅
- Daily Login ✅
- Article Read ✅
- News Share ✅
- Comment Reward ✅
- Available Coupons ✅
- Leaderboard ✅

⚠️ **Needs Fix**: 2/9 (22.2%)
- Wallet Balance (Database column issue)
- Transaction History (404 Not Found)

---

## 🗄️ Database Tables

- `users` - User accounts
- `user_wallets` - Coin balances and streaks
- `wallet_transactions` - Transaction history
- `user_referrals` - Referral tracking
- `reward_settings` - System configuration
- `otp_tokens` - Authentication tokens
- `user_sessions` - User sessions

---

## 🐘 PostgreSQL Setup

- **Database**: news_platform
- **Host**: localhost
- **Port**: 5432
- **User**: postgres
- **Password**: password

Use pgAdmin to manage the database and view tables.
