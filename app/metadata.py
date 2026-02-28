import requests
import sqlite3
import time
import os

DB_FILE = "albums.db"
USER_AGENT = "MediaAggregator/1.0 ( marwan@example.com )"

def ms_to_time(ms):
    if ms is None:
        return "0:00"
    seconds = int(ms // 1000)
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes}:{remaining_seconds:02d}"

def fetch_album_metadata(album_id, artist, title):
    print(f"Fetching metadata for {artist} - {title} (ID: {album_id})...")
    
    # Search for the release on MusicBrainz
    search_url = "https://musicbrainz.org/ws/2/release/"
    params = {
        'query': f'artist:"{artist}" AND release:"{title}"',
        'fmt': 'json'
    }
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = requests.get(search_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        releases = data.get('releases', [])
        if not releases:
            print("  - Could not find release on MusicBrainz.")
            return False
            
        release_id = releases[0]['id']
        
        # URL for the front cover art
        cover_url = f"https://coverartarchive.org/release/{release_id}/front"
        
        # Get tracks for the release
        details_url = f"https://musicbrainz.org/ws/2/release/{release_id}"
        params = {
            'inc': 'recordings',
            'fmt': 'json'
        }
        
        # Wait a bit to respect rate limit
        time.sleep(1.1)
        
        response = requests.get(details_url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        media = data.get('media', [])
        if not media or not media[0].get('tracks'):
            print("  - No tracks found for this release.")
            return False
            
        tracks = media[0]['tracks']
        
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # First, clear any existing tracks for this album (to avoid duplicates)
        cursor.execute("DELETE FROM favorite_songs WHERE album_id = ?", (album_id,))
        
        total_ms = 0
        for track in tracks:
            track_title = track.get('title')
            duration_ms = track.get('length')
            
            if duration_ms:
                total_ms += duration_ms
                
            duration_str = ms_to_time(duration_ms)
            
            cursor.execute(
                "INSERT INTO favorite_songs (album_id, duration, track_title) VALUES (?, ?, ?)",
                (album_id, duration_str, track_title)
            )
            
        total_runtime = ms_to_time(total_ms)
        
        # Update runtime AND cover
        cursor.execute(
            "UPDATE albums SET runtime = ?, cover = ? WHERE id = ?", 
            (total_runtime, cover_url, album_id)
        )
        
        conn.commit()
        conn.close()
        
        print(f"  - Successfully updated tracks, runtime ({total_runtime}), and cover.")
        return True
        
    except Exception as e:
        print(f"  - Error fetching metadata: {e}")
        return False

if __name__ == "__main__":
    # Example usage: fetch metadata for all albums that don't have a runtime
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    albums = conn.execute("SELECT * FROM albums WHERE runtime IS NULL").fetchall()
    conn.close()
    
    for album in albums:
        fetch_album_metadata(album['id'], album['artist'], album['title'])
        time.sleep(1.1)
