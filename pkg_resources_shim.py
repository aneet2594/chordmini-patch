"""
Minimal pkg_resources shim.

This module provides just enough of the pkg_resources API surface
for librosa / audioread / numba / soundfile to import without crashing.
It is NOT a real pkg_resources — it's a lightweight stub that prevents
'No module named pkg_resources' errors in environments where setuptools
cannot be properly installed.
"""


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
    """Return empty string for resource lookups."""
    return ""


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
