""" FileCache - caches files for ModelAdmins with confirmations.

Code modified from: https://github.com/MaistrenkoAnton/filefield-cache/blob/master/filefield_cache/cache.py
Original copy date: April 22, 2021
---
Modified to be compatible with more versions of Django/Python
---
MIT License

Copyright (c) 2020 Maistrenko Anton

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from django.core.files.uploadedfile import InMemoryUploadedFile

try:
    from cStringIO import StringIO as BytesIO  # noqa: WPS433
except ImportError:
    from io import BytesIO  # noqa: WPS433, WPS440

from django.core.cache import cache

from admin_confirm.constants import CACHE_TIMEOUT
from admin_confirm.utils import log


class FileCache(object):
    "Cache file data and retain the file upon confirmation."

    timeout = CACHE_TIMEOUT

    def __init__(self):
        self.cache = cache
        self.cached_keys = []

    def set(self, key, upload):
        """
        Set file data to cache for 1000s

        :param key: cache key
        :param upload: file data
        """
        try:  # noqa: WPS229
            state = {
                "name": upload.name,
                "size": upload.size,
                "content_type": upload.content_type,
                "charset": upload.charset,
                "content": upload.file.read(),
            }
            upload.file.seek(0)
            self.cache.set(key, state, self.timeout)
            log(f"Setting file cache with {key}")
            self.cached_keys.append(key)
        except AttributeError:  # pragma: no cover
            pass  # noqa: WPS420

    def get(self, key):
        """
        Get the file data from cache using specific cache key

        :param key: cache key
        :return: File data
        """
        upload = None
        state = self.cache.get(key)
        if state:
            file = BytesIO()
            file.write(state["content"])
            upload = InMemoryUploadedFile(
                file=file,
                field_name="file",
                name=state["name"],
                content_type=state["content_type"],
                size=state["size"],
                charset=state["charset"],
            )
            upload.file.seek(0)
            log(f"Getting file cache with {key}")
        return upload

    def delete(self, key):
        """
        Delete file data from cache

        :param key: cache key
        """
        self.cache.delete(key)
        self.cached_keys.remove(key)

    def delete_all(self):
        "Delete all cached file data from cache."
        self.cache.delete_many(self.cached_keys)
        self.cached_keys = []
