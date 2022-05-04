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
    (but only has to specify them once). - done
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

import filecmp
import requests
import shutil
import validators

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
        
        self.files = {}
        
    def get(self, filename):
        """Return path to cached copy of file, getting as needed."""
        if filename not in self.files:
            cache_path = Path(self.cache_dir, filename)
            # check if valid URL, which implies it can be downloaded
            if validators.url(filename) is True:
                if self._download_file(filename, cache_path):
                    self.files[filename] = cache_path
                else:
                    # download failed
                    print(f"{filename} could not be downloaded.")
            else:
                self._get_file(filename, cache_path)
                self.files[filename] = cache_path
        else:
            # 4 - do a further check that the file is actually the same
            if filecmp.cmp(Path(self.cache_dir, filename), Path(self.remote_url, filename)) is True:  # this doesn't work for remote URLs
                return self.files[filename]
            else:
                self._get_file(filename, cache_path)
                self.files[filename] = cache_path

    def clear(self):
        """Clear the cache, deleting local files."""
        self.files.clear()
        for filename in self.cache_dir.iterdir():
            filename.unlink()

    def _get_file(self, remote_path, local_path):
        """Simulate getting a remote file."""
        remote_path = Path(self.remote_url, remote_path)
        # print(remote_path)
        assert remote_path.exists(), f"{remote_path} does not exist"
        shutil.copyfile(remote_path, local_path)

    def _download_file(self, remote_url, local_path):
        """Downloads a file from a remote url"""
        # restrict download size - set 250 MB limit
        h = requests.head(remote_url, allow_redirects=True)
        header = h.headers
        content_length = header.get("content-length", None)
        if content_length > 2.5e-8:  # this is in bytes
            print(f"File is too large")
            return False
        # TODO: file type restrictions?
        r = requests.get(remote_url, allow_redirects=True)
        if r.status_code == 200:
            with open(local_path, "wb") as fhandle:
                fhandle.write(r.content)
            return True
        else:
            return False
