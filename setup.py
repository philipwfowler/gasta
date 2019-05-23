from setuptools import setup
from vasta import __version__

setup(
    name='vasta',
    version=__version__,
    author='Philip W Fowler',
    author_email="philip.fowler@ndm.ox.ac.uk",
    packages=['vasta'],
    package_data={'': ['../config/*']},
    install_requires=[
        "numpy >= 1.13",
        "PyVCF >= 0.6.8",
        "Biopython >= 1.70",
        "h5py >= 2.8.0"
    ],
    license='MIT',
    scripts=['bin/vasta-run.py'],
    long_description=open('README.md').read(),
    zip_safe=False
)
