import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, "README.md")).read()

setup(
    name="django-admin-confirm",
    version="0.2.4",
    packages=["admin_confirm"],
    description=("Adds confirmation to Django Admin changes, additions and actions"),
    long_description_content_type="text/markdown",
    long_description=README,
    author="Thu Trang Pham",
    author_email="thuutrangpham@gmail.com",
    url="https://github.com/trangpham/django-admin-confirm/",
    license="Apache 2.0",
    install_requires=[
        "Django>=2.2",
    ],
    python_requires=">=3",
    project_urls={
        "Release Notes": "https://github.com/TrangPham/django-admin-confirm/releases",
    },
    # ISSUE-4: Ensure that package includes template and css folders
    # list files in MANIFEST.in
    include_package_data=True,
    classifiers=[
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3 :: Only",
    ],
)
