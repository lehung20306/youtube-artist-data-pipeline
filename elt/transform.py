import logging
from google.cloud import bigquery

logger = logging.getLogger(__name__)

def transform_data_on_bigquery():
    client = bigquery.Client()

    sql_channel = """
        CREATE OR REPLACE TABLE `data-project-511514.artist_youtube_elt.processed_channel_data` AS
        SELECT 
            id AS channel_id,
            snippet.title AS channel_name,
            CAST(statistics.subscriberCount AS INT64) AS subscriber_count,
            CAST(statistics.videoCount AS INT64) AS video_count,
            CAST(statistics.viewCount AS INT64) AS view_count,
            CURRENT_TIMESTAMP() AS extracted_at
        FROM `data-project-511514.artist_youtube_elt.raw_channel_data`
    """

    sql_video = """
        CREATE OR REPLACE TABLE `data-project-511514.artist_youtube_elt.processed_video_data` AS
        SELECT 
            v.snippet.channelId AS channel_id,
            v.snippet.resourceId.videoId AS video_id,
            v.snippet.title AS video_title,
            v.snippet.description AS description,
            CAST(v.snippet.publishedAt AS TIMESTAMP) AS published_at,
            CAST(s.statistics.viewCount AS INT64) AS view_count,
            CAST(s.statistics.likeCount AS INT64) AS like_count,
            CAST(s.statistics.commentCount AS INT64) AS comment_count,
            CURRENT_TIMESTAMP() AS extracted_at
        FROM 
            `data-project-511514.artist_youtube_elt.raw_latest_videos` v
        INNER JOIN 
            `data-project-511514.artist_youtube_elt.raw_video_statistics` s
        ON 
            v.snippet.resourceId.videoId = s.id
    """

    sql_comment = """
        CREATE OR REPLACE TABLE `data-project-511514.artist_youtube_elt.processed_video_comments` AS
        SELECT 
            snippet.videoId AS video_id,
            id AS comment_id,
            snippet.topLevelComment.snippet.authorDisplayName AS author_name,
            snippet.topLevelComment.snippet.textDisplay AS comment_text,
            CAST(snippet.topLevelComment.snippet.publishedAt AS TIMESTAMP) AS published_at,
            CAST(snippet.topLevelComment.snippet.updatedAt AS TIMESTAMP) AS updated_at,
            CAST(snippet.topLevelComment.snippet.likeCount AS INT64) AS like_count,
            CAST(snippet.totalReplyCount AS INT64) AS reply_count,
            CURRENT_TIMESTAMP() AS extracted_at
        FROM 
            `data-project-511514.artist_youtube_elt.raw_video_comments`
    """

    try:
        job_channel = client.query(sql_channel)
        job_channel.result()

        job_video = client.query(sql_video)
        job_video.result()

        job_comment = client.query(sql_comment)
        job_comment.result()

    except Exception as e:
        logger.error(f"Transform error: {e}")
        raise

if __name__ == "__main__":
    print(1)