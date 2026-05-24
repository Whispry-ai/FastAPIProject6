# from datetime import datetime
# from typing import List, Optional
# from fastapi import APIRouter, Depends, HTTPException, Query, status
# import requests
# from sqlalchemy.orm import Session
# from auth.dependencies import admin_required
# from models.base_location import City, District, Language
# from models.engagement import Notification
# from sqlalchemy import desc, or_
# from models.content import Advertisement, Event, Poll, SponsoredPost, YouTubeShort
# from models.news import News, Reaction, Comment, Share, NewsView, Category
# from database import get_db
# from models.user import User, UserPreference
# from schemas import BreakingNewsUpdate, NewsCreate, NewsOut, VideoItem
# from models.news import News, Reaction, Share, NewsView
# from utility import YOUTUBE_API_KEY, YOUTUBE_SEARCH_URL, generate_news_uid
# from datetime import datetime, timezone, timedelta

# router = APIRouter(prefix="/v1", tags=["News"])
# # router = APIRouter()




# # =====================================================
# # CREATE NEWS
# # =====================================================

# @router.post("/news1", response_model=NewsOut)
# def create_news(payload: NewsCreate, db: Session = Depends(get_db)):

#     # 1️⃣ Verify user
#     user = db.query(User).filter_by(user_uid=payload.user_uid).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # 2️⃣ Verify language
#     language = db.query(Language).filter_by(id=payload.language_id).first()
#     if not language:
#         raise HTTPException(status_code=404, detail="Language not found")

#     # 3️⃣ Handle city → district → state
#     city = None
#     district = None
#     state = None

#     if payload.city_id:
#         city = db.query(City).filter_by(id=payload.city_id).first()

#         if not city:
#             raise HTTPException(status_code=404, detail="City not found")

#         district = city.district
#         state = district.state if district else None

#     # 4️⃣ Generate unique news UID
#     news_uid = generate_news_uid()

#     # 5️⃣ Create news object
#     news = News(
#         news_uid=news_uid,
#         title=payload.title,
#         summary=payload.summary,
#         image_url=payload.image_url,
#         language_id=payload.language_id,
#         user_uid=payload.user_uid,
#         city_id=payload.city_id,
#         source_url=payload.source_url,
#         source_name=payload.source_name
#     )

#     # 6️⃣ Attach categories
#     if payload.category_ids:
#         categories = db.query(Category).filter(
#             Category.id.in_(payload.category_ids)
#         ).all()

#         news.categories = categories

#     # 7️⃣ Save to database
#     db.add(news)
#     db.commit()
#     db.refresh(news)

#     # 8️⃣ Return structured response
#     return {
#         "news_uid": news.news_uid,
#         "title": news.title,
#         "summary": news.summary,
#         "image_url": news.image_url,

#         "language": {
#             "id": language.id,
#             "name": language.name,
#             "code": language.code
#         },

#         "user_uid": news.user_uid,
#         "is_approved": news.is_approved,
#         "created_at": news.created_at,

#         "city": {
#             "id": city.id,
#             "name": city.name,
#             "district_id": city.district_id
#         } if city else None,

#         "district": {
#             "id": district.id,
#             "name": district.name
#         } if district else None,

#         "state": {
#             "id": state.id,
#             "name": state.name
#         } if state else None,

#         "source_url": news.source_url,
#         "source_name": news.source_name,

#         "category_ids": [c.id for c in news.categories]
#     }
    
# # =====================================================
# # POST BREAKING NEWS
# # =====================================================

# @router.put("/admin/news/{news_uid}/breaking", tags=["Admin"])
# def set_breaking_news(
#     news_uid: str,
#     payload: BreakingNewsUpdate,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(admin_required)
# ):

#     news = db.query(News).filter(
#         News.news_uid == news_uid
#     ).first()

#     if not news:
#         raise HTTPException(404, "News not found")

#     if payload.is_breaking:

#         news.is_breaking = True
#         news.breaking_priority = payload.priority
#         news.breaking_expires_at = (
#             datetime.now(timezone.utc)
#             + timedelta(hours=payload.expire_hours)
#         )

#     else:

#         news.is_breaking = False
#         news.breaking_priority = 0
#         news.breaking_expires_at = None

#     db.commit()

#     return {
#         "message": "Breaking news updated",
#         "news_uid": news_uid
#     }

# @router.get("/news/breaking")
# def get_breaking_news(
#     db: Session = Depends(get_db)
# ):

#     breaking_news = db.query(News).filter(
#         News.is_breaking == True,
#         News.breaking_expires_at > datetime.now(timezone.utc),
#         News.is_approved == 1
#     ).order_by(desc(News.breaking_priority)).limit(5).all()

#     return breaking_news
# # =====================================================
# # GET News Ranking Feed 
# # =====================================================


# @router.get("/v1/news/feed")
# def get_news_feed(
#     user_uid: str,
#     cursor: Optional[datetime] = None,
#     limit: int = Query(20, le=50),
#     db: Session = Depends(get_db)
# ):

#     now = datetime.now(timezone.utc)

#     user_pref = db.query(UserPreference).filter(
#         UserPreference.user_uid == user_uid
#     ).first()

#     if not user_pref:
#         raise HTTPException(404, "User preference not found")

#     feed_news = []
#     seen_ids = set()

#     # --------------------------------------------------
#     # BREAKING NEWS
#     # --------------------------------------------------

#     breaking_news = db.query(News).filter(
#         News.is_breaking == True,
#         News.is_approved == 1,
#         (News.breaking_expires_at == None) |
#         (News.breaking_expires_at > now),
#         News.language_id == user_pref.language_id
#     ).order_by(desc(News.breaking_priority)).limit(3).all()

#     for news in breaking_news:
#         feed_news.append(news)
#         seen_ids.add(news.id)

#     # --------------------------------------------------
#     # CITY NEWS
#     # --------------------------------------------------

#     if user_pref.city_id:

#         city_news = db.query(News).filter(
#             News.city_id == user_pref.city_id,
#             News.language_id == user_pref.language_id,
#             News.is_approved == 1
#         ).order_by(desc(News.created_at)).limit(30).all()

#         for n in city_news:
#             if n.id not in seen_ids:
#                 feed_news.append(n)
#                 seen_ids.add(n.id)

#     # --------------------------------------------------
#     # DISTRICT NEWS
#     # --------------------------------------------------

#     if len(feed_news) < limit and user_pref.district_id:

#         district_news = db.query(News).join(City).filter(
#             City.district_id == user_pref.district_id,
#             News.language_id == user_pref.language_id,
#             News.is_approved == 1
#         ).order_by(desc(News.created_at)).limit(30).all()

#         for n in district_news:
#             if n.id not in seen_ids:
#                 feed_news.append(n)
#                 seen_ids.add(n.id)

#     # --------------------------------------------------
#     # STATE NEWS
#     # --------------------------------------------------

#     if len(feed_news) < limit and user_pref.state_id:

#         state_news = db.query(News).join(City).join(District).filter(
#             District.state_id == user_pref.state_id,
#             News.language_id == user_pref.language_id,
#             News.is_approved == 1
#         ).order_by(desc(News.created_at)).limit(30).all()

#         for n in state_news:
#             if n.id not in seen_ids:
#                 feed_news.append(n)
#                 seen_ids.add(n.id)

#     # --------------------------------------------------
#     # LANGUAGE NEWS
#     # --------------------------------------------------

#     if len(feed_news) < limit:

#         lang_news = db.query(News).filter(
#             News.language_id == user_pref.language_id,
#             News.is_approved == 1
#         ).order_by(desc(News.created_at)).limit(30).all()

#         for n in lang_news:
#             if n.id not in seen_ids:
#                 feed_news.append(n)
#                 seen_ids.add(n.id)

#     # --------------------------------------------------
#     # TRENDING FALLBACK
#     # --------------------------------------------------

#     if len(feed_news) < limit:

#         trending = db.query(News).filter(
#             News.is_approved == 1
#         ).order_by(desc(News.views_count)).limit(30).all()

#         for n in trending:
#             if n.id not in seen_ids:
#                 feed_news.append(n)
#                 seen_ids.add(n.id)

#     feed_news = feed_news[:limit]

#     # --------------------------------------------------
#     # CONTENT SOURCES
#     # --------------------------------------------------

#     ads = db.query(Advertisement).filter(
#         Advertisement.is_active == True,
#         Advertisement.start_date <= now,
#         Advertisement.end_date >= now
#     ).all()

#     polls = db.query(Poll).filter(
#         Poll.is_approved == True,
#         (Poll.expires_at == None) | (Poll.expires_at > now)
#     ).all()

#     events = db.query(Event).filter(
#         Event.is_approved == True,
#         Event.event_date >= now
#     ).all()

#     sponsored = db.query(SponsoredPost).filter(
#         SponsoredPost.is_approved == True,
#         SponsoredPost.start_date <= now,
#         SponsoredPost.end_date >= now
#     ).all()

#     ad_index = poll_index = event_index = sponsored_index = 0

#     feed = []

#     for i, news in enumerate(feed_news):

#         feed.append({
#             "type": "breaking" if news.is_breaking else "news",
#             "news_uid": news.news_uid,
#             "title": news.title,
#             "summary": news.summary,
#             "image_url": news.image_url,
#             "created_at": news.created_at,

#             "engagement": {
#                 "likes": news.likes_count,
#                 "comments": news.comments_count,
#                 "shares": news.shares_count,
#                 "views": news.views_count
#             }
#         })

#         # -------------------------------
#         # AD every 4 items
#         # -------------------------------

#         if (i + 1) % 4 == 0 and ads:

#             ad = ads[ad_index % len(ads)]

#             feed.append({
#                 "type": "ad",
#                 "title": ad.title,
#                 "image_url": ad.image_url,
#                 "redirect_url": ad.redirect_url
#             })

#             ad_index += 1

#         # -------------------------------
#         # POLL every 10 items
#         # -------------------------------

#         if (i + 1) % 10 == 0 and polls:

#             poll = polls[poll_index % len(polls)]

#             feed.append({
#                 "type": "poll",
#                 "poll_uid": poll.poll_uid,
#                 "question": poll.question,
#                 "options": poll.options
#             })

#             poll_index += 1

#         # -------------------------------
#         # EVENT every 12 items
#         # -------------------------------

#         if (i + 1) % 12 == 0 and events:

#             event = events[event_index % len(events)]

#             feed.append({
#                 "type": "event",
#                 "event_uid": event.event_uid,
#                 "title": event.title,
#                 "event_date": event.event_date
#             })

#             event_index += 1

#         # -------------------------------
#         # SPONSORED every 15 items
#         # -------------------------------

#         if (i + 1) % 15 == 0 and sponsored:

#             s = sponsored[sponsored_index % len(sponsored)]

#             feed.append({
#                 "type": "sponsored",
#                 "title": s.title,
#                 "image_url": s.image_url,
#                 "cta_text": s.cta_text,
#                 "cta_url": s.cta_url
#             })

#             sponsored_index += 1

#     next_cursor = feed_news[-1].created_at if feed_news else None

#     return {
#         "items": feed,
#         "next_cursor": next_cursor
#     }
# # =====================================================
# # GET SINGLE NEWS
# # =====================================================

# @router.get("/news/{news_uid}", response_model=NewsOut)
# def get_news(news_uid: str,
#              user_uid: str | None = None,
#              db: Session = Depends(get_db)):

#     news = db.query(News).filter(
#         News.news_uid == news_uid
#     ).first()

#     if not news:
#         raise HTTPException(status_code=404, detail="News not found")

#     city = news.city
#     district = city.district if city else None
#     state = district.state if district else None
#     language = news.language

#     # check if user liked
#     user_liked = False

#     if user_uid:
#         liked = db.query(Reaction).filter(
#             Reaction.news_uid == news_uid,
#             Reaction.user_uid == user_uid
#         ).first()

#         user_liked = True if liked else False

#     return NewsOut(
#         news_uid=news.news_uid,
#         title=news.title,
#         summary=news.summary,
#         image_url=news.image_url,

#         language={
#             "id": language.id,
#             "name": language.name,
#             "code": language.code
#         },

#         user_uid=news.user_uid,
#         is_approved=news.is_approved,
#         created_at=news.created_at,

#         city={
#             "id": city.id,
#             "name": city.name,
#             "district_id": city.district_id
#         } if city else None,

#         district={
#             "id": district.id,
#             "name": district.name
#         } if district else None,

#         state={
#             "id": state.id,
#             "name": state.name
#         } if state else None,

#         source_url=news.source_url,
#         source_name=news.source_name,

#         category_ids=[c.id for c in news.categories],

#         engagement={
#             "likes": news.likes_count,
#             "comments": news.comments_count,
#             "shares": news.shares_count,
#             "views": news.views_count,
#             "user_liked": user_liked
#         }
#     )

# #-----------------------------------------------
# # Comment News
# #------------------------------------------------

# @router.post("/user/news/{news_uid}/comment",tags=["News Engagement"])
# def add_comment(news_uid: str, user_uid: str, comment_text: str, db: Session = Depends(get_db)):

#     news = db.query(News).filter_by(news_uid=news_uid).first()

#     if not news:
#         raise HTTPException(404, "News not found")

#     comment = Comment(
#         news_uid=news_uid,
#         user_uid=user_uid,
#         comment_text=comment_text
#     )

#     news.comments_count += 1

#     db.add(comment)
#     db.commit()
#     db.refresh(comment)

#     return {
#         "message": "Comment added",
#         "comment_id": comment.id
#     }

# #-----------------------------------------------
# # GET COMMENTS
# #------------------------------------------------
# @router.delete("/user/news/{news_uid}/comment/{comment_id}",tags=["News Engagement"])
# def delete_comment(news_uid: str, comment_id: int, user_uid: str, db: Session = Depends(get_db)):

#     comment = db.query(Comment).filter(
#         Comment.id == comment_id,
#         Comment.news_uid == news_uid,
#         Comment.user_uid == user_uid
#     ).first()

#     if not comment:
#         raise HTTPException(404, "Comment not found or unauthorized")

#     news = db.query(News).filter_by(news_uid=news_uid).first()

#     if news and news.comments_count > 0:
#         news.comments_count -= 1

#     db.delete(comment)
#     db.commit()

#     return {"message": "Comment deleted"}


# @router.get("/news/{news_uid}/comments",tags=["News Engagement"])
# def get_comments(
#     news_uid: str,
#     page: int = 1,
#     limit: int = 20,
#     db: Session = Depends(get_db)
# ):

#     offset = (page - 1) * limit

#     comments = db.query(Comment).filter(
#         Comment.news_uid == news_uid
#     ).order_by(
#         desc(Comment.created_at)
#     ).offset(offset).limit(limit).all()

#     return comments


# @router.post("/user/news/{news_uid}/like",tags=["News Engagement"])
# def like_news(news_uid: str, user_uid: str, db: Session = Depends(get_db)):

#     news = db.query(News).filter_by(news_uid=news_uid).first()

#     if not news:
#         raise HTTPException(404, "News not found")

#     existing = db.query(Reaction).filter(
#         Reaction.news_uid == news_uid,
#         Reaction.user_uid == user_uid
#     ).first()

#     if existing:
#         raise HTTPException(400, "Already liked")

#     reaction = Reaction(
#         news_uid=news_uid,
#         user_uid=user_uid,
#         reaction_type=1
#     )

#     news.likes_count += 1

#     db.add(reaction)
#     db.commit()

#     return {"message": "News liked"}

# #-----------------------------------------------
# # UNLIKED NEWS
# #------------------------------------------------

# @router.delete("/user/news/{news_uid}/like",tags=["News Engagement"])
# def unlike_news(news_uid: str, user_uid: str, db: Session = Depends(get_db)):

#     reaction = db.query(Reaction).filter(
#         Reaction.news_uid == news_uid,
#         Reaction.user_uid == user_uid
#     ).first()

#     if not reaction:
#         raise HTTPException(404, "Like not found")

#     news = db.query(News).filter_by(news_uid=news_uid).first()

#     if news.likes_count > 0:
#         news.likes_count -= 1

#     db.delete(reaction)
#     db.commit()

#     return {"message": "Like removed"}

# #-----------------------------------------------
# # Record View
# #------------------------------------------------
# @router.post("/user/news/{news_uid}/view", tags=["News Engagement"])
# def record_view(news_uid: str, user_uid: Optional[str] = None, db: Session = Depends(get_db)):

#     news = db.query(News).filter_by(news_uid=news_uid).first()

#     if not news:
#         raise HTTPException(404, "News not found")

#     view = NewsView(
#         news_uid=news_uid,
#         user_uid=user_uid
#     )

#     news.views_count += 1

#     db.add(view)
#     db.commit()

#     return {"message": "View recorded"}
# #-----------------------------------------------
# # Record View
# #------------------------------------------------

# @router.delete("/user/news/{news_uid}", status_code=status.HTTP_204_NO_CONTENT)
# def delete_news_by_user(news_uid: str, user_uid: str, db: Session = Depends(get_db)):
#     news = db.query(News).filter_by(news_uid=news_uid, user_uid=user_uid).first()
#     if not news:
#         raise HTTPException(status_code=404, detail="News not found or unauthorized")
    
#     db.delete(news)
#     db.commit()
#     return {"detail": "Your news has been deleted"}



# @router.get("/search", tags=["Search"])
# def realtime_search(
#     q: Optional[str] = Query(None, description="Search keyword"),
#     state_id: Optional[int] = None,
#     district_id: Optional[int] = None,
#     city_id: Optional[int] = None,
#     start_date: Optional[datetime] = None,
#     end_date: Optional[datetime] = None,
#     db: Session = Depends(get_db)
# ):
#     """
#     Real-time search across approved news.
#     Searches title, summary, source name, reporter username, category.
#     """

#     # ✅ FIX: is_approved is INTEGER (0/1)
#     query = db.query(News).filter(News.is_approved == 1)

#     # 🔎 Keyword Search
#     if q:
#         query = (
#             query.join(User, News.user_uid == User.user_uid)
#                  .outerjoin(News.categories)   # ✅ ONLY THIS (no extra Category join)
#                  .filter(
#                     or_(
#                         News.title.ilike(f"%{q}%"),
#                         News.summary.ilike(f"%{q}%"),
#                         News.source_name.ilike(f"%{q}%"),
#                         User.user_name.ilike(f"%{q}%"),
#                         Category.name.ilike(f"%{q}%")
#                     )
#                  )
#         )

#     # 📍 Location Filters
#     if city_id:
#         query = query.filter(News.city_id == city_id)

#     elif district_id:
#         query = query.join(City).filter(City.district_id == district_id)

#     elif state_id:
#         query = query.join(City).join(District).filter(District.state_id == state_id)

#     # 📅 Date Filters
#     if start_date:
#         query = query.filter(News.created_at >= start_date)

#     if end_date:
#         query = query.filter(News.created_at <= end_date)

#     # ⚡ Prevent duplicates + order + limit for real-time speed
#     news_results = (
#         query.distinct()
#              .order_by(News.created_at.desc())
#              .limit(20)
#              .all()
#     )

#     return [
#         {
#             "news_uid": n.news_uid,
#             "title": n.title,
#             "summary": n.summary,
#             "image_url": n.image_url,
#             "source_name": n.source_name,
#             "created_at": n.created_at,
#         }
#         for n in news_results
#     ]




# @router.post("/news", response_model=NewsOut)
# def create_news(news: NewsCreate, db: Session = Depends(get_db)):
#     # 1️⃣ Verify user exists
#     user = db.query(User).filter_by(user_uid=news.user_uid).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     # 2️⃣ Verify language exists
#     language = db.query(Language).filter_by(id=news.language_id).first()
#     if not language:
#         raise HTTPException(status_code=404, detail="Language not found")

#     # 3️⃣ Handle optional city_id
#     city, district, state = None, None, None
#     if news.city_id:   # only if provided
#         city = db.query(City).filter_by(id=news.city_id).first()
#         if not city:
#             raise HTTPException(status_code=404, detail="City not found")
#         district = city.district
#         state = district.state

#     # 4️⃣ Generate unique ID
#     news_uid = generate_news_uid()

#     # 5️⃣ Create new News object
#     new_news = News(
#     news_uid=news_uid,
#     title=news.title,
#     summary=news.summary,
#     image_url=news.image_url,
#     language_id=news.language_id,
#     user_uid=news.user_uid,
#     city_id=news.city_id if news.city_id else None,   # ✅ Important fix
#     source_url=news.source_url if news.source_url else None,
#     source_name=news.source_name if news.source_name else None,
# )

#     # 6️⃣ Attach categories
#     if news.category_ids:
#         categories = db.query(Category).filter(Category.id.in_(news.category_ids)).all()
#         new_news.categories = categories

#     # 7️⃣ Save to DB
#     db.add(new_news)
#     db.commit()
#     db.refresh(new_news)

#     # 8️⃣ Build response safely
#     return NewsOut(
#         news_uid=news_uid,
#         title=new_news.title,
#         summary=new_news.summary,
#         image_url=new_news.image_url,
#         language={"id": language.id, "code": language.code, "name": language.name},
#         user_uid=new_news.user_uid,
#         posted_username=user.user_name,
#         posted_userid=user.user_uid,
#         source_url=new_news.source_url,
#         source_name=new_news.source_name,
#         is_approved=new_news.is_approved,
#         created_at=new_news.created_at,
#         city={"id": city.id, "name": city.name} if city else None,
#         district={"id": district.id, "name": district.name} if district else None,
#         state={"id": state.id, "name": state.name} if state else None,
#         category_ids=[cat.id for cat in new_news.categories]
#     )


# @router.post("/v1/user/news/{news_uid}/share", tags=["News Engagement"])
# def share_news(news_uid: str, user_uid: str, platform: str = None, db: Session = Depends(get_db)):

#     news = db.query(News).filter(News.news_uid == news_uid).first()
#     if not news:
#         raise HTTPException(status_code=404, detail="News not found")

#     existing = db.query(Share).filter(
#         Share.news_uid == news_uid,
#         Share.user_uid == user_uid
#     ).first()

#     if existing:
#         return {"message": "Already shared"}

#     share = Share(
#         news_uid=news_uid,
#         user_uid=user_uid,
#         platform=platform
#     )

#     db.add(share)
#     db.commit()

#     return {"message": "News shared"}



# @router.get("/v1/news/{news_uid}/engagement", tags=["News Engagement"])
# def get_news_engagement(
#     news_uid: str,
#     user_uid: str | None = Query(None),
#     db: Session = Depends(get_db)
# ):

#     news = db.query(News).filter(News.news_uid == news_uid).first()

#     if not news:
#         raise HTTPException(status_code=404, detail="News not found")

#     # Counts
#     views = db.query(NewsView).filter(NewsView.news_uid == news_uid).count()

#     likes = db.query(Reaction).filter(
#         Reaction.news_uid == news_uid,
#         Reaction.reaction_type == 1
#     ).count()

#     comments = db.query(Comment).filter(
#         Comment.news_uid == news_uid
#     ).count()

#     shares = db.query(Share).filter(
#         Share.news_uid == news_uid
#     ).count()

#     # Check if user liked
#     user_liked = False

#     if user_uid:
#         liked = db.query(Reaction).filter(
#             Reaction.news_uid == news_uid,
#             Reaction.user_uid == user_uid,
#             Reaction.reaction_type == 1
#         ).first()

#         user_liked = True if liked else False

#     return {
#         "news_uid": news_uid,
#         "views": views,
#         "likes": likes,
#         "comments": comments,
#         "shares": shares,
#         "user_liked": user_liked
#     }

# @router.put("/news/{news_uid}", response_model=NewsOut)
# def update_news(news_uid: str, news: NewsCreate, db: Session = Depends(get_db)):

#     existing_news = db.query(News).filter_by(news_uid=news_uid).first()
#     if not existing_news:
#         raise HTTPException(status_code=404, detail="News not found")

#     user = db.query(User).filter_by(user_uid=news.user_uid).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     language = db.query(Language).filter_by(id=news.language_id).first()
#     if not language:
#         raise HTTPException(status_code=404, detail="Language not found")

#     city, district, state = None, None, None

#     if news.city_id:
#         city = db.query(City).filter_by(id=news.city_id).first()
#         if not city:
#             raise HTTPException(status_code=404, detail="City not found")

#         district = city.district
#         state = district.state if district else None

#     # Update fields
#     existing_news.title = news.title
#     existing_news.summary = news.summary
#     existing_news.image_url = news.image_url
#     existing_news.language_id = news.language_id
#     existing_news.city_id = news.city_id
#     existing_news.source_url = news.source_url
#     existing_news.source_name = news.source_name

#     # Update categories
#     if news.category_ids:
#         categories = db.query(Category).filter(
#             Category.id.in_(news.category_ids)
#         ).all()
#         existing_news.categories = categories
#     else:
#         existing_news.categories = []

#     db.commit()
#     db.refresh(existing_news)

#     return NewsOut(
#         news_uid=existing_news.news_uid,
#         title=existing_news.title,
#         summary=existing_news.summary,
#         image_url=existing_news.image_url,
#         language=language,
#         user_uid=existing_news.user_uid,
#         is_approved=existing_news.is_approved,
#         created_at=existing_news.created_at,
#         city=city,
#         district=district,
#         state=state,
#         source_url=existing_news.source_url,
#         source_name=existing_news.source_name,
#         category_ids=[c.id for c in existing_news.categories],

#         engagement={
#             "likes": existing_news.likes_count,
#             "comments": existing_news.comments_count,
#             "shares": existing_news.shares_count,
#             "views": existing_news.views_count,
#             "user_liked": False
#         }
#     )


# @router.get("/news-shorts", response_model=List[VideoItem])
# def get_news_shorts(
#     language: str = Query(..., description="Language code like 'en' or 'te'"),
#     limit: int = 10,
#     db: Session = Depends(get_db)
# ):

#     shorts = db.query(YouTubeShort).filter(
#         YouTubeShort.language == language
#     ).order_by(
#         YouTubeShort.published_at.desc()
#     ).limit(limit).all()

#     return [
#         VideoItem(
#             title=s.title,
#             video_id=s.video_id,
#             thumbnail_url=s.thumbnail_url,
#             channel_title=s.channel_title,
#             published_at=s.published_at.isoformat()
#         ) for s in shorts
#     ]
    
# @router.get("/admin/news-shorts/telugu", response_model=List[VideoItem], tags=["Admin"])
# def fetch_and_store_telugu_shorts(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(admin_required)  # Enforces admin token & role
# ):
#     return fetch_and_store_shorts_by_language("telugu news", "te", db)


# @router.get("/admin/news-shorts/english", response_model=List[VideoItem], tags=["Admin"])
# def fetch_and_store_english_shorts(
#     db: Session = Depends(get_db),
#     current_user: User = Depends(admin_required)  # Enforces admin token & role
# ):
#     return fetch_and_store_shorts_by_language("english news", "en", db)

# def fetch_and_store_shorts_by_language(query: str, lang: str, db: Session):
#     params = {
#         "key": YOUTUBE_API_KEY,
#         "part": "snippet",
#         "q": query,
#         "maxResults": 5,
#         "type": "video",
#         "videoDuration": "short",
#         "order": "date",
#         "videoEmbeddable": "true"
#     }

#     response = requests.get(YOUTUBE_SEARCH_URL, params=params)
#     data = response.json()
#     result = []

#     for item in data.get("items", []):
#         if item["id"]["kind"] == "youtube#video":
#             video_id = item["id"]["videoId"]
#             snippet = item["snippet"]

#             existing = db.query(YouTubeShort).filter_by(video_id=video_id).first()
#             if existing:
#                 continue

#             short = YouTubeShort(
#                 video_id=video_id,
#                 title=snippet["title"],
#                 thumbnail_url=snippet["thumbnails"]["high"]["url"],
#                 channel_title=snippet["channelTitle"],
#                 published_at=snippet["publishedAt"],
#                 video_url=f"https://www.youtube.com/watch?v={video_id}",
#                 language=lang  # ✅ IMPORTANT: Language column
#             )
#             db.add(short)
#             db.commit()

#             result.append(VideoItem(
#                 title=short.title,
#                 video_id=short.video_id,
#                 thumbnail_url=short.thumbnail_url,
#                 channel_title=short.channel_title,
#                 published_at=short.published_at.isoformat(),
#             ))

#     return result

from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
import requests
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, or_
from auth.dependencies import admin_required, get_current_user
from models.base_location import City, District, Language, State
from models.content import Advertisement, Event, Poll, SponsoredPost, YouTubeShort
from models.news import News, NewsFlag, Reaction, Comment, ScheduledNews, Share, NewsView, Category
from database import get_db
from models.user import User, UserPreference
from routes.content_routes import get_active_advertisements
from schemas import BreakingNewsUpdate, NewsCreate, NewsOut, ScheduledNewsCreate, ScheduledNewsOut, ScheduledNewsUpdate, VideoItem
from utility import YOUTUBE_API_KEY, YOUTUBE_SEARCH_URL, generate_news_uid
from database import get_db
from schemas import (
    BreakingNewsUpdate, NewsCreate, NewsOut, VideoItem,
    DailyNewsStats, WeeklyNewsStats, MonthlyNewsStats,
    TopPerformingNews, TrendingNews, NewsFlagCreate, 
    NewsFlagOut, FlagReview, PendingFlagOut
)
from routes.content_routes import get_active_advertisements, get_active_sponsored_posts

from utility import generate_news_uid

router = APIRouter(prefix="/v1", tags=["News"])


# =====================================================
# CREATE NEWS
# =====================================================

@router.post("/news", response_model=NewsOut, status_code=status.HTTP_201_CREATED)
def create_news(news: NewsCreate, db: Session = Depends(get_db)):
    # 1️⃣ Verify user exists
    user = db.query(User).filter_by(user_uid=news.user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 2️⃣ Verify language exists
    language = db.query(Language).filter_by(id=news.language_id).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")

    # 3️⃣ Handle optional city_id
    city, district, state = None, None, None
    if news.city_id:
        city = db.query(City).filter_by(id=news.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        district = city.district
        state = district.state if district else None

    # 4️⃣ Generate unique ID
    news_uid = generate_news_uid()

    # 5️⃣ Create new News object
    new_news = News(
        news_uid=news_uid,
        title=news.title,
        summary=news.summary,
        image_url=news.image_url,
        language_id=news.language_id,
        user_uid=news.user_uid,
        city_id=news.city_id if news.city_id else None,
        source_url=news.source_url if news.source_url else None,
        source_name=news.source_name if news.source_name else None,
        is_approved=0
    )

    # 6️⃣ Attach categories
    if news.category_ids:
        categories = db.query(Category).filter(Category.id.in_(news.category_ids)).all()
        new_news.categories = categories

    # 7️⃣ Save to DB
    db.add(new_news)
    db.commit()
    db.refresh(new_news)

    # 8️⃣ Build response
    return NewsOut(
        news_uid=new_news.news_uid,
        title=new_news.title,
        summary=new_news.summary,
        image_url=new_news.image_url,
        language={"id": language.id, "code": language.code, "name": language.name},
        user_uid=new_news.user_uid,
        posted_username=user.user_name if hasattr(user, 'user_name') else None,
        posted_userid=user.user_uid,
        source_url=new_news.source_url,
        source_name=new_news.source_name,
        is_approved=new_news.is_approved,
        created_at=new_news.created_at,
        city={"id": city.id, "name": city.name} if city else None,
        district={"id": district.id, "name": district.name} if district else None,
        state={"id": state.id, "name": state.name} if state else None,
        category_ids=[cat.id for cat in new_news.categories]
    )


# =====================================================
# POST BREAKING NEWS
# =====================================================

@router.put("/admin/news/{news_uid}/breaking", tags=["Admin"])
def set_breaking_news(
    news_uid: str,
    payload: BreakingNewsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(404, "News not found")

    if payload.is_breaking:
        news.is_breaking = True
        news.breaking_priority = payload.priority
        news.breaking_expires_at = datetime.now(timezone.utc) + timedelta(hours=payload.expire_hours)
    else:
        news.is_breaking = False
        news.breaking_priority = 0
        news.breaking_expires_at = None

    db.commit()
    return {"message": "Breaking news updated", "news_uid": news_uid}


@router.get("/news/breaking")
def get_breaking_news(db: Session = Depends(get_db)):
    breaking_news = db.query(News).filter(
        News.is_breaking == True,
        News.breaking_expires_at > datetime.now(timezone.utc),
        News.is_approved == 1
    ).order_by(desc(News.breaking_priority)).limit(5).all()

    return [
        {
            "news_uid": n.news_uid,
            "title": n.title,
            "summary": n.summary[:150] if n.summary else None,
            "image_url": n.image_url,
            "priority": n.breaking_priority,
            "expires_at": n.breaking_expires_at
        }
        for n in breaking_news
    ]


# =====================================================
# GET News Feed
# =====================================================




# =========================================================
# NEWS RANKING ALGORITHM
# =========================================================

def calculate_news_score(news, user_pref, current_time):
    """
    Calculate ranking score for a news article
    
    Score Components:
    - Recency Score (40% weight): Newer news gets higher score
    - Engagement Score (30% weight): Views, likes, comments, shares
    - Location Score (20% weight): User's city/district/state match
    - Category Score (10% weight): User's preferred categories
    - Breaking News Boost: +50 points for breaking news
    """
    score = 0
    
    # =========================================================
    # 1. RECENCY SCORE (0-100)
    # =========================================================
    age_hours = (current_time - news.created_at).total_seconds() / 3600
    
    if age_hours < 1:  # Less than 1 hour old
        recency_score = 100
    elif age_hours < 6:  # 1-6 hours
        recency_score = 80
    elif age_hours < 24:  # 6-24 hours
        recency_score = 60
    elif age_hours < 72:  # 1-3 days
        recency_score = 40
    elif age_hours < 168:  # 3-7 days
        recency_score = 20
    else:
        recency_score = 10
    
    score += recency_score * 0.4  # 40% weight
    
    # =========================================================
    # 2. ENGAGEMENT SCORE (0-100)
    # =========================================================
    # Normalize engagement (max reference: 1000 views, 100 likes, 50 comments, 20 shares)
    engagement_score = min(
        (news.views_count / 1000) * 50 +
        (news.likes_count / 100) * 30 +
        (news.comments_count / 50) * 15 +
        (news.shares_count / 20) * 5,
        100
    )
    
    score += engagement_score * 0.3  # 30% weight
    
    # =========================================================
    # 3. LOCATION SCORE (0-100)
    # =========================================================
    location_score = 0
    
    if user_pref:
        if user_pref.city_id and news.city_id == user_pref.city_id:
            location_score = 100  # Exact city match
        elif user_pref.district_id and news.city_id and news.city.district_id == user_pref.district_id:
            location_score = 80  # District match
        elif user_pref.state_id and news.city_id and news.city.district.state_id == user_pref.state_id:
            location_score = 60  # State match
        elif user_pref.city_id and not news.city_id:
            location_score = 30  # No location, but user has preference
        else:
            location_score = 10  # No match
    
    score += location_score * 0.2  # 20% weight
    
    # =========================================================
    # 4. CATEGORY SCORE (0-100)
    # =========================================================
    category_score = 0
    
    if user_pref and user_pref.categories and news.categories:
        user_category_ids = [c.id for c in user_pref.categories]
        news_category_ids = [c.id for c in news.categories]
        
        matching_categories = set(user_category_ids) & set(news_category_ids)
        
        if matching_categories:
            # More matching categories = higher score
            match_ratio = len(matching_categories) / len(news_category_ids)
            category_score = min(match_ratio * 100, 100)
    
    score += category_score * 0.1  # 10% weight
    
    # =========================================================
    # 5. BREAKING NEWS BOOST
    # =========================================================
    if news.is_breaking:
        # Check if still breaking (not expired)
        if not news.breaking_expires_at or news.breaking_expires_at > current_time:
            score += 50  # +50 points for breaking news
    
    return round(score, 2)


# =========================================================
# NEWS FEED API
# =========================================================
# =========================================================
# HELPER FUNCTIONS
# =========================================================

def calculate_news_score(news, user_pref, current_time):
    """
    Calculate ranking score for a news article
    
    Score Components:
    - Recency Score (40% weight): Newer news gets higher score
    - Engagement Score (30% weight): Views, likes, comments, shares
    - Location Score (20% weight): User's city/district/state match
    - Category Score (10% weight): User's preferred categories
    - Breaking News Boost: +50 points for breaking news
    """
    score = 0
    
    # =========================================================
    # 1. RECENCY SCORE (0-100)
    # =========================================================
    # Ensure both datetimes are timezone-aware
    news_created = news.created_at
    if news_created.tzinfo is None:
        news_created = news_created.replace(tzinfo=timezone.utc)
    
    age_hours = (current_time - news_created).total_seconds() / 3600
    
    if age_hours < 1:
        recency_score = 100
    elif age_hours < 6:
        recency_score = 80
    elif age_hours < 24:
        recency_score = 60
    elif age_hours < 72:
        recency_score = 40
    elif age_hours < 168:
        recency_score = 20
    else:
        recency_score = 10
    
    score += recency_score * 0.4
    
    # =========================================================
    # 2. ENGAGEMENT SCORE (0-100)
    # =========================================================
    engagement_score = min(
        (news.views_count / 1000) * 50 +
        (news.likes_count / 100) * 30 +
        (news.comments_count / 50) * 15 +
        (news.shares_count / 20) * 5,
        100
    )
    
    score += engagement_score * 0.3
    
    # =========================================================
    # 3. LOCATION SCORE (0-100)
    # =========================================================
    location_score = 0
    
    if user_pref:
        if user_pref.city_id and news.city_id == user_pref.city_id:
            location_score = 100
        elif user_pref.district_id and news.city_id and hasattr(news.city, 'district_id') and news.city.district_id == user_pref.district_id:
            location_score = 80
        elif user_pref.state_id and news.city_id and hasattr(news.city, 'district') and news.city.district and news.city.district.state_id == user_pref.state_id:
            location_score = 60
        elif user_pref.city_id and not news.city_id:
            location_score = 30
        else:
            location_score = 10
    
    score += location_score * 0.2
    
    # =========================================================
    # 4. CATEGORY SCORE (0-100)
    # =========================================================
    category_score = 0
    
    if user_pref and hasattr(user_pref, 'categories') and user_pref.categories and news.categories:
        user_category_ids = [c.id for c in user_pref.categories]
        news_category_ids = [c.id for c in news.categories]
        
        matching_categories = set(user_category_ids) & set(news_category_ids)
        
        if matching_categories:
            match_ratio = len(matching_categories) / len(news_category_ids)
            category_score = min(match_ratio * 100, 100)
    
    score += category_score * 0.1
    
    # =========================================================
    # 5. BREAKING NEWS BOOST
    # =========================================================
    if news.is_breaking:
        if not news.breaking_expires_at or news.breaking_expires_at > current_time:
            score += 50
    
    return round(score, 2)


# =========================================================
# NEWS FEED API (Using Current User from Token)
# =========================================================

@router.get("/feed", response_model=dict)
def get_news_feed(
    cursor: Optional[datetime] = Query(None, description="Pagination cursor (created_at timestamp)"),
    limit: int = Query(20, ge=5, le=50, description="Number of items per page"),
    session_id: Optional[str] = Query(None, description="Session ID for ad rotation"),
    include_ads: bool = Query(True, description="Include advertisements"),
    include_sponsored: bool = Query(True, description="Include sponsored posts"),
    include_events: bool = Query(True, description="Include upcoming events"),
    include_polls: bool = Query(True, description="Include active polls"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Personalized news feed with ranking algorithm and strategic ad placement.
    Uses the authenticated user from the token for personalization.
    """
    current_time = datetime.now(timezone.utc)
    
    # Get user_uid from current_user (from token)
    user_uid = current_user.user_uid
    
    # Make cursor timezone-aware if provided
    if cursor:
        if cursor.tzinfo is None:
            cursor = cursor.replace(tzinfo=timezone.utc)
    
    # =========================================================
    # 1. GET USER PREFERENCES
    # =========================================================
    user_pref = db.query(UserPreference).options(
        joinedload(UserPreference.categories)
    ).filter(UserPreference.user_uid == user_uid).first()
    
    if not user_pref:
        raise HTTPException(status_code=404, detail="User preferences not found. Please set your preferences first.")
    
    # =========================================================
    # 2. GET NEWS WITH RANKING
    # =========================================================
    
    # Base query: approved news in user's language
    news_query = db.query(News).options(
        joinedload(News.categories),
        joinedload(News.city).joinedload(City.district).joinedload(District.state),
        joinedload(News.language)
    ).filter(
        News.is_approved == 1,
        News.language_id == user_pref.language_id
    )
    
    # Apply cursor pagination
    if cursor:
        news_query = news_query.filter(News.created_at < cursor)
    
    # Get all eligible news (get extra for ranking)
    all_news = news_query.all()
    
    # Calculate scores for each news article
    scored_news = []
    for news in all_news:
        score = calculate_news_score(news, user_pref, current_time)
        scored_news.append((score, news))
    
    # Sort by score (highest first)
    scored_news.sort(key=lambda x: x[0], reverse=True)
    
    # Take top news for feed (limit + extra for ad insertion)
    ranked_news = [news for score, news in scored_news[:limit + 10]]
    
    # =========================================================
    # 3. GET ADS (Targeted) - USING HELPER
    # =========================================================
    
    ads = []
    if include_ads:
        try:
            # Import the helper function from content_routes
            from routes.content_routes import get_active_ads_helper
            ads_response = get_active_ads_helper(
                user_uid=user_uid,
                placement="feed",
                limit=10,
                session_id=session_id,
                include_premium=True,
                premium_limit=1,
                exclude_seen=True,
                db=db
            )
            ads = ads_response.get("ads", [])
            print(f"DEBUG: Retrieved {len(ads)} ads")
        except Exception as e:
            print(f"Error fetching ads: {e}")
            ads = []
    
    # =========================================================
    # 4. GET SPONSORED POSTS - USING HELPER
    # =========================================================
    
    sponsored_posts = []
    if include_sponsored:
        try:
            from routes.content_routes import get_active_sponsored_posts_helper
            sponsored_response = get_active_sponsored_posts_helper(
                user_uid=user_uid,
                limit=5,
                session_id=session_id,
                exclude_seen=True,
                db=db
            )
            sponsored_posts = sponsored_response.get("posts", [])
            print(f"DEBUG: Retrieved {len(sponsored_posts)} sponsored posts")
        except Exception as e:
            print(f"Error fetching sponsored posts: {e}")
            sponsored_posts = []
    
    # =========================================================
    # 5. GET UPCOMING EVENTS
    # =========================================================
    
    events = []
    if include_events:
        events = db.query(Event).filter(
            Event.is_approved == True,
            Event.event_date >= current_time.date()
        ).order_by(Event.event_date.asc()).limit(3).all()
        print(f"DEBUG: Retrieved {len(events)} events")
    
    # =========================================================
    # 6. GET ACTIVE POLLS
    # =========================================================
    
    polls = []
    if include_polls:
        polls = db.query(Poll).filter(
            Poll.is_approved == True,
            (Poll.expires_at == None) | (Poll.expires_at > current_time)
        ).order_by(desc(Poll.created_at)).limit(2).all()
        print(f"DEBUG: Retrieved {len(polls)} polls")
    
    # =========================================================
    # 7. BUILD FEED WITH STRATEGIC AD PLACEMENT
    # =========================================================
    
    feed = []
    ad_index = 0
    sponsored_index = 0
    event_index = 0
    poll_index = 0
    news_index = 0
    
    # Helper function to get news data
    def get_news_data(news):
        return {
            "news_uid": news.news_uid,
            "title": news.title,
            "summary": news.summary[:200] if news.summary else None,
            "image_url": news.image_url,
            "created_at": news.created_at.isoformat() if news.created_at else None,
            "views": news.views_count,
            "likes": news.likes_count,
            "comments": news.comments_count,
            "shares": news.shares_count,
            "is_breaking": news.is_breaking,
            "category_names": [c.name for c in news.categories] if news.categories else [],
            "location": {
                "city": news.city.name if news.city else None,
                "district": news.city.district.name if news.city and news.city.district else None,
                "state": news.city.district.state.name if news.city and news.city.district and news.city.district.state else None
            }
        }
    
    print(f"DEBUG: Starting feed build - Ads: {len(ads)}, Sponsored: {len(sponsored_posts)}, Events: {len(events)}, Polls: {len(polls)}, News: {len(ranked_news)}")
    
    # POSITION 0: PREMIUM AD
    if ads and len(ads) > 0 and hasattr(ads[0], 'priority') and ads[0].priority == "premium":
        feed.append({
            "type": "ad",
            "priority": "premium",
            "is_premium": True,
            "data": {
                "id": ads[0].id,
                "title": ads[0].title,
                "image_url": ads[0].image_url,
                "redirect_url": ads[0].redirect_url,
                "cta_text": "Learn More"
            },
            "position": len(feed)
        })
        ad_index += 1
        print(f"DEBUG: Added premium ad at position {len(feed)-1}")
    
    # POSITIONS 1-3: Top News
    for i in range(min(3, len(ranked_news))):
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": get_news_data(news),
                "position": len(feed),
                "ranking_score": scored_news[news_index][0] if news_index < len(scored_news) else 0
            })
            news_index += 1
            print(f"DEBUG: Added news at position {len(feed)-1}")
    
    # POSITION 4: CITY/DISTRICT AD
    if ad_index < len(ads) and hasattr(ads[ad_index], 'priority') and ads[ad_index].priority in ["city", "district"]:
        ad = ads[ad_index]
        feed.append({
            "type": "ad",
            "priority": ad.priority,
            "data": {
                "id": ad.id,
                "title": ad.title,
                "image_url": ad.image_url,
                "redirect_url": ad.redirect_url,
                "cta_text": "Learn More"
            },
            "position": len(feed)
        })
        ad_index += 1
        print(f"DEBUG: Added city/district ad at position {len(feed)-1}")
    else:
        print("DEBUG: No city/district ad available")
        # Fill with news if no ad
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": get_news_data(news),
                "position": len(feed),
                "ranking_score": scored_news[news_index][0] if news_index < len(scored_news) else 0
            })
            news_index += 1
    
    # POSITIONS 5-7: News
    for i in range(3):
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": get_news_data(news),
                "position": len(feed),
                "ranking_score": scored_news[news_index][0] if news_index < len(scored_news) else 0
            })
            news_index += 1
        else:
            break
    
    # POSITION 8: STATE/LANGUAGE AD
    if ad_index < len(ads) and hasattr(ads[ad_index], 'priority') and ads[ad_index].priority in ["state", "language"]:
        ad = ads[ad_index]
        feed.append({
            "type": "ad",
            "priority": ad.priority,
            "data": {
                "id": ad.id,
                "title": ad.title,
                "image_url": ad.image_url,
                "redirect_url": ad.redirect_url,
                "cta_text": "Learn More"
            },
            "position": len(feed)
        })
        ad_index += 1
        print(f"DEBUG: Added state/language ad at position {len(feed)-1}")
    else:
        print("DEBUG: No state/language ad available")
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": get_news_data(news),
                "position": len(feed),
                "ranking_score": scored_news[news_index][0] if news_index < len(scored_news) else 0
            })
            news_index += 1
    
    # POSITIONS 9-11: News + Mixed Content
    for i in range(3):
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": get_news_data(news),
                "position": len(feed),
                "ranking_score": scored_news[news_index][0] if news_index < len(scored_news) else 0
            })
            news_index += 1
        
        # Insert sponsored post after first news in this block
        if i == 0 and sponsored_index < len(sponsored_posts):
            post = sponsored_posts[sponsored_index]
            feed.append({
                "type": "sponsored",
                "data": {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content[:150] if post.content else None,
                    "image_url": post.image_url,
                    "cta_text": post.cta_text,
                    "cta_url": post.cta_url
                },
                "position": len(feed)
            })
            sponsored_index += 1
            print(f"DEBUG: Added sponsored post at position {len(feed)-1}")
        
        # Insert event after second news
        if i == 1 and event_index < len(events):
            event = events[event_index]
            feed.append({
                "type": "event",
                "data": {
                    "event_uid": event.event_uid,
                    "title": event.title,
                    "event_date": event.event_date.isoformat() if event.event_date else None,
                    "location": event.location,
                    "is_online": event.is_online
                },
                "position": len(feed)
            })
            event_index += 1
            print(f"DEBUG: Added event at position {len(feed)-1}")
        
        # Insert poll after third news
        if i == 2 and poll_index < len(polls):
            poll = polls[poll_index]
            feed.append({
                "type": "poll",
                "data": {
                    "poll_uid": poll.poll_uid,
                    "question": poll.question,
                    "options": poll.options[:2] if poll.options else [],
                    "total_votes": sum(poll.votes) if poll.votes else 0
                },
                "position": len(feed)
            })
            poll_index += 1
            print(f"DEBUG: Added poll at position {len(feed)-1}")
    
    # POSITION 12: NATIONAL AD
    if ad_index < len(ads) and hasattr(ads[ad_index], 'priority') and ads[ad_index].priority == "national":
        ad = ads[ad_index]
        feed.append({
            "type": "ad",
            "priority": "national",
            "data": {
                "id": ad.id,
                "title": ad.title,
                "image_url": ad.image_url,
                "redirect_url": ad.redirect_url,
                "cta_text": "Learn More"
            },
            "position": len(feed)
        })
        ad_index += 1
        print(f"DEBUG: Added national ad at position {len(feed)-1}")
    else:
        print("DEBUG: No national ad available")
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": get_news_data(news),
                "position": len(feed),
                "ranking_score": scored_news[news_index][0] if news_index < len(scored_news) else 0
            })
            news_index += 1
    
    # POSITIONS 13-15: News
    for i in range(3):
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": get_news_data(news),
                "position": len(feed),
                "ranking_score": scored_news[news_index][0] if news_index < len(scored_news) else 0
            })
            news_index += 1
        else:
            break
    
    # POSITION 16: ROTATED LOCAL AD
    if ad_index < len(ads) and hasattr(ads[ad_index], 'priority') and ads[ad_index].priority in ["city", "district"]:
        ad = ads[ad_index]
        feed.append({
            "type": "ad",
            "priority": ad.priority,
            "data": {
                "id": ad.id,
                "title": ad.title,
                "image_url": ad.image_url,
                "redirect_url": ad.redirect_url,
                "cta_text": "Learn More"
            },
            "position": len(feed)
        })
        ad_index += 1
        print(f"DEBUG: Added rotated local ad at position {len(feed)-1}")
    else:
        print("DEBUG: No rotated local ad available")
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": get_news_data(news),
                "position": len(feed),
                "ranking_score": scored_news[news_index][0] if news_index < len(scored_news) else 0
            })
            news_index += 1
    
    # REMAINING NEWS ITEMS
    while news_index < len(ranked_news):
        news = ranked_news[news_index]
        feed.append({
            "type": "news",
            "data": get_news_data(news),
            "position": len(feed),
            "ranking_score": scored_news[news_index][0] if news_index < len(scored_news) else 0
        })
        news_index += 1
    
    # GET NEXT CURSOR
    next_cursor = ranked_news[-1].created_at if ranked_news else None
    if next_cursor and next_cursor.tzinfo is None:
        next_cursor = next_cursor.replace(tzinfo=timezone.utc)
    
    print(f"=== FEED BUILD SUMMARY ===")
    print(f"Total feed items: {len(feed)}")
    print(f"News items: {news_index}")
    print(f"Ads shown: {ad_index}")
    print(f"Sponsored shown: {sponsored_index}")
    print(f"Events shown: {event_index}")
    print(f"Polls shown: {poll_index}")
    
    return {
        "items": feed[:limit],
        "metadata": {
            "total_items": len(feed),
            "returned_items": len(feed[:limit]),
            "next_cursor": next_cursor.isoformat() if next_cursor else None,
            "has_more": len(ranked_news) >= limit,
            "user_uid": user_uid,
            "ranking_summary": {
                "total_scored": len(scored_news),
                "top_score": scored_news[0][0] if scored_news else 0,
                "avg_score": sum(s for s, _ in scored_news[:20]) / min(20, len(scored_news)) if scored_news else 0
            },
            "ad_metadata": {
                "ads_shown": ad_index,
                "premium_ad_shown": ad_index > 0 and feed and len(feed) > 0 and feed[0].get("type") == "ad" if feed else False,
                "sponsored_shown": sponsored_index,
                "events_shown": event_index,
                "polls_shown": poll_index
            }
        }
    }
@router.get("/feed0", response_model=dict)
def get_news_feed(
    user_uid: str = Query(..., description="User UID for personalization"),
    cursor: Optional[datetime] = Query(None, description="Pagination cursor (created_at timestamp)"),
    limit: int = Query(20, ge=5, le=50, description="Number of items per page"),
    session_id: Optional[str] = Query(None, description="Session ID for ad rotation"),
    include_ads: bool = Query(True, description="Include advertisements"),
    include_sponsored: bool = Query(True, description="Include sponsored posts"),
    include_events: bool = Query(True, description="Include upcoming events"),
    include_polls: bool = Query(True, description="Include active polls"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Personalized news feed with ranking algorithm and strategic ad placement.
    
    Feed Structure:
    - Position 0: Premium Ad (if available) - Highest revenue
    - Positions 1-3: Top ranked news
    - Position 4: City/District Ad - High revenue
    - Positions 5-7: News
    - Position 8: State/Language Ad - Medium revenue
    - Positions 9-11: News + Sponsored/Events/Polls
    - Position 12: National Ad - Fill inventory
    - Positions 13-15: News
    - Position 16: Rotated Local Ad
    - Remaining: More news
    """
    current_time = datetime.utcnow()
    
    # =========================================================
    # 1. GET USER PREFERENCES
    # =========================================================
    user_pref = db.query(UserPreference).filter(
        UserPreference.user_uid == user_uid
    ).first()
    
    if not user_pref:
        raise HTTPException(status_code=404, detail="User preferences not found")
    
    # =========================================================
    # 2. GET NEWS WITH RANKING
    # =========================================================
    
    # Base query: approved news in user's language
    news_query = db.query(News).options(
        joinedload(News.categories),
        joinedload(News.city).joinedload(City.district).joinedload(District.state),
        joinedload(News.language)
    ).filter(
        News.is_approved == 1,
        News.language_id == user_pref.language_id
    )
    
    # Apply cursor pagination
    if cursor:
        news_query = news_query.filter(News.created_at < cursor)
    
    # Get all eligible news (get extra for ranking)
    all_news = news_query.all()
    
    # Calculate scores for each news article
    scored_news = []
    for news in all_news:
        score = calculate_news_score(news, user_pref, current_time)
        scored_news.append((score, news))
    
    # Sort by score (highest first)
    scored_news.sort(key=lambda x: x[0], reverse=True)
    
    # Take top news for feed (limit + extra for ad insertion)
    ranked_news = [news for score, news in scored_news[:limit + 10]]
    
    # =========================================================
    # 3. GET ADS (Targeted)
    # =========================================================
    
    ads = []
    if include_ads:
        ads_response = get_active_advertisements(
            user_uid=user_uid,
            placement="feed",
            limit=10,
            session_id=session_id,
            include_premium=True,
            premium_limit=1,
            exclude_seen=True,
            db=db
        )
        ads = ads_response.get("ads", [])
    
    # =========================================================
    # 4. GET SPONSORED POSTS
    # =========================================================
    
    sponsored_posts = []
    if include_sponsored:
        sponsored_response = get_active_sponsored_posts(
            user_uid=user_uid,
            limit=5,
            session_id=session_id,
            exclude_seen=True,
            db=db
        )
        sponsored_posts = sponsored_response.get("posts", [])
    
    # =========================================================
    # 5. GET UPCOMING EVENTS
    # =========================================================
    
    events = []
    if include_events:
        events = db.query(Event).filter(
            Event.is_approved == True,
            Event.event_date >= current_time.date()
        ).order_by(Event.event_date.asc()).limit(3).all()
    
    # =========================================================
    # 6. GET ACTIVE POLLS
    # =========================================================
    
    polls = []
    if include_polls:
        polls = db.query(Poll).filter(
            Poll.is_approved == True,
            (Poll.expires_at == None) | (Poll.expires_at > current_time)
        ).order_by(desc(Poll.created_at)).limit(2).all()
    
    # =========================================================
    # 7. BUILD FEED WITH STRATEGIC AD PLACEMENT
    # =========================================================
    
    feed = []
    ad_index = 0
    sponsored_index = 0
    event_index = 0
    poll_index = 0
    news_index = 0
    
    # =========================================================
    # POSITION 0: PREMIUM AD (Highest revenue - First impression)
    # =========================================================
    if ads and ads[0].priority == "premium":
        feed.append({
            "type": "ad",
            "priority": "premium",
            "is_premium": True,
            "data": {
                "id": ads[0].id,
                "title": ads[0].title,
                "image_url": ads[0].image_url,
                "redirect_url": ads[0].redirect_url,
                "cta_text": "Learn More",
                "priority_level": 0
            },
            "position": 0
        })
        ad_index += 1
    
    # =========================================================
    # POSITIONS 1-3: Top News (3 items)
    # =========================================================
    for i in range(min(3, len(ranked_news))):
        news = ranked_news[news_index]
        feed.append({
            "type": "news",
            "data": {
                "news_uid": news.news_uid,
                "title": news.title,
                "summary": news.summary[:200] if news.summary else None,
                "image_url": news.image_url,
                "created_at": news.created_at,
                "views": news.views_count,
                "likes": news.likes_count,
                "comments": news.comments_count,
                "shares": news.shares_count,
                "is_breaking": news.is_breaking,
                "category_names": [c.name for c in news.categories],
                "location": {
                    "city": news.city.name if news.city else None,
                    "district": news.city.district.name if news.city and news.city.district else None,
                    "state": news.city.district.state.name if news.city and news.city.district and news.city.district.state else None
                }
            },
            "position": i + 1,
            "ranking_score": calculate_news_score(news, user_pref, current_time)
        })
        news_index += 1
    
    # =========================================================
    # POSITION 4: CITY/DISTRICT AD (High Revenue)
    # =========================================================
    if ad_index < len(ads) and ads[ad_index].priority in ["city", "district"]:
        ad = ads[ad_index]
        feed.append({
            "type": "ad",
            "priority": ad.priority,
            "data": {
                "id": ad.id,
                "title": ad.title,
                "image_url": ad.image_url,
                "redirect_url": ad.redirect_url,
                "cta_text": "Learn More",
                "priority_level": ad.priority_level
            },
            "position": 4
        })
        ad_index += 1
    
    # =========================================================
    # POSITIONS 5-7: News (3 items)
    # =========================================================
    for i in range(3):
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": {
                    "news_uid": news.news_uid,
                    "title": news.title,
                    "summary": news.summary[:200] if news.summary else None,
                    "image_url": news.image_url,
                    "created_at": news.created_at,
                    "views": news.views_count,
                    "likes": news.likes_count,
                    "comments": news.comments_count,
                    "shares": news.shares_count,
                    "is_breaking": news.is_breaking,
                    "category_names": [c.name for c in news.categories]
                },
                "position": i + 5,
                "ranking_score": calculate_news_score(news, user_pref, current_time)
            })
            news_index += 1
        else:
            break
    
    # =========================================================
    # POSITION 8: STATE/LANGUAGE AD (Medium Revenue)
    # =========================================================
    if ad_index < len(ads) and ads[ad_index].priority in ["state", "language"]:
        ad = ads[ad_index]
        feed.append({
            "type": "ad",
            "priority": ad.priority,
            "data": {
                "id": ad.id,
                "title": ad.title,
                "image_url": ad.image_url,
                "redirect_url": ad.redirect_url,
                "cta_text": "Learn More"
            },
            "position": 8
        })
        ad_index += 1
    
    # =========================================================
    # POSITIONS 9-11: News + Mixed Content
    # =========================================================
    for i in range(3):
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": {
                    "news_uid": news.news_uid,
                    "title": news.title,
                    "summary": news.summary[:200] if news.summary else None,
                    "image_url": news.image_url,
                    "created_at": news.created_at,
                    "views": news.views_count,
                    "likes": news.likes_count,
                    "comments": news.comments_count,
                    "shares": news.shares_count,
                    "is_breaking": news.is_breaking
                },
                "position": i + 9,
                "ranking_score": calculate_news_score(news, user_pref, current_time)
            })
            news_index += 1
        
        # Insert sponsored post after news
        if i == 0 and sponsored_index < len(sponsored_posts):
            post = sponsored_posts[sponsored_index]
            feed.append({
                "type": "sponsored",
                "data": {
                    "id": post.id,
                    "title": post.title,
                    "content": post.content[:150],
                    "image_url": post.image_url,
                    "cta_text": post.cta_text,
                    "cta_url": post.cta_url
                },
                "position": 10
            })
            sponsored_index += 1
        
        # Insert event after second news
        if i == 1 and event_index < len(events):
            event = events[event_index]
            feed.append({
                "type": "event",
                "data": {
                    "event_uid": event.event_uid,
                    "title": event.title,
                    "event_date": event.event_date,
                    "location": event.location,
                    "is_online": event.is_online
                },
                "position": 11
            })
            event_index += 1
        
        # Insert poll after third news
        if i == 2 and poll_index < len(polls):
            poll = polls[poll_index]
            feed.append({
                "type": "poll",
                "data": {
                    "poll_uid": poll.poll_uid,
                    "question": poll.question,
                    "options": poll.options[:2],
                    "total_votes": sum(poll.votes) if poll.votes else 0
                },
                "position": 12
            })
            poll_index += 1
    
    # =========================================================
    # POSITION 12: NATIONAL AD (Fill Inventory)
    # =========================================================
    if ad_index < len(ads) and ads[ad_index].priority == "national":
        ad = ads[ad_index]
        feed.append({
            "type": "ad",
            "priority": "national",
            "data": {
                "id": ad.id,
                "title": ad.title,
                "image_url": ad.image_url,
                "redirect_url": ad.redirect_url,
                "cta_text": "Learn More"
            },
            "position": 12
        })
        ad_index += 1
    
    # =========================================================
    # POSITIONS 13-15: News (3 items)
    # =========================================================
    for i in range(3):
        if news_index < len(ranked_news):
            news = ranked_news[news_index]
            feed.append({
                "type": "news",
                "data": {
                    "news_uid": news.news_uid,
                    "title": news.title,
                    "summary": news.summary[:200] if news.summary else None,
                    "image_url": news.image_url,
                    "created_at": news.created_at,
                    "views": news.views_count,
                    "likes": news.likes_count,
                    "comments": news.comments_count,
                    "shares": news.shares_count
                },
                "position": i + 13,
                "ranking_score": calculate_news_score(news, user_pref, current_time)
            })
            news_index += 1
        else:
            break
    
    # =========================================================
    # POSITION 16: ROTATED LOCAL AD (City/District)
    # =========================================================
    if ad_index < len(ads) and ads[ad_index].priority in ["city", "district"]:
        ad = ads[ad_index]
        feed.append({
            "type": "ad",
            "priority": ad.priority,
            "data": {
                "id": ad.id,
                "title": ad.title,
                "image_url": ad.image_url,
                "redirect_url": ad.redirect_url,
                "cta_text": "Learn More"
            },
            "position": 16
        })
        ad_index += 1
    
    # =========================================================
    # REMAINING NEWS ITEMS
    # =========================================================
    while news_index < len(ranked_news):
        news = ranked_news[news_index]
        feed.append({
            "type": "news",
            "data": {
                "news_uid": news.news_uid,
                "title": news.title,
                "summary": news.summary[:200] if news.summary else None,
                "image_url": news.image_url,
                "created_at": news.created_at,
                "views": news.views_count,
                "likes": news.likes_count,
                "comments": news.comments_count,
                "shares": news.shares_count
            },
            "position": len(feed) + 1,
            "ranking_score": calculate_news_score(news, user_pref, current_time)
        })
        news_index += 1
    
    # =========================================================
    # 8. GET NEXT CURSOR FOR PAGINATION
    # =========================================================
    next_cursor = ranked_news[-1].created_at if ranked_news else None
    
    # =========================================================
    # 9. RETURN RESPONSE
    # =========================================================
    
    return {
        "items": feed[:limit],
        "metadata": {
            "total_items": len(feed),
            "returned_items": len(feed[:limit]),
            "next_cursor": next_cursor.isoformat() if next_cursor else None,
            "has_more": len(ranked_news) >= limit,
            "ranking_summary": {
                "total_scored": len(scored_news),
                "top_score": scored_news[0][0] if scored_news else 0,
                "avg_score": sum(s for s, _ in scored_news[:20]) / min(20, len(scored_news)) if scored_news else 0
            },
            "ad_metadata": {
                "ads_shown": ad_index,
                "premium_ad_shown": ad_index > 0 and feed[0].get("type") == "ad" if feed else False,
                "sponsored_shown": sponsored_index,
                "events_shown": event_index,
                "polls_shown": poll_index
            },
            "feed_structure": {
                "position_0": "premium_ad" if feed and feed[0].get("type") == "ad" else "news",
                "position_4": "city/district_ad" if ad_index >= 1 else "none",
                "position_8": "state/language_ad" if ad_index >= 2 else "none",
                "position_12": "national_ad" if ad_index >= 3 else "none",
                "position_16": "rotated_local_ad" if ad_index >= 4 else "none"
            },
            "user_preferences": {
                "language_id": user_pref.language_id,
                "city_id": user_pref.city_id,
                "district_id": user_pref.district_id,
                "state_id": user_pref.state_id,
                "category_count": len(user_pref.categories) if user_pref.categories else 0
            }
        }
    }
@router.get("/news/feedz")
def get_news_feed(
    user_uid: str,
    cursor: Optional[datetime] = None,
    limit: int = Query(20, le=50),
    db: Session = Depends(get_db)
):
    now = datetime.now(timezone.utc)

    user_pref = db.query(UserPreference).filter(
        UserPreference.user_uid == user_uid
    ).first()

    if not user_pref:
        raise HTTPException(404, "User preference not found")

    feed_news = []
    seen_ids = set()

    # Base query
    base_query = db.query(News).filter(
        News.is_approved == 1,
        News.language_id == user_pref.language_id
    )
    
    if cursor:
        base_query = base_query.filter(News.created_at < cursor)

    # BREAKING NEWS
    breaking_news = base_query.filter(
        News.is_breaking == True,
        (News.breaking_expires_at == None) | (News.breaking_expires_at > now)
    ).order_by(desc(News.breaking_priority)).limit(3).all()

    for news in breaking_news:
        feed_news.append(news)
        seen_ids.add(news.id)

    # CITY NEWS
    if user_pref.city_id and len(feed_news) < limit:
        city_news = base_query.filter(
            News.city_id == user_pref.city_id,
            News.id.notin_(seen_ids)
        ).order_by(desc(News.created_at)).limit(30).all()
        
        for n in city_news:
            if len(feed_news) >= limit:
                break
            if n.id not in seen_ids:
                feed_news.append(n)
                seen_ids.add(n.id)

    # DISTRICT NEWS
    if user_pref.district_id and len(feed_news) < limit:
        district_news = base_query.join(City).filter(
            City.district_id == user_pref.district_id,
            News.id.notin_(seen_ids)
        ).order_by(desc(News.created_at)).limit(30).all()
        
        for n in district_news:
            if len(feed_news) >= limit:
                break
            if n.id not in seen_ids:
                feed_news.append(n)
                seen_ids.add(n.id)

    # STATE NEWS
    if user_pref.state_id and len(feed_news) < limit:
        state_news = base_query.join(City).join(District).filter(
            District.state_id == user_pref.state_id,
            News.id.notin_(seen_ids)
        ).order_by(desc(News.created_at)).limit(30).all()
        
        for n in state_news:
            if len(feed_news) >= limit:
                break
            if n.id not in seen_ids:
                feed_news.append(n)
                seen_ids.add(n.id)

    # LANGUAGE NEWS
    if len(feed_news) < limit:
        lang_news = base_query.filter(
            News.id.notin_(seen_ids)
        ).order_by(desc(News.created_at)).limit(30).all()
        
        for n in lang_news:
            if len(feed_news) >= limit:
                break
            if n.id not in seen_ids:
                feed_news.append(n)
                seen_ids.add(n.id)

    # TRENDING FALLBACK
    if len(feed_news) < limit:
        trending = db.query(News).filter(
            News.is_approved == 1,
            News.id.notin_(seen_ids)
        ).order_by(desc(News.views_count)).limit(limit - len(feed_news)).all()
        feed_news.extend(trending)

    feed_news = feed_news[:limit]

    # GET MIXED CONTENT
    ads = db.query(Advertisement).filter(
        Advertisement.is_active == True,
        Advertisement.start_date <= now,
        Advertisement.end_date >= now
    ).all()

    polls = db.query(Poll).filter(
        Poll.is_approved == True,
        (Poll.expires_at == None) | (Poll.expires_at > now)
    ).all()

    events = db.query(Event).filter(
        Event.is_approved == True,
        Event.event_date >= now
    ).order_by(Event.event_date.asc()).all()

    sponsored = db.query(SponsoredPost).filter(
        SponsoredPost.is_approved == True,
        SponsoredPost.start_date <= now,
        SponsoredPost.end_date >= now
    ).all()

    ad_index = poll_index = event_index = sponsored_index = 0
    feed = []

    for i, news in enumerate(feed_news):
        feed.append({
            "type": "breaking" if news.is_breaking else "news",
            "news_uid": news.news_uid,
            "title": news.title,
            "summary": news.summary[:200] if news.summary else None,
            "image_url": news.image_url,
            "created_at": news.created_at,
            "engagement": {
                "likes": news.likes_count,
                "comments": news.comments_count,
                "shares": news.shares_count,
                "views": news.views_count
            }
        })

        # AD every 3 items
        if (i + 1) % 3 == 0 and ads:
            ad = ads[ad_index % len(ads)]
            feed.append({
                "type": "ad",
                "title": ad.title,
                "image_url": ad.image_url,
                "redirect_url": ad.redirect_url
            })
            ad_index += 1

        # POLL every 10 items
        if (i + 1) % 10 == 0 and polls:
            poll = polls[poll_index % len(polls)]
            feed.append({
                "type": "poll",
                "poll_uid": poll.poll_uid,
                "question": poll.question,
                "options": poll.options
            })
            poll_index += 1

        # EVENT every 12 items
        if (i + 1) % 12 == 0 and events:
            event = events[event_index % len(events)]
            feed.append({
                "type": "event",
                "event_uid": event.event_uid,
                "title": event.title,
                "event_date": event.event_date
            })
            event_index += 1

        # SPONSORED every 15 items
        if (i + 1) % 15 == 0 and sponsored:
            s = sponsored[sponsored_index % len(sponsored)]
            feed.append({
                "type": "sponsored",
                "title": s.title,
                "image_url": s.image_url,
                "cta_text": s.cta_text,
                "cta_url": s.cta_url
            })
            sponsored_index += 1

    next_cursor = feed_news[-1].created_at if feed_news else None

    return {
        "items": feed,
        "next_cursor": next_cursor.isoformat() if next_cursor else None,
        "has_more": len(feed_news) == limit
    }


# =====================================================
# GET SINGLE NEWS
# =====================================================

@router.get("/news/{news_uid}", response_model=NewsOut)
def get_news(
    news_uid: str,
    user_uid: Optional[str] = None,
    db: Session = Depends(get_db)
):
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    city = news.city
    district = city.district if city else None
    state = district.state if district else None
    language = news.language

    # Check if user liked
    user_liked = False
    if user_uid:
        liked = db.query(Reaction).filter(
            Reaction.news_uid == news_uid,
            Reaction.user_uid == user_uid
        ).first()
        user_liked = True if liked else False

    return NewsOut(
        news_uid=news.news_uid,
        title=news.title,
        summary=news.summary,
        image_url=news.image_url,
        language={
            "id": language.id,
            "name": language.name,
            "code": language.code
        },
        user_uid=news.user_uid,
        is_approved=news.is_approved,
        created_at=news.created_at,
        city={
            "id": city.id,
            "name": city.name,
            "district_id": city.district_id
        } if city else None,
        district={
            "id": district.id,
            "name": district.name
        } if district else None,
        state={
            "id": state.id,
            "name": state.name
        } if state else None,
        source_url=news.source_url,
        source_name=news.source_name,
        category_ids=[c.id for c in news.categories],
        engagement={
            "likes": news.likes_count,
            "comments": news.comments_count,
            "shares": news.shares_count,
            "views": news.views_count,
            "user_liked": user_liked
        }
    )


# =====================================================
# COMMENTS
# =====================================================

@router.post("/user/news/{news_uid}/comment", tags=["News Engagement"])
def add_comment(
    news_uid: str,
    user_uid: str,
    comment_text: str,
    db: Session = Depends(get_db)
):
    news = db.query(News).filter_by(news_uid=news_uid).first()
    if not news:
        raise HTTPException(404, "News not found")

    comment = Comment(
        news_uid=news_uid,
        user_uid=user_uid,
        comment_text=comment_text
    )

    news.comments_count += 1

    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        "message": "Comment added",
        "comment_id": comment.id,
        "comment": comment.comment_text,
        "created_at": comment.created_at
    }


@router.delete("/user/news/{news_uid}/comment/{comment_id}", tags=["News Engagement"])
def delete_comment(
    news_uid: str,
    comment_id: int,
    user_uid: str,
    db: Session = Depends(get_db)
):
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.news_uid == news_uid,
        Comment.user_uid == user_uid
    ).first()

    if not comment:
        raise HTTPException(404, "Comment not found or unauthorized")

    news = db.query(News).filter_by(news_uid=news_uid).first()
    if news and news.comments_count > 0:
        news.comments_count -= 1

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted"}


@router.get("/news/{news_uid}/comments", tags=["News Engagement"])
def get_comments(
    news_uid: str,
    page: int = 1,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    offset = (page - 1) * limit

    comments = db.query(Comment).filter(
        Comment.news_uid == news_uid
    ).order_by(
        desc(Comment.created_at)
    ).offset(offset).limit(limit).all()

    return [
        {
            "id": c.id,
            "user_uid": c.user_uid,
            "comment_text": c.comment_text,
            "created_at": c.created_at
        }
        for c in comments
    ]


# =====================================================
# LIKES
# =====================================================

@router.post("/user/news/{news_uid}/like", tags=["News Engagement"])
def like_news(
    news_uid: str,
    user_uid: str,
    db: Session = Depends(get_db)
):
    news = db.query(News).filter_by(news_uid=news_uid).first()
    if not news:
        raise HTTPException(404, "News not found")

    existing = db.query(Reaction).filter(
        Reaction.news_uid == news_uid,
        Reaction.user_uid == user_uid,
        Reaction.reaction_type == 1
    ).first()

    if existing:
        raise HTTPException(400, "Already liked")

    reaction = Reaction(
        news_uid=news_uid,
        user_uid=user_uid,
        reaction_type=1
    )

    news.likes_count += 1

    db.add(reaction)
    db.commit()

    return {"message": "News liked", "likes_count": news.likes_count}


@router.delete("/user/news/{news_uid}/like", tags=["News Engagement"])
def unlike_news(
    news_uid: str,
    user_uid: str,
    db: Session = Depends(get_db)
):
    reaction = db.query(Reaction).filter(
        Reaction.news_uid == news_uid,
        Reaction.user_uid == user_uid,
        Reaction.reaction_type == 1
    ).first()

    if not reaction:
        raise HTTPException(404, "Like not found")

    news = db.query(News).filter_by(news_uid=news_uid).first()
    if news and news.likes_count > 0:
        news.likes_count -= 1

    db.delete(reaction)
    db.commit()

    return {"message": "Like removed", "likes_count": news.likes_count if news else 0}


# =====================================================
# VIEWS
# =====================================================

@router.post("/user/news/{news_uid}/view", tags=["News Engagement"])
def record_view(
    news_uid: str,
    user_uid: Optional[str] = None,
    db: Session = Depends(get_db)
):
    news = db.query(News).filter_by(news_uid=news_uid).first()
    if not news:
        raise HTTPException(404, "News not found")

    view = NewsView(
        news_uid=news_uid,
        user_uid=user_uid
    )

    news.views_count += 1

    db.add(view)
    db.commit()

    return {"message": "View recorded", "views_count": news.views_count}


# =====================================================
# DELETE NEWS (User)
# =====================================================

@router.delete("/user/news/{news_uid}", status_code=status.HTTP_204_NO_CONTENT)
def delete_news_by_user(
    news_uid: str,
    user_uid: str,
    db: Session = Depends(get_db)
):
    news = db.query(News).filter_by(news_uid=news_uid, user_uid=user_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found or unauthorized")
    
    db.delete(news)
    db.commit()
    return None


# =====================================================
# SEARCH
# =====================================================

@router.get("/search", tags=["Search"])
def realtime_search(
    q: Optional[str] = Query(None, description="Search keyword"),
    state_id: Optional[int] = None,
    district_id: Optional[int] = None,
    city_id: Optional[int] = None,
    category_id: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(News).filter(News.is_approved == 1)

    # Keyword Search
    if q:
        query = query.outerjoin(User, News.user_uid == User.user_uid).outerjoin(News.categories).filter(
            or_(
                News.title.ilike(f"%{q}%"),
                News.summary.ilike(f"%{q}%"),
                News.source_name.ilike(f"%{q}%"),
                User.user_name.ilike(f"%{q}%"),
                Category.name.ilike(f"%{q}%")
            )
        )

    # Category Filter
    if category_id:
        query = query.join(News.categories).filter(Category.id == category_id)

    # Location Filters
    if city_id:
        query = query.filter(News.city_id == city_id)
    elif district_id:
        query = query.join(City).filter(City.district_id == district_id)
    elif state_id:
        query = query.join(City).join(District).filter(District.state_id == state_id)

    # Date Filters
    if start_date:
        query = query.filter(News.created_at >= start_date)
    if end_date:
        query = query.filter(News.created_at <= end_date)

    total = query.count()

    news_results = query.distinct().order_by(
        desc(News.created_at)
    ).offset(offset).limit(limit).all()

    return {
        "total": total,
        "items": [
            {
                "news_uid": n.news_uid,
                "title": n.title,
                "summary": n.summary[:200] if n.summary else None,
                "image_url": n.image_url,
                "source_name": n.source_name,
                "created_at": n.created_at,
                "views": n.views_count,
                "likes": n.likes_count
            }
            for n in news_results
        ],
        "limit": limit,
        "offset": offset,
        "has_next": offset + limit < total
    }


# =====================================================
# SHARE NEWS
# =====================================================

@router.post("/user/news/{news_uid}/share", tags=["News Engagement"])
def share_news(
    news_uid: str,
    user_uid: str,
    platform: str = None,
    db: Session = Depends(get_db)
):
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    existing = db.query(Share).filter(
        Share.news_uid == news_uid,
        Share.user_uid == user_uid
    ).first()

    if existing:
        return {"message": "Already shared", "share_count": news.shares_count}

    share = Share(
        news_uid=news_uid,
        user_uid=user_uid,
        platform=platform
    )

    news.shares_count += 1

    db.add(share)
    db.commit()

    return {"message": "News shared", "share_count": news.shares_count}


# =====================================================
# ENGAGEMENT SUMMARY
# =====================================================

@router.get("/news/{news_uid}/engagement", tags=["News Engagement"])
def get_news_engagement(
    news_uid: str,
    user_uid: Optional[str] = None,
    db: Session = Depends(get_db)
):
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")

    # Check if user liked
    user_liked = False
    if user_uid:
        liked = db.query(Reaction).filter(
            Reaction.news_uid == news_uid,
            Reaction.user_uid == user_uid,
            Reaction.reaction_type == 1
        ).first()
        user_liked = True if liked else False

    return {
        "news_uid": news_uid,
        "views": news.views_count,
        "likes": news.likes_count,
        "comments": news.comments_count,
        "shares": news.shares_count,
        "user_liked": user_liked
    }


# =====================================================
# UPDATE NEWS
# =====================================================

@router.put("/news/{news_uid}", response_model=NewsOut)
def update_news(
    news_uid: str,
    news: NewsCreate,
    db: Session = Depends(get_db)
):
    existing_news = db.query(News).filter_by(news_uid=news_uid).first()
    if not existing_news:
        raise HTTPException(status_code=404, detail="News not found")

    user = db.query(User).filter_by(user_uid=news.user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    language = db.query(Language).filter_by(id=news.language_id).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")

    city, district, state = None, None, None
    if news.city_id:
        city = db.query(City).filter_by(id=news.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        district = city.district
        state = district.state if district else None

    # Update fields
    existing_news.title = news.title
    existing_news.summary = news.summary
    existing_news.image_url = news.image_url
    existing_news.language_id = news.language_id
    existing_news.city_id = news.city_id
    existing_news.source_url = news.source_url
    existing_news.source_name = news.source_name

    # Update categories
    if news.category_ids:
        categories = db.query(Category).filter(Category.id.in_(news.category_ids)).all()
        existing_news.categories = categories
    else:
        existing_news.categories = []

    db.commit()
    db.refresh(existing_news)

    return NewsOut(
        news_uid=existing_news.news_uid,
        title=existing_news.title,
        summary=existing_news.summary,
        image_url=existing_news.image_url,
        language=language,
        user_uid=existing_news.user_uid,
        is_approved=existing_news.is_approved,
        created_at=existing_news.created_at,
        city=city,
        district=district,
        state=state,
        source_url=existing_news.source_url,
        source_name=existing_news.source_name,
        category_ids=[c.id for c in existing_news.categories],
        engagement={
            "likes": existing_news.likes_count,
            "comments": existing_news.comments_count,
            "shares": existing_news.shares_count,
            "views": existing_news.views_count,
            "user_liked": False
        }
    )


# =====================================================
# NEWS SHORTS (YouTube)
# =====================================================

@router.get("/news-shorts", response_model=List[VideoItem])
def get_news_shorts(
    language: str = Query(..., description="Language code like 'en' or 'te'"),
    limit: int = 10,
    db: Session = Depends(get_db)
):
    shorts = db.query(YouTubeShort).filter(
        YouTubeShort.language == language
    ).order_by(
        YouTubeShort.published_at.desc()
    ).limit(limit).all()

    return [
        VideoItem(
            title=s.title,
            video_id=s.video_id,
            thumbnail_url=s.thumbnail_url,
            channel_title=s.channel_title,
            published_at=s.published_at.isoformat() if s.published_at else None
        ) for s in shorts
    ]


@router.get("/admin/news-shorts/telugu", response_model=List[VideoItem], tags=["Admin"])
def fetch_and_store_telugu_shorts(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    return fetch_and_store_shorts_by_language("telugu news", "te", db)


@router.get("/admin/news-shorts/english", response_model=List[VideoItem], tags=["Admin"])
def fetch_and_store_english_shorts(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    return fetch_and_store_shorts_by_language("english news", "en", db)


def fetch_and_store_shorts_by_language(query: str, lang: str, db: Session):
    params = {
        "key": YOUTUBE_API_KEY,
        "part": "snippet",
        "q": query,
        "maxResults": 5,
        "type": "video",
        "videoDuration": "short",
        "order": "date",
        "videoEmbeddable": "true"
    }

    response = requests.get(YOUTUBE_SEARCH_URL, params=params)
    data = response.json()
    result = []

    for item in data.get("items", []):
        if item["id"]["kind"] == "youtube#video":
            video_id = item["id"]["videoId"]
            snippet = item["snippet"]

            existing = db.query(YouTubeShort).filter_by(video_id=video_id).first()
            if existing:
                continue

            short = YouTubeShort(
                video_id=video_id,
                title=snippet["title"],
                thumbnail_url=snippet["thumbnails"]["high"]["url"],
                channel_title=snippet["channelTitle"],
                published_at=datetime.fromisoformat(snippet["publishedAt"].replace('Z', '+00:00')),
                video_url=f"https://www.youtube.com/watch?v={video_id}",
                language=lang
            )
            db.add(short)
            db.commit()

            result.append(VideoItem(
                title=short.title,
                video_id=short.video_id,
                thumbnail_url=short.thumbnail_url,
                channel_title=short.channel_title,
                published_at=short.published_at.isoformat() if short.published_at else None
            ))

    return result

# =====================================================
# NEWS STATISTICS & ANALYTICS
# =====================================================

@router.get(
    "/news/analytics/daily",
    response_model=Dict[str, Any],
    tags=["Analytics", "News"]
)
def get_daily_news_stats(
    date: Optional[datetime] = Query(None, description="Specific date (default: today)"),
    db: Session = Depends(get_db)
):
    """
    Get daily news statistics
    """
    target_date = date or datetime.now(timezone.utc)
    start_of_day = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    # News created today
    news_created = db.query(News).filter(
        News.created_at >= start_of_day,
        News.created_at < end_of_day
    ).count()
    
    # News approved today
    news_approved = db.query(News).filter(
        News.approved_at >= start_of_day,
        News.approved_at < end_of_day,
        News.is_approved == 1
    ).count() if hasattr(News, 'approved_at') else 0
    
    # Total views today
    total_views = db.query(func.sum(News.views_count)).filter(
        News.created_at >= start_of_day,
        News.created_at < end_of_day,
        News.is_approved == 1
    ).scalar() or 0
    
    # Total likes today
    total_likes = db.query(func.sum(News.likes_count)).filter(
        News.created_at >= start_of_day,
        News.created_at < end_of_day,
        News.is_approved == 1
    ).scalar() or 0
    
    # Total comments today
    total_comments = db.query(func.sum(News.comments_count)).filter(
        News.created_at >= start_of_day,
        News.created_at < end_of_day,
        News.is_approved == 1
    ).scalar() or 0
    
    # Total shares today
    total_shares = db.query(func.sum(News.shares_count)).filter(
        News.created_at >= start_of_day,
        News.created_at < end_of_day,
        News.is_approved == 1
    ).scalar() or 0
    
    # Top news by views today
    top_news = db.query(News).filter(
        News.created_at >= start_of_day,
        News.created_at < end_of_day,
        News.is_approved == 1
    ).order_by(desc(News.views_count)).limit(5).all()
    
    return {
        "date": start_of_day.isoformat(),
        "summary": {
            "news_created": news_created,
            "news_approved": news_approved,
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares
        },
        "top_news": [
            {
                "news_uid": n.news_uid,
                "title": n.title,
                "views": n.views_count,
                "likes": n.likes_count,
                "image_url": n.image_url
            }
            for n in top_news
        ]
    }


@router.get(
    "/news/analytics/weekly",
    response_model=Dict[str, Any],
    tags=["Analytics", "News"]
)
def get_weekly_news_stats(
    week_start: Optional[datetime] = Query(None, description="Start of week (Monday)"),
    db: Session = Depends(get_db)
):
    """
    Get weekly news statistics
    """
    if week_start:
        start_date = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        today = datetime.now(timezone.utc).date()
        start_date = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
    
    end_date = start_date + timedelta(days=7)
    
    # Daily breakdown
    daily_stats = []
    for i in range(7):
        day_start = start_date + timedelta(days=i)
        day_end = day_start + timedelta(days=1)
        
        news_count = db.query(News).filter(
            News.created_at >= day_start,
            News.created_at < day_end
        ).count()
        
        views = db.query(func.sum(News.views_count)).filter(
            News.created_at >= day_start,
            News.created_at < day_end,
            News.is_approved == 1
        ).scalar() or 0
        
        daily_stats.append({
            "date": day_start.isoformat(),
            "news_count": news_count,
            "views": views
        })
    
    # Weekly totals
    total_news = db.query(News).filter(
        News.created_at >= start_date,
        News.created_at < end_date
    ).count()
    
    total_views = db.query(func.sum(News.views_count)).filter(
        News.created_at >= start_date,
        News.created_at < end_date,
        News.is_approved == 1
    ).scalar() or 0
    
    total_likes = db.query(func.sum(News.likes_count)).filter(
        News.created_at >= start_date,
        News.created_at < end_date,
        News.is_approved == 1
    ).scalar() or 0
    
    # Top categories this week
    top_categories = db.query(
        Category.id,
        Category.name,
        func.count(News.id).label('news_count')
    ).join(News.categories).filter(
        News.created_at >= start_date,
        News.created_at < end_date,
        News.is_approved == 1
    ).group_by(Category.id).order_by(desc('news_count')).limit(5).all()
    
    return {
        "week_start": start_date.isoformat(),
        "week_end": (end_date - timedelta(days=1)).isoformat(),
        "summary": {
            "total_news": total_news,
            "total_views": total_views,
            "total_likes": total_likes,
            "average_views_per_news": total_views / total_news if total_news > 0 else 0
        },
        "daily_breakdown": daily_stats,
        "top_categories": [
            {"id": c.id, "name": c.name, "news_count": c.news_count}
            for c in top_categories
        ]
    }


@router.get(
    "/news/analytics/top",
    response_model=Dict[str, Any],
    tags=["Analytics", "News"]
)
def get_top_performing_news(
    period: str = Query("week", enum=["day", "week", "month", "all"], description="Time period"),
    metric: str = Query("views", enum=["views", "likes", "comments", "shares"], description="Metric to sort by"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: Session = Depends(get_db)
):
    """
    Get top performing news based on various metrics
    """
    now = datetime.now(timezone.utc)
    
    # Define time range
    if period == "day":
        start_date = now - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = datetime(2000, 1, 1, 0, 0, 0)
    
    query = db.query(News).filter(
        News.is_approved == 1,
        News.created_at >= start_date
    )
    
    # Apply sorting based on metric
    if metric == "views":
        query = query.order_by(desc(News.views_count))
    elif metric == "likes":
        query = query.order_by(desc(News.likes_count))
    elif metric == "comments":
        query = query.order_by(desc(News.comments_count))
    elif metric == "shares":
        query = query.order_by(desc(News.shares_count))
    
    top_news = query.limit(limit).all()
    
    return {
        "period": period,
        "metric": metric,
        "items": [
            {
                "rank": idx + 1,
                "news_uid": n.news_uid,
                "title": n.title,
                "summary": n.summary[:150] if n.summary else None,
                "image_url": n.image_url,
                "created_at": n.created_at,
                "views": n.views_count,
                "likes": n.likes_count,
                "comments": n.comments_count,
                "shares": n.shares_count,
                "engagement_rate": round(
                    (n.likes_count + n.comments_count + n.shares_count) / n.views_count * 100 if n.views_count > 0 else 0, 2
                )
            }
            for idx, n in enumerate(top_news)
        ]
    }


@router.get(
    "/news/analytics/trending",
    response_model=Dict[str, Any],
    tags=["Analytics", "News"]
)
def get_trending_news(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours"),
    limit: int = Query(10, ge=1, le=50, description="Number of results"),
    db: Session = Depends(get_db)
):
    """
    Get trending news based on views velocity (views per hour)
    """
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(hours=hours)
    
    # Get news created in the last 'hours' with high view velocity
    trending = db.query(News).filter(
        News.is_approved == 1,
        News.created_at >= start_date,
        News.views_count > 0
    ).all()
    
    # Calculate trending score manually
    results = []
    for n in trending:
        age_hours = (now - n.created_at).total_seconds() / 3600
        views_per_hour = n.views_count / age_hours if age_hours > 0 else 0
        
        results.append({
            "news_uid": n.news_uid,
            "title": n.title,
            "image_url": n.image_url,
            "views": n.views_count,
            "likes": n.likes_count,
            "created_at": n.created_at,
            "age_hours": round(age_hours, 1),
            "views_per_hour": round(views_per_hour, 2),
            "trending_score": round(views_per_hour, 2)
        })
    
    # Sort by trending score
    results.sort(key=lambda x: x['trending_score'], reverse=True)
    
    return {
        "time_window_hours": hours,
        "items": results[:limit]
    }


@router.get(
    "/admin/analytics/overview",
    response_model=Dict[str, Any],
    tags=["Admin", "Analytics"]
)
def get_admin_analytics_overview(
    days: int = Query(30, ge=1, le=90, description="Number of days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Get comprehensive analytics overview for admin dashboard
    """
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    # Total counts
    total_news = db.query(News).count()
    total_approved = db.query(News).filter(News.is_approved == 1).count()
    total_pending = db.query(News).filter(News.is_approved == 0).count()
    
    # Engagement totals
    total_views = db.query(func.sum(News.views_count)).scalar() or 0
    total_likes = db.query(func.sum(News.likes_count)).scalar() or 0
    total_comments = db.query(func.sum(News.comments_count)).scalar() or 0
    total_shares = db.query(func.sum(News.shares_count)).scalar() or 0
    
    # Daily trends for chart
    daily_trends = []
    for i in range(min(days, 30)):  # Limit to 30 days for chart
        day_start = (now - timedelta(days=days-i-1)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_news = db.query(News).filter(
            News.created_at >= day_start,
            News.created_at < day_end
        ).count()
        
        day_views = db.query(func.sum(News.views_count)).filter(
            News.created_at >= day_start,
            News.created_at < day_end,
            News.is_approved == 1
        ).scalar() or 0
        
        daily_trends.append({
            "date": day_start.isoformat(),
            "news_count": day_news,
            "views": day_views
        })
    
    # Category distribution
    category_stats = db.query(
        Category.id,
        Category.name,
        func.count(News.id).label('count')
    ).join(News.categories).filter(
        News.is_approved == 1
    ).group_by(Category.id).order_by(desc('count')).limit(10).all()
    
    # Top reporters
    top_reporters = db.query(
        News.user_uid,
        func.count(News.id).label('news_count'),
        func.sum(News.views_count).label('total_views')
    ).filter(
        News.is_approved == 1
    ).group_by(News.user_uid).order_by(desc('news_count')).limit(10).all()
    
    # Growth rate
    previous_period_start = start_date - timedelta(days=days)
    current_news = total_news
    previous_news = db.query(News).filter(
        News.created_at >= previous_period_start,
        News.created_at < start_date
    ).count()
    
    growth_rate = ((current_news - previous_news) / previous_news * 100) if previous_news > 0 else 0
    
    return {
        "period_days": days,
        "summary": {
            "total_news": total_news,
            "approved_news": total_approved,
            "pending_news": total_pending,
            "approval_rate": round(total_approved / total_news * 100, 2) if total_news > 0 else 0,
            "growth_rate": round(growth_rate, 2)
        },
        "engagement": {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "avg_views_per_news": round(total_views / total_approved, 2) if total_approved > 0 else 0,
            "engagement_rate": round((total_likes + total_comments + total_shares) / total_views * 100, 2) if total_views > 0 else 0
        },
        "daily_trends": daily_trends,
        "top_categories": [
            {"id": c.id, "name": c.name, "count": c.count}
            for c in category_stats
        ],
        "top_reporters": [
            {
                "user_uid": r.user_uid,
                "news_count": r.news_count,
                "total_views": r.total_views
            }
            for r in top_reporters
        ]
    }


# =====================================================
# NEWS MODERATION SYSTEM (Flag & Report)
# =====================================================

@router.post(
    "/news/{news_uid}/flag",
    response_model=Dict[str, Any],
    status_code=status.HTTP_201_CREATED,
    tags=["Moderation", "News"]
)
def flag_news(
    news_uid: str,
    flag_data: NewsFlagCreate,
    user_uid: str = Query(..., description="User UID who is flagging"),
    db: Session = Depends(get_db)
):
    """
    Report news as inappropriate
    """
    # Check if news exists
    news = db.query(News).filter(News.news_uid == news_uid).first()
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    # Check if user already flagged this news
    existing_flag = db.query(NewsFlag).filter(
        NewsFlag.news_uid == news_uid,
        NewsFlag.user_uid == user_uid,
        NewsFlag.status == "pending"
    ).first()
    
    if existing_flag:
        raise HTTPException(status_code=400, detail="You have already flagged this news")
    
    # Create flag
    new_flag = NewsFlag(
        news_uid=news_uid,
        user_uid=user_uid,
        reason=flag_data.reason,
        status="pending"
    )
    
    db.add(new_flag)
    db.commit()
    db.refresh(new_flag)
    
    return {
        "message": "News flagged for review",
        "flag_id": new_flag.id,
        "news_uid": news_uid,
        "status": "pending"
    }


@router.get(
    "/admin/flags/pending",
    response_model=List[Dict[str, Any]],
    tags=["Admin", "Moderation"]
)
def get_pending_flags(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Get all pending flags for review (Admin only)
    """
    flags = db.query(NewsFlag).filter(
        NewsFlag.status == "pending"
    ).order_by(desc(NewsFlag.created_at)).offset(offset).limit(limit).all()
    
    results = []
    for flag in flags:
        news = db.query(News).filter(News.news_uid == flag.news_uid).first()
        user = db.query(User).filter(User.user_uid == flag.user_uid).first()
        
        results.append({
            "id": flag.id,
            "type": "news",
            "content_id": flag.news_uid,
            "content_title": news.title if news else "Unknown",
            "reporter_uid": flag.user_uid,
            "reporter_name": user.user_name if user else "Unknown",
            "reason": flag.reason,
            "status": flag.status,
            "created_at": flag.created_at,
            "review_notes": flag.review_notes
        })
    
    return results


@router.put(
    "/admin/flags/{flag_id}/review",
    response_model=Dict[str, Any],
    tags=["Admin", "Moderation"]
)
def review_flagged_content(
    flag_id: int,
    review: FlagReview,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Review flagged content and take action (Admin only)
    """
    flag = db.query(NewsFlag).filter(NewsFlag.id == flag_id).first()
    if not flag:
        raise HTTPException(status_code=404, detail="Flag not found")
    
    # Update flag status
    flag.status = "reviewed" if review.action == "approve" else "dismissed"
    flag.review_notes = review.review_notes
    flag.reviewed_by = current_user.user_uid
    flag.reviewed_at = datetime.now(timezone.utc)
    
    # Take action on the content if rejected
    if review.action == "reject":
        news = db.query(News).filter(News.news_uid == flag.news_uid).first()
        if news:
            news.is_approved = 2  # Rejected/Blocked
            news.rejected_at = datetime.now(timezone.utc)
    
    db.commit()
    
    return {
        "message": f"Flag {review.action}d successfully",
        "flag_id": flag_id,
        "action": review.action,
        "content_id": flag.news_uid
    }


@router.get(
    "/admin/flags/stats",
    response_model=Dict[str, Any],
    tags=["Admin", "Moderation"]
)
def get_flag_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Get flag statistics for admin dashboard
    """
    total_flags = db.query(NewsFlag).count()
    pending_flags = db.query(NewsFlag).filter(NewsFlag.status == "pending").count()
    reviewed_flags = db.query(NewsFlag).filter(NewsFlag.status == "reviewed").count()
    dismissed_flags = db.query(NewsFlag).filter(NewsFlag.status == "dismissed").count()
    
    # Most flagged news
    most_flagged = db.query(
        NewsFlag.news_uid,
        func.count(NewsFlag.id).label('flag_count')
    ).group_by(NewsFlag.news_uid).order_by(desc('flag_count')).limit(5).all()
    
    # Most active flaggers
    top_flaggers = db.query(
        NewsFlag.user_uid,
        func.count(NewsFlag.id).label('flag_count')
    ).group_by(NewsFlag.user_uid).order_by(desc('flag_count')).limit(5).all()
    
    return {
        "total_flags": total_flags,
        "pending_flags": pending_flags,
        "reviewed_flags": reviewed_flags,
        "dismissed_flags": dismissed_flags,
        "most_flagged_news": [
            {"news_uid": f.news_uid, "flag_count": f.flag_count}
            for f in most_flagged
        ],
        "top_flaggers": [
            {"user_uid": f.user_uid, "flag_count": f.flag_count}
            for f in top_flaggers
        ]
    }
    
# =====================================================
# NEWS SCHEDULING APIs
# =====================================================

@router.post(
    "/admin/news/schedule",
    response_model=ScheduledNewsOut,
    status_code=status.HTTP_201_CREATED,
    tags=["Admin", "Scheduling", "News"]
)
def schedule_news(
    schedule_data: ScheduledNewsCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Schedule a news article for future publishing (Admin only)
    
    - **title**: News title
    - **summary**: News summary
    - **image_url**: Optional image URL
    - **language_id**: Language ID
    - **user_uid**: Publisher/Reporter UID
    - **category_ids**: List of category IDs
    - **city_id**: Optional city ID
    - **source_url**: Optional source URL
    - **source_name**: Optional source name
    - **scheduled_at**: When to publish the news
    """
    # Verify user exists
    user = db.query(User).filter_by(user_uid=schedule_data.user_uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify language exists
    language = db.query(Language).filter_by(id=schedule_data.language_id).first()
    if not language:
        raise HTTPException(status_code=404, detail="Language not found")

    # Handle optional city
    city = None
    district = None
    state = None
    if schedule_data.city_id:
        city = db.query(City).filter_by(id=schedule_data.city_id).first()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")
        district = city.district
        state = district.state if district else None

    # Check if scheduled time is in the future
    if schedule_data.scheduled_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=400, 
            detail="Scheduled time must be in the future"
        )

    # Generate unique news UID
    news_uid = generate_news_uid()

    # Create scheduled news entry
    scheduled_news = ScheduledNews(
        news_uid=news_uid,
        title=schedule_data.title,
        summary=schedule_data.summary,
        image_url=schedule_data.image_url,
        language_id=schedule_data.language_id,
        user_uid=schedule_data.user_uid,
        city_id=schedule_data.city_id,
        source_url=schedule_data.source_url,
        source_name=schedule_data.source_name,
        scheduled_at=schedule_data.scheduled_at,
        scheduled_by=current_user.user_uid,
        status="pending"
    )

    db.add(scheduled_news)
    db.flush()  # Get ID without committing

    # Attach categories
    if schedule_data.category_ids:
        categories = db.query(Category).filter(
            Category.id.in_(schedule_data.category_ids)
        ).all()
        scheduled_news.categories = categories

    db.commit()
    db.refresh(scheduled_news)

    return {
        "id": scheduled_news.id,
        "news_uid": scheduled_news.news_uid,
        "title": scheduled_news.title,
        "summary": scheduled_news.summary,
        "image_url": scheduled_news.image_url,
        "language_id": scheduled_news.language_id,
        "user_uid": scheduled_news.user_uid,
        "city_id": scheduled_news.city_id,
        "source_url": scheduled_news.source_url,
        "source_name": scheduled_news.source_name,
        "category_ids": [c.id for c in scheduled_news.categories],
        "scheduled_at": scheduled_news.scheduled_at,
        "status": scheduled_news.status,
        "created_at": scheduled_news.created_at,
        "published_at": scheduled_news.published_at
    }


@router.get(
    "/admin/news/scheduled",
    response_model=Dict[str, Any],
    tags=["Admin", "Scheduling", "News"]
)
def get_scheduled_news(
    status: Optional[str] = Query(None, enum=["pending", "published", "failed", "cancelled"]),
    language_id: Optional[int] = Query(None, description="Filter by language"),
    from_date: Optional[datetime] = Query(None, description="Schedule from date"),
    to_date: Optional[datetime] = Query(None, description="Schedule to date"),
    search: Optional[str] = Query(None, description="Search by title"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Get all scheduled news articles (Admin only)
    """
    query = db.query(ScheduledNews)
    
    if status:
        query = query.filter(ScheduledNews.status == status)
    
    if language_id:
        query = query.filter(ScheduledNews.language_id == language_id)
    
    if from_date:
        query = query.filter(ScheduledNews.scheduled_at >= from_date)
    
    if to_date:
        query = query.filter(ScheduledNews.scheduled_at <= to_date)
    
    if search:
        query = query.filter(
            or_(
                ScheduledNews.title.ilike(f"%{search}%"),
                ScheduledNews.summary.ilike(f"%{search}%")
            )
        )
    
    total = query.count()
    
    scheduled = query.order_by(
        ScheduledNews.scheduled_at.asc()
    ).offset(offset).limit(limit).all()
    
    results = []
    for s in scheduled:
        # Get category names
        category_names = [c.name for c in s.categories]
        
        results.append({
            "id": s.id,
            "news_uid": s.news_uid,
            "title": s.title,
            "summary": s.summary[:150] if s.summary else None,
            "image_url": s.image_url,
            "language_id": s.language_id,
            "user_uid": s.user_uid,
            "city_id": s.city_id,
            "scheduled_at": s.scheduled_at,
            "status": s.status,
            "category_names": category_names,
            "created_at": s.created_at,
            "published_at": s.published_at
        })
    
    return {
        "total": total,
        "items": results,
        "limit": limit,
        "offset": offset,
        "has_next": offset + limit < total
    }


@router.get(
    "/admin/news/scheduled/{schedule_id}",
    response_model=ScheduledNewsOut,
    tags=["Admin", "Scheduling", "News"]
)
def get_scheduled_news_details(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Get details of a specific scheduled news article (Admin only)
    """
    scheduled = db.query(ScheduledNews).filter(
        ScheduledNews.id == schedule_id
    ).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled news not found"
        )
    
    return {
        "id": scheduled.id,
        "news_uid": scheduled.news_uid,
        "title": scheduled.title,
        "summary": scheduled.summary,
        "image_url": scheduled.image_url,
        "language_id": scheduled.language_id,
        "user_uid": scheduled.user_uid,
        "city_id": scheduled.city_id,
        "source_url": scheduled.source_url,
        "source_name": scheduled.source_name,
        "category_ids": [c.id for c in scheduled.categories],
        "scheduled_at": scheduled.scheduled_at,
        "status": scheduled.status,
        "created_at": scheduled.created_at,
        "published_at": scheduled.published_at
    }


@router.put(
    "/admin/news/scheduled/{schedule_id}",
    response_model=ScheduledNewsOut,
    tags=["Admin", "Scheduling", "News"]
)
def update_scheduled_news(
    schedule_id: int,
    update_data: ScheduledNewsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Update a scheduled news article (Admin only)
    """
    scheduled = db.query(ScheduledNews).filter(
        ScheduledNews.id == schedule_id
    ).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled news not found"
        )
    
    if scheduled.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update scheduled news with status: {scheduled.status}"
        )
    
    # Update fields
    if update_data.title is not None:
        scheduled.title = update_data.title
    if update_data.summary is not None:
        scheduled.summary = update_data.summary
    if update_data.image_url is not None:
        scheduled.image_url = update_data.image_url
    if update_data.language_id is not None:
        # Verify language exists
        language = db.query(Language).filter_by(id=update_data.language_id).first()
        if not language:
            raise HTTPException(status_code=404, detail="Language not found")
        scheduled.language_id = update_data.language_id
    if update_data.city_id is not None:
        if update_data.city_id:
            city = db.query(City).filter_by(id=update_data.city_id).first()
            if not city:
                raise HTTPException(status_code=404, detail="City not found")
        scheduled.city_id = update_data.city_id
    if update_data.source_url is not None:
        scheduled.source_url = update_data.source_url
    if update_data.source_name is not None:
        scheduled.source_name = update_data.source_name
    if update_data.scheduled_at is not None:
        if update_data.scheduled_at <= datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Scheduled time must be in the future")
        scheduled.scheduled_at = update_data.scheduled_at
    
    # Update categories
    if update_data.category_ids is not None:
        categories = db.query(Category).filter(
            Category.id.in_(update_data.category_ids)
        ).all()
        scheduled.categories = categories
    
    db.commit()
    db.refresh(scheduled)
    
    return {
        "id": scheduled.id,
        "news_uid": scheduled.news_uid,
        "title": scheduled.title,
        "summary": scheduled.summary,
        "image_url": scheduled.image_url,
        "language_id": scheduled.language_id,
        "user_uid": scheduled.user_uid,
        "city_id": scheduled.city_id,
        "source_url": scheduled.source_url,
        "source_name": scheduled.source_name,
        "category_ids": [c.id for c in scheduled.categories],
        "scheduled_at": scheduled.scheduled_at,
        "status": scheduled.status,
        "created_at": scheduled.created_at,
        "published_at": scheduled.published_at
    }


@router.delete(
    "/admin/news/scheduled/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Admin", "Scheduling", "News"]
)
def cancel_scheduled_news(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Cancel a scheduled news article (Admin only)
    """
    scheduled = db.query(ScheduledNews).filter(
        ScheduledNews.id == schedule_id
    ).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled news not found"
        )
    
    if scheduled.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot cancel schedule with status: {scheduled.status}"
        )
    
    scheduled.status = "cancelled"
    db.commit()
    
    return None


@router.post(
    "/admin/news/scheduled/{schedule_id}/publish-now",
    response_model=NewsOut,
    tags=["Admin", "Scheduling", "News"]
)
def publish_scheduled_news_now(
    schedule_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Immediately publish a scheduled news article (Admin only)
    """
    scheduled = db.query(ScheduledNews).filter(
        ScheduledNews.id == schedule_id
    ).first()
    
    if not scheduled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled news not found"
        )
    
    if scheduled.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot publish schedule with status: {scheduled.status}"
        )
    
    # Create actual news article
    new_news = News(
        news_uid=scheduled.news_uid,
        title=scheduled.title,
        summary=scheduled.summary,
        image_url=scheduled.image_url,
        language_id=scheduled.language_id,
        user_uid=scheduled.user_uid,
        city_id=scheduled.city_id,
        source_url=scheduled.source_url,
        source_name=scheduled.source_name,
        is_approved=1,  # Auto-approve when publishing
        created_at=datetime.now(timezone.utc)
    )
    
    # Attach categories
    if scheduled.categories:
        new_news.categories = scheduled.categories
    
    db.add(new_news)
    
    # Update scheduled record
    scheduled.status = "published"
    scheduled.published_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(new_news)
    
    return NewsOut(
        news_uid=new_news.news_uid,
        title=new_news.title,
        summary=new_news.summary,
        image_url=new_news.image_url,
        language=new_news.language,
        user_uid=new_news.user_uid,
        is_approved=new_news.is_approved,
        created_at=new_news.created_at,
        city=new_news.city,
        district=new_news.city.district if new_news.city else None,
        state=new_news.city.district.state if new_news.city and new_news.city.district else None,
        source_url=new_news.source_url,
        source_name=new_news.source_name,
        category_ids=[c.id for c in new_news.categories],
        engagement={
            "likes": new_news.likes_count,
            "comments": new_news.comments_count,
            "shares": new_news.shares_count,
            "views": new_news.views_count,
            "user_liked": False
        }
    )


@router.get(
    "/admin/news/scheduled/upcoming",
    response_model=List[Dict[str, Any]],
    tags=["Admin", "Scheduling", "News"]
)
def get_upcoming_scheduled_news(
    hours: int = Query(24, ge=1, le=168, description="Hours ahead to check"),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Get upcoming scheduled news within next X hours (Admin only)
    """
    now = datetime.now(timezone.utc)
    upcoming_time = now + timedelta(hours=hours)
    
    upcoming = db.query(ScheduledNews).filter(
        ScheduledNews.status == "pending",
        ScheduledNews.scheduled_at >= now,
        ScheduledNews.scheduled_at <= upcoming_time
    ).order_by(ScheduledNews.scheduled_at.asc()).limit(limit).all()
    
    results = []
    for s in upcoming:
        results.append({
            "id": s.id,
            "news_uid": s.news_uid,
            "title": s.title,
            "scheduled_at": s.scheduled_at,
            "minutes_until": round((s.scheduled_at - now).total_seconds() / 60, 0),
            "user_uid": s.user_uid
        })
    
    return results


@router.get(
    "/admin/news/scheduled/stats",
    response_model=Dict[str, Any],
    tags=["Admin", "Scheduling", "News"]
)
def get_scheduling_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(admin_required)
):
    """
    Get scheduling statistics for admin dashboard (Admin only)
    """
    now = datetime.now(timezone.utc)
    
    total_scheduled = db.query(ScheduledNews).count()
    pending = db.query(ScheduledNews).filter(ScheduledNews.status == "pending").count()
    published = db.query(ScheduledNews).filter(ScheduledNews.status == "published").count()
    failed = db.query(ScheduledNews).filter(ScheduledNews.status == "failed").count()
    cancelled = db.query(ScheduledNews).filter(ScheduledNews.status == "cancelled").count()
    
    # Upcoming in next 24 hours
    upcoming_24h = db.query(ScheduledNews).filter(
        ScheduledNews.status == "pending",
        ScheduledNews.scheduled_at >= now,
        ScheduledNews.scheduled_at <= now + timedelta(hours=24)
    ).count()
    
    # Overdue (should have been published but still pending)
    overdue = db.query(ScheduledNews).filter(
        ScheduledNews.status == "pending",
        ScheduledNews.scheduled_at < now
    ).count()
    
    # Most scheduled users
    top_schedulers = db.query(
        ScheduledNews.user_uid,
        func.count(ScheduledNews.id).label('count')
    ).group_by(ScheduledNews.user_uid).order_by(desc('count')).limit(5).all()
    
    return {
        "total_scheduled": total_scheduled,
        "status_breakdown": {
            "pending": pending,
            "published": published,
            "failed": failed,
            "cancelled": cancelled
        },
        "upcoming_24h": upcoming_24h,
        "overdue": overdue,
        "top_schedulers": [
            {"user_uid": s.user_uid, "count": s.count}
            for s in top_schedulers
        ]
    }

