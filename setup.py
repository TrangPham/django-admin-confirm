import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    README = f.read()

setup(
    name="django-admin-confirm",
    version="1.2.0",
    packages=["admin_confirm"],
    description=("Adds confirmation to Django Admin changes, additions and actions"),
    long_description_content_type="text/markdown",
    long_description=README,
    author="Thu Trang Pham",
    author_email="thuutrangpham@gmail.com",
    url="https://github.com/trangpham/django-admin-confirm/",
    license="Apache 2.0",
    install_requires=[
        "Django>=4.2",
    ],
    python_requires=">=3.10",
    project_urls={
        "Release Notes": "https://github.com/TrangPham/django-admin-confirm/releases",
    },
    # ISSUE-4: Ensure that package includes template and css folders
    # list files in MANIFEST.in
    include_package_data=True,
    classifiers=[
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.0",
        "Framework :: Django :: 5.1",
        "Framework :: Django :: 5.2",
        "Framework :: Django :: 6.0",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
