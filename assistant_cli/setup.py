from setuptools import setup, find_packages

setup(
    name="assistant-cli",
    version="0.1",
    packages=find_packages(),
    install_requires=["click", "requests", "apscheduler", "notify2", "python-dotenv"],
    entry_points={
        "console_scripts": [
            "assistant = assistant.cli:cli"
        ]
    }
)