from django.core.files.uploadedfile import SimpleUploadedFile
from admin_confirm.file_cache import FileCache

file = SimpleUploadedFile(
    name="test_file.jpg",
    content=open("screenshot.png", "rb").read(),
    content_type="image/jpeg",
)


def test_should_set_file_cache():
    file_cache = FileCache()
    file_cache.set("key", file)
    assert "key" in file_cache.cached_keys
    assert file_cache.get("key") is not None


def test_should_delete_file_cache():
    file_cache = FileCache()
    file_cache.set("key", file)
    file_cache.delete("key")
    assert "key" not in file_cache.cached_keys
    assert file_cache.get("key") is None


def test_should_delete_all_file_cache():
    file_cache = FileCache()
    file_cache.set("key", file)
    file_cache.set("key2", file)
    file_cache.delete_all()
    assert len(file_cache.cached_keys) == 0
    assert file_cache.get("key") is None
    assert file_cache.get("key2") is None
