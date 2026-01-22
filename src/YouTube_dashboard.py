import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from sqlalchemy import create_engine
import os

# =========================
# Database Configuration from environment variables
# =========================
DB_HOST = os.getenv("DB_HOST", "db")  # default to 'db' for Docker
DB_PORT = int(os.getenv("DB_PORT", 5432))
DB_NAME = os.getenv("DB_NAME", "youtube_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")


# SQLAlchemy engine for pandas
def get_engine():
    try:
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        return engine
    except Exception as e:
        st.error(f"Failed to create database engine: {e}")
        return None


# =========================
# Load Data
# =========================
@st.cache_data
def load_data():
    engine = get_engine()
    if engine is None:
        return pd.DataFrame()

    query = "SELECT * FROM youtube_videos"
    try:
        df = pd.read_sql(query, engine)
        if 'published_at' in df.columns:
            df['published_at'] = pd.to_datetime(df['published_at'])
        return df
    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()


df = load_data()
if df.empty:
    st.warning("No data available or failed to connect to the database.")
    st.stop()

# =========================
# Streamlit Layout
# =========================
st.set_page_config(page_title="YouTube Dashboard", layout="wide")
st.title("📊 YouTube Channel Dashboard")
st.markdown("Insights from selected YouTube channels")

# =========================
# Sidebar Filters
# =========================
channels = df['channel_title'].unique()
selected_channels = st.sidebar.multiselect("Select Channels", channels, default=channels)

date_min = df['published_at'].min().date()
date_max = df['published_at'].max().date()
selected_dates = st.sidebar.date_input("Select Date Range", [date_min, date_max])

min_views, max_views = int(df['view_count'].min()), int(df['view_count'].max())
selected_views = st.sidebar.slider("Filter by Views", min_views, max_views, (min_views, max_views))

df_filtered = df[
    (df['channel_title'].isin(selected_channels)) &
    (df['published_at'].dt.date >= selected_dates[0]) &
    (df['published_at'].dt.date <= selected_dates[1]) &
    (df['view_count'] >= selected_views[0]) &
    (df['view_count'] <= selected_views[1])
    ]


# =========================
# KPI Colors Helper
# =========================
def kpi_color(value, thresholds=(1000, 10000)):
    if value >= thresholds[1]:
        return "normal"  # green
    elif value >= thresholds[0]:
        return "inverse"  # yellow
    else:
        return "off"  # red


# =========================
# Metrics Cards
# =========================
total_videos = len(df_filtered)
total_views = df_filtered['view_count'].sum()
total_likes = df_filtered['like_count'].sum()
total_comments = df_filtered['comment_count'].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🎥 Total Videos", total_videos)
col2.metric("👁 Total Views", f"{total_views:,}")
col3.metric("👍 Total Likes", f"{total_likes:,}")
col4.metric("💬 Total Comments", f"{total_comments:,}")

st.markdown("---")

# =========================
# Views Over Time Chart
# =========================
st.subheader("📈 Views Over Time")
views_chart = df_filtered.groupby(['published_at', 'channel_title']).sum().reset_index()
fig_views = px.line(
    views_chart,
    x='published_at',
    y='view_count',
    color='channel_title',
    markers=True,
    hover_data={'channel_title': True, 'view_count': True},
    title="Views Trend"
)
st.plotly_chart(fig_views, width="stretch")

# =========================
# Likes vs Comments Scatter
# =========================
st.subheader("👍 Likes vs 💬 Comments")
fig_scatter = px.scatter(
    df_filtered,
    x='like_count',
    y='comment_count',
    color='channel_title',
    hover_data=['title', 'view_count'],
    size='view_count',
    title="Engagement: Likes vs Comments (size=views)"
)
st.plotly_chart(fig_scatter, width="stretch")

# =========================
# Latest Videos with Thumbnails and Playable Video
# =========================
st.subheader("🎥 Latest Videos")
for _, row in df_filtered.sort_values("published_at", ascending=False).iterrows():
    col1, col2 = st.columns([1, 3])
    with col1:
        thumbnail_url = f"https://img.youtube.com/vi/{row['video_id']}/hqdefault.jpg"
        st.image(thumbnail_url, width="stretch")
    with col2:
        st.markdown(f"**{row['title']}**")
        st.markdown(f"*Channel:* {row['channel_title']}")
        st.markdown(f"*Published:* {row['published_at'].strftime('%Y-%m-%d')}")
        st.markdown(
            f"*Views:* {row['view_count']:,} | *Likes:* {row['like_count']:,} | *Comments:* {row['comment_count']:,}")
        st.video(f"https://www.youtube.com/watch?v={row['video_id']}")
        st.markdown("---")
