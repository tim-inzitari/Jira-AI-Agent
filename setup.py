from setuptools import setup, find_packages

setup(
    name="jira-ai-agent",
    version="1.0.0",
    description="AI-powered Jira task management",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=[
        "fastapi>=0.109.1",
        "uvicorn>=0.27.0",
        "pydantic>=2.6.0",
        "python-dotenv>=1.0.0",
        "openai>=1.9.0",
        "aiohttp>=3.9.1",
        "jira>=3.6.0",
        "tenacity>=8.2.3",
        "jinja2>=3.1.3",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.5",
            "pytest-cov>=4.1.0",
            "black>=24.1.1",
            "isort>=5.13.2",
            "mypy>=1.8.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "jira-ai-agent=src.web.app:start",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)