FROM ptnghia/chordminiapp-backend:latest

# Change default detector from librosa (broken in base image) to beat-transformer
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
