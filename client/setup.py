from setuptools import setup
from setuptools import find_packages
from ccu import __version__ as v

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='cca',
    version=v,
    author="Chris Allison",
    author_email="chris.allison@hivehome.com",
    url="https://github.com/ConnectedHomes/chaim/client",
    description="Centrica Chaim AWS Accounts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'Click',
        'requests',
        'pyperclip',
        'chardet',
        'certifi',
        ],
    python_requires='>=3',
    entry_points={
        'console_scripts': [
            'cca=ccu.ccu:account',
            'ccm=ccu.ccu:ccm',
        ]
    },
    classifiers=(
        'Development Status :: 4 - Beta',
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: OS Independent",
    ),
)
