FROM ptnghia/chordminiapp-backend:latest

# The base image has a corrupted librosa installation (missing intervals.msgpack
# and other data files). Force-reinstall a fresh complete copy without touching
# any other packages.
RUN /opt/venv/bin/pip install --no-cache-dir --force-reinstall librosa

# Override beat_detection_service.py to prefer librosa (~200MB) over madmom (~800MB)
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
