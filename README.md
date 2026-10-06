# YouTube Finder

Search YouTube videos and see what's trending, using the YouTube Data API v3.
A small Flask app with a one-page UI, deployed on Vercel.

Live: https://tubefinder-pro.vercel.app

## Endpoints

| Path | Parameters |
|------|------------|
| `/` | Web UI (search, trending, CSV/JSON export) |
| `/search` | `q`, `max_results` (1-50), `order` (`relevance`, `date`, `viewCount`) |
| `/trending` | `region` (e.g. `PK`, `US`), `max_results`, `category` (optional) |
| `/video` | `video_id` |
| `/channel` | `channel_id` |
| `/info` | Endpoint list and whether the key is configured |

## Setup

1. Create an API key in Google Cloud Console and enable **YouTube Data API v3**. Restrict the key to that API.
2. Set it as an environment variable. Never commit it:
   - Locally: `export YOUTUBE_API_KEY=...` then `flask --app app run`
   - Vercel: Project Settings, Environment Variables, `YOUTUBE_API_KEY`
3. Deploy to Vercel (the Flask framework is detected from `app.py`).

The tool reads public data only and cannot download videos. Search requests use much more of the daily API quota than lookups.
