FROM ptnghia/chordminiapp-backend:latest

# Patch 1: Override the beat detection auto-selector to prefer librosa (~200MB RAM)
#           instead of madmom (~800MB RAM) which causes SIGKILL on Railway free tier.
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py

# Patch 2: Override the librosa detector to pre-convert MP3→WAV via ffmpeg before
#           calling librosa.load(). This avoids the audioread→pkg_resources chain
#           that crashes when setuptools is not available in the venv.
#           WAV files are loaded by librosa using soundfile (no pkg_resources needed).
COPY librosa_detector.py /app/services/detectors/librosa_detector.py
