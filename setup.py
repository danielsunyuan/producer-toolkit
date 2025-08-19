#!/usr/bin/env python3

import os
from setuptools import setup, find_packages

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
def parse_requirements(filename):
    """Load requirements from a pip requirements file."""
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

requirements = parse_requirements('requirements.txt')

setup(
    name="producer-toolkit",
    version="1.0.0",
    author="Daniel",
    author_email="your-email@example.com",
    description="A command-line toolkit for music producers to download audio/video from YouTube and extract stems using Spleeter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/producer-toolkit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pt=producer_toolkit.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "producer_toolkit": ["*.md", "docs/*"],
    },
    zip_safe=False,
    keywords="audio, music, youtube, spleeter, stems, separation, download",
)
