from setuptools import setup, find_packages

setup(
    name="assistant-cli",  # Hyphenated for pip
    version="0.1",
    packages=find_packages(),  # Should find assistant_cli and assistant_cli.assistant
    install_requires=["click", "requests", "apscheduler", "notify2", "python-dotenv"],
    entry_points={
        "console_scripts": [
            "assistant = assistant_cli.assistant.cli:cli"  # Correct path
        ]
    }
)