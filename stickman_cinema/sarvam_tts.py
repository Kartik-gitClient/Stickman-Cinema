"""
Sarvam AI Text-to-Speech (TTS) Integration for Hindi Narration.
Synthesizes per-shot Hindi voiceovers with Sarvam's Bulbul engine.
"""

import os
import base64
import requests
import subprocess

SARVAM_TTS_URL = "https://api.sarvam.ai/text-to-speech"

def get_audio_duration(file_path):
    if not os.path.exists(file_path):
        return 0.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return float(res.stdout.strip())
    except:
        return 0.0

class SarvamVoiceEngine:
    def __init__(self, api_key=None, speaker="shubh", model="bulbul:v1", pace=1.0):
        """
        Initializes the Sarvam AI Hindi Voice Engine.
        
        Args:
            api_key (str): Sarvam API subscription key. If None, reads from SARVAM_API_KEY env var.
            speaker (str): Speaker persona ('shubh', 'arvind', 'amol', 'meera', 'pavithra', etc.)
            model (str): 'bulbul:v1' or 'bulbul:v2'
            pace (float): Speed multiplier (0.5 to 2.0). Default 1.0.
        """
        self.api_key = api_key or os.environ.get("SARVAM_API_KEY", "")
        self.speaker = speaker
        self.model = model
        self.pace = pace

    def synthesize_single(self, text, out_wav_path, target_language_code="hi-IN"):
        """
        Synthesizes a single Hindi sentence and saves it to out_wav_path.
        """
        if not self.api_key:
            raise ValueError("Sarvam API Key is required! Pass api_key or set SARVAM_API_KEY environment variable.")
            
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "inputs": [text],
            "target_language_code": target_language_code,
            "speaker": self.speaker,
            "pitch": 0,
            "pace": self.pace,
            "loudness": 1.5,
            "speech_sample_rate": 44100,
            "enable_preprocessing": True,
            "model": self.model
        }
        
        response = requests.post(SARVAM_TTS_URL, json=payload, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"Sarvam AI Error ({response.status_code}): {response.text}")
            
        data = response.json()
        audio_b64 = data["audios"][0]
        audio_bytes = base64.b64decode(audio_b64)
        
        os.makedirs(os.path.dirname(out_wav_path), exist_ok=True)
        with open(out_wav_path, "wb") as f:
            f.write(audio_bytes)
            
        return get_audio_duration(out_wav_path)

    def synthesize_batch(self, lines, output_dir, min_dur=3.0, max_dur=4.8):
        """
        Synthesizes a full list of Hindi narration lines to sequential WAVs (shot_001.wav, etc.)
        
        Returns:
            list[tuple(str, float)]: (audio_file_path, effective_duration_seconds)
        """
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        print(f"🎙️ Synthesizing {len(lines)} Hindi lines via Sarvam AI ('{self.speaker}')...")
        for idx, text in enumerate(lines):
            shot_pad = f"{idx + 1:03d}"
            out_wav = os.path.join(output_dir, f"shot_{shot_pad}.wav")
            
            if not os.path.exists(out_wav) or os.path.getsize(out_wav) < 1000:
                raw_dur = self.synthesize_single(text, out_wav)
                print(f"   [Shot {shot_pad}/{len(lines)}] ✓ Generated ({raw_dur:.2f}s)")
            else:
                raw_dur = get_audio_duration(out_wav)
                
            effective_dur = max(min_dur, min(raw_dur + 0.25, max_dur))
            results.append((out_wav, effective_dur))
            
        total_time = sum(r[1] for r in results)
        print(f"✓ All {len(lines)} Hindi audio files ready! Total runtime: {total_time:.1f}s ({total_time/60:.2f} mins)")
        return results
