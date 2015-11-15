#!/usr/bin/env python

import sys

from setuptools import setup
from hangupsbot.version import __version__

install_requires=[
    "hangups>=0.3.0",
    "appdirs"
]

if sys.version_info < (3, 4):
    install_requires.append("asyncio")

setup(
    name="HangupsBot",
    version=__version__,
    description="Bot for Google Hangouts",
    author="Michal Krenek (Mikos)",
    author_email="m.krenek@gmail.com",
    url="https://github.com/xmikos/hangupsbot",
    license="GNU GPLv3",
    packages=["hangupsbot", "hangupsbot.handlers", "hangupsbot.commands"],
    package_data={
        "hangupsbot": [
            "config.json",
            "locale/*/*/*.mo",
            "locale/*/*/*.po"
        ]
    },
    entry_points={
        "console_scripts": [
            "hangupsbot=hangupsbot.__main__:main"
        ],
    },
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Topic :: Communications :: Chat"
    ]
)
