"""
Setup script for FHIR Client package.
"""
from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fhir-client',
    version='1.0.0',
    author='Vijay Tarun Ghadiyaram',
    author_email='vijaytarun555@gmail.com',
    description='A comprehensive Python client for interacting with FHIR servers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/vijaytarun-blip/fhir_client',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests>=2.28.0',
        'urllib3>=1.26.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-cov>=4.0.0',
            'pytest-mock>=3.10.0',
            'black>=23.0.0',
            'flake8>=6.0.0',
            'mypy>=1.0.0',
        ],
        'dotenv': [
            'python-dotenv>=1.0.0',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    keywords='fhir healthcare hl7 api client medical',
    project_urls={
        'Bug Reports': 'https://github.com/vijaytarun-blip/fhir_client/issues',
        'Source': 'https://github.com/vijaytarun-blip/fhir_client',
        'Documentation': 'https://github.com/vijaytarun-blip/fhir_client#readme',
    },
)