# Script for pulling YouTube comments using API
import yaml
import os
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


def load_api_key():
    # Load the API key from the YAML file
    with open("../config/config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config["api_keys"]["youtube"]


def search_videos(api_key, query, max_results=5):
    # Search for videos using the YouTube Data API
    youtube = build("youtube", "v3", developerKey=api_key)
    search_response = (
        youtube.search()
        .list(q=query, type="video", part="id", maxResults=max_results)
        .execute()
    )

    video_ids = []
    for item in search_response.get("items", []):
        video_id = item.get("id", {}).get("videoId")
        print(video_ids)
        video_ids.append(video_id) if video_id else None
    return video_ids


def get_comments(api_key, video_id, max_comments=100):
    # Get comments for a specific video using the YouTube Data API
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    try:
        response = (
            youtube.commentThreads()
            .list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=max_comments,
            )
            .execute()
        )
        for item in response.get("items", []):
            comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append(
                {
                    "author": comment["authorDisplayName"],
                    "text": comment["textDisplay"],
                    "like_count": comment["likeCount"],
                    "published_at": comment["publishedAt"],
                }
            )
    except HttpError as e:
        print(f"An error occurred: {e}")

    print(len(comments), "comments retrieved for video ID:", video_id)
    return comments


def run_scraper(query, max_results=5, max_comments=100):
    # Main function to run the scraper
    api_key = load_api_key()
    video_ids = search_videos(api_key, query, max_results)

    all_comments = []
    for video_id in video_ids:
        comments = get_comments(api_key, video_id, max_comments)
        all_comments.extend(comments)

    # Make sure the raw folder exists
    os.makedirs("../data/raw", exist_ok=True)

    # Save comments to a CSV file
    df = pd.DataFrame(all_comments)
    df.to_csv("../data/raw/comments.csv", index=False)
    print("Comments saved to comments.csv")


if __name__ == "__main__":
    # Example usage
    run_scraper("Python programming", max_results=1, max_comments=100)
