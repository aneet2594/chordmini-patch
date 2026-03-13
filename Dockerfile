FROM ptnghia/chordminiapp-backend:latest

RUN /opt/venv/bin/pip install --no-deps librosa==0.10.1

# Default detector: beat-transformer
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
