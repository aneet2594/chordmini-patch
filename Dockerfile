FROM ptnghia/chordminiapp-backend:latest

# Force-reinstall setuptools into the venv so pkg_resources is available.
# The build-time python check guarantees the image is BROKEN immediately if this fails,
# rather than silently producing an image where librosa crashes at runtime.
RUN /opt/venv/bin/pip install --no-cache-dir --force-reinstall "setuptools>=67.0" && \
    /opt/venv/bin/python -c "import pkg_resources; print('pkg_resources OK:', pkg_resources.__version__)"

COPY beat_detection_service.py /app/services/audio/beat_detection_service.py
