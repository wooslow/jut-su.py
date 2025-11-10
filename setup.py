from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="jut-su.py",
    version="0.1.5",
    author="wooslow",
    author_email="private@wooslow.dev",
    description="Modern Python library for parsing anime data from jut.su website",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wooslow/jut-su.py",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "pydantic>=2.0.0",
        "typing-extensions>=4.5.0",
        "fake-useragent>=1.4.0",
    ],
)

