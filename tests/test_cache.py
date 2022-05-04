import filecmp
import pytest
import tempfile
import os

from pathlib import Path
from unittest import mock

from dnadoh.cache import FileCache

def _create_file_in_remote(test_fname, cacher):
    target_path = Path(cacher.cache_dir, test_fname)
    source_path = Path(cacher.remote_url, test_fname)
    # remove the file if exists 
    if os.path.exists(target_path):
        os.remove(target_path)
    # create file in remote dir 
    with open(source_path, "w") as fhandle:
        fhandle.write("Hello World!")
    return source_path, target_path


@pytest.fixture(scope="module")
def cacher():
    cacher = FileCache()    

    # set up default directories
    for dir in [cacher.cache_dir, cacher.remote_url]:
        if not os.path.exists(dir):
            os.mkdir(dir)

    return cacher


@pytest.fixture(scope="module")
def non_empty_cacher():
    cacher = FileCache()    

    # set up default directories
    for dir in [cacher.cache_dir, cacher.remote_url]:
        if not os.path.exists(dir):
            os.mkdir(dir)
    
    test_fname = "test.txt"
    source_path, target_path = _create_file_in_remote(test_fname, cacher)

    return cacher


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
    source_path, target_path = _create_file_in_remote(test_fname, cacher)
    cacher.get(test_fname)
    assert filecmp.cmp(source_path, target_path) is True
    assert cacher.files[test_fname] == Path(target_path)
    cacher.clear()


@mock.patch.object(FileCache, "_get_file")
def test_get_when_cached(mock, non_empty_cacher):
    """Tests that when a file is cached, it is not fetched using _get_file()"""
    test_fname = "test.txt"
    non_empty_cacher.get(test_fname)
    assert mock.call_count == 1


def test_remote_download(cacher):
    remote_file = "https://github.com/tammy-dg/tammys-simple-web-server/blob/master/test/test.png"
    cacher.get(remote_file)
    assert cacher.files[remote_file] == Path(cacher.cache_dir, "test.png")
    cacher.clear()


