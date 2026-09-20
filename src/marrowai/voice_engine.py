from __future__ import annotations

import asyncio
import hashlib
import os
import shutil
import subprocess
import tempfile
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from .config import get_config

# Global LRU Audio Cache for ultra-low latency (<5ms replay)
_AUDIO_CACHE: OrderedDict[str, bytes] = OrderedDict()
_CACHE_MAX_ENTRIES = 256


VOICE_PROFILES: dict[str, dict[str, Any]] = {
    "indian_female": {
        "espeak_voice": "en-in+f2",
        "speed": 150,
        "pitch": 55,
        "label": "Indian English (Female - Neerja)",
        "sapi_voice": "Microsoft Heera",
        "neural_voice": "en-IN-NeerjaNeural",
        "neural_voice_alt": "en-IN-NeerjaExpressiveNeural",
    },
    "indian_male": {
        "espeak_voice": "en-in+m3",
        "speed": 145,
        "pitch": 42,
        "label": "Indian English (Male - Prabhat)",
        "sapi_voice": "Microsoft Ravi",
        "neural_voice": "en-IN-PrabhatNeural",
        "neural_voice_alt": "en-IN-PrabhatNeural",
    },
    "hindi_female": {
        "espeak_voice": "hi",
        "speed": 150,
        "pitch": 55,
        "label": "Hindi / Indian (Female - Swara)",
        "sapi_voice": "Microsoft Kalpana",
        "neural_voice": "hi-IN-SwaraNeural",
        "neural_voice_alt": "hi-IN-SwaraNeural",
    },
    "hindi_male": {
        "espeak_voice": "hi",
        "speed": 145,
        "pitch": 42,
        "label": "Hindi / Indian (Male - Madhur)",
        "sapi_voice": "Microsoft Hemant",
        "neural_voice": "hi-IN-MadhurNeural",
        "neural_voice_alt": "hi-IN-MadhurNeural",
    },
}


@dataclass
class VoiceStatus:
    ok: bool
    engine: str
    message: str
    provider: str
    profile: str = "indian_female"


class OfflineVoiceEngine:
    """Local-first voice engine supporting natural Indian English neural speech synthesis and offline fallback."""

    def __init__(
        self,
        profile: str | None = None,
        speed: int | None = None,
        pitch: int | None = None,
    ) -> None:
        config = get_config()
        self.profile_name = profile or config.voice_profile or "indian_female"
        if self.profile_name not in VOICE_PROFILES:
            self.profile_name = "indian_female"
        self.profile = VOICE_PROFILES[self.profile_name]
        self.speed = speed or config.voice_speed or self.profile["speed"]
        self.pitch = pitch or config.voice_pitch or self.profile["pitch"]
        self.offline_backend = self._detect_offline_backend()
        self.tts_backend = self._detect_tts_backend()
        self.stt_backend = self._detect_stt_backend()

    def set_profile(self, profile_name: str) -> None:
        if profile_name in VOICE_PROFILES:
            self.profile_name = profile_name
            self.profile = VOICE_PROFILES[profile_name]
            self.speed = self.profile["speed"]
            self.pitch = self.profile["pitch"]

    def _check_neural_available(self) -> bool:
        try:
            import edge_tts  # noqa: F401
            return True
        except ImportError:
            pass
        if shutil.which("edge-tts"):
            return True
        local_bin = os.path.expanduser("~/.local/bin/edge-tts")
        return os.path.isfile(local_bin) and os.access(local_bin, os.X_OK)

    def _detect_tts_backend(self) -> str:
        if self._check_neural_available():
            return "neural-edge"
        return self._detect_offline_backend()

    def _detect_offline_backend(self) -> str:
        if shutil.which("powershell.exe") or shutil.which("powershell"):
            return "powershell"
        if shutil.which("espeak-ng"):
            return "espeak-ng"
        if shutil.which("espeak"):
            return "espeak"
        if shutil.which("spd-say"):
            return "spd-say"
        return "fallback"

    def _detect_stt_backend(self) -> str:
        if shutil.which("ffmpeg"):
            return "ffmpeg"
        return "fallback"

    def synthesize_neural_audio(self, text: str, profile_name: str | None = None) -> bytes | None:
        if not text or not text.strip():
            return None

        clean_text = text.replace("*", "").replace("#", "").replace("`", "").strip()[:800]
        if not clean_text:
            return None

        prof = VOICE_PROFILES.get(profile_name or self.profile_name, self.profile)
        candidates = [prof.get("neural_voice", "en-IN-NeerjaNeural")]
        alt = prof.get("neural_voice_alt")
        if alt and alt not in candidates:
            candidates.append(alt)

        for voice_name in candidates:
            # Fast path: check low-latency memory cache
            cache_key = hashlib.sha256(f"{voice_name}:{clean_text}".encode("utf-8")).hexdigest()
            if cache_key in _AUDIO_CACHE:
                _AUDIO_CACHE.move_to_end(cache_key)
                return _AUDIO_CACHE[cache_key]

            # 1. Try Python edge_tts module directly
            try:
                import edge_tts

                async def _generate_stream() -> bytes:
                    comm = edge_tts.Communicate(clean_text, voice_name)
                    chunks = []
                    async for chunk in comm.stream():
                        if chunk["type"] == "audio":
                            chunks.append(chunk["data"])
                    return b"".join(chunks)

                try:
                    loop = asyncio.get_running_loop()
                except RuntimeError:
                    loop = None

                if loop and loop.is_running():
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                        audio_bytes = pool.submit(asyncio.run, _generate_stream()).result(timeout=12)
                else:
                    audio_bytes = asyncio.run(_generate_stream())

                if audio_bytes and len(audio_bytes) > 200:
                    if len(_AUDIO_CACHE) >= _CACHE_MAX_ENTRIES:
                        _AUDIO_CACHE.popitem(last=False)
                    _AUDIO_CACHE[cache_key] = audio_bytes
                    return audio_bytes
            except Exception:
                pass

            # 2. Try CLI edge-tts
            edge_bin = shutil.which("edge-tts")
            if not edge_bin:
                local_bin = os.path.expanduser("~/.local/bin/edge-tts")
                if os.path.isfile(local_bin):
                    edge_bin = local_bin

            if edge_bin:
                try:
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                        out_path = tmp.name
                    cmd = [edge_bin, "--voice", voice_name, "--text", clean_text, "--write-media", out_path]
                    res = subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
                    if res.returncode == 0 and os.path.exists(out_path):
                        with open(out_path, "rb") as f:
                            data = f.read()
                        try:
                            os.unlink(out_path)
                        except Exception:
                            pass
                        if data and len(data) > 200:
                            if len(_AUDIO_CACHE) >= _CACHE_MAX_ENTRIES:
                                _AUDIO_CACHE.popitem(last=False)
                            _AUDIO_CACHE[cache_key] = data
                            return data
                except Exception:
                    pass

        return None

    def synthesize_offline_wav(self, text: str, profile_name: str | None = None) -> bytes | None:
        if not text or not text.strip():
            return None

        clean_text = text.replace("*", "").replace("#", "").replace("`", "").strip()[:800]
        if not clean_text:
            return None

        prof = VOICE_PROFILES.get(profile_name or self.profile_name, self.profile)
        voice = prof.get("espeak_voice", "en-in+f2")
        speed = prof.get("speed", self.speed)
        pitch = prof.get("pitch", self.pitch)

        cache_key = hashlib.sha256(f"wav:{voice}:{clean_text}".encode("utf-8")).hexdigest()
        if cache_key in _AUDIO_CACHE:
            _AUDIO_CACHE.move_to_end(cache_key)
            return _AUDIO_CACHE[cache_key]

        # 1. Try PowerShell SAPI on Windows (natural human voice instead of robotic espeak)
        ps_bin = shutil.which("powershell.exe") or shutil.which("powershell")
        if ps_bin:
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    out_path = tmp.name
                import base64
                b64 = base64.b64encode(clean_text[:600].encode("utf-8")).decode("ascii")
                is_female = "female" in (profile_name or self.profile_name)
                pattern = "Zira|Heera|Female" if is_female else "David|Ravi|Male"
                rate = 1 if speed > 150 else (0 if speed >= 135 else -1)
                ps_script = (
                    f"$txt = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{b64}')); "
                    f"$v = New-Object -ComObject SAPI.SpVoice; "
                    f"$v.Rate = {rate}; "
                    f"foreach ($voice in $v.GetVoices()) {{ if ($voice.GetDescription() -match '{pattern}') {{ $v.Voice = $voice; break }} }}; "
                    f"$f = New-Object -ComObject SAPI.SpFileStream; "
                    f"$f.Open('{out_path}', 3, $false); "
                    f"$v.AudioOutputStream = $f; "
                    f"$v.Speak($txt); "
                    f"$f.Close()"
                )
                res = subprocess.run([ps_bin, "-Command", ps_script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
                if res.returncode == 0 and os.path.exists(out_path) and os.path.getsize(out_path) > 44:
                    with open(out_path, "rb") as f:
                        data = f.read()
                    try:
                        os.unlink(out_path)
                    except Exception:
                        pass
                    if data:
                        if len(_AUDIO_CACHE) >= _CACHE_MAX_ENTRIES:
                            _AUDIO_CACHE.popitem(last=False)
                        _AUDIO_CACHE[cache_key] = data
                        return data
            except Exception:
                pass

        # 2. Try espeak-ng / espeak -w <tmp.wav> as secondary fallback
        espeak_bin = shutil.which("espeak-ng") or shutil.which("espeak")
        if espeak_bin:
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                    out_path = tmp.name
                cmd = [espeak_bin, "-v", voice, "-s", str(speed), "-p", str(pitch), "-w", out_path, clean_text]
                res = subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=12)
                if res.returncode == 0 and os.path.exists(out_path):
                    with open(out_path, "rb") as f:
                        data = f.read()
                    try:
                        os.unlink(out_path)
                    except Exception:
                        pass
                    if data:
                        if len(_AUDIO_CACHE) >= _CACHE_MAX_ENTRIES:
                            _AUDIO_CACHE.popitem(last=False)
                        _AUDIO_CACHE[cache_key] = data
                        return data
            except Exception:
                pass

        return None

    def _play_audio_bytes(self, audio_bytes: bytes) -> bool:
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(audio_bytes)

        played = False
        try:
            if shutil.which("ffplay"):
                res = subprocess.run(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=15,
                )
                if res.returncode == 0:
                    played = True
            elif shutil.which("mpv"):
                res = subprocess.run(
                    ["mpv", "--no-video", "--really-quiet", tmp_path],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=15,
                )
                if res.returncode == 0:
                    played = True
            elif shutil.which("mpg123"):
                res = subprocess.run(
                    ["mpg123", "-q", tmp_path],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=15,
                )
                if res.returncode == 0:
                    played = True
            else:
                ps_bin = shutil.which("powershell.exe") or shutil.which("powershell")
                if ps_bin:
                    playback_path = tmp_path
                    if shutil.which("wslpath") and os.path.exists("/proc/version"):
                        try:
                            wsl_conv = subprocess.run(
                                ["wslpath", "-w", tmp_path],
                                capture_output=True,
                                text=True,
                                check=False,
                                timeout=2,
                            )
                            if wsl_conv.returncode == 0 and wsl_conv.stdout.strip():
                                playback_path = wsl_conv.stdout.strip().replace("\\", "\\\\")
                        except Exception:
                            pass

                    ps_script = (
                        f"$w = New-Object -ComObject WMPlayer.OCX; "
                        f"$w.URL = '{playback_path}'; "
                        f"$w.controls.play(); "
                        f"while($w.playState -eq 3 -or $w.playState -eq 9) {{ Start-Sleep -Milliseconds 100 }}; "
                    )
                    res = subprocess.run(
                        [ps_bin, "-Command", ps_script],
                        check=False,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        timeout=15,
                    )
                    if res.returncode == 0:
                        played = True
        except Exception:
            played = False
        finally:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass

        return played

    def speak(self, text: str, profile_name: str | None = None) -> VoiceStatus:
        if not text or not text.strip():
            return VoiceStatus(False, self.tts_backend, "empty text", "tts", self.profile_name)

        active_prof_name = profile_name or self.profile_name
        prof = VOICE_PROFILES.get(active_prof_name, self.profile)

        # 1. Primary: Natural Expressive Neural Voice
        audio_bytes = self.synthesize_neural_audio(text, active_prof_name)
        if audio_bytes:
            if self._play_audio_bytes(audio_bytes):
                return VoiceStatus(
                    True,
                    "neural-edge",
                    f"spoken via Natural Expressive Neural Voice ({prof['label']})",
                    "tts",
                    active_prof_name,
                )

        # 2. Secondary: Offline Fallback Pipeline
        return self._speak_offline_fallback(text, prof, active_prof_name)

    def _speak_offline_fallback(self, text: str, prof: dict[str, Any], profile_name: str) -> VoiceStatus:
        voice = prof["espeak_voice"]
        speed = prof.get("speed", self.speed)
        pitch = prof.get("pitch", self.pitch)
        backend = self.offline_backend

        if backend in {"espeak-ng", "espeak"}:
            cmd = [backend, "-v", voice, "-s", str(speed), "-p", str(pitch), text]
            try:
                subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
                return VoiceStatus(True, backend, f"spoken via {backend} ({prof['label']})", "tts", profile_name)
            except Exception as exc:
                return VoiceStatus(False, backend, str(exc), "tts", profile_name)

        if backend == "spd-say":
            try:
                subprocess.run(["spd-say", "-t", "female1" if "female" in profile_name else "male1", text], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
                return VoiceStatus(True, "spd-say", "spoken via spd-say", "tts", profile_name)
            except Exception as exc:
                return VoiceStatus(False, backend, str(exc), "tts", profile_name)

        if backend == "powershell":
            import base64
            b64 = base64.b64encode(text[:600].encode("utf-8")).decode("ascii")
            is_female = "female" in profile_name
            pattern = "Zira|Heera|Female" if is_female else "David|Ravi|Male"
            rate = 1 if speed > 150 else (0 if speed >= 135 else -1)
            ps_cmd = (
                f"$txt = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('{b64}')); "
                f"$v = New-Object -ComObject SAPI.SpVoice; "
                f"$v.Rate = {rate}; "
                f"foreach ($voice in $v.GetVoices()) {{ if ($voice.GetDescription() -match '{pattern}') {{ $v.Voice = $voice; break }} }}; "
                f"$v.Speak($txt)"
            )
            try:
                ps_bin = shutil.which("powershell.exe") or "powershell"
                res = subprocess.run([ps_bin, "-Command", ps_cmd], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15)
                if res.returncode == 0:
                    return VoiceStatus(True, "powershell", f"spoken via PowerShell SAPI ({prof['label']})", "tts", profile_name)
                return VoiceStatus(False, "powershell", f"PowerShell returned code {res.returncode}", "tts", profile_name)
            except Exception as exc:
                return VoiceStatus(False, backend, str(exc), "tts", profile_name)

        return VoiceStatus(True, "fallback", "text-only fallback; no speech engine installed", "tts", profile_name)

    def transcribe(self, audio_bytes: bytes | None = None, source_text: str | None = None) -> VoiceStatus:
        if source_text is not None:
            return VoiceStatus(True, self.stt_backend, source_text, "stt", self.profile_name)

        if audio_bytes is None:
            return VoiceStatus(False, self.stt_backend, "no audio provided", "stt", self.profile_name)

        if self.stt_backend == "ffmpeg":
            return VoiceStatus(True, "ffmpeg", "audio bytes accepted for offline transcription pipeline", "stt", self.profile_name)

        return VoiceStatus(True, "fallback", "audio fallback accepted; no speech engine installed", "stt", self.profile_name)

    def status(self) -> dict[str, Any]:
        neural_ok = self._check_neural_available()
        return {
            "tts_backend": self.tts_backend,
            "offline_backend": self.offline_backend,
            "stt_backend": self.stt_backend,
            "active_profile": self.profile_name,
            "profile_label": self.profile["label"],
            "speed": self.speed,
            "pitch": self.pitch,
            "available_profiles": list(VOICE_PROFILES.keys()),
            "voice_ready": self.tts_backend != "fallback" or self.stt_backend != "fallback",
            "neural_tts_active": neural_ok,
            "neural_voice": self.profile.get("neural_voice", "en-IN-NeerjaExpressiveNeural"),
        }


def main() -> None:
    engine = OfflineVoiceEngine()
    print("Voice Engine Status:", engine.status())
    res = engine.speak("Namaste, I am MarrowAI. I am ready to help you.")
    print("Speak test:", res)


if __name__ == "__main__":
    main()
