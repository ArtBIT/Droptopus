from setuptools import setup, find_packages
from os import path
exec(open('droptopus/version.py').read())

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# This call to setup() does all the work
setup(
    name="droptopus",
    version=__version__,
    description="Droptopus is a drag'n'drop router, which routes dropped objects to the designated actions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ArtBIT/Droptopus",
    author="Djordje Ungar",
    author_email="mail@djordjeungar.com",
    license="MIT",
    classifiers=[
        # https://pypi.org/classifiers/
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="sample setuptools development",
    packages=["droptopus"],
    package_data={
        "droptopus": ["assets/*.png"]
    },
    include_package_data=True,
    install_requires=[
        "PyQt5",
        "python-magic",
        "requests>=2.21.0",
        "urllib3==1.24.1",
    ],
    project_urls={
        'Bug Reports': 'https://github.com/ArtBIT/Droptopus/issues',
        'Say Thanks!': 'http://saythanks.io/to/ArtBIT',
        'Source': 'https://github.com/ArtBIT/Droptopus/',
    },
    entry_points={
        'console_scripts': [
            'droptopus=droptopus:main',
        ],
    },
)
