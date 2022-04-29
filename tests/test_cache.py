import filecmp
import pytest
import tempfile
import os

from pathlib import Path

from dnadoh.cache import FileCache, CONFIG

@pytest.fixture(scope="module")
def cacher():
    # set up default directories
    for _,dir in CONFIG.items():
        if not os.path.exists(dir):
            os.mkdir(dir)

    cacher = FileCache()    
    return cacher

# def test_init():
#     """Tests that the cache and remote directories are set properly"""
#     cache_dir = "/some/test/dir"
#     remote = "https://www.github.com"
#     cache = FileCache(cache_dir, remote)
#     assert cache.config["cache"] == cache_dir
#     assert cache.config["remote"] == remote

def test_get_when_not_in_cache(cacher):
    # create file in remote dir first
    test_fname = "test.txt"
    with open(Path(CONFIG["remote"], test_fname), "w") as fhandle:
        fhandle.write("Hello World!")
    cacher.get(test_fname)
    assert filecmp.cmp(Path(CONFIG["remote"], test_fname), Path(CONFIG["cache"], test_fname)) is True
