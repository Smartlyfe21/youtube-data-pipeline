from extract import fetch_videos_by_usernames
from transform import transform_videos
from load import load_to_db

def run_etl():
    print("🚀 Starting YouTube ETL process...")

    # --- Extract raw videos and stats from multiple handles ---
    print("📥 Fetching videos from YouTube...")
    handles = ["@melrobbins", "@TheDiaryOfACEO", "@JayShettyPodcast"]
    videos_df, stats_df = fetch_videos_by_usernames(handles=handles, max_results=50)

    if videos_df.empty:
        print("⚠️ No videos extracted from any channels. Exiting ETL.")
        return
    if stats_df.empty:
        print("⚠️ No statistics fetched. Exiting ETL.")
        return

    # --- Transform ---
    print("🧹 Transforming data...")
    df_transformed = transform_videos(videos_df, stats_df)
    if df_transformed.empty:
        print("⚠️ Transformation resulted in empty DataFrame. Exiting ETL.")
        return

    # --- Load ---
    print("💾 Loading data into PostgreSQL...")
    load_to_db(df_transformed)

    print("✅ ETL process completed successfully!")

if __name__ == "__main__":
    run_etl()
