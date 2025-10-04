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
        'noplaylist': True,  # Disable playlist processing - only single videos
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'default_search': 'ytsearch',  # Use YouTube search by default
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
    """Get song info from a YouTube URL or search query
    
    Returns:
        tuple: (list of songs, dict with metadata)
    """
    try:
        # Playlists are disabled - only single videos and searches
        if is_youtube_playlist(url):
            raise ValueError("Playlists are not supported. Please add songs individually.")
        
        # Handle single video or search
        logger.info(f"Extracting video info for: {url}")
        info = await extract_info(ytdl, url)
        
        if not info:
            raise ValueError("Could not extract video information")
        
        if 'entries' in info and info['entries']:
            # Take first entry if search result
            info = info['entries'][0]
            if not info:
                raise ValueError("No results found")
        
        title = info.get('title', 'Unknown')
        video_url = info.get('url')
        webpage_url = info.get('webpage_url', url)
        
        # Return single song
        return [{'title': title,
                'url': video_url,
                'webpage_url': webpage_url,
                'duration': info.get('duration', 0),
                'video_id': info.get('id', None)}], {'skipped_count': 0, 'total_entries': 1}
    except Exception as e:
        logger.error(f"Error extracting info: {e}")
        # Check for private video error
        error_str = str(e)
        if "Private video" in error_str or "private video" in error_str.lower():
            raise ValueError("This is a private video and requires authentication. Please try a different video.")
        raise

async def get_fresh_stream_url(ytdl, webpage_url):
    """Get a fresh stream URL for playback (to avoid expired URLs)"""
    try:
        logger.debug(f"Extracting fresh stream URL from: {webpage_url}")
        
        # Create a new ytdl instance with different options for single video extraction
        single_video_opts = get_ytdlp_options()
        single_video_opts['extract_flat'] = False  # Force full extraction
        single_video_opts['noplaylist'] = True  # Don't process as playlist
        
        single_ytdl = yt_dlp.YoutubeDL(single_video_opts)
        
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, lambda: single_ytdl.extract_info(webpage_url, download=False))
        
        if not info:
            logger.error("No info returned from yt-dlp")
            return None
            
        if 'entries' in info and info['entries']:
            info = info['entries'][0]
            
        url = info.get('url')
        
        if not url:
            logger.error(f"No URL in extracted info. Available keys: {info.keys() if info else 'None'}")
            return None
            
        logger.debug(f"Successfully extracted stream URL")
        return url
        
    except Exception as e:
        logger.error(f"Error getting fresh stream URL from {webpage_url}: {e}", exc_info=True)
        return None