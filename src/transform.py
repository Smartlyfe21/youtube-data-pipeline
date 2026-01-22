import pandas as pd

def transform_videos(videos_df, stats_df):
    """
    Merge raw video info with statistics and clean data.
    Returns a transformed DataFrame ready for loading into DB.
    """
    # Merge on video_id
    df = pd.merge(videos_df, stats_df, on='video_id', how='left')

    # Standardize column names
    df.rename(columns={
        'title_x': 'title',
        'published_at_x': 'published_at'
    }, inplace=True)

    # Convert published_at to datetime
    df['published_at'] = pd.to_datetime(df['published_at'], errors='coerce')

    # Fill missing stats with 0
    df['view_count'] = df['view_count'].fillna(0).astype(int)
    df['like_count'] = df['like_count'].fillna(0).astype(int)
    df['comment_count'] = df['comment_count'].fillna(0).astype(int)

    # Optional: clean text fields
    df['title'] = df['title'].astype(str).str.strip()
    df['description'] = df['description'].astype(str).str.strip()
    df['channel_title'] = df['channel_title'].astype(str).str.strip()

    # Remove duplicates if any
    df.drop_duplicates(subset=['video_id'], inplace=True)

    return df
