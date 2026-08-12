# ============================================================
# src/youtube_api.py
# ============================================================
# Purpose:
#   A thin, well-documented wrapper around the YouTube Data
#   API v3.  Handles authentication, pagination, quota errors,
#   and missing fields so that collect_data.py stays clean.
#
# API documentation:
#   https://developers.google.com/youtube/v3/docs
#
# QUOTA NOTE:
#   YouTube gives each project 10,000 quota units per day.
#   • search.list  costs 100 units per call
#   • videos.list  costs  1 unit per call (up to 50 IDs)
#   This module minimises quota usage by batching video IDs.
# ============================================================

import time
import logging
from typing import Optional

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.utils import get_logger, safe_int

logger = get_logger(__name__)


class YouTubeAPI:
    """
    Wrapper for the YouTube Data API v3.

    Usage
    -----
    api = YouTubeAPI(api_key="YOUR_KEY")
    videos = api.search_videos(query="data analytics", max_results=100)
    """

    # Maximum number of results the API allows per single request
    MAX_PER_PAGE = 50

    def __init__(self, api_key: str):
        """
        Build the authenticated API client.

        Parameters
        ----------
        api_key : str
            Your YouTube Data API v3 key from Google Cloud Console.
        """
        if not api_key:
            raise ValueError(
                "YouTube API key is empty. "
                "Please set YOUTUBE_API_KEY in your .env file."
            )

        self._api_key = api_key
        # build() creates the API client object
        self._youtube = build("youtube", "v3", developerKey=api_key)
        logger.info("YouTube API client initialised successfully.")

    # ── Public methods ───────────────────────────────────────

    def search_videos(self, query: str, max_results: int = 50) -> list[dict]:
        """
        Search YouTube for videos matching a keyword query.

        Parameters
        ----------
        query       : str  — search term (e.g. "data analytics")
        max_results : int  — total videos to retrieve (up to ~500
                             before quota limits become a concern)

        Returns
        -------
        list[dict]  — list of enriched video dictionaries
        """
        logger.info(f"Searching for '{query}' — target {max_results} videos")
        video_ids = self._search_video_ids(query=query, max_results=max_results)
        logger.info(f"Retrieved {len(video_ids)} video IDs from search")
        return self._get_video_details(video_ids)

    def get_channel_videos(self, channel_id: str, max_results: int = 50) -> list[dict]:
        """
        Retrieve videos from a specific YouTube channel.

        Parameters
        ----------
        channel_id  : str — YouTube channel ID (starts with "UC")
        max_results : int

        Returns
        -------
        list[dict]
        """
        logger.info(f"Fetching videos for channel {channel_id}")
        video_ids = self._get_channel_video_ids(channel_id, max_results)
        logger.info(f"Found {len(video_ids)} videos in channel")
        return self._get_video_details(video_ids)

    def get_videos_by_ids(self, video_ids: list[str]) -> list[dict]:
        """
        Retrieve details for a specific list of video IDs.

        Parameters
        ----------
        video_ids : list[str]

        Returns
        -------
        list[dict]
        """
        return self._get_video_details(video_ids)

    # ── Private helpers ──────────────────────────────────────

    def _search_video_ids(self, query: str, max_results: int) -> list[str]:
        """
        Use search.list to collect video IDs for a keyword.
        Handles pagination automatically.
        """
        video_ids = []
        page_token = None

        while len(video_ids) < max_results:
            # How many to request in this page (max 50 per API call)
            page_size = min(self.MAX_PER_PAGE, max_results - len(video_ids))

            try:
                response = self._youtube.search().list(
                    part="id",
                    q=query,
                    type="video",
                    maxResults=page_size,
                    pageToken=page_token,
                ).execute()
            except HttpError as e:
                self._handle_http_error(e)
                break

            for item in response.get("items", []):
                vid_id = item.get("id", {}).get("videoId")
                if vid_id:
                    video_ids.append(vid_id)

            page_token = response.get("nextPageToken")
            if not page_token:
                break   # No more pages available

            # Polite pause to avoid hitting rate limits
            time.sleep(0.5)

        return video_ids

    def _get_channel_video_ids(self, channel_id: str, max_results: int) -> list[str]:
        """
        Use search.list filtered by channelId to get video IDs.
        """
        video_ids = []
        page_token = None

        while len(video_ids) < max_results:
            page_size = min(self.MAX_PER_PAGE, max_results - len(video_ids))

            try:
                response = self._youtube.search().list(
                    part="id",
                    channelId=channel_id,
                    type="video",
                    order="date",
                    maxResults=page_size,
                    pageToken=page_token,
                ).execute()
            except HttpError as e:
                self._handle_http_error(e)
                break

            for item in response.get("items", []):
                vid_id = item.get("id", {}).get("videoId")
                if vid_id:
                    video_ids.append(vid_id)

            page_token = response.get("nextPageToken")
            if not page_token:
                break

            time.sleep(0.5)

        return video_ids

    def _get_video_details(self, video_ids: list[str]) -> list[dict]:
        """
        Use videos.list to fetch snippet + contentDetails + statistics
        for a list of video IDs.

        Batches requests in groups of 50 (API maximum).
        """
        if not video_ids:
            logger.warning("No video IDs provided — returning empty list")
            return []

        all_videos = []

        # Split into batches of 50
        for i in range(0, len(video_ids), self.MAX_PER_PAGE):
            batch = video_ids[i : i + self.MAX_PER_PAGE]
            ids_str = ",".join(batch)

            try:
                response = self._youtube.videos().list(
                    part="snippet,contentDetails,statistics",
                    id=ids_str,
                ).execute()
            except HttpError as e:
                self._handle_http_error(e)
                continue

            for item in response.get("items", []):
                video_data = self._parse_video_item(item)
                if video_data:
                    all_videos.append(video_data)

            time.sleep(0.2)   # polite pause between batch requests

        logger.info(f"Successfully parsed {len(all_videos)} videos")
        return all_videos

    def _parse_video_item(self, item: dict) -> Optional[dict]:
        """
        Extract and flatten all required fields from a single
        API response item.

        Uses .get() throughout so missing fields never cause
        a KeyError — they just return None or a default value.
        """
        try:
            snippet         = item.get("snippet", {})
            content_details = item.get("contentDetails", {})
            statistics      = item.get("statistics", {})

            return {
                # Identifiers
                "video_id":             item.get("id"),
                "title":                snippet.get("title", ""),
                "description":          snippet.get("description", ""),
                "channel_id":           snippet.get("channelId", ""),
                "channel_title":        snippet.get("channelTitle", ""),

                # Publication
                "published_at":         snippet.get("publishedAt"),
                "category_id":          snippet.get("categoryId", ""),

                # Content details
                "duration":             content_details.get("duration", ""),
                "definition":           content_details.get("definition", ""),
                "caption_status":       content_details.get("caption", ""),
                "live_broadcast_content": snippet.get("liveBroadcastContent", ""),

                # Tags (stored as pipe-separated string)
                "tags": "|".join(snippet.get("tags", [])),

                # Statistics — use safe_int because some may be hidden
                "view_count":           safe_int(statistics.get("viewCount")),
                "like_count":           safe_int(statistics.get("likeCount")),
                "comment_count":        safe_int(statistics.get("commentCount")),
                "favorite_count":       safe_int(statistics.get("favoriteCount")),
            }
        except Exception as exc:
            logger.warning(f"Could not parse video item: {exc}")
            return None

    @staticmethod
    def _handle_http_error(error: HttpError) -> None:
        """
        Log a helpful message for common YouTube API HTTP errors.
        """
        code = error.resp.status
        if code == 400:
            logger.error("Bad request — check your query parameters.")
        elif code == 403:
            logger.error(
                "API quota exceeded or key invalid. "
                "Check https://console.cloud.google.com/ for quota usage."
            )
        elif code == 404:
            logger.error("Resource not found — video or channel may be deleted.")
        else:
            logger.error(f"YouTube API HTTP error {code}: {error}")
