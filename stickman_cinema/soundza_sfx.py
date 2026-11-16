"""
Soundza API Client & SFX Kit Builder.
Integrates Soundza's library of sound effects, cinematic whooshes, impacts,
alarms, and monster sounds for stickman animation videos.
"""

import os
import requests
import json

SOUNDZA_BASE_URL = "https://api.soundza.com/v1"

def load_env_file():
    """Simple parser to load .env file from root directory."""
    pkg_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(pkg_root, ".env"),
        os.path.join(os.getcwd(), ".env")
    ]
    for env_path in candidates:
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip("'\"")
                        if k and k not in os.environ:
                            os.environ[k] = v

class SoundzaClient:
    def __init__(self, api_key=None):
        load_env_file()
        self.api_key = api_key or os.environ.get("SOUNDZA_API_KEY", "")

    def _get_headers(self):
        headers = {
            "Accept": "application/json",
            "User-Agent": "Stickman-Cinema/1.0"
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def search(self, query, sound_type="sound_effect", per_page=5, page=1):
        """
        Searches Soundza sound effects.
        Works both with or without an API key (key provides higher limits & full download access).
        
        Returns:
            list[dict]: List of sound result objects.
        """
        url = f"{SOUNDZA_BASE_URL}/sounds/search"
        params = {
            "q": query,
            "type": sound_type,
            "per_page": per_page,
            "page": page
        }
        resp = requests.get(url, params=params, headers=self._get_headers(), timeout=30)
        if resp.status_code != 200:
            raise RuntimeError(f"Soundza Search Error ({resp.status_code}): {resp.text}")
            
        data = resp.json()
        return data.get("sounds", [])

    def download_sound(self, sound_id, output_path):
        """
        Downloads full-quality audio file for a given sound ID.
        Requires SOUNDZA_API_KEY.
        """
        if not self.api_key:
            raise ValueError("SOUNDZA_API_KEY is required to download full-quality files! Set it in .env or pass api_key.")
            
        url = f"{SOUNDZA_BASE_URL}/sounds/{sound_id}/file"
        headers = self._get_headers()
        
        # -L follow redirects
        resp = requests.get(url, headers=headers, allow_redirects=True, stream=True, timeout=30)
        if resp.status_code not in (200, 302, 307):
            raise RuntimeError(f"Soundza Download Error ({resp.status_code}): {resp.text}")
            
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        return output_path

    def download_best_match(self, query, output_path, sound_type="sound_effect"):
        """
        Searches for query, picks the highest-ranking sound, and downloads it.
        """
        sounds = self.search(query=query, sound_type=sound_type, per_page=1)
        if not sounds:
            raise ValueError(f"No sounds found for query: '{query}'")
            
        best = sounds[0]
        ext = best.get("file_extension", "wav")
        if not output_path.endswith(f".{ext}") and not output_path.endswith(".wav"):
            output_path = f"{output_path}.{ext}"
            
        return self.download_sound(best["id"], output_path)

    def download_curated_survival_kit(self, output_dir):
        """
        Downloads an essential survival animation SFX kit:
        - whoosh, explosion, crowbar clang, emergency siren, acid hiss, door breach, achievement.
        """
        kit_queries = {
            "sfx_transition_whoosh.wav": "fast whoosh transition",
            "sfx_asteroid_explosion.wav": "huge explosion rumble",
            "sfx_crowbar_impact.wav": "metal iron bar strike clang",
            "sfx_bunker_alarm.wav": "emergency facility siren alarm",
            "sfx_acid_sizzle.wav": "acid chemical hiss sizzle",
            "sfx_heavy_gate_slam.wav": "massive steel blast door slam",
            "sfx_titan_roar.wav": "deep monster roar growl",
            "sfx_achievement_bell.wav": "achievement unlock chime bell"
        }
        
        os.makedirs(output_dir, exist_ok=True)
        print(f"📦 Downloading Curated Survival SFX Kit to {output_dir}...")
        downloaded = {}
        for filename, query in kit_queries.items():
            dest = os.path.join(output_dir, filename)
            try:
                print(f"   Downloading: {filename} ('{query}')...")
                self.download_best_match(query, dest)
                downloaded[filename] = dest
                print(f"   ✓ Saved: {dest}")
            except Exception as e:
                print(f"   ✗ Failed {filename}: {e}")
                
        return downloaded
