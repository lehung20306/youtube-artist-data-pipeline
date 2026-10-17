import os
import logging
from dotenv import load_dotenv
import pandas as pd

from elt.extract import get_channel_data, get_latest_videos, get_video_statistics, get_video_comments
from elt.transform import transform_data_on_bigquery
from elt.load import load_data_to_bigquery
from elt.utils.file_io import load_from_json

# Set up logging
logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    logger.info("Starting ELT process...")

    # Define the list of YouTube channels to extract data from
    youtube_channel = pd.read_csv("data/top100_artists_seed.csv", encoding="latin1").to_dict('records')

    # Load environment variables from .env file
    load_dotenv()
    API_KEY = os.getenv("API_KEY")
    if not API_KEY:
        logger.error("API_KEY not found in environment variables.")
        return

    # Extract data from YouTube API
    
    channel_data = get_channel_data(youtube_channel, API_KEY=API_KEY)
    latest_videos = get_latest_videos(youtube_channel, API_KEY=API_KEY, max_videos_per_channel = 50)
    video_ids = [video["snippet"]["resourceId"]["videoId"] for video in latest_videos]
    video_stats = get_video_statistics(video_ids, API_KEY=API_KEY)
    videos_for_comments = []
    for channel in youtube_channel:
        chan_id = channel["channel_id"]
        chan_videos = [v["snippet"]["resourceId"]["videoId"] for v in latest_videos if v["snippet"]["channelId"] == chan_id]
        videos_for_comments.extend(chan_videos[:30])
    video_comments = get_video_comments(videos_for_comments, API_KEY=API_KEY)

    # channel_data = load_from_json("channel_metadata.json")
    # latest_videos = load_from_json("playlist_latest_videos.json")
    # video_stats = load_from_json("video_statistics.json")
    # video_comments = load_from_json("video_comments.json")

    # Load the raw data into BigQuery
    load_data_to_bigquery(channel_data, "data-project-511514.artist_youtube_elt.raw_channel_data")
    load_data_to_bigquery(video_stats, "data-project-511514.artist_youtube_elt.raw_video_statistics")
    load_data_to_bigquery(latest_videos, "data-project-511514.artist_youtube_elt.raw_latest_videos")
    load_data_to_bigquery(video_comments, "data-project-511514.artist_youtube_elt.raw_video_comments")

    # transform data on Bigquery
    transform_data_on_bigquery()

if __name__ == "__main__":
    main()
    logger.info("ELT process completed successfully.")