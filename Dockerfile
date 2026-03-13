FROM ptnghia/chordminiapp-backend:latest

# Patch 1: Drop a minimal pkg_resources shim into the venv.
#           The real setuptools/pkg_resources cannot be installed in this venv,
#           but librosa/audioread/numba need it at import time.
#           This shim provides just enough API surface to prevent crashes.
COPY pkg_resources_shim.py /opt/venv/lib/python3.10/site-packages/pkg_resources/__init__.py

# Patch 2: Override the beat detection auto-selector to prefer librosa (~200MB RAM)
#           instead of madmom (~800MB RAM) which causes SIGKILL on Railway free tier.
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py

# Patch 3: Override the librosa detector to pre-convert MP3→WAV via ffmpeg before
#           loading with soundfile — bypasses audioread entirely.
COPY librosa_detector.py /app/services/detectors/librosa_detector.py
