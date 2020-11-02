import os
from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()

setup(
    name='django-admin-confirm',
    version='0.1',
    packages=['admin_confirm'],
    description='Adds confirmation to Django Admin changes and additions',
    long_description=README,
    author='Thu Trang Pham',
    author_email='thuutrangpham@gmail.com',
    url='https://github.com/trangpham/django-admin-confirm/',
    license='Apache 2.0',
    install_requires=[
        'Django>=1.7',
    ]
)