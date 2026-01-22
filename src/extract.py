import pandas as pd
from googleapiclient.discovery import build
from config import API_KEY

# Default handles — you can add/remove handles here
CHANNEL_HANDLES = ["@melrobbins", "@TheDiaryOfACEO", "@JayShettyPodcast"]

def get_youtube_client():
    """Initialize YouTube API client"""
    return build('youtube', 'v3', developerKey=API_KEY, cache_discovery=False)

def get_channel_id_from_handle(youtube, handle):
    """
    Convert a handle (e.g., @melrobbins) to a channel ID using search.
    """
    handle_name = handle.lstrip("@")
    request = youtube.search().list(
        part='snippet',
        q=handle_name,
        type='channel',
        maxResults=1
    )
    response = request.execute()
    items = response.get('items', [])
    if not items:
        print(f"⚠️ Could not find channel ID for handle: {handle}")
        return None, None
    channel_id = items[0]['snippet']['channelId']
    channel_title = items[0]['snippet']['title']
    print(f"✅ Found channel ID for {handle}: {channel_id} ({channel_title})")
    return channel_id, channel_title

def fetch_videos(youtube, channel_id, channel_title, max_results=50):
    """Fetch videos from a specific channel ID."""
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        maxResults=max_results,
        order='date',
        type='video'
    )
    response = request.execute()
    items = response.get('items', [])
    videos = []
    for item in items:
        if item.get('id', {}).get('kind') == 'youtube#video':
            videos.append({
                'video_id': item['id']['videoId'],
                'title': item['snippet']['title'],
                'description': item['snippet']['description'],
                'published_at': item['snippet']['publishedAt'],
                'channel_id': channel_id,
                'channel_title': channel_title
            })
    return pd.DataFrame(videos)

def fetch_video_stats(youtube, video_ids):
    """Fetch video statistics such as views, likes, and comments."""
    all_stats = []
    for i in range(0, len(video_ids), 50):
        batch_ids = video_ids[i:i + 50]
        request = youtube.videos().list(
            part='statistics,snippet',
            id=','.join(batch_ids)
        )
        response = request.execute()
        for item in response.get('items', []):
            stats = item.get('statistics', {})
            video_data = {
                'video_id': item['id'],
                'title': item['snippet']['title'],
                'published_at': item['snippet']['publishedAt'],
                'view_count': int(stats.get('viewCount', 0)),
                'like_count': int(stats.get('likeCount', 0)),
                'comment_count': int(stats.get('commentCount', 0))
            }
            all_stats.append(video_data)
    return pd.DataFrame(all_stats)

def fetch_videos_by_usernames(handles=None, max_results=50):
    """
    Fetch videos and stats from multiple handles.
    Returns two DataFrames: all_videos, all_stats.
    """
    if handles is None:
        handles = CHANNEL_HANDLES

    youtube = get_youtube_client()
    all_videos_list = []
    all_stats_list = []

    for handle in handles:
        print(f"🔎 Fetching videos for handle: {handle}")
        channel_id, channel_title = get_channel_id_from_handle(youtube, handle)
        if not channel_id:
            continue

        videos_df = fetch_videos(youtube, channel_id, channel_title, max_results=max_results)
        if videos_df.empty:
            print(f"⚠️ No videos found for channel: {handle}")
            continue
        all_videos_list.append(videos_df)

        video_ids = videos_df['video_id'].tolist()
        stats_df = fetch_video_stats(youtube, video_ids)
        all_stats_list.append(stats_df)

    all_videos = pd.concat(all_videos_list, ignore_index=True) if all_videos_list else pd.DataFrame()
    all_stats = pd.concat(all_stats_list, ignore_index=True) if all_stats_list else pd.DataFrame()
    return all_videos, all_stats
