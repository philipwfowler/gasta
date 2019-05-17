from setuptools import setup
from piezo import __version__

setup(
    name='gasta',
    version=__version__,
    author='Philip W Fowler',
    author_email="philip.fowler@ndm.ox.ac.uk",
    packages=['gasta'],
    package_data={'': ['../config/*']},
    install_requires=[
        "numpy >= 1.13",
        "PyVCF >= 0.6.8",
        "Biopython >= 1.70",
    ],
    license='MIT',
    scripts=['bin/gasta-run.py'],
    long_description=open('README.md').read(),
    zip_safe=False
)
