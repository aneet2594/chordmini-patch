"""
Audio processing utilities.

This module provides utility functions for audio processing including
silence trimming, duration calculation, and audio format handling.

PATCHED: All librosa.load() calls replaced with soundfile.read() + ffmpeg
         to avoid the audioread -> pkg_resources crash.
"""

import os
import subprocess
import tempfile
from typing import Tuple, Optional
from utils.logging import log_info, log_error, log_debug


def _load_audio_safe(audio_path: str, sr: Optional[int] = None,
                     duration: Optional[float] = None):
    """
    Load audio using soundfile (via ffmpeg for non-WAV formats).
    Drop-in replacement for librosa.load() that avoids audioread/pkg_resources.

    Returns:
        tuple: (audio_array, sample_rate)
    """
    import numpy as np
    import soundfile as sf

    load_path = audio_path

    # If not WAV, convert via ffmpeg first
    if not audio_path.lower().endswith('.wav'):
        load_path = audio_path + '_tmp.wav'
        cmd = ['ffmpeg', '-y', '-i', audio_path]
        if duration is not None:
            cmd += ['-t', str(duration)]
        if sr is not None:
            cmd += ['-ar', str(sr)]
        cmd += ['-ac', '1', load_path]
        result = subprocess.run(cmd, capture_output=True, timeout=60)
        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr.decode()[:200]}")

    try:
        y, file_sr = sf.read(load_path, dtype='float32', always_2d=False)
        if y.ndim > 1:
            y = y.mean(axis=1)  # mix to mono

        # If duration was requested and file was WAV (no ffmpeg truncation)
        if duration is not None and audio_path.lower().endswith('.wav'):
            max_samples = int(file_sr * duration)
            y = y[:max_samples]

        # Resample if needed (simple case — just return native sr if not specified)
        actual_sr = sr if sr else file_sr
        if sr and sr != file_sr:
            try:
                import librosa
                y = librosa.resample(y, orig_sr=file_sr, target_sr=sr)
            except Exception:
                actual_sr = file_sr  # can't resample, use original

        return y, actual_sr

    finally:
        # Clean up temp WAV if we created one
        if load_path != audio_path and os.path.exists(load_path):
            try:
                os.remove(load_path)
            except Exception:
                pass


def trim_silence_from_audio(audio_path: str, output_path: Optional[str] = None,
                          top_db: int = 20, frame_length: int = 2048,
                          hop_length: int = 512) -> Tuple:
    """
    Trim silence from the beginning and end of an audio file.
    """
    try:
        import librosa
        import soundfile as sf

        y, sr = _load_audio_safe(audio_path)
        y_trimmed, index = librosa.effects.trim(y, top_db=top_db,
                                                 frame_length=frame_length,
                                                 hop_length=hop_length)

        trim_start_time = index[0] / sr
        trim_end_time = index[1] / sr

        log_debug(f"Audio trimming: {len(y)/sr:.3f}s -> {len(y_trimmed)/sr:.3f}s")

        if output_path:
            sf.write(output_path, y_trimmed, sr)

        return y_trimmed, sr, trim_start_time, trim_end_time

    except Exception as e:
        log_error(f"Failed to trim silence: {e}")
        try:
            y, sr = _load_audio_safe(audio_path)
            return y, sr, 0.0, len(y) / sr
        except Exception as load_error:
            log_error(f"Failed to load audio: {load_error}")
            raise


def get_audio_duration(audio_path: str) -> float:
    """Get the duration of an audio file in seconds."""
    try:
        y, sr = _load_audio_safe(audio_path)
        return float(len(y) / sr)
    except Exception as e:
        log_error(f"Failed to get audio duration: {e}")
        return 0.0


def resample_audio(audio_path: str, target_sr: int = 44100) -> Tuple:
    """Resample audio to a target sample rate."""
    try:
        y, sr = _load_audio_safe(audio_path, sr=target_sr)
        log_debug(f"Resampled audio to {target_sr}Hz")
        return y, sr
    except Exception as e:
        log_error(f"Failed to resample audio: {e}")
        raise


def validate_audio_file(audio_path: str) -> bool:
    """
    Validate that an audio file can be loaded and processed.
    Uses ffmpeg probe instead of librosa.load to avoid audioread/pkg_resources.
    """
    try:
        # Fast validation: probe with ffmpeg (no full decode needed)
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True, timeout=10
        )
        if result.returncode == 0:
            duration = float(result.stdout.decode().strip())
            return duration > 0
        return False
    except Exception as e:
        log_error(f"Audio validation failed: {e}")
        # Fallback: just check file exists and has content
        return os.path.exists(audio_path) and os.path.getsize(audio_path) > 0
