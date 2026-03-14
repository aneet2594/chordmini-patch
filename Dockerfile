FROM ptnghia/chordminiapp-backend:latest

# Fix 1: pkg_resources shim — needed by ALL detectors for audioread import
COPY pkg_resources_shim.py /opt/venv/lib/python3.10/site-packages/pkg_resources/__init__.py

# Fix 2: Copy missing librosa data file (pre-downloaded from librosa 0.10.1).
# Network calls during buildx are unreliable, so the file is committed to this repo.
# Placed in both locations to cover all possible import paths.
COPY intervals.msgpack /opt/venv/lib/python3.10/site-packages/librosa/core/intervals.msgpack
COPY intervals.msgpack /opt/venv/lib/python3.10/site-packages/librosa/intervals.msgpack

# Fix 3: Relax audio validation — base image's validate_audio_file uses librosa.load
#         which fails for MP3 in some Docker PATH configurations.
COPY audio_utils.py /app/services/audio/audio_utils.py

# Fix 4: Default detector is beat-transformer
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
