#!/usr/bin/env python3
"""
setup.py

Setuptools configuration for Sudoku Automation Solver.
This file provides fallback build configuration if pyproject.toml alone is insufficient.

Used by: pip, Render, development installations
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sudoku-automation-solver",
    version="4.0.0",
    author="Sudoku Automation Team",
    description="High-accuracy Sudoku extraction and solving system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sudoku-automation-solver",
    license="MIT",
    packages=find_packages(),
    package_data={
        "app": ["services/models/sudoku_digit_mlp.joblib"],
    },
    python_requires=">=3.11,<3.12",
    install_requires=[
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "python-multipart==0.0.6",
        "opencv-python-headless==4.8.1.78",
        "numpy==1.24.3",
        "pydantic==2.5.0",
        "pydantic-settings==2.1.0",
        "scikit-learn==1.3.2",
        "joblib==1.3.2",
        "gunicorn==21.2.0",
    ],
    entry_points={
        "console_scripts": [
            "sudoku-solver=backend.main:app",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ],
)
