FROM ptnghia/chordminiapp-backend:latest

RUN /opt/venv/bin/pip install --upgrade setuptools
RUN /opt/venv/bin/python -c "import pkg_resources" && echo "pkg_resources OK"

# Default detector is beat-transformer (librosa is broken in base image)
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
