FROM ptnghia/chordminiapp-backend:latest

# ALL detectors (beat-transformer, madmom, librosa) fail with
# "No module named 'pkg_resources'" because the venv is missing setuptools
# and pip install cannot fix it in this Docker build environment.
#
# Solution: drop a minimal pkg_resources shim into site-packages.
# The shim provides iter_entry_points (for audioread), get_distribution,
# and resource_filename (using importlib.util so resampy/librosa data files
# resolve to real on-disk paths).
COPY pkg_resources_shim.py /opt/venv/lib/python3.10/site-packages/pkg_resources/__init__.py

# validate_audio_file() in audio_utils.py uses librosa.load() which triggers
# the audioread → pkg_resources chain even before the detector runs.
# Patched version uses ffprobe (instant, no Python deps) for validation.
COPY audio_utils.py /app/services/audio/audio_utils.py

# Default detector: beat-transformer (original author's default).
# Librosa is broken at the data-file level in the base image.
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
