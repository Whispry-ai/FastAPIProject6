"""
Models package initialization
"""

# Import all models to make them available
from .user import User, OTPStore, UserPreference
from .news import News, Reaction, Comment, Share, NewsView, NewsFlag, ScheduledNews, Category
from .content import Advertisement, Event, Poll, SponsoredPost, YouTubeShort, ContentSchedule, FlaggedContent, ContentTagMapping, ContentVersion
from .engagement import Bookmark, Notification
from .guest import GuestUser, GuestPreference
from .base_location import State, District, City, Language
from .insorts import Insight, InsightPage, InsightShare

__all__ = [
    'User', 'OTPStore', 'UserPreference',
    'News', 'Reaction', 'Comment', 'Share', 'NewsView', 'NewsFlag', 'ScheduledNews',
    'Category', 'Advertisement', 'Event', 'Poll', 'SponsoredPost', 'YouTubeShort', 'ContentSchedule', 'FlaggedContent', 'ContentTagMapping', 'ContentVersion',
    'Bookmark', 'Notification',
    'GuestUser', 'GuestPreference',
    'State', 'District', 'City', 'Language',
    'Insight', 'InsightPage', 'InsightShare'
]