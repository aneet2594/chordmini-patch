"""
Librosa detector service.

This module provides a wrapper around librosa beat detection
with a normalized interface for the beat detection service.

PATCH: Pre-converts MP3 files to WAV via ffmpeg before loading with librosa.
       This avoids the audioread -> pkg_resources dependency chain that
       crashes when setuptools is not installed in the venv.
       soundfile (used by librosa for WAV) has no pkg_resources dependency.
"""

import os
import time
import subprocess
import tempfile
import numpy as np
from typing import Dict, Any, List
from utils.logging import log_info, log_error, log_debug


def _convert_to_wav(input_path: str) -> str:
    """
    Convert an audio file to WAV using ffmpeg.
    Returns the path to the WAV file.
    Raises RuntimeError if ffmpeg is not available or conversion fails.
    """
    # If already a WAV, return as-is
    if input_path.lower().endswith('.wav'):
        return input_path

    wav_path = input_path + '_converted.wav'
    result = subprocess.run(
        ['ffmpeg', '-y', '-i', input_path, '-ar', '22050', '-ac', '1', wav_path],
        capture_output=True, timeout=60
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {result.stderr.decode()[:200]}")
    return wav_path


class LibrosaDetectorService:
    """
    Service wrapper for librosa beat detection with normalized interface.
    """

    def __init__(self):
        """Initialize the librosa detector service."""
        self._available = None

    def is_available(self) -> bool:
        """
        Check if librosa is available.

        Returns:
            bool: True if librosa can be used
        """
        if self._available is not None:
            return self._available

        try:
            import librosa
            self._available = True
            log_debug(f"Librosa availability: {self._available}, version: {getattr(librosa, '__version__', 'unknown')}")
            return True
        except ImportError as e:
            log_error(f"Librosa import failed: {e}")
            self._available = False
            return False

    def detect_beats(self, file_path: str, **kwargs) -> Dict[str, Any]:
        """
        Detect beats in an audio file using librosa.

        Args:
            file_path: Path to the audio file
            **kwargs: Additional parameters (unused for librosa)

        Returns:
            Dict containing normalized beat detection results
        """
        if not self.is_available():
            return {
                "success": False,
                "error": "Librosa is not available",
                "model_used": "librosa",
                "model_name": "Librosa"
            }

        start_time = time.time()
        wav_path = None

        try:
            log_info(f"Running librosa detection on: {file_path}")

            import librosa

            # Pre-convert to WAV so librosa uses soundfile (instead of
            # audioread which calls pkg_resources.iter_entry_points and crashes
            # when setuptools is not properly installed in the venv).
            try:
                wav_path = _convert_to_wav(file_path)
                log_info(f"Converted to WAV for librosa: {wav_path}")
            except Exception as conv_err:
                log_error(f"ffmpeg conversion failed, falling back to direct load: {conv_err}")
                wav_path = file_path   # fallback — may still fail for MP3

            # Load audio (will use soundfile backend for WAV — no pkg_resources needed)
            y, sr = librosa.load(wav_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)

            # Detect beats
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beats, sr=sr)

            # Estimate downbeats (every 4th beat as a simple heuristic)
            downbeat_times = beat_times[::4]

            # Simple time signature detection (default to 4/4)
            time_signature = 4

            processing_time = time.time() - start_time

            log_info(f"Librosa detection successful: {len(beat_times)} beats, {len(downbeat_times)} downbeats")

            return {
                "success": True,
                "beats": beat_times.tolist() if hasattr(beat_times, 'tolist') else list(beat_times),
                "downbeats": downbeat_times.tolist() if hasattr(downbeat_times, 'tolist') else list(downbeat_times),
                "total_beats": len(beat_times),
                "total_downbeats": len(downbeat_times),
                "bpm": float(tempo),
                "time_signature": f"{time_signature}/4",
                "duration": float(duration),
                "model_used": "librosa",
                "model_name": "Librosa",
                "processing_time": processing_time
            }

        except Exception as e:
            error_msg = f"Librosa detection error: {str(e)}"
            log_error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "model_used": "librosa",
                "model_name": "Librosa",
                "processing_time": time.time() - start_time
            }

        finally:
            # Clean up the temporary WAV file if we created one
            if wav_path and wav_path != file_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception:
                    pass
