import re
import asyncio
import logging
import yt_dlp

# YouTube URL regex patterns
YOUTUBE_URL_REGEX = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
YOUTUBE_PLAYLIST_REGEX = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(playlist\?list=)([^&=%\?]+)'

logger = logging.getLogger('discord')

def get_ytdlp_options():
    """Get the options for yt-dlp"""
    return {
        'format': 'bestaudio/best',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': False,  # Allow playlist processing
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        # Add cookies and user agent to avoid 403 errors
        'cookiefile': None,
        'age_limit': None,
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash']
            }
        }
    }

def get_ffmpeg_options():
    """Get the options for FFmpeg"""
    return {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn',
    }

def is_youtube_url(url):
    """Check if a URL is a valid YouTube video URL"""
    return re.match(YOUTUBE_URL_REGEX, url) is not None

def is_youtube_playlist(url):
    """Check if a URL is a valid YouTube playlist URL"""
    return re.match(YOUTUBE_PLAYLIST_REGEX, url) is not None

async def extract_info(ytdl, url, download=False):
    """Extract info from a YouTube URL using yt-dlp"""
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=download))
    return data

async def get_song_info(ytdl, url):
    """Get song info from a YouTube URL or search query"""
    try:
        if is_youtube_playlist(url):
            # Handle playlist
            info = await extract_info(ytdl, url)
            if 'entries' not in info:
                raise ValueError("Could not find any videos in the playlist")
            return [{'title': entry.get('title', 'Unknown'), 
                    'url': entry.get('url', None),
                    'webpage_url': entry.get('webpage_url', url),
                    'duration': entry.get('duration', 0),
                    'video_id': entry.get('id', None)} 
                    for entry in info['entries']]
        else:
            # Handle single video or search
            info = await extract_info(ytdl, url)
            if 'entries' in info:
                # Take first entry if search result
                info = info['entries'][0]
            
            return [{'title': info.get('title', 'Unknown'),
                    'url': info.get('url', None),
                    'webpage_url': info.get('webpage_url', url),
                    'duration': info.get('duration', 0),
                    'video_id': info.get('id', None)}]
    except Exception as e:
        logger.error(f"Error extracting info: {e}")
        # Check for private video error
        error_str = str(e)
        if "Private video" in error_str:
            raise ValueError("This is a private video and requires authentication. Please try a different video.")
        raise

async def get_fresh_stream_url(ytdl, webpage_url):
    """Get a fresh stream URL for playback (to avoid expired URLs)"""
    try:
        info = await extract_info(ytdl, webpage_url)
        if 'entries' in info:
            info = info['entries'][0]
        return info.get('url', None)
    except Exception as e:
        logger.error(f"Error getting fresh stream URL: {e}")
        raise