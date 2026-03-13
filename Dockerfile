FROM ptnghia/chordminiapp-backend:latest

# Fix 1: pkg_resources shim — needed by ALL detectors for audioread import
COPY pkg_resources_shim.py /opt/venv/lib/python3.10/site-packages/pkg_resources/__init__.py

# Fix 2: Repair corrupted librosa install (missing core data files like intervals.msgpack)
RUN /opt/venv/bin/pip install --no-deps librosa==0.10.1

# Fix 3: Relax audio validation — base image's validate_audio_file uses librosa.load
#         which fails for MP3 in some Docker PATH configurations.
#         Patched version just checks file exists and has content.
COPY audio_utils.py /app/services/audio/audio_utils.py

# Fix 4: Default detector is beat-transformer
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py

