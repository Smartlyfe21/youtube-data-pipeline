from googleapiclient.discovery import build
from config import API_KEY

# Default handles — you can modify/add more here
CHANNEL_HANDLES = ["@melrobbins", "@TheDiaryOfACEO", "@JayShettyPodcast"]

def get_channel_id(channel_handle):
    # Remove leading @ if present
    channel_name = channel_handle.lstrip("@")
    youtube = build("youtube", "v3", developerKey=API_KEY)
    request = youtube.search().list(
        part="snippet",
        q=channel_name,
        type="channel",
        maxResults=1
    )
    response = request.execute()
    if response.get("items"):
        channel_id = response["items"][0]["snippet"]["channelId"]
        print(f"✅ Channel ID for '{channel_handle}': {channel_id}")
    else:
        print(f"❌ No channel found for '{channel_handle}'")

if __name__ == "__main__":
    print("🔎 Fetching channel IDs for default handles...\n")
    for handle in CHANNEL_HANDLES:
        get_channel_id(handle)
