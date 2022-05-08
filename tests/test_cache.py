import csv
import pytest
import os
import pyfakefs

from pathlib import Path
from unittest import mock

from dnadoh.cache import FileCache, CACHE_INDEX, CONFIG, CACHE_HEADER


@pytest.fixture()
def cache(fs):
    for path in CONFIG.values():
        fs.create_dir(path)
    cacher = FileCache()    
    return cacher


@pytest.fixture()
def non_empty_cache(fs):
    for path in CONFIG.values():
        fs.create_dir(path)

    cache = FileCache()    
    
    test_fname = "foo.txt"
    fs.create_file(Path(cache.cache_dir, test_fname))

    return cache

def test_init(fs):
    """Tests that the cache and remote directories are set properly"""
    cache_dir = "/some/test/dir"
    fs.create_dir(cache_dir)
    remote = "https://www.github.com"
    cache = FileCache(cache_dir, remote)
    assert cache.cache_dir == cache_dir
    assert cache.remote_url == remote
    assert Path(cache_dir, CACHE_INDEX).exists()


def test_get_when_not_in_cache(fs, cache):
    """Tests that when a file is not in the cache, that it is fetched"""
    test_fname = "test.txt"
    fs.create_file(Path(cache.remote_url, test_fname))
    cache.get(test_fname)
    assert Path(cache.cache_dir, test_fname).exists()


@mock.patch.object(FileCache, "_get_file")
def test_get_when_cached(mock, non_empty_cache):
    """Tests that when a file is cached, it is not fetched using _get_file()"""
    test_fname = "test.txt"
    non_empty_cache.get(test_fname)
    assert mock.call_count == 1

# not sure why this is failing now
# OSError: Could not find a suitable TLS CA certificate bundle, invalid path: /Users/tammylau/conda/envs/dnadoh_dev/lib/python3.8/site-packages/certifi/cacert.pem
def test_remote_download(cache):
    remote_file = "https://github.com/tammy-dg/tammys-simple-web-server/blob/master/test/test.png"
    cache.get(remote_file)
    print(cache.cache_index)
    cache.clear()


