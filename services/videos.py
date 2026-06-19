"""
services/videos.py — free public video section.

YouTube supports multiple audio tracks per video (Studio > Subtitles >
Add language, or the Audio Tracks feature) — one video carries all 14
language dubs, and the viewer switches language from the player's own
settings gear (⚙ → Audio). So this service does NOT sort videos by
language at all — that's handled entirely inside the YouTube player.

Auto-populate setup:
  1. Set YOUTUBE_CHANNEL_ID in .env to your channel's ID (Studio > Settings
     > Channel > Advanced, or from your channel URL if it's a /channel/UC...
     style URL).
  2. Push a video to your channel, with extra audio tracks added for each
     language if you want — it appears on /videos automatically.

We read the channel's public "uploads" RSS feed — free, no API key, no
quota — cached for 15 minutes so the site isn't hitting YouTube on every
visit.
"""
import os
import time
from xml.etree import ElementTree as ET
import requests

ATOM_NS = {
    "atom":  "http://www.w3.org/2005/Atom",
    "yt":    "http://www.youtube.com/xml/schemas/2015",
    "media": "http://search.yahoo.com/mrss/",
}

CACHE_TTL = 900  # 15 minutes
_cache = {"videos": [], "fetched_at": 0}


def _channel_id() -> str:
    return os.environ.get("YOUTUBE_CHANNEL_ID", "").strip()


def _fetch_channel_feed(channel_id: str) -> list:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    root = ET.fromstring(r.text)

    videos = []
    for entry in root.findall("atom:entry", ATOM_NS):
        video_id_el = entry.find("yt:videoId", ATOM_NS)
        title_el    = entry.find("atom:title", ATOM_NS)
        pub_el      = entry.find("atom:published", ATOM_NS)
        if video_id_el is None or title_el is None:
            continue

        video_id = video_id_el.text
        thumb_url = f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        media_group = entry.find("media:group", ATOM_NS)
        if media_group is not None:
            thumb = media_group.find("media:thumbnail", ATOM_NS)
            if thumb is not None and thumb.get("url"):
                thumb_url = thumb.get("url")

        videos.append({
            "id":        video_id,
            "title":     title_el.text or "",
            "published": pub_el.text if pub_el is not None else "",
            "thumb":     thumb_url,
        })

    videos.sort(key=lambda v: v["published"], reverse=True)
    return videos


def get_videos(force: bool = False) -> list:
    now = time.time()
    if not force and (now - _cache["fetched_at"] < CACHE_TTL) and _cache["videos"]:
        return _cache["videos"]

    channel_id = _channel_id()
    if not channel_id:
        return []

    try:
        videos = _fetch_channel_feed(channel_id)
    except Exception as e:
        print(f"[videos] Failed to fetch channel feed: {e}")
        videos = _cache["videos"]

    _cache["videos"] = videos
    _cache["fetched_at"] = now
    return videos
