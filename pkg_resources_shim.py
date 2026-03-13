"""
Minimal pkg_resources shim.

This module provides just enough of the pkg_resources API surface
for librosa / audioread / numba / resampy to import and run without crashing.
It is NOT a real pkg_resources — it's a lightweight stub that prevents
'No module named pkg_resources' errors in environments where setuptools
cannot be properly installed.

Key fix: resource_filename() uses importlib.util.find_spec to return
actual on-disk paths so that resampy can find its filter data files
(e.g. data/kaiser_best.npz) that librosa.beat.beat_track() needs.
"""

import os
import importlib.util


class DistributionNotFound(Exception):
    pass


class VersionConflict(Exception):
    pass


class _FakeDistribution:
    """Minimal Distribution stub."""

    def __init__(self, project_name="unknown", version="0.0.0"):
        self.project_name = project_name
        self.version = version
        self.key = project_name.lower()
        self.location = ""

    def __str__(self):
        return f"{self.project_name} {self.version}"


class _FakeWorkingSet(list):
    """Minimal WorkingSet stub."""

    def __init__(self):
        super().__init__()

    def find(self, req):
        return None

    def __iter__(self):
        return iter([])


# Module-level attributes that pkg_resources consumers expect
working_set = _FakeWorkingSet()
__version__ = "0.0.0"


def iter_entry_points(group, name=None):
    """Return an empty iterator — no entry points available."""
    return iter([])


def get_distribution(dist):
    """Return a fake distribution to avoid DistributionNotFound."""
    return _FakeDistribution(str(dist))


def require(*args, **kwargs):
    """No-op require."""
    return []


def resource_filename(package, resource):
    """
    Return the real on-disk path for a package resource.
    Uses importlib.util.find_spec so that packages like resampy can
    find their data files (e.g. data/kaiser_best.npz) at runtime.
    """
    try:
        package_name = str(package).split('.')[0]
        spec = importlib.util.find_spec(package_name)
        if spec and spec.origin:
            package_dir = os.path.dirname(spec.origin)
            return os.path.join(package_dir, resource)
    except Exception:
        pass
    return resource  # return resource name as-is rather than empty string


def resource_string(package, resource):
    """Return empty bytes for resource lookups."""
    return b""


def resource_exists(package, resource):
    """Always return False."""
    return False


def get_entry_map(dist, group=None):
    """Return empty dict."""
    return {}


def resource_isdir(package, resource):
    """Always return False."""
    return False


def declare_namespace(name):
    """No-op namespace declaration."""
    pass
