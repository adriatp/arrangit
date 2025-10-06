from setuptools import setup, find_packages
import os

setup(
    name="planit",
    version="1.0.0",
    description="Git project task manager - Organize and manage your tasks directly from your Git repository",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=['planit'],
    install_requires=[],
    entry_points={
        "console_scripts": [
            "planit=planit.cli:main",
        ],
    },
    author="atp",
    python_requires=">=3.6",
)
