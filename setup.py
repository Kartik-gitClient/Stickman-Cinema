from setuptools import setup, find_packages

setup(
    name="stickman-cinema",
    version="1.0.0",
    description="Autonomous 2D Stickman Video Generation & Pipeline Engine",
    author="Kartik",
    packages=find_packages(),
    install_requires=[
        "Pillow>=9.0.0",
        "soundfile>=0.12.0",
        "numpy>=1.20.0",
        "kokoro-onnx>=0.3.0",
    ],
    entry_points={
        "console_scripts": [
            "stickman-cinema=stickman_cinema.cli:main",
        ],
    },
    python_requires=">=3.8",
)
