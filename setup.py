# setup.py
from setuptools import setup, find_packages

setup(
    name="agll-glyph-vehicle",
    version="1.0.0",
    packages=find_packages(),
    install_requires=open("requirements.txt").readlines(),
    author="Two Mile Solutions LLC",
    description="Interpretable AI for LandBack Governance",
)
from setuptools import setup

setup(
    name="agll-clean-drum",
    version="61.0.0",
    py_modules=["blackbox_defense"],
    install_requires=["opencv-python", "numpy", "matplotlib"],
    author="Two Mile Solutions LLC",
    description="AGŁL v61 — The Clean Drum",
    license="MIT"
)
from setuptools import setup, find_packages

setup(
    name="agll-blackbox",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "opencv-python",
        "numpy",
        "matplotlib"
    ],
    description="BlackBoxDefense for GibberLink v0.3.0",
    author="Two Mile Solutions LLC",
    license="MIT"
)
"""
Feedback Processor Theory - Setup Configuration
Created by John Carroll (Two Mile Solutions LLC)
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_file(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

setup(
    name="feedback-processor-theory",
    version="0.1.0",
    author="John Carroll",
    author_email="contact@twomilesolutions.com",
    description="A framework for self-adaptive intelligence through recursive feedback and resonance",
    long_description=read_file('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/ak-skwaa-mahawk/Feedback_processor_theory",
    packages=find_packages(exclude=['tests*', 'examples*', 'docs*']),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0",
        "matplotlib>=3.4.0",
        "cryptography>=3.4.0",
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=3.0.0',
            'black>=22.0.0',
            'flake8>=4.0.0',
            'mypy>=0.950',
        ],
        'docs': [
            'sphinx>=4.5.0',
            'sphinx-rtd-theme>=1.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'fpt-demo=examples.demo_conversation:main',
            'fpt-verify=tools.verify_backups:main',
        ],
    },
    keywords=[
        'feedback-theory',
        'ai',
        'adaptive-systems',
        'self-reference',
        'ethics',
        'transparency',
        'recursion',
        'linguistics',
        'resonance',
        'consciousness',
    ],
    project_urls={
        "Bug Reports": "https://github.com/ak-skwaa-mahawk/Feedback_processor_theory/issues",
        "Source": "https://github.com/ak-skwaa-mahawk/Feedback_processor_theory",
        "Documentation": "https://github.com/ak-skwaa-mahawk/Feedback_processor_theory/tree/main/docs",
    },
    include_package_data=True,
    zip_safe=False,
)