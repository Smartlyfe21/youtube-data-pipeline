import psycopg2
from config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD

REQUIRED_COLUMNS = [
    'video_id', 'title', 'description', 'published_at',
    'channel_id', 'channel_title', 'view_count', 'like_count', 'comment_count'
]

def load_to_db(df, table_name="youtube_videos"):
    """
    Load transformed DataFrame into PostgreSQL.
    Ensures all required columns exist.
    """
    # Check for missing columns
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

    # Connection
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()

    # Create table if not exists
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        video_id TEXT PRIMARY KEY,
        title TEXT,
        description TEXT,
        published_at TIMESTAMP,
        channel_id TEXT,
        channel_title TEXT,
        view_count BIGINT,
        like_count BIGINT,
        comment_count BIGINT
    );
    """
    cursor.execute(create_table_query)
    conn.commit()

    # Insert data
    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT INTO {table_name} (video_id, title, description, published_at, channel_id, channel_title, view_count, like_count, comment_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (video_id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                published_at = EXCLUDED.published_at,
                channel_id = EXCLUDED.channel_id,
                channel_title = EXCLUDED.channel_title,
                view_count = EXCLUDED.view_count,
                like_count = EXCLUDED.like_count,
                comment_count = EXCLUDED.comment_count;
        """, (
            row['video_id'], row['title'], row['description'], row['published_at'],
            row['channel_id'], row['channel_title'], row['view_count'],
            row['like_count'], row['comment_count']
        ))
    conn.commit()
    cursor.close()
    conn.close()
    print(f"✅ Loaded {len(df)} records into {table_name}.")
