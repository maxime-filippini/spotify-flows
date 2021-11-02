from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()


setup(
    name="flows",
    version="0.1.0",
    description="Spotify automation",
    author="M. Filippini",
    author_email="maxime.filippini@gmaik.com",
    packages=find_packages(),
    python_requires=">=3.7, <4",
    install_requires=["spotipy"],
    extras_require={"dev": ["pytest", "black"]},
    entry_points={"console_scripts": ["flows=spotify_flows.scripts.commands:main"]},
)
