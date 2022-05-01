import filecmp
import pytest
import tempfile
import os

from pathlib import Path

from dnadoh.cache import FileCache, CONFIG

@pytest.fixture(scope="module")
def cacher():
    cacher = FileCache()    

    # set up default directories
    for dir in [cacher.cache_dir, cacher.remote_url]:
        if not os.path.exists(dir):
            os.mkdir(dir)

    return cacher

# TODO: how to automatically do this after each test?
def _clear_cache(cache_dir):
    """Clears the cache"""
    for x in os.listdir(cache_dir):
        full_path = os.path.join(cache_dir, x)
        if os.path.isfile(full_path):
            os.remove(full_path)


def test_init():
    """Tests that the cache and remote directories are set properly"""
    cache_dir = "/some/test/dir"
    remote = "https://www.github.com"
    cache = FileCache(cache_dir, remote)
    assert cache.cache_dir == cache_dir
    assert cache.remote_url == remote


def test_get_when_not_in_cache(cacher):
    """Tests that when a file is not in the cache, that it is fetched"""
    test_fname = "test.txt"
    target_path = Path(cacher.cache_dir, test_fname)
    source_path = Path(cacher.remote_url, test_fname)
    # remove the file if exists 
    if os.path.exists(target_path):
        os.remove(target_path)
    # create file in remote dir 
    with open(source_path, "w") as fhandle:
        fhandle.write("Hello World!")
    cacher.get(test_fname)
    assert filecmp.cmp(source_path, target_path) is True
    _clear_cache(cacher.cache_dir)


