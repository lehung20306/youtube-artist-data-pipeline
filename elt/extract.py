import requests
from .utils.file_io import save_to_json
import logging

logger = logging.getLogger(__name__)

def get_channel_data(channels_list:list, API_KEY:str):
    if not channels_list:
        logger.warning("No channels provided for metadata extraction.")
        return []   
    
    url = "https://www.googleapis.com/youtube/v3/channels"

    all_data = []

    for i in range(0, len(channels_list), 50):
        batch_channels = channels_list[i:i + 50]

        params = {
            "id": ",".join([ch["channel_id"] for ch in batch_channels]),
            "key": API_KEY,
            "part": "snippet,statistics,contentDetails"
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json().get("items", [])
            all_data.extend(data)
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")

    save_to_json(all_data, "channel_metadata.json")
    return all_data

def get_latest_videos(channels_list:list, API_KEY:str, max_videos_per_channel=150):
    if not channels_list:
        logger.warning("No channels provided for video extraction.")
        return []   
    
    url = "https://www.googleapis.com/youtube/v3/playlistItems"

    all_videos = []

    for channel in channels_list:
        video_fetch = 0
        next_page_token = None

        while video_fetch < max_videos_per_channel:
            fetch_count = min(50, max_videos_per_channel - video_fetch)
            params = {
                "part": "snippet",
                "playlistId": channel["uploads_playlist_id"],
                "maxResults": fetch_count,
                "key": API_KEY
            }

            if next_page_token:
                params["pageToken"] = next_page_token

            response = requests.get(url, params=params)

            if response.status_code == 200:
                all_videos.extend(response.json().get("items", []))
                video_fetch += len(response.json().get("items", []))
                next_page_token = response.json().get("nextPageToken")
            else:
                logger.error(f"Error: {response.status_code} - {response.text}")
            
            if not next_page_token:
                break

    save_to_json(all_videos, "playlist_latest_videos.json")
    return all_videos


def get_video_statistics(video_id_list: list, API_KEY:str):
    if not video_id_list:
        logger.warning("No video IDs provided for statistics extraction.")
        return []   
    
    url = "https://www.googleapis.com/youtube/v3/videos"

    all_stats = []

    for i in range(0, len(video_id_list), 50):
        batch_ids = video_id_list[i:i + 50]

        params = {
            "id": ",".join(batch_ids),
            "key": API_KEY,
            "part": "snippet,statistics"
        
        }
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            all_stats.extend(response.json().get("items", []))
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")
    
    save_to_json(all_stats, "video_statistics.json")
    return all_stats

def get_video_comments(video_id_list: list, API_KEY:str, max_results=50):
    if not video_id_list:
        logger.warning("No video IDs provided for comment extraction.")
        return []
    
    url = "https://www.googleapis.com/youtube/v3/commentThreads"

    all_comments = []

    for video_id in video_id_list:
        params = {
            "videoId": video_id,
            "key": API_KEY,
            "part": "snippet",
            "maxResults": max_results,
            "order": "relevance"
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            all_comments.extend(response.json().get("items", []))
        else:
            logger.error(f"Error: {response.status_code} - {response.text}")

    save_to_json(all_comments, "video_comments.json")
    return all_comments

if __name__ == "__main__":
    print(1)