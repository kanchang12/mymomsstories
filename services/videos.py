"""
services/videos.py — free public video section, one YouTube playlist.

YouTube supports multiple audio tracks per video (Studio > Subtitles >
Add language, or Audio Tracks) — one video carries all 14 language dubs,
and the viewer switches language from the player's own settings gear
(⚙ → Audio). So this service does NOT sort videos by language — that's
handled entirely inside the YouTube player.

Auto-populate setup:
  1. Create one playlist on YouTube and add your story videos to it.
  2. Get its ID — the part after "list=" in the playlist URL, e.g.
       youtube.com/playlist?list=PLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     → PLxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
  3. Set YOUTUBE_PLAYLIST_ID to that value in .env.

From then on, just add new videos to that playlist — they show up on
/videos automatically (cached ~15 min, no redeploy). We read the
playlist's public RSS feed — free, no API key, no quota.
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


def _playlist_id() -> str:
    return os.environ.get("YOUTUBE_PLAYLIST_ID", "").strip()


def _fetch_playlist_feed(playlist_id: str) -> list:
    url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
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

    playlist_id = _playlist_id()
    if not playlist_id:
        return []

    try:
        videos = _fetch_playlist_feed(playlist_id)
    except Exception as e:
        print(f"[videos] Failed to fetch playlist feed: {e}")
        videos = _cache["videos"]

    _cache["videos"] = videos
    _cache["fetched_at"] = now
    return videos
