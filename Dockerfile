FROM ptnghia/chordminiapp-backend:latest

# pkg_resources is missing from the venv — all detectors fail without it.
# No pip install can fix it in this build context, so use a shim.
COPY pkg_resources_shim.py /opt/venv/lib/python3.10/site-packages/pkg_resources/__init__.py

# Download the single missing librosa data file directly from GitHub.
# The base image has a corrupted librosa install that is missing this file.
RUN wget -q https://raw.githubusercontent.com/librosa/librosa/0.10.1/librosa/intervals.msgpack \
    -O /opt/venv/lib/python3.10/site-packages/librosa/intervals.msgpack

# validate_audio_file() calls librosa.load() which crashes without pkg_resources.
# Patched version uses ffprobe instead — instant, no Python deps.
COPY audio_utils.py /app/services/audio/audio_utils.py

# Default detector: beat-transformer (librosa package data is broken in base image).
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
