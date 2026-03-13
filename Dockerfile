FROM ptnghia/chordminiapp-backend:latest
RUN /opt/venv/bin/pip install --no-cache-dir setuptools
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
