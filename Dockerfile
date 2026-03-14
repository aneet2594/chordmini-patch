FROM ptnghia/chordminiapp-backend:latest

# Fix 1: pkg_resources shim — needed by ALL detectors for audioread import
COPY pkg_resources_shim.py /opt/venv/lib/python3.10/site-packages/pkg_resources/__init__.py

# Download the missing librosa data file — pip install is a no-op (same version
# already installed) so we must patch the file directly.
# Source: librosa/core/intervals.msgpack (verified via GitHub API)
# Destination: both core/ and root of the package to cover all import paths.
RUN /opt/venv/bin/python -c "\
    import urllib.request; \
    url = 'https://raw.githubusercontent.com/librosa/librosa/0.10.1/librosa/core/intervals.msgpack'; \
    urllib.request.urlretrieve(url, '/opt/venv/lib/python3.10/site-packages/librosa/core/intervals.msgpack'); \
    urllib.request.urlretrieve(url, '/opt/venv/lib/python3.10/site-packages/librosa/intervals.msgpack'); \
    print('intervals.msgpack downloaded OK')"

# Fix 3: Relax audio validation — base image's validate_audio_file uses librosa.load
#         which fails for MP3 in some Docker PATH configurations.
#         Patched version just checks file exists and has content.
COPY audio_utils.py /app/services/audio/audio_utils.py

# Fix 4: Default detector is beat-transformer
COPY beat_detection_service.py /app/services/audio/beat_detection_service.py

