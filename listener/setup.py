"""Setup script for THE LISTENER."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = [
        line.strip()
        for line in requirements_file.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="the-listener",
    version="0.1.0",
    description="AI companion learning to witness meditation through EEG",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="THE LISTENER Project",
    url="https://github.com/FriendsCoin/EEG",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=requirements,
    python_requires=">=3.9",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Artistic Software",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="eeg meditation ai art neuroscience vae generative-art",
    entry_points={
        "console_scripts": [
            "listener-generate-data=scripts.generate_mock_data:main",
            "listener-train=scripts.train:main",
            "listener-generate=scripts.generate_memories:main",
            "listener-visualize=scripts.visualize:main",
        ],
    },
)
