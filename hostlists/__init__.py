import os


_metadata_file = os.path.join(
    os.path.dirname(__file__),
    'package_metadata.json'
)
if os.path.exists(_metadata_file):
    with open(_metadata_file) as fh:
        _package_metadata = json.load(fh)
        __version__ = _package_metadata['version']
else:
    __version__ = '0.0.0'

try:
    from hostlists.hostlists import *
except ImportError:
    from hostlists import *
