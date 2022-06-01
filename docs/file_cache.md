# Different approaches to implementing a file cache

There are three different ways that we can build a file cache (like the one in `../dnadoh/cache.py`).
This document will briefly discuss each of the approaches.

First an overview of static, class, and instance methods. There are many
articles out there already that compare each the three, so I won't
reiterate them, but I'll link to [one that I found useful](https://realpython.com/instance-class-and-static-methods-demystified/)
and summarize some key points:

* instance methods
  * have access to variables on the same **object** (where an object is an instance of the class)
  * can also access class variables
  * can modify object and class state
* class methods (`@classmethod`)
  * can only access class variable
    * if a class variable is modified, then it is modified across all class objects
  * can modify class state
* static methods (`@staticmethod`)
  * don't have access to either class or instance variables

Let's see what this actually means in the case of the file cache we built, though.

## Instance methods

Our file cache (`../dnadoh/cache.py`) was implemented with instance methods in mind.
This means that each time the `FileCache` is initiated, we are creating a specific 
instance of the cache that would have its own remote and cache directory. 

So I could initiate two different file caches that have different cache directories
where files are downloaded to. For example:

```python
from dnadoh.cache import FileCache

first_cache = FileCache('/tmp/cache_dir_01/', '/tmp/remote_dir/')
second_cache = FileCache('/tmp/cache_dir_01/', '/tmp/remote_dir/'
```

The possibilities of caches are endless because the cache
directory (and the `cache_index`) is bound to the instance of the class,
also known as the Object. 

With the instance methods, all the operations are done on the specific
instance of the FileCache. These methods can't be applied to all
instances of the cache at once, or any other cache.

## Class methods

We could have built our file cache by assigning the cache as a class variable
and then having class methods to manipulate and operate on the file cache.

This would have looked like something like this:

```python
import shutil
from pathlib import Path

CONFIG = {
    "cache": "temp/cache",
    "remote": "temp/remote",
}

class FileCache:
    _cache = {}

    @classmethod
    def get(cls, filename):
        """Return path to cached copy of file, getting as needed."""
        if filename not in cls._cache:
            cache_path = Path(CONFIG["cache"], filename)
            _get_file(filename, cache_path)
            cls._cache[filename] = cache_path
        return cls._cache[filename]
    
def _get_file(remote_path, local_path):
    """Simulate getting a remote file."""
    remote_path = Path(CONFIG["remote"], remote_path)
    assert remote_path.exists(), f"{remote_path} does not exist"
    shutil.copyfile(remote_path, local_path)
```

Since `_cache` is a class variable, this means that the file cache 
would be the same across all FileCache objects and we would only
have one file cache existing (as dictated by `CONFIG`).

To test this, I can do:

```python
first = FileCache
print(first._cache)  # returns '{}'
first.get("test.txt")  

second = FileCache
print(second._cache)  # returns '{'test.txt': PosixPath('temp/cache/test.txt')}'
```

The fact that I created a new instance of the FileCache, `second`,
and printed out the class variable `cache`, and the file that was 
downloaded using the first instance was present,
indicates that the file cache is shared between all instances of the class.
Therefore, it would not have been possible to have multiple, separate
instances of the file cache. 

## Static methods

The final way we could have built the file cache is by strictly using
static methods. By doing so, these functions would not have had access
to class or instance variables and thus, the cache we would like to 
perform our operations on would have to be passed in to each function call.

For example:

```python
import shutil

class FileCache:

    @staticmethod
    def create_file_cache():
        cache = {}
        return cache
    
    @staticmethod
    def get(cache, source_path, destination_path):
        try:
            shutil.copyfile(source_path, destination_path)
            cache[destination_path] = source_path
        except IOError:
            pass
        return cache

cache = FileCache.create_file_cache()
cache = FileCache.get(cache, "temp/remote/test.txt", "temp/cache/test.txt")
print(cache)  # returns {'temp/cache/test.txt': 'temp/remote/test.txt'}
```

I see this implementation as using the `FileCache` class mainly just to organize
functions related to file caching. Management of the file cache itself
would happen outside of the class. Therefore, it is possible to 
have multiple caches floating around by assigning different variables to  `FileCache.create_file_cache()`
and operating on them as necessary with other static methods.

## Final thoughts

There are several different ways that a file cache can be implemented
with no right or wrong way. It just depends on your needs.

Looking at our `../dnadoh/cache.py` code again now,
the remote directory being an instance variable that is assigned
at initialization might be annoying when it comes time to actually use the cache.
That is because a different FileCache object must be created for each 
remote directory/URL that we want to download files from. Perhaps
it would be better to remove the remote directory as an object variable
so that we don't have to create multiple FileCache instances for
each of the different URLs we would like to download from,
despite wanting to use the same cache directory.
