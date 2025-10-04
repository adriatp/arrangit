from setuptools import setup, find_packages
import os

setup(
    name="arrangit",
    version="1.0.0",
    description="Gestor de tareas para proyectos Git - Organiza y gestiona tus tareas directamente desde tu repositorio Git",
    long_description=open("README.md").read() if os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "arrangit=arrangit.cli:main",
        ],
    },
    author="atp",
    python_requires=">=3.6",
)
