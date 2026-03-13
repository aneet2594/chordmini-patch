FROM ptnghia/chordminiapp-backend:latest

# Fix 1: pkg_resources shim — needed by ALL detectors for audioread import
COPY pkg_resources_shim.py /opt/venv/lib/python3.10/site-packages/pkg_resources/__init__.py

# Fix 2: Repair corrupted librosa install (missing core data files like intervals.msgpack)
RUN /opt/venv/bin/pip install --no-deps librosa==0.10.1

# Fix 3: Default detector is beat-transformer
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
