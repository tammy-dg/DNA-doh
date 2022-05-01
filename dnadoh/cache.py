"""Simulate a local cache for remote files.

Tools like DataCorral download files from the cloud on demand.
If there's already a local copy of the file, DC re-uses that
rather than downloading the file again.

`FileCache` simulates this by "downloading" (copying) files
from one local directory to another.  When a caller asks for
a file called "tammy.csv", `FileCache` downloads the file if
its name isn't already in the cache, then returns the path
to the local copy of the file.

Things to change:

1.  Download from URLs using the `requests` library.
2.  Make `FileCache` configurable so that a caller can specify
    a base URL for remote files and the local cache directory
    (but only has to specify them once).
3.  Make `FileCache` able to download both remote files and
    local files.
4.  Check that files whose names are in the cache are actually
    stored locally rather than trusting the cache.
5.  Rebuild the cache from the files that we already have on
    disk, and explain why this is both useful and dangerous.
6.  Explain why we need to be able to clear the cache. (Hint:
    think about testing.)
7.  Discuss why `get` and `clear` are `classmethod` rather than
    `staticmethod`.  # because depends on the cache path?
"""

import requests
import shutil
from pathlib import Path
from urllib.parse import urljoin


CONFIG = {
    "cache": Path(__file__).parent.parent.joinpath("cache"),  # prints DNA-doh rootdir + cache
    "remote": Path(__file__).parent.parent.joinpath("remote"),
}


class FileCache:
    """Cache large remote files."""

    def __init__(self, cache_dir=None, remote_url=None):
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            self.cache_dir = CONFIG["cache"]
        
        if remote_url:
            self.remote_url = remote_url
        else:
            self.remote_url = CONFIG["remote"]
        
    # Map remote filenames to local cached filenames.
    _cache = {}


    @classmethod
    def get(cls, filename):
        """Return path to cached copy of file, getting as needed."""
        if filename not in cls._cache:
            cache_path = Path(CONFIG["cache"], filename)
            _get_file(filename, cache_path)
            cls._cache[filename] = cache_path
        return cls._cache[filename]

    @classmethod
    def clear(cls):
        """Clear the cache, deleting local files."""
        cls._cache.clear()
        for filename in CONFIG["cache"].iterdir():
            filename.unlink()



def _get_file(remote_path, local_path):
    """Simulate getting a remote file."""
    # TODO; how to check if a remote URL
    remote_path = Path(CONFIG["remote"], remote_path)
    # print(remote_path)
    assert remote_path.exists(), f"{remote_path} does not exist"
    shutil.copyfile(remote_path, local_path)
