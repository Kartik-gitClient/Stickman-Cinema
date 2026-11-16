"""
Fast In-Memory Voice Synthesis Engine.
Integrates Kokoro ONNX to produce 1:1 frame-accurate narration and single-line subtitles.
"""

import os
import subprocess
import tempfile
import inspect
import shutil

DEFAULT_MODEL_PATH = r"C:\Users\karti\.cache\hyperframes\tts\models\kokoro-v1.0.onnx"
DEFAULT_VOICES_PATH = r"C:\Users\karti\.cache\hyperframes\tts\voices\voices-v1.0.bin"

def get_audio_duration(file_path):
    if not os.path.exists(file_path):
        return 0.0
    cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True)
        return float(res.stdout.strip())
    except:
        return 0.0

def format_ass_timestamp(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

class VoiceEngine:
    def __init__(self, model_path=None, voices_path=None):
        self.model_path = model_path or DEFAULT_MODEL_PATH
        self.voices_path = voices_path or DEFAULT_VOICES_PATH
        self._kokoro = None

    def _init_kokoro(self):
        if self._kokoro is not None:
            return
        import kokoro_onnx
        
        kwargs = {}
        if os.name == "nt" and "espeak_config" in inspect.signature(kokoro_onnx.Kokoro.__init__).parameters:
            try:
                import espeakng_loader
                from kokoro_onnx.config import EspeakConfig
                source = espeakng_loader.get_data_path()
                if len(source) >= 200:
                    target = os.path.join(tempfile.gettempdir(), "stickman-espeak-ng-data")
                    if not os.path.isdir(target):
                        staging = target + "." + str(os.getpid())
                        shutil.copytree(source, staging)
                        try:
                            os.rename(staging, target)
                        except OSError:
                            shutil.rmtree(staging, ignore_errors=True)
                    kwargs["espeak_config"] = EspeakConfig(data_path=target)
            except ImportError:
                pass

        self._kokoro = kokoro_onnx.Kokoro(self.model_path, self.voices_path, **kwargs)

    def synthesize_lines(self, lines, output_dir, voice="am_liam", speed=0.98, min_dur=3.0, max_dur=4.8):
        """
        Synthesizes a list of narration lines to individual WAV files.
        Clamps shot duration within [min_dur, max_dur].
        
        Returns:
            list[tuple(str, float)]: List of (audio_path, effective_duration_seconds).
        """
        os.makedirs(output_dir, exist_ok=True)
        import soundfile as sf
        self._init_kokoro()
        
        results = []
        for idx, text in enumerate(lines):
            shot_pad = f"{idx + 1:03d}"
            out_wav = os.path.join(output_dir, f"shot_{shot_pad}.wav")
            
            if not os.path.exists(out_wav) or os.path.getsize(out_wav) < 1000:
                samples, sample_rate = self._kokoro.create(text, voice=voice, speed=speed)
                sf.write(out_wav, samples, sample_rate)
                raw_dur = len(samples) / sample_rate
            else:
                raw_dur = get_audio_duration(out_wav)
                
            effective_dur = max(min_dur, min(raw_dur + 0.25, max_dur))
            results.append((out_wav, effective_dur))
            
        return results

    def generate_single_line_ass(self, lines, durations, output_file, title="Stickman Cinema Subtitles"):
        """
        Generates standard single-line centered .ASS subtitles.
        """
        header = f"""[Script Info]
Title: {title}
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.601
PlayResX: 1920
PlayResY: 1080

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,28,&H00FFFFFF,&H0000D4FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2.5,1.5,2,40,40,75,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        current_time = 0.0
        for text, dur in zip(lines, durations):
            start_str = format_ass_timestamp(current_time)
            end_str = format_ass_timestamp(current_time + dur - 0.08)
            clean_text = text.replace("'", "’")
            events.append(f"Dialogue: 0,{start_str},{end_str},Default,,0,0,0,,{clean_text}")
            current_time += dur
            
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events) + "\n")
        return output_file
